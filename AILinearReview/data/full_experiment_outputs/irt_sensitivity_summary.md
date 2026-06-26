# IRT Sensitivity Analysis

This experiment fixes the target weak concept first, then compares item-selection policies within the same concept-specific candidate pools.

| Policy | Trials | Weak cov. | Hit@0.5 | Hit@0.75 | Diff. error | Mean info |
|---|---:|---:|---:|---:|---:|---:|
| random_within_target | 26 | 1.000 | 0.077 | 0.077 | 1.250 | 0.171 |
| syllabus_ranked | 26 | 1.000 | 0.231 | 0.269 | 0.964 | 0.195 |
| difficulty_only | 26 | 1.000 | 0.615 | 0.731 | 0.459 | 0.233 |
| graph_irt | 26 | 1.000 | 0.538 | 0.731 | 0.512 | 0.230 |
