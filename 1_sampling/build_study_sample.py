"""Draw the main study sample from the 371 MAST 3.3 coding candidates.
Usage: python3 build_study_sample.py candidates_3.3.jsonl pilot_traces.zip OUT_DIR
Design: stratified by system x LLM, seed 2026, pilot traces excluded, no task repeated
within the sample, 2 reserve traces per stratum (used in listed order if a trace is dropped)."""
import json, sys, os, random, re, zipfile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

SRC, PILOT, OUT = sys.argv[1:4]
SEED = 2026
STRATA = [  # (system, benchmark, llm, main n)
    ("MetaGPT", "ProgramDev", "GPT-4o", 8),
    ("MetaGPT", "ProgramDev", "Claude", 8),
    ("MetaGPT", "ProgramDev-v2", "Qwen", 7),
    ("MetaGPT", "ProgramDev-v2", "CodeLlama", 7),
    ("ChatDev", "ProgramDev", "GPT-4o", 4),
    ("ChatDev", "ProgramDev-v2", "Qwen", 3),
    ("ChatDev", "ProgramDev-v2", "CodeLlama", 3),
]
RESERVE = 2
NAMES = {"1.1":"Disobey Task Specification","1.2":"Disobey Role Specification","1.3":"Step Repetition",
 "1.4":"Loss of Conversation History","1.5":"Unaware of Termination Conditions","2.1":"Conversation Reset",
 "2.2":"Fail to Ask for Clarification","2.3":"Task Derailment","2.4":"Information Withholding",
 "2.5":"Ignored Other Agent's Input","2.6":"Reasoning-Action Mismatch","3.1":"Premature Termination",
 "3.2":"No or Incomplete Verification","3.3":"Incorrect Verification"}

recs = [json.loads(l) for l in open(SRC, encoding="utf-8")]
def tr(r):
    t = r["trace"]
    return t if isinstance(t, dict) else eval(t, {"__builtins__": {}})  # stored as python-repr string in some rows
def ann(r):
    a = r["mast_annotation"]
    return a if isinstance(a, dict) else eval(a, {"__builtins__": {}})
def words(r): return len(tr(r)["trajectory"].split())
def task(r):
    t = tr(r)["trajectory"]
    m = re.search(r"\*\*task_prompt\*\*:\s*(.+)", t) or re.search(r"CONTENT:\s*\n(.+)", t)
    return m.group(1).strip() if m else ""

pilot = set()
with zipfile.ZipFile(PILOT) as z:
    for n in z.namelist():
        if n.endswith(".txt"):
            head = z.read(n).decode("utf-8")[:2000]
            m = re.search(r"trace\.key=(\S+), trace\.index=(\d+)", head)
            pilot.add((m.group(1), int(m.group(2))))
assert len(pilot) == 7, pilot

rng = random.Random(SEED)
used_tasks = {task(r) for r in recs if (tr(r)["key"], int(tr(r)["index"])) in pilot}
rows, n_pilot_removed = [], 0
for mas, bench, llm, k in STRATA:
    pool = [r for r in recs if r["mas_name"] == mas and r["benchmark_name"] == bench and r["llm_name"] == llm and ann(r).get("3.3") == 1]
    before = len(pool)
    pool = [r for r in pool if (tr(r)["key"], int(tr(r)["index"])) not in pilot]
    n_pilot_removed += before - len(pool)
    pool.sort(key=lambda r: (tr(r)["key"], int(tr(r)["index"])))
    rng.shuffle(pool)
    picked = []
    for r in pool:
        if task(r) in used_tasks: continue
        picked.append(r); used_tasks.add(task(r))
        if len(picked) == k + RESERVE: break
    for i, r in enumerate(picked):
        rows.append((mas, bench, llm, "Main" if i < k else "Reserve", r, len(pool)))
assert n_pilot_removed == 7

