from collections import Counter
from pathlib import Path
import csv

from classify_check import classify, normalize_desc

CSV_FILES = ['EVERYDAY OPTIONS.csv', 'Savings.csv', 'Short.csv']

counter = Counter()
raw_examples = {}

for name in CSV_FILES:
    path = Path(name)
    if not path.exists():
        continue
    with path.open('r', encoding='utf-8-sig', newline='') as h:
        rows = list(csv.reader(h))
    for r in rows:
        if len(r) < 4:
            continue
        date = r[0].strip()
        desc = r[1].strip()
        amt = r[2].strip()
        if '/' not in date or not any(ch.isdigit() for ch in date):
            continue
        cat = classify(desc, amt)
        if cat == 'Unsorted':
            norm = normalize_desc(desc)
            counter[norm] += 1
            if norm not in raw_examples:
                raw_examples[norm] = desc

print('Top Unsorted descriptions (normalized)')
print('-------------------------------------')
for i, (norm, cnt) in enumerate(counter.most_common(50), 1):
    example = raw_examples.get(norm, '')
    print(f'{i:2d}. {cnt:4d}  | {norm}  | example: {example}')

print('\nTotal unique unsorted tokens:', len(counter))
print('Total unsorted transactions:', sum(counter.values()))
