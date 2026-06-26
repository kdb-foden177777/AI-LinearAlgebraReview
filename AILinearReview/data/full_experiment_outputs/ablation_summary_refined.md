# Refined Primary-Metric Ablation Summary

This refined table is the version used in the manuscript after two metric-design corrections.

First, the retrieval ablation reports the nontrivial degradation from concept-filtered retrieval to lexical retrieval, rather than a no-retrieval condition whose MRR is structurally zero. Second, the IRT ablation uses the fixed-target IRT sensitivity analysis, where weak-concept targets are fixed before comparing selection policies.

| Condition | Removed | Primary metric | Full | Ablated | Change |
|---|---|---|---:|---:|---:|
| A1 no syllabus alignment | M1 syllabus alignment | Alignment score ↑ | 0.472 | 0.469 | -0.003 |
| A2 no mastery loop | M4 mastery loop | Weak-concept coverage ↑ | 0.979 | 0.604 | -0.375 |
| A3 no concept-filtered retrieval | M2 concept filter | Retrieval MRR@5 ↑ | 1.000 | 0.751 | -0.249 |
| A4 no dependency propagation | Prerequisite propagation | Prerequisite risk flag ↓ | 0.854 | 0.896 | +0.042 |
| A5 no IRT adaptation | E2 IRT weighting | Difficulty hit@0.5 ↑ | 0.538 | 0.231 | -0.307 |
| A6 fixed dialogue flow | E1 dialogue agent | Dialogue flexibility ↑ | 0.915 | 0.250 | -0.665 |
