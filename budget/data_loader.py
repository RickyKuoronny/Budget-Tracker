import pandas as pd
from pathlib import Path
import re
from typing import List


def find_account_files(folder: str) -> List[Path]:
    p = Path(folder)
    files = list(p.glob('*.csv')) + list(p.glob('*.xlsx'))
    return files


def load_account_file(filepath: Path) -> pd.DataFrame:
    """
    Load a CSV or XLSX account file. Returns a DataFrame with columns:
    Date, Description, Amount, Balance, Account
    """
    if filepath.suffix.lower() == '.csv':
        # Many bank export CSVs don't contain a clean header row; read first 4 columns
        df = pd.read_csv(filepath, header=None, names=['Date', 'Description', 'Amount', 'Balance'], engine='python')
    else:
        df = pd.read_excel(filepath, header=0)

    # Drop rows where Date is NaN (these are non-transaction rows)
    df = df.dropna(subset=['Date'])

    # Remove known header/footer lines that are not transactions
    df = df[~df['Date'].astype(str).str.lower().str.contains('account history|items|account:')]

    # Clean columns
    df = df.rename(columns=lambda x: x.strip())
    # Ensure required columns exist
    expected = ['Date', 'Description', 'Amount', 'Balance']
    present = [c for c in expected if c in df.columns]
    if len(present) < 4:
        # try positional columns
        df = df.iloc[:, :4]
        df.columns = expected

    # Add Account name from filename
    account_name = filepath.stem
    df['Account'] = account_name

    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean Date, Amount columns and standardize Amount as float (positive for credits, negative for debits)
    """
    df = df.copy()

    # Parse Date
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

    # Drop rows with unparseable dates introduced by headers/footers
    df = df.dropna(subset=['Date'])

    # Clean Amount: remove $ and commas, parentheses
    def parse_amount(x):
        if pd.isna(x):
            return 0.0
        s = str(x)
        s = s.replace('$', '').replace(',', '').strip()
        # Handle parentheses or leading -
        s = s.replace('(', '-').replace(')', '')
        # Sometimes amounts are like "-$1,535.28" or "$6,000.00"
        try:
            return float(re.sub('[^0-9\-\.]+', '', s))
        except Exception:
            return 0.0

    df['Amount'] = df['Amount'].apply(parse_amount)

    # Ensure Balance is numeric (but keep per-file running balance untouched)
    def parse_balance(x):
        if pd.isna(x):
            return None
        s = str(x).replace('$', '').replace(',', '').strip()
        s = s.replace('(', '-').replace(')', '')
        try:
            return float(re.sub('[^0-9\-\.]+', '', s))
        except Exception:
            return None

    df['Balance_Clean'] = df['Balance'].apply(parse_balance)

    return df
