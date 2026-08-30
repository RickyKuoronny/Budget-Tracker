import streamlit as st
import os
import calendar
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import subprocess
import importlib
import tools.category_rules
import tools.classify_check
from pathlib import Path
from datetime import date, timedelta
import re

importlib.reload(tools.category_rules)
importlib.reload(tools.classify_check)

from tools.classify_check import classify

# Consistent color mapping for all categories
CATEGORY_COLORS = {
    'Transfers': '#95A5A6',
    'Revolut': '#3498DB',
    'Giving': '#E74C3C',
    'Refunds': '#2ECC71',
    'Reimbursements': '#9B59B6',
    'Income': '#27AE60',
    'Mobile Phone': '#1ABC9C',
    'Utilities & Subscriptions': '#F39C12',
    'Groceries': '#E67E22',
    'Food & Dining': '#D35400',
    'Transport': '#34495E',
    'Sports & Recreation': '#16A085',
    'Health': '#C0392B',
    'Shopping': '#8E44AD',
    'Entertainment': '#2980B9',
    'Travel': '#16A085',
    'Experiences': '#D68910',
    'Cash': '#7F8C8D',
    'Unsorted': '#BDC3C7',
}

st.set_page_config(layout='wide', page_title='Finance', page_icon='💰')

st.write("WATCHING FILE:", os.path.abspath(__file__))
DB_PATH = Path(__file__).parent / 'transactions.db'
ACCOUNTS = ['Everyday', 'Savings', 'Short-Term', 'All accounts']

CATEGORY_ICONS = {
    'Food & Dining':             '🍜',
    'Groceries':                 '🛒',
    'Transport':                 '🚗',
    'Shopping':                  '🛍️',
    'Health':                    '💊',
    'Entertainment':             '🎮',
    'Sports & Recreation':       '🏃',
    'Utilities & Subscriptions': '📱',
    'Mobile Phone':              '📞',
    'Travel':                    '✈️',
    'Experiences':               '🎭',
    'Giving':                    '🙏',
    'Income':                    '💵',
    'Transfers':                 '↔️',
    'Reimbursements':            '↩️',
    'Refunds':                   '↩️',
    'Cash':                      '💸',
    'Unsorted':                  '❓',
}

QUICK_RANGES = [
    'Today',
    'Last 7 days',
    'This month',
    'Last 3 months',
    'Last 6 months',
    'This year',
    'All time',
    'Custom range',
]

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base typography ── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
}
.block-container { padding-top: 1.75rem; max-width: 1200px; }
.stTabs [data-baseweb="tab"] { font-size: 14px; font-weight: 500; }
[data-testid="stSidebar"] hr { margin: 0.5rem 0; opacity: 0.25; }

