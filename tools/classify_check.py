import re
from tools.category_rules import CATEGORY_RULES, PRIORITY_CATS, STANDARD_CATS


def normalize_desc(raw_desc: str) -> str:
    if raw_desc is None:
        return ''
    s = str(raw_desc).upper()
    s = re.sub(r'VISA PURCHASE', ' ', s)
    s = re.sub(r'EFTPOS WDL', ' ', s)
    s = re.sub(r'ATM WITHDRAWAL', 'ATM', s)
    s = re.sub(r'EFTPOS DEP', ' ', s)
    s = re.sub(r'SQ \*', ' ', s)
    s = re.sub(r'\bLS ', ' ', s)
    s = re.sub(r'ZLR\*', ' ', s)
    s = re.sub(r'SMP\*', ' ', s)
    s = re.sub(r'REVOLUT\*\*\d+\*', 'REVOLUT', s)
    s = re.sub(r'PAYPAL \*', ' ', s)
    s = re.sub(r'[^A-Z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def matches_any(desc: str, keywords: list) -> bool:
    return any(k in desc for k in keywords) if keywords else False


def classify(description: str, amount) -> str:
    desc = normalize_desc(description)

    amt_str = str(amount) if amount is not None else ''
    amt_clean = amt_str.replace('$', '').replace(',', '').strip()
    is_debit = amt_clean.startswith('-')

    # Priority categories (order matters)
    for cat in PRIORITY_CATS:
        keywords = CATEGORY_RULES.get(cat, [])
        if matches_any(desc, keywords):
            return cat

    # Standard categories
    for cat in STANDARD_CATS:
        if matches_any(desc, CATEGORY_RULES.get(cat, [])):
            return cat

    return 'Unsorted'


# Run directly to get a quick category count across all CSVs
if __name__ == '__main__':
    from pathlib import Path
    import csv

    files = ['EVERYDAY OPTIONS.csv', 'Savings.csv', 'Short.csv']
    for name in files:
        path = Path(name)
        if not path.exists():
            print(f'Missing: {name}')
            continue
        with path.open('r', encoding='utf-8-sig', newline='') as h:
            rows = list(csv.reader(h))
        cats: dict[str, int] = {}
        for r in rows:
            if len(r) >= 4:
                date, desc, amt = r[0].strip(), r[1].strip(), r[2].strip()
                if '/' in date and any(ch.isdigit() for ch in date):
                    cat = classify(desc, amt)
                    cats[cat] = cats.get(cat, 0) + 1
        print(name)
        for k, v in sorted(cats.items(), key=lambda x: -x[1]):
            print(f'  {k}: {v}')
        print()