os.makedirs(OUT, exist_ok=True)
tdir = "study_traces"
main_i = res_i = 0
out_rows = []
zpath = os.path.join(OUT, "study_traces.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for mas, bench, llm, role, r, poolsize in rows:
        if role == "Main": main_i += 1; sid = f"S{main_i:02d}"
        else: res_i += 1; sid = f"R{res_i:02d}"
        t = tr(r); modes = [m for m, v in ann(r).items() if v == 1]
        fname = f"{sid}_{mas}_{llm}_{bench}.txt"
        header = (f"Sample ID: {sid} ({role})\nSystem: {mas}\nLLM: {llm}\nBenchmark: {bench}\n"
                  f"Source in MAD_full_dataset.json: trace.key={t['key']}, trace.index={t['index']}\n"
                  f"Task: {task(r)}\nLLM-judge MAST labels: " + ", ".join(f"{m} {NAMES[m]}" for m in modes) +
                  f"\nLength: {words(r):,} words\n" + "=" * 80 + "\n\n")
        z.writestr(f"{tdir}/{fname}", header + t["trajectory"])
        out_rows.append([sid, role, mas, llm, bench, t["key"], int(t["index"]), task(r), ", ".join(modes), words(r), fname])

F = "Arial"
H = Font(name=F, bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor="1F3864")
B = Font(name=F); BB = Font(name=F, bold=True); T = Font(name=F, bold=True, size=14)
thin = Side(style="thin", color="BFBFBF"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WR = Alignment(wrap_text=True, vertical="top")
cols = ["Sample ID", "Role", "System", "LLM", "Benchmark", "trace.key", "trace.index", "Task", "LLM-judge MAST labels", "Length (words)", "Trace file"]
widths = [10, 9, 10, 11, 14, 30, 11, 70, 26, 13, 40]

wb = Workbook()
ws = wb.active; ws.title = "Read Me"; ws.column_dimensions["A"].width = 120
main = [r for r in out_rows if r[1] == "Main"]; res = [r for r in out_rows if r[1] == "Reserve"]
mw = sum(r[9] for r in main if r[2] == "MetaGPT"); cw = sum(r[9] for r in main if r[2] == "ChatDev")
lines = [
 ("Study sample - CpE-508 group paper (AGENT 2027)", T), ("", B),
 ("What this is", BB),
 (f"The traces to annotate in the main study: {len(main)} Main traces ({sum(r[2]=='MetaGPT' for r in main)} MetaGPT + {sum(r[2]=='ChatDev' for r in main)} ChatDev) and {len(res)} Reserve traces.", B),
 ("Drawn from the 371 coding traces that MAST-Data's LLM judge labelled 3.3 Incorrect Verification (MAD_full_dataset.json, Hugging Face mcemri/MAD).", B),
 ("", B), ("How it was drawn (write this in the Methodology)", BB),
 (f"- Stratified random sample by system x LLM, random seed {SEED}. Script: build_study_sample.py (same folder).", B),
 ("- The 7 pilot traces (P01-P07) were excluded.", B),
 ("- No task appears twice in the sample or overlaps a pilot task, so each trace is a different program.", B),
 ("- MetaGPT: 8 GPT-4o + 8 Claude (ProgramDev), 7 Qwen + 7 CodeLlama (ProgramDev-v2). ChatDev: 4 GPT-4o (ProgramDev), 3 Qwen + 3 CodeLlama (ProgramDev-v2).", B),
 ("- HyperAgent and OpenManus are not included (the plan covers MetaGPT and ChatDev only).", B),
 ("", B), ("How to use it", BB),
 ("- Annotate the Main traces. If a trace cannot be used (e.g., unreadable), replace it with the first unused Reserve trace from the same system and LLM, and log why.", B),
 ("- If the pilot shows you need a smaller sample, drop Main traces from the bottom of each stratum, not by choosing ones you like.", B),
 ("- Trace texts are in study_traces.zip, one .txt per trace, same header format as the pilot traces.", B),
 ("", B), ("Workload warning", BB),
 (f"- Main MetaGPT traces total {mw:,} words; Main ChatDev traces total {cw:,} words. ChatDev Qwen/CodeLlama traces are very long (60k-120k words each).", B),
 ("- Decide after the pilot whether ChatDev Qwen/CodeLlama is feasible; if not, use ChatDev GPT-4o only and state it as a limitation.", B),
 ("", B), ("Labels in this file come from the dataset's LLM judge, not from humans. Annotation must be done by the authors.", B),
]
for i, (txt, f) in enumerate(lines, 1):
    c = ws.cell(i, 1, txt); c.font = f; c.alignment = Alignment(wrap_text=True)

for title, data in (("Sample", main), ("Reserve", res)):
    s = wb.create_sheet(title)
    for c, (n, w) in enumerate(zip(cols, widths), 1):
        cell = s.cell(1, c, n); cell.font = H; cell.fill = HF; cell.alignment = WR; cell.border = BOX
        s.column_dimensions[get_column_letter(c)].width = w
    for ri, row in enumerate(data, 2):
        for c, v in enumerate(row, 1):
            cell = s.cell(ri, c, v); cell.font = B; cell.alignment = WR; cell.border = BOX
        s.cell(ri, 10).number_format = "#,##0"
    s.freeze_panes = "B2"; s.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(data)+1}"

s = wb.create_sheet("Strata")
hdr = ["System", "Benchmark", "LLM", "3.3 traces (after removing pilot)", "Main", "Reserve", "Main words (total)"]
for c, n in enumerate(hdr, 1):
    cell = s.cell(1, c, n); cell.font = H; cell.fill = HF; cell.border = BOX; s.column_dimensions[get_column_letter(c)].width = 18
seen = {}
for mas, bench, llm, role, r, poolsize in rows: seen[(mas, bench, llm)] = poolsize
for ri, (mas, bench, llm, k) in enumerate(STRATA, 2):
    vals = [mas, bench, llm, seen[(mas, bench, llm)],
            f'=COUNTIFS(Sample!C:C,A{ri},Sample!E:E,B{ri},Sample!D:D,C{ri})',
            f'=COUNTIFS(Reserve!C:C,A{ri},Reserve!E:E,B{ri},Reserve!D:D,C{ri})',
            f'=SUMIFS(Sample!J:J,Sample!C:C,A{ri},Sample!E:E,B{ri},Sample!D:D,C{ri})']
    for c, v in enumerate(vals, 1):
        cell = s.cell(ri, c, v); cell.font = B; cell.border = BOX
    s.cell(ri, 7).number_format = "#,##0"
tr_ = len(STRATA) + 2
s.cell(tr_, 1, "Total").font = BB
for c, L in ((4, "D"), (5, "E"), (6, "F"), (7, "G")):
    cell = s.cell(tr_, c, f"=SUM({L}2:{L}{tr_-1})"); cell.font = BB; cell.border = BOX
s.cell(tr_, 7).number_format = "#,##0"
wb.save(os.path.join(OUT, "Study_Sample.xlsx"))
print(len(main), len(res), mw, cw)
for r in out_rows: print(r[0], r[1], r[2], r[3], r[4], r[6], r[9], r[7][:50])
