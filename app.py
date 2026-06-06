import streamlit as st
import pandas as pd
from pathlib import Path


st.set_page_config(layout='wide', page_title='CSV Viewer')

st.title('Base CSV Viewer')
st.write('Showing the raw contents of the three CSV files in this folder.')


DATA_FOLDER = Path(__file__).parent
CSV_FILES = ['EVERYDAY OPTIONS.csv', 'Savings.csv', 'Short.csv']


@st.cache_data(show_spinner=False)
def load_raw_csv(filepath: Path) -> pd.DataFrame:
    return pd.read_csv(filepath, header=None)


for filename in CSV_FILES:
    file_path = DATA_FOLDER / filename
    st.header(filename)

    if not file_path.exists():
        st.error(f'Missing file: {file_path}')
        continue

    raw_df = load_raw_csv(file_path)
    st.caption(f'{len(raw_df)} rows x {len(raw_df.columns)} columns')
    st.dataframe(raw_df, use_container_width=True, height=520)
