# True Configuration Ablation Summary

Each condition was evaluated by changing the executable configuration and recomputing metrics from saved benchmark items, corpus chunks, simulated learner profiles, and saved agent logs. No row is manually filled.

| Condition | Removed | Align | Weak cov. | Upstream cov. | MRR@5 | Support | Diff. err. | Risk flag | Dialogue |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 full system | - | 0.472 | 0.979 | 1 | 1.0 | 0.65 | 1.317 | 0.854 | 0.915 |
| A1 no syllabus alignment | M1 syllabus alignment | 0.469 | 0.979 | 1 | 1.0 | 0.65 | 1.298 | 0.833 | 0.915 |
| A2 no mastery loop | M4 mastery loop | 0.577 | 0.604 | 1 | 1.0 | 0.65 | 0.698 | 0.542 | 0.915 |
| A3 no retrieval | M2 retrieval | 0.472 | 0.979 | 1 | 0.0 | 0.0 | 1.317 | 0.854 | 0.915 |
| A4 no dependency propagation | prerequisite propagation | 0.459 | 1 | 1 | 1.0 | 0.65 | 1.297 | 0.896 | 0.915 |
| A5 no IRT adaptation | E2 IRT weighting | 0.472 | 0.979 | 1 | 1.0 | 0.65 | 1.322 | 0.854 | 0.915 |
| A6 fixed dialogue flow | E1 dialogue agent | 0.472 | 0.979 | 1 | 1.0 | 0.65 | 1.317 | 0.854 | 0.25 |

## Primary-Metric Deltas

| Condition | Removed | Primary metric | Full | Ablated | Raw change | Effect on quality |
|---|---|---|---:|---:|---:|---:|
| A1 no syllabus alignment | M1 syllabus alignment | Alignment score | 0.472 | 0.469 | -0.003 | -0.003 |
| A2 no mastery loop | M4 mastery loop | Weak-concept coverage | 0.979 | 0.604 | -0.375 | -0.375 |
| A3 no retrieval | M2 retrieval | Retrieval MRR@5 | 1.0 | 0.0 | -1.0 | -1.0 |
| A3 no retrieval | M2 retrieval | Grounding support proxy | 0.65 | 0.0 | -0.65 | -0.65 |
| A4 no dependency propagation | prerequisite propagation | Prerequisite risk flag | 0.854 | 0.896 | 0.042 | -0.042 |
| A5 no IRT adaptation | E2 IRT weighting | Difficulty match error | 1.317 | 1.322 | 0.005 | -0.005 |
| A6 fixed dialogue flow | E1 dialogue agent | Dialogue flexibility | 0.915 | 0.25 | -0.665 | -0.665 |
