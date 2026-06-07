import streamlit as st
import pandas as pd
import sqlite3
import importlib
import tools.category_rules
import tools.classify_check

importlib.reload(tools.category_rules)
importlib.reload(tools.classify_check)

from tools.classify_check import classify

st.set_page_config(layout='wide', page_title='CSV Viewer')
st.title('Base CSV Viewer')
st.write('Transactions from all accounts, categorised automatically.')

DB_PATH = __import__('pathlib').Path(__file__).parent / 'transactions.db'
ACCOUNTS = ['Everyday', 'Savings', 'Short-Term']


def load_and_classify(account: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Balance', 'Category'])

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        'SELECT date AS Date, description AS Description, amount AS Amount, balance AS Balance '
        'FROM transactions WHERE account = ? ORDER BY date DESC',
        conn,
        params=(account,),
    )
    conn.close()

    if df.empty:
        return df

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Category'] = df.apply(lambda row: classify(row['Description'], row['Amount']), axis=1)
    return df


if not DB_PATH.exists():
    st.warning('No database found. Run `python tools/import_csv.py` to import your CSV files first.')
    st.stop()


with st.sidebar:
    st.header('DATA Import')
    if st.button('Import CSVs', use_container_width=True):
        import subprocess
        result = subprocess.run(
            ['python', 'tools/import_csv.py'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            st.success(result.stdout)
        else:
            st.error(result.stderr)

tabs = st.tabs(ACCOUNTS)

for tab, account in zip(tabs, ACCOUNTS):
    with tab:
        df = load_and_classify(account)
        st.subheader(account)

        if df.empty:
            st.warning(f'No transactions found for {account}. Run `python tools/import_csv.py` to import.')
            continue

        category_counts = (
            df['Category'].value_counts()
            .rename_axis('Category')
            .reset_index(name='Count')
        )
        st.caption(f'{len(df)} transactions · {df["Category"].nunique()} categories')

        col1, col2 = st.columns([1, 3])
        with col1:
            st.dataframe(category_counts, use_container_width=True, hide_index=True)
        with col2:
            category_options = ['All'] + sorted(df['Category'].unique().tolist())
            selected = st.selectbox('Filter by category', category_options, key=f'cat-{account}')
            view_df = df if selected == 'All' else df[df['Category'] == selected]
            st.dataframe(view_df.reset_index(drop=True), use_container_width=True, height=520)