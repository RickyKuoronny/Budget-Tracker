import streamlit as st
import pandas as pd
from pathlib import Path
import csv
import re


st.set_page_config(layout='wide', page_title='CSV Viewer')

st.title('Base CSV Viewer')
st.write('Showing the three base CSV files in separate tabs with simple transaction categories.')


DATA_FOLDER = Path(__file__).parent
CSV_FILES = ['EVERYDAY OPTIONS.csv', 'Savings.csv', 'Short.csv']


from tools.classify_check import CATEGORY_RULES


def classify_transaction(desc, amount, balance):
    desc = (desc or '').upper()
    amt_clean = str(amount).replace(',', '').replace('$', '').strip()
    is_debit = False
    if isinstance(amount, str):
        is_debit = amount.strip().startswith('-') or amount.strip().upper().startswith('DR')

    # Special-case transfers
    if 'INTERNET TRANSFER' in desc or 'TRANSFER TO' in desc or 'TRANSFER FROM' in desc:
        return 'Transfers'

    # Special-case giving
    if 'CHURCH' in desc or 'TITHE' in desc or 'GIVING' in desc:
        return 'Giving'

    # Keyword match across categories
    for cat, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in desc:
                return cat

    # If amount parses positive, mark as Income
    try:
        val = float(amt_clean)
        if val > 0 and not is_debit:
            return 'Income'
    except Exception:
        pass

    return 'Unsorted'


@st.cache_data(show_spinner=False)
def load_raw_csv(filepath: Path) -> pd.DataFrame:
    with filepath.open('r', encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.reader(handle))

    return pd.DataFrame(rows)


def normalize_transactions(raw_df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row in raw_df.itertuples(index=False, name=None):
        values = [value for value in row if value not in (None, '')]
        if len(values) < 4:
            continue

        date_value = values[0]
        description_value = values[1]
        amount_value = values[2]
        balance_value = values[3]

        if not re.match(r'^\d{2}/\d{2}/\d{4}$', str(date_value).strip()):
            continue

        records.append({
            'Date': date_value,
            'Description': description_value,
            'Amount': amount_value,
            'Balance': balance_value,
        })

    if not records:
        return pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Balance', 'Category'])

    df = pd.DataFrame(records)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Category'] = df.apply(
        lambda row: classify_transaction(row['Description'], row['Amount'], ''),
        axis=1,
    )

    return df


tabs = st.tabs(CSV_FILES)

for tab, filename in zip(tabs, CSV_FILES):
    with tab:
        file_path = DATA_FOLDER / filename

        if not file_path.exists():
            st.error(f'Missing file: {file_path}')
            continue

        raw_df = load_raw_csv(file_path)
        transactions = normalize_transactions(raw_df)

        st.subheader(filename)

        if transactions.empty:
            st.warning('No transactions found in this file.')
            continue

        category_options = ['All'] + sorted(transactions['Category'].fillna('Unsorted').unique().tolist())
        selected_category = st.selectbox('Show category', category_options, key=f'category-{filename}')

        view_df = transactions.copy()
        if selected_category != 'All':
            view_df = view_df[view_df['Category'] == selected_category]

        category_counts = transactions['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']

        st.caption(f'{len(transactions)} transactions found')
        st.dataframe(category_counts, use_container_width=True, hide_index=True)
        st.dataframe(view_df.reset_index(drop=True), use_container_width=True, height=520)
