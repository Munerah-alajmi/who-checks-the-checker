# Online Appendix: "Who Checks the Checker? A Human Oversight Stage for Failures Missed in LLM Multi-Agent Code Generation"

Replication package for the AGENT 2027 (ICSE 2027 workshop) submission.

## Contents

| Folder | What it contains |
|---|---|
| `1_sampling/` | `build_study_sample.py` (stratified sample, seed 2026), `Study_Sample.xlsx` (40 study traces S01–S40 and reserves), `study_traces_40.zip` (the 40 traces as text) |
| `2_annotation/0_codebook_and_template/` | `Codebook_v1.xlsx` (the codebook on its own) and `Annotation_Template_blank.xlsx` (the empty annotation sheet each author filled, with drop-down values) |
| `2_annotation/round1_independent/` | Both annotators' independent labels (round 1) and the disagreement list |
| `2_annotation/round2_independent_reexamination/` | Labels after the decision rule was added and each annotator re-examined disputed traces independently (round 2, Table "kappa") |
| `2_annotation/final_after_discussion/` | Final labels after discussion, used for RQ1 |
| `3_phase2/cut_traces/` | The ten MetaGPT traces (T01–T10) cut after Requirements, Coding, Testing and Review; LLM-judge labels removed |
| `3_phase2/materials/` | Participant instructions, blank comment sheet, checkpoint assignment (mix design, 2 teams × 3 checkpoints) |
| `3_phase2/Phase2_Judging_FINAL.xlsx` | All 40 participant reviews (anonymized P1–P4, verbatim comments), the confirmed failure per trace, and the Yes/Partial/No judgment with quoted evidence |
| `analysis/` | `kappa.py`, `rq1.py`, `sensitivity.py`, `rq2.py`, `requirements.txt` |

Annotator files are named A1/A2. Participants are identified only as P1–P4.

## Reproducing the numbers

```bash
pip install -r analysis/requirements.txt
# Table: agreement (round 1 and round 2)
python3 analysis/kappa.py 2_annotation/round1_independent/Annotation_A1_round1.xlsx 2_annotation/round1_independent/Annotation_A2_round1.xlsx
python3 analysis/kappa.py 2_annotation/round2_independent_reexamination/Annotation_A1_round2.xlsx 2_annotation/round2_independent_reexamination/Annotation_A2_round2.xlsx
# RQ1: confirmed failures, earliest detectable stage, binomial and Fisher tests
python3 analysis/rq1.py 2_annotation/final_after_discussion/Annotation_A1_final.xlsx 2_annotation/final_after_discussion/Annotation_A2_final.xlsx
# Sensitivity check (Threats to Validity): failures agreed in Round 1 / Round 2 only
python3 analysis/sensitivity.py 2_annotation/round1_independent/Annotation_A1_round1.xlsx 2_annotation/round1_independent/Annotation_A2_round1.xlsx
python3 analysis/sensitivity.py 2_annotation/round2_independent_reexamination/Annotation_A1_round2.xlsx 2_annotation/round2_independent_reexamination/Annotation_A2_round2.xlsx
# RQ2: catch rate per checkpoint (Table VI, descriptive only)
python3 analysis/rq2.py 3_phase2/Phase2_Judging_FINAL.xlsx
```

## Notes

- **Codebook.** The codebook (v1) is included as the `Codebook v1` sheet of every annotation workbook.
- **Phase 2 judging.** Both authors judged every review (Yes/Partial/No) independently and agreed on all 40.
- **S22** was resolved by discussion as an escaped failure in the tests (see `RESOLVED` in `rq1.py`).

## Data source and licence

The traces come from MAST-Data (Cemri et al., "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025; Hugging Face `mcemri/MAD`), released under CC BY 4.0. The trace files here are excerpts of that dataset, redistributed under the same licence. Our annotations, scripts and Phase 2 materials are released under CC BY 4.0.
