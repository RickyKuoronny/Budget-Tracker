from collections import Counter
from pathlib import Path
import csv

from tools.classify_check import classify, normalize_desc

CSV_FILES = ['EVERYDAY OPTIONS.csv', 'Savings.csv', 'Short.csv']

counter: Counter = Counter()
raw_examples: dict[str, str] = {}

for name in CSV_FILES:
    path = Path(name)
    if not path.exists():
        print(f'Skipping missing file: {name}')
        continue
    with path.open('r', encoding='utf-8-sig', newline='') as h:
        rows = list(csv.reader(h))
    for r in rows:
        if len(r) < 4:
            continue
        date, desc, amt = r[0].strip(), r[1].strip(), r[2].strip()
        if '/' not in date or not any(ch.isdigit() for ch in date):
            continue
        if classify(desc, amt) == 'Unsorted':
            norm = normalize_desc(desc)
            counter[norm] += 1
            raw_examples.setdefault(norm, desc)

print('Top Unsorted descriptions (normalized)')
print('-------------------------------------')
for i, (norm, cnt) in enumerate(counter.most_common(50), 1):
    print(f'{i:2d}. {cnt:4d}  | {norm:<60} | example: {raw_examples.get(norm, "")}')

print(f'\nTotal unique unsorted tokens : {len(counter)}')
print(f'Total unsorted transactions  : {sum(counter.values())}')
