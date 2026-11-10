"""RQ2: catch rates per checkpoint (Table VI), reported descriptively.
No significance tests: the 40 reviews come from 4 participants x 10 traces and are not independent.
Usage: python3 rq2.py Phase2_Judging_FINAL.xlsx"""
import sys, collections, openpyxl
ws = openpyxl.load_workbook(sys.argv[1], data_only=True)["2 Judging (40 reviews)"]
rows = [r for r in ws.iter_rows(min_row=3, max_row=42, values_only=True)]
CP = {"Coding": "CP1", "Testing": "CP2", "Review": "CP3"}
FINAL = 18  # column S (0-based index 18): authors' agreed judgment
c = collections.defaultdict(collections.Counter)
for r in rows: c[CP[r[3]]][r[FINAL]] += 1
for k in sorted(c): print(k, sum(c[k].values()), 'reviews', dict(c[k]))
print('Total', collections.Counter(r[FINAL] for r in rows))
