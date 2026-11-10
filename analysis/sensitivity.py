"""Sensitivity check for RQ1 (Threats to Validity): earliest detectable stage restricted to the
confirmed failures on which both annotators already agreed in one annotation round.
Confirmed failures = the 38 from rq1.py (final labels; S34 and S36 excluded).
Usage: python3 sensitivity.py ROUND_A.xlsx ROUND_B.xlsx"""
import sys, openpyxl, collections
from scipy import stats
def L(f):
    ws=openpyxl.load_workbook(f,data_only=True)['Annotation']
    return {r[0]:list(r) for r in ws.iter_rows(values_only=True) if r[0] and str(r[0])[:1]=='S' and str(r[0])[1:].isdigit()}
A,B=L(sys.argv[1]),L(sys.argv[2])
n=lambda v:str(v).strip().lower().replace(' ','')
NOT_CONFIRMED={'S34','S36'}
conf=[s for s in sorted(A) if s not in NOT_CONFIRMED]
agreed=[s for s in conf if n(A[s][8])==n(B[s][8])]
c=collections.Counter(str(A[s][8]).strip() for s in agreed)
k,t=c['Coding'],c['Testing']
print(f'{len(agreed)} of {len(conf)} confirmed failures agreed on earliest stage: {dict(c)}')
print('binomial Coding vs Testing', k, t, round(stats.binomtest(k,k+t,0.5).pvalue,3))
