"""RQ1 counts and tests on the agreed (final) labels.
Usage: python3 rq1.py ANNOTATOR_A_FINAL.xlsx ANNOTATOR_B_FINAL.xlsx
A field counts as agreed when both annotators gave the same value. S22 was resolved
by discussion as an escaped failure in the tests (first author's labels used), see RESOLVED."""
import sys, openpyxl, collections
from scipy import stats
def L(f):
    ws=openpyxl.load_workbook(f,data_only=True)['Annotation']
    return {r[0]:list(r) for r in ws.iter_rows(values_only=True) if r[0] and str(r[0])[:1]=='S' and str(r[0])[1:].isdigit()}
M,Z=L(sys.argv[1]),L(sys.argv[2])
F={'faulty':4,'artifact':5,'missed':6,'origin':7,'earliest':8,'intro':9,'missedby':10,'reason':13}
n=lambda v:str(v).strip().lower().replace(' ','')
RESOLVED={'S22':{'faulty':'Yes','missed':'Yes','artifact':'Tests','origin':'Testing','earliest':'Testing','intro':'SimpleTester','missedby':'Simple Reviewer'}}
over=dict(RESOLVED)
def agreed(s,k):
    if s in over and k in over[s]: return over[s][k]
    a,b=M[s][F[k]],Z[s][F[k]]
    return str(a).strip() if n(a)==n(b) else None
ids=sorted(M)
unres=[s for s in ids if any(agreed(s,k) is None for k in ['faulty','missed','earliest'])]
conf=[s for s in ids if s not in unres and n(agreed(s,'faulty'))=='yes' and n(agreed(s,'missed'))=='yes']
sysof=lambda s:M[s][1]
print('unresolved',unres)
print('confirmed',len(conf),collections.Counter(sysof(s) for s in conf))
print('not faulty',[s for s in ids if s not in unres and n(agreed(s,'faulty'))=='no'])
print('caught',[s for s in ids if s not in unres and n(agreed(s,'faulty'))=='yes' and n(agreed(s,'missed'))=='no'])
E=collections.Counter(agreed(s,'earliest') for s in conf); print('earliest',E)
O=collections.Counter((agreed(s,'origin'),agreed(s,'earliest')) for s in conf); print('origin x earliest',O)
for sy in ['MetaGPT','ChatDev']: print(sy,collections.Counter(agreed(s,'earliest') for s in conf if sysof(s)==sy))
print('artifact',collections.Counter(agreed(s,'artifact') for s in conf))
c,t=E.get('Coding',0),E.get('Testing',0)
print('binomial Coding vs Testing',c,t,stats.binomtest(c,c+t,0.5).pvalue)
mg=collections.Counter(agreed(s,'earliest') for s in conf if sysof(s)=='MetaGPT'); cd=collections.Counter(agreed(s,'earliest') for s in conf if sysof(s)=='ChatDev')
print('fisher fw',stats.fisher_exact([[mg['Coding'],mg['Testing']],[cd['Coding'],cd['Testing']]]))
for k in ['intro','missedby','reason']:
    print(k,'agreed on',sum(agreed(s,k) is not None for s in conf),collections.Counter(agreed(s,k) for s in conf))