/* ── Summary cards ── */
.card {
    background: #fafafa;
    border: 1px solid #ebebeb;
    border-radius: 14px;
    padding: 1.1rem 1.3rem 1rem;
    margin-bottom: 0.5rem;
}
.card-label {
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.35rem;
}
.card-value {
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #111;
    line-height: 1;
}
.card-sub {
    font-size: 0.8rem;
    color: #9ca3af;
    margin-top: 0.3rem;
}
.card-trend-good { color: #16a34a; font-size: 0.82rem; font-weight: 500; margin-top: 0.25rem; }
.card-trend-bad  { color: #dc2626; font-size: 0.82rem; font-weight: 500; margin-top: 0.25rem; }

/* ── Date range pill row ── */
.range-label {
    display: inline-block;
    font-size: 0.82rem;
    font-weight: 500;
    color: #374151;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 0.3rem 0.85rem;
    margin-bottom: 1rem;
}

/* ── Section divider label ── */
.tx-group-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #c4c8d0;
    padding: 0.9rem 0.5rem 0.3rem;
}

/* ── Transaction row ── */
.tx-row {
    display: flex;
    align-items: center;
    padding: 0.6rem 0.6rem;
    border-radius: 10px;
    margin-bottom: 2px;
    gap: 0.8rem;
    transition: background 0.1s;
}
.tx-row:hover { background: #f5f6f8; }

.tx-icon {
    font-size: 1.2rem;
    min-width: 32px;
    text-align: center;
    line-height: 1;
}
.tx-body { flex: 1; min-width: 0; }
.tx-desc {
    font-size: 0.92rem;
    font-weight: 500;
    color: #1f2937;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.tx-cat {
    font-size: 0.73rem;
    color: #9ca3af;
    margin-top: 1px;
}
.tx-date-inline {
    font-size: 0.73rem;
    color: #9ca3af;
    min-width: 50px;
    text-align: right;
}
.tx-amt {
    font-size: 0.97rem;
    font-weight: 600;
    min-width: 82px;
    text-align: right;
    letter-spacing: -0.01em;
}
.tx-amt.debit  { color: #dc2626; }
.tx-amt.credit { color: #16a34a; }

/* ── Category progress bars ── */
.bbar { margin-bottom: 0.9rem; }
.bbar-top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 5px;
}
.bbar-name {
    font-size: 0.88rem;
    font-weight: 500;
    color: #1f2937;
}
.bbar-count {
    font-size: 0.73rem;
    color: #9ca3af;
    margin-left: 5px;
}
.bbar-amount {
    font-size: 0.88rem;
    font-weight: 600;
    color: #111;
}
.bbar-track {
    background: #f0f0f0;
    border-radius: 99px;
    height: 7px;
    overflow: hidden;
}
.bbar-fill {
    height: 7px;
    border-radius: 99px;
    background: #6366f1;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def parse_amount(a) -> float:
    try:
        return float(str(a).replace('$', '').replace(',', '').strip())
    except Exception:
        return 0.0


_NOISE = re.compile(
    r'^(VISA PURCHASE\s*|EFTPOS WDL\s*|EFTPOS DEP\s*|OSKO PAYMENT (TO|FROM)\s*'
    r'|NPP PAYMENT (FROM|TO)\s*|INTERNET TRANSFER (DEBIT TO|CREDIT FROM)\s*'
    r'|DIRECT CREDIT\s*|BPAY DEBIT VIA INTERNET\s*)',
    re.I
)

def clean_desc(raw: str) -> str:
    """Strip leading bank boilerplate for display."""
    s = re.sub(_NOISE, '', str(raw)).strip()
    # Remove trailing location junk like "TOOWONG      15/03 AU AUD"
    s = re.sub(r'\s{2,}\S+\s+\d{2}/\d{2}\s+\w+\s+\w+$', '', s).strip()
    s = re.sub(r'\s{2,}', ' ', s)
    return s if s else raw


def quick_range(label: str) -> tuple[date, date]:
    today = date.today()

    if label == 'Today':
        return today, today

    if label == 'Last 7 days':
        return today - timedelta(days=6), today

    if label == 'This month':
        return date(today.year, today.month, 1), today

    if label == 'Last 3 months':
        return today - timedelta(days=89), today

    if label == 'Last 6 months':
        return today - timedelta(days=179), today

    if label == 'This year':
        return date(today.year, 1, 1), today

    return date(2000, 1, 1), today   # All time


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

    df['Date']     = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Category'] = df.apply(lambda r: classify(r['Description'], r['Amount']), axis=1)
    df['_amt']     = df['Amount'].apply(parse_amount)
    df['_display'] = df['Description'].apply(clean_desc)
    return df


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('### 💰 Finance')
    st.markdown('---')

    st.markdown('**Account**')
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
    st.warning('No database found — click **Import CSVs** in the sidebar to get started.')
    st.stop()

df = load_account(account)

if df.empty:
    st.warning(f'No transactions found for **{account}**.')
    st.stop()

df['_month'] = df['Date'].dt.to_period('M')


# ── Date range selector ────────────────────────────────────────────────────────
st.markdown(f'## {account}')

rc1, rc2, rc3 = st.columns([2, 2, 3])

with rc1:
    range_mode = st.selectbox('Date range', QUICK_RANGES, index=2, label_visibility='collapsed')

if range_mode == 'Custom range':
    with rc2:
        start_date = st.date_input('From', value=date.today() - timedelta(days=29),
                                   key='cust_start', label_visibility='collapsed')
    with rc3:
        end_date = st.date_input('To', value=date.today(),
                                 key='cust_end', label_visibility='collapsed')
else:
    start_date, end_date = quick_range(range_mode)

start_ts = pd.Timestamp(start_date)
end_ts   = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

df_range = df[(df['Date'] >= start_ts) & (df['Date'] <= end_ts)].copy()

# Range label pill
if range_mode == 'Custom range':
    range_str = f"{start_date.day} {start_date.strftime('%b %Y')} – {end_date.day} {end_date.strftime('%b %Y')}"
else:
    range_str = range_mode
    if range_mode not in ('Today', 'This year', 'All time'):
        range_str += (
        f"  ·  "
        f"{start_date.day} {start_date.strftime('%b')} – "
        f"{end_date.day} {end_date.strftime('%b %Y')}"
)

st.markdown(f'<div class="range-label">📅 {range_str}</div>', unsafe_allow_html=True)


# ── Summary cards ──────────────────────────────────────────────────────────────
clean = df_range[df_range["Category"] != "Transfers"]

debits_range = clean[clean['_amt'] < 0]
credits_range = clean[clean['_amt'] > 0]

this_spend  = abs(debits_range['_amt'].sum())
this_income = credits_range['_amt'].sum()
this_net    = this_income - this_spend
transfer_total = (df_range[df_range["Category"] == "Transfers"]["_amt"].abs().sum()) / 2

# Previous equivalent period for comparison
period_days = max((end_date - start_date).days, 1)
prev_start  = start_date - timedelta(days=period_days)
prev_end    = start_date - timedelta(days=1)
prev_ts_s   = pd.Timestamp(prev_start)
prev_ts_e   = pd.Timestamp(prev_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
prev_spend  = abs(df[(df['Date'] >= prev_ts_s) & (df['Date'] <= prev_ts_e) & (df['_amt'] < 0)]['_amt'].sum())

spend_delta = this_spend - prev_spend

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if prev_spend > 0:
        arrow = '▲' if spend_delta > 0 else '▼'
        cls   = 'card-trend-bad' if spend_delta > 0 else 'card-trend-good'
        trend = f'<div class="{cls}">{arrow} ${abs(spend_delta):,.0f} vs prior period</div>'
    else:
        trend = ''
    st.markdown(f"""
    <div class="card">
        <div class="card-label">Spent</div>
        <div class="card-value">${this_spend:,.0f}</div>
        <div class="card-sub">{range_str.split('·')[0].strip()}</div>
        {trend}
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">Income</div>
        <div class="card-value" style="color:#16a34a">${this_income:,.0f}</div>
        <div class="card-sub">{range_str.split('·')[0].strip()}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    net_color = '#16a34a' if this_net >= 0 else '#dc2626'
    st.markdown(f"""
    <div class="card">
        <div class="card-label">Net</div>
        <div class="card-value" style="color:{net_color}">${this_net:+,.0f}</div>
        <div class="card-sub">income minus spending</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">Transactions</div>
        <div class="card-value">{len(df_range)}</div>
        <div class="card-sub">{len(df):,} total in history</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">Transfers</div>
        <div class="card-value">${transfer_total:,.0f}</div>
        <div class="card-sub">Excluded in spending</div>
    </div>""", unsafe_allow_html=True)

st.markdown('---')


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_tx, tab_chart, tab_cats = st.tabs(['📋  Transactions', '📊  Spending chart', '🗂  Category breakdown'])


# ── Tab 1: Transactions ────────────────────────────────────────────────────────
with tab_tx:
    f1, f2 = st.columns([2, 3])
    with f1:
        all_cats = sorted(df_range['Category'].unique().tolist())
        selected_cat = st.selectbox('Category', ['All'] + all_cats, key='cat_filter')
    with f2:
        search = st.text_input('Search', placeholder='e.g. KFC, Woolworths…', key='tx_search')

    view = df_range.copy()
    if selected_cat != 'All':
        view = view[view['Category'] == selected_cat]
    if search:
        view = view[view['Description'].str.contains(search, case=False, na=False)
                  | view['_display'].str.contains(search, case=False, na=False)]

    # 1. Ensure the Date column is a datetime type and sort it descending (newest first)
    view['Date'] = pd.to_datetime(view['Date'])
    view = view.sort_values('Date', ascending=False)

    today_d     = date.today()
    yesterday_d = today_d - timedelta(days=1)

    def date_group(d: pd.Timestamp) -> str:
        if pd.isna(d): return 'Unknown'
        dd = d.date()
        if dd == today_d:     return 'Today'
        if dd == yesterday_d: return 'Yesterday'
        if dd.year == today_d.year:
            return f"{d.strftime('%A')}, {d.day} {d.strftime('%b')}"     # "Monday, 3 Jun"
        return f"{d.strftime('%A')}, {d.day} {d.strftime('%b %Y')}"

    # 2. Assign the display string group
    view['_group'] = view['Date'].apply(date_group)

    if view.empty:
        st.info('No transactions match your filters.')
    else:
        rows_html = []
        
        # 3. FIX: Use loop-based ordering from the already sorted DataFrame.
        # By iterating through unique groups in the order they naturally appear in 'view',
        # they are automatically perfectly sorted from newest to oldest.
        for grp in view['_group'].unique():
            rows_html.append(f'<div class="tx-group-header">{grp}</div>')

            group_df = view[view['_group'] == grp]

            for _, row in group_df.iterrows():
                icon    = CATEGORY_ICONS.get(row['Category'], '•')
                amt     = row['_amt']
                cls     = 'credit' if amt > 0 else 'debit'
                amt_str = f"+${amt:,.2f}" if amt > 0 else f"−${abs(amt):,.2f}"
                desc    = str(row['_display'])
                if len(desc) > 52:
                    desc = desc[:49] + '…'

                rows_html.append(f"""
                <div class="tx-row">
                <span class="tx-icon">{icon}</span>
                <span class="tx-body">
                    <div class="tx-desc">{desc}</div>
                    <div class="tx-cat">{row['Category']}</div>
                </span>
                <span class="tx-amt {cls}">{amt_str}</span>
                </div>""")

        st.markdown(''.join(rows_html), unsafe_allow_html=True)
        st.caption(f'{len(view):,} transaction{"s" if len(view) != 1 else ""} shown')

# ── Tab 2: Spending chart ──────────────────────────────────────────────────────
with tab_chart:
    debits_df = df[df['_amt'] < 0].copy()
    debits_df['_month'] = debits_df['Date'].dt.to_period('M')

    monthly = (
        debits_df.groupby('_month')['_amt']
        .sum().abs()
        .reset_index()
        .rename(columns={'_month': 'Month', '_amt': 'Spent'})
        .sort_values('Month')
    )
    monthly['Month'] = monthly['Month'].apply(lambda p: pd.Period(p, 'M').strftime('%b %Y'))

    if monthly.empty:
        st.info('No spending data to chart.')
    else:
        st.markdown('**Monthly spending — all time**')
        st.bar_chart(monthly.set_index('Month')['Spent'], use_container_width=True)

        st.markdown(f'**Top categories — {range_str.split("·")[0].strip()}**')
        cat_spend = (
            debits_range.groupby('Category')['_amt']
            .sum().abs()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        cat_spend.columns = ['Category', 'Spent']
        cat_spend['Category'] = cat_spend['Category'].apply(
            lambda c: f"{CATEGORY_ICONS.get(c, '')} {c}"
        )
        st.bar_chart(cat_spend.set_index('Category')['Spent'], use_container_width=True)


# ── Tab 3: Category breakdown ──────────────────────────────────────────────────
with tab_cats:

    # ─────────────────────────────────────────────
    # BASE DATA (REMOVE TRANSFERS FROM EVERYTHING)
    # ─────────────────────────────────────────────
    base = df_range.copy()

    spent_all = base[
        (base['_amt'] < 0) &
        (base['Category'] != 'Transfers')
    ].copy()

    # ─────────────────────────────────────────────
    # PIE CHART (GLOBAL ONLY, NO DRILL IMPACT)
    # ─────────────────────────────────────────────
    pie_data = (
        spent_all.groupby('Category')['_amt']
        .sum()
        .abs()
        .reset_index()
        .rename(columns={'_amt': 'Spent'})
    )

    if not pie_data.empty:
        # Map colors to categories
        pie_colors = [CATEGORY_COLORS.get(cat, '#BDC3C7') for cat in pie_data['Category']]
        
        fig = px.pie(
            pie_data,
            names='Category',
            values='Spent',
            hole=0.45,
            title="Spending Breakdown",
            color_discrete_sequence=pie_colors
        )
        
        fig.update_layout(
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02,
                font=dict(size=11),
                bgcolor="rgba(255,255,255,0.8)",
            ),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ─────────────────────────────────────────────
    # DRILL (AFFECTS ONLY METRICS + CALENDAR)
    # ─────────────────────────────────────────────
    all_cats = sorted(df_range['Category'].unique().tolist())
    selected_cat = st.selectbox(
        "Drill into category",
        ["All"] + all_cats,
        key="drill_cat"
    )

    if selected_cat == "All":
        drill = spent_all.copy()
    else:
        drill = spent_all[spent_all["Category"] == selected_cat].copy()

    # ─────────────────────────────────────────────
    # METRICS (KEEP YOUR STYLE)
    # ─────────────────────────────────────────────
    d1, d2, d3 = st.columns(3)

    total_spent = drill["_amt"].sum().__abs__()
    avg_spent = drill["_amt"].abs().mean() if len(drill) else 0

    d1.metric("Transactions", len(drill))
    d2.metric("Total spent", f"${total_spent:,.2f}")
    d3.metric("Avg per transaction", f"${avg_spent:,.2f}")

    st.markdown("---")


    if not drill.empty:

        drill["Date"] = pd.to_datetime(drill["Date"])

        daily = (
            drill.groupby(drill["Date"].dt.date)["_amt"]
            .sum()
            .abs()
            .reset_index()
        )

        daily.columns = ["Date", "Spent"]
        daily["Date"] = pd.to_datetime(daily["Date"])

        spend_lookup = {
            d.date(): s
            for d, s in zip(daily["Date"], daily["Spent"])
        }

        max_spend = daily["Spent"].max() if not daily.empty else 1

        def cell_colour(amount):
            if amount <= 0:
                return "#fafafa"

            pct = amount / max_spend

            if pct < 0.20:
                return "#dcfce7"
            elif pct < 0.40:
                return "#bbf7d0"
            elif pct < 0.60:
                return "#86efac"
            elif pct < 0.80:
                return "#fca5a5"
            else:
                return "#ef4444"

        cal = calendar.Calendar(firstweekday=0)

        start_month = drill["Date"].min()
        end_month = drill["Date"].max()

        current_year = start_month.year
        current_month = start_month.month

        while (
            current_year < end_month.year
            or (
                current_year == end_month.year
                and current_month <= end_month.month
            )
        ):

            st.markdown(
                f"### {calendar.month_name[current_month]} {current_year}"
            )

            weeks = cal.monthdatescalendar(
                current_year,
                current_month
            )

            html = """
            <table style='width:100%; border-collapse:separate; border-spacing:6px; table-layout:fixed'>
            <tr>
                <th>Mon</th>
                <th>Tue</th>
                <th>Wed</th>
                <th>Thu</th>
                <th>Fri</th>
                <th>Sat</th>
                <th>Sun</th>
            </tr>
            """

            for week in weeks:

                html += "<tr>"

                for day in week:

                    if day.month != current_month:

                        html += """
                        <td style='height:90px;background:#f8f8f8;border-radius:10px'></td>
                        """
                        continue

                    spend = spend_lookup.get(day, 0)

                    html += f"""
                    <td
                        style="
                            height:90px;
                            vertical-align:top;
                            border-radius:10px;
                            padding:8px;
                            background:{cell_colour(spend)};
                            border:1px solid #ececec;
                        "
                    >
                        <div style="
                            font-size:12px;
                            font-weight:600;
                            color:#111;
                        ">
                            {day.day}
                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:14px;
                            font-weight:700;
                            color:#111;
                        ">
                            ${spend:,.0f}
                        </div>
                    </td>
                    """

                html += "</tr>"

            html += "</table>"

            st.markdown(html, unsafe_allow_html=True)

            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1

    else:
        st.info("No spending data for selected filter.")