"""Per-field percent agreement and Cohen's kappa between the two annotators.
Usage: python3 kappa.py ANNOTATOR_A.xlsx ANNOTATOR_B.xlsx"""
import sys, collections, openpyxl
FIELDS = {"Output faulty": 4, "Faulty artifact": 5, "Verifier missed it": 6, "Origin stage": 7,
          "Earliest detectable stage": 8, "Introduced by": 9, "Missed by": 10, "Miss reason": 13}
def load(f):
    ws = openpyxl.load_workbook(f, data_only=True)["Annotation"]
    return {r[0]: r for r in ws.iter_rows(values_only=True)
            if r[0] and str(r[0])[:1] == "S" and str(r[0])[1:].isdigit()}
norm = lambda v: str(v).strip().lower().replace(" ", "")
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0
A, B = load(sys.argv[1]), load(sys.argv[2]); ids = sorted(set(A) & set(B))
print(f"{len(ids)} traces")
for name, c in FIELDS.items():
    po, k = kappa([norm(A[s][c]) for s in ids], [norm(B[s][c]) for s in ids])
    print(f"{name:28s} {100*po:5.1f}%  kappa={k:.2f}")
