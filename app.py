import streamlit as st
import pandas as pd
from pathlib import Path
from budget.data_loader import find_account_files, load_account_file, clean_transactions
from budget.categorizer import TransactionCategorizer
import plotly.express as px


st.set_page_config(layout='wide', page_title='Personal Finance Dashboard')

st.title('Personal Finance Dashboard')

# --- Load files ---
DATA_FOLDER = Path(__file__).parent
files = find_account_files(DATA_FOLDER)

if not files:
    st.error(f'No CSV/XLSX account files found in {DATA_FOLDER}. Place your account files there.')
    st.stop()

# Load and clean each account
account_dfs = []
for f in files:
    df = load_account_file(f)
    df = clean_transactions(df)
    account_dfs.append(df)

# Keep original per-account dataframes
accounts = {df['Account'].iloc[0]: df for df in account_dfs}

# Combined dataset for analysis
combined = pd.concat([df for df in account_dfs], ignore_index=True)

# Categorize
categorizer = TransactionCategorizer()
combined = categorizer.categorize_df(combined)

# Identify spending rows (negative Amounts)
combined['Spending'] = combined['Amount'].apply(lambda x: -x if x < 0 else 0.0)
combined['Income'] = combined['Amount'].apply(lambda x: x if x > 0 else 0.0)

# Sidebar filters
st.sidebar.header('Filters')
min_date = combined['Date'].min()
max_date = combined['Date'].max()
start_date, end_date = st.sidebar.date_input('Date range', [min_date, max_date])
selected_accounts = st.sidebar.multiselect('Accounts', options=list(accounts.keys()), default=list(accounts.keys()))
selected_categories = st.sidebar.multiselect('Categories', options=sorted(combined['Category'].unique()), default=sorted(combined['Category'].unique()))

# Apply filters to combined
mask = (combined['Date'] >= pd.to_datetime(start_date)) & (combined['Date'] <= pd.to_datetime(end_date))
mask &= combined['Account'].isin(selected_accounts)
mask &= combined['Category'].isin(selected_categories)
filtered = combined[mask]

# --- Account Overview ---
st.header('Account Overview')
cols = st.columns(len(accounts))
for i, (acct_name, df) in enumerate(accounts.items()):
    with cols[i]:
        st.subheader(acct_name)
        # show current balance (first non-null Balance_Clean from top)
        bal = df['Balance_Clean'].dropna()
        if not bal.empty:
            st.metric('Current balance', f'${bal.iloc[0]:,.2f}')
        else:
            st.write('Balance not available')
        # recent transactions
        recent = df.sort_values('Date', ascending=False).head(10)[['Date', 'Description', 'Amount', 'Balance_Clean']]
        st.dataframe(recent.reset_index(drop=True), height=300)

# --- Combined Spending Analysis ---
st.header('Combined Spending Analysis')
col1, col2 = st.columns([3,2])

# Summary numbers
total_spending = filtered['Spending'].sum()
total_income = filtered['Income'].sum()
col2.metric('Total spending', f'${total_spending:,.2f}')
col2.metric('Total income', f'${total_income:,.2f}')

# Monthly spending summary
monthly = filtered.copy()
monthly['YearMonth'] = monthly['Date'].dt.to_period('M').dt.to_timestamp()
monthly_summary = monthly.groupby('YearMonth')['Spending'].sum().reset_index()
fig_line = px.line(monthly_summary, x='YearMonth', y='Spending', title='Monthly Spending Trend')
col1.plotly_chart(fig_line, use_container_width=True)

# Spending by category
cat_summary = filtered.groupby('Category')['Spending'].sum().reset_index().sort_values('Spending', ascending=False)
fig_pie = px.pie(cat_summary, values='Spending', names='Category', title='Spending by Category')
col1.plotly_chart(fig_pie, use_container_width=True)

# Which account contributes most to spending (bonus)
acct_spend = filtered.groupby('Account')['Spending'].sum().reset_index().sort_values('Spending', ascending=False)
st.subheader('Spending by Account')
st.table(acct_spend)

# Top 5 merchants (by Description)
st.subheader('Top 5 Spending Merchants')
merchants = filtered[filtered['Spending']>0].groupby('Description')['Spending'].sum().reset_index().sort_values('Spending', ascending=False).head(5)
st.table(merchants)

# Budget comparison simple
st.subheader('Simple Budget Check')
budget_food = st.number_input('Monthly budget for Food', value=500.0, step=50.0)
food_spend = filtered[filtered['Category']=='Food']['Spending'].sum()
st.write(f'Food spending in selected range: ${food_spend:,.2f}')
if food_spend > budget_food:
    st.warning(f'You exceeded your Food budget (${budget_food:,.2f}) by ${food_spend - budget_food:,.2f}')
else:
    st.success('Food spending within budget')

# Show filtered transactions table
st.header('Transactions (filtered)')
st.dataframe(filtered.sort_values('Date', ascending=False).reset_index(drop=True))
