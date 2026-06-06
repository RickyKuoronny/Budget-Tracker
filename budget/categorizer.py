from typing import Dict, List
import re
import pandas as pd


DEFAULT_CATEGORIES = {
    'Food': ['restaurant', 'cafe', 'coffee', 'takeaway', 'uber eats', 'deliveroo', 'maccas', 'kfc', 'pizza'],
    'Groceries': ['woolworths', 'coles', 'safeway', 'iga', 'grocery', 'aldi'],
    'Transport': ['uber', 'taxi', 'bus', 'train', 'transit', 'petrol', 'bp', 'caltex'],
    'Bills': ['electricity', 'water', 'telstra', 'optus', 'bill', 'internet', 'payments', 'bpay'],
    'Transfers': ['transfer', 'internet transfer', 'osko', 'payment to', 'debit to', 'credit from'],
    'Giving': ['tithe', 'tithes', 'charity', 'donation'],
    'Other': []
}


class TransactionCategorizer:
    def __init__(self, categories: Dict[str, List[str]] = None):
        self.categories = categories or DEFAULT_CATEGORIES
        # compile regexes
        self.compiled = []
        for cat, kws in self.categories.items():
            if not kws:
                continue
            pattern = r'(' + '|'.join(re.escape(k) for k in kws) + r')'
            self.compiled.append((cat, re.compile(pattern, flags=re.IGNORECASE)))

    def categorize_description(self, desc: str) -> str:
        if pd.isna(desc):
            return 'Other'
        s = str(desc)
        for cat, rx in self.compiled:
            if rx.search(s):
                return cat
        # heuristics
        s_low = s.lower()
        if any(x in s_low for x in ['transfer', 'debit', 'credit']):
            return 'Transfers'
        return 'Other'

    def categorize_df(self, df: pd.DataFrame, desc_col: str = 'Description') -> pd.DataFrame:
        df = df.copy()
        df['Category'] = df[desc_col].apply(self.categorize_description)
        return df
