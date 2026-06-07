"""
import_csv.py — Import bank CSV files into transactions.db

Usage:
    python tools/import_csv.py                        # imports all 3 default CSVs
    python tools/import_csv.py "EVERYDAY OPTIONS.csv" # imports one specific file
"""

import csv
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'transactions.db'

ACCOUNT_MAP = {
    'EVERYDAY OPTIONS.csv': 'Everyday',
    'Savings.csv': 'Savings',
    'Short.csv': 'Short-Term',
}

DEFAULT_FILES = list(ACCOUNT_MAP.keys())


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account     TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            amount      TEXT    NOT NULL,
            balance     TEXT    NOT NULL,
            UNIQUE(account, date, description, amount, balance)
        )
    ''')
    conn.commit()


def import_file(conn: sqlite3.Connection, filepath: Path, account: str) -> tuple[int, int]:
    """Returns (inserted, skipped) counts."""
    with filepath.open('r', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))

    inserted = 0
    skipped = 0

    for row in rows:
        values = [v for v in row if v not in (None, '')]
        if len(values) < 4:
            continue
        date_val, desc_val, amt_val, bal_val = values[0], values[1], values[2], values[3]
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_val.strip()):
            continue

        try:
            conn.execute(
                'INSERT INTO transactions (account, date, description, amount, balance) '
                'VALUES (?, ?, ?, ?, ?)',
                (account, date_val, desc_val, amt_val, bal_val)
            )
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
            # print(f'    DUPE: {date_val} | {desc_val} | {amt_val} | {bal_val}')

    conn.commit()
    return inserted, skipped


def main() -> None:
    # Determine which files to import
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        filenames = DEFAULT_FILES

    project_root = Path(__file__).parent.parent
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    total_inserted = 0
    total_skipped = 0

    for filename in filenames:
        filepath = project_root / filename
        if not filepath.exists():
            print(f'  Not found: {filepath}')
            continue

        account = ACCOUNT_MAP.get(filename, filename.replace('.csv', ''))
        inserted, skipped = import_file(conn, filepath, account)
        total_inserted += inserted
        total_skipped += skipped
        print(f'  OK {filename} -> {inserted} new, {skipped} duplicates skipped')

    conn.close()
    print(f'\nDone. {total_inserted} new transactions added to {DB_PATH.name}')


if __name__ == '__main__':
    main()