import streamlit as st
import pandas as pd
import sqlite3
import subprocess
import importlib
import tools.category_rules
import tools.classify_check
from pathlib import Path

importlib.reload(tools.category_rules)
importlib.reload(tools.classify_check)

from tools.classify_check import classify

st.set_page_config(layout='wide', page_title='Finance', page_icon='💰')

DB_PATH = Path(__file__).parent / 'transactions.db'
ACCOUNTS = ['Everyday', 'Savings', 'Short-Term', 'All accounts']

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: var(--background-color); }
[data-testid="stSidebar"] hr { margin: 0.5rem 0; opacity: 0.3; }
div[data-testid="metric-container"] {
    background: #f8f8f6;
    border: 0.5px solid rgba(0,0,0,0.08);
    border-radius: 10px;
    padding: 0.75rem 1rem;
}
.stTabs [data-baseweb="tab"] { font-size: 13px; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_account(account: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Balance', 'Category'])

    conn = sqlite3.connect(DB_PATH)
    if account == 'All accounts':
        df = pd.read_sql_query(
            'SELECT account AS Account, date AS Date, description AS Description, '
            'amount AS Amount, balance AS Balance FROM transactions ORDER BY date DESC',
            conn,
        )
    else:
        df = pd.read_sql_query(
            'SELECT date AS Date, description AS Description, amount AS Amount, balance AS Balance '
            'FROM transactions WHERE account = ? ORDER BY date DESC',
            conn, params=(account,),
        )
    conn.close()

    if df.empty:
        return df

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Category'] = df.apply(lambda r: classify(r['Description'], r['Amount']), axis=1)

    def parse_amount(a):
        try:
            return float(str(a).replace('$', '').replace(',', '').strip())
        except Exception:
            return 0.0

    df['_amt'] = df['Amount'].apply(parse_amount)
    return df


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('### 💰 Finance')
    st.markdown('---')

    st.markdown('**Accounts**')
    account = st.radio('account', ACCOUNTS, label_visibility='collapsed')

    st.markdown('---')
    st.markdown('**Import**')
    if st.button('⬆ Import CSVs', use_container_width=True):
        with st.spinner('Importing...'):
            result = subprocess.run(
                ['python', 'tools/import_csv.py'],
                capture_output=True, text=True, cwd=Path(__file__).parent
            )
        if result.returncode == 0:
            st.success(result.stdout)
            st.cache_data.clear()
        else:
            st.error(result.stderr or 'Import failed.')


# ── Load data ──────────────────────────────────────────────────────────────────
if not DB_PATH.exists():
    st.warning('No database found. Click **Import CSVs** in the sidebar to get started.')
    st.stop()

df = load_account(account)

if df.empty:
    st.warning(f'No transactions found for **{account}**.')
    st.stop()


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f'## {account}')

credits = df[df['_amt'] > 0]['_amt'].sum()
debits  = df[df['_amt'] < 0]['_amt'].sum()
net     = credits + debits

c1, c2, c3, c4 = st.columns(4)
c1.metric('Money in',      f'${credits:,.0f}')
c2.metric('Money out',     f'${abs(debits):,.0f}')
c3.metric('Net',           f'${net:+,.0f}')
c4.metric('Transactions',  len(df))

st.markdown('---')


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_tx, tab_chart, tab_cats = st.tabs(['Transactions', 'Spending chart', 'Category breakdown'])


# ── Tab 1: Transactions ────────────────────────────────────────────────────────
with tab_tx:
    col_filter, col_search = st.columns([2, 3])

    with col_filter:
        all_cats = sorted(df['Category'].unique().tolist())
        selected_cat = st.selectbox('Category', ['All'] + all_cats)

    with col_search:
        search = st.text_input('Search description', placeholder='e.g. KFC, Woolworths...')

    col_left, col_right = st.columns([1, 3])

    with col_left:
        st.markdown('**Categories**')
        cat_counts = df['Category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        cat_totals = df.groupby('Category')['_amt'].sum().abs().reset_index()
        cat_totals.columns = ['Category', 'Total']
        cat_summary = cat_counts.merge(cat_totals, on='Category')
        cat_summary['Total'] = cat_summary['Total'].apply(lambda x: f'${x:,.0f}')
        st.dataframe(
            cat_summary,
            use_container_width=True,
            hide_index=True,
            height=480,
        )

    with col_right:
        view = df.copy()
        if selected_cat != 'All':
            view = view[view['Category'] == selected_cat]
        if search:
            view = view[view['Description'].str.contains(search, case=False, na=False)]

        display_cols = ['Date', 'Description', 'Amount', 'Category']
        if 'Account' in view.columns:
            display_cols = ['Account'] + display_cols

        st.dataframe(
            view[display_cols].reset_index(drop=True),
            use_container_width=True,
            height=520,
        )


# ── Tab 2: Spending chart ──────────────────────────────────────────────────────
with tab_chart:
    debits_only = df[df['_amt'] < 0].copy()
    debits_only['Month'] = debits_only['Date'].dt.to_period('M').astype(str)

    monthly = debits_only.groupby('Month')['_amt'].sum().abs().reset_index()
    monthly.columns = ['Month', 'Spent']
    monthly = monthly.sort_values('Month')

    if monthly.empty:
        st.info('No spending data to chart.')
    else:
        st.markdown('**Monthly spending**')
        st.bar_chart(monthly.set_index('Month')['Spent'], use_container_width=True)

        st.markdown('**Spending by category**')
        cat_spend = debits_only.groupby('Category')['_amt'].sum().abs().sort_values(ascending=False).reset_index()
        cat_spend.columns = ['Category', 'Spent']
        st.bar_chart(cat_spend.set_index('Category')['Spent'], use_container_width=True)


# ── Tab 3: Category breakdown ──────────────────────────────────────────────────
with tab_cats:
    selected_drill = st.selectbox('Pick a category to drill into', all_cats)

    drilled = df[df['Category'] == selected_drill].copy()

    d1, d2, d3 = st.columns(3)
    d1.metric('Transactions', len(drilled))
    d2.metric('Total spent',  f"${drilled[drilled['_amt'] < 0]['_amt'].sum().__abs__():,.2f}")
    d3.metric('Avg per transaction', f"${drilled['_amt'].abs().mean():,.2f}")

    st.markdown(f'**All {selected_drill} transactions**')
    display_cols = ['Date', 'Description', 'Amount']
    if 'Account' in drilled.columns:
        display_cols = ['Account'] + display_cols
    st.dataframe(
        drilled[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=440,
    )