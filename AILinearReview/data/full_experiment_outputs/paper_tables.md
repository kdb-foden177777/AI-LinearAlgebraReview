# Paper Tables

## Corpus Composition

| Folder | Files | Lines | Characters | Approx. tokens |
|---|---:|---:|---:|---:|
| `slides_md` | 54 | 22873 | 1309998 | 327500 |
| `flipped_md` | 81 | 4679 | 192308 | 48077 |
| `mit_linear_algebra_md` | 65 | 10280 | 676584 | 169146 |

## Benchmark Summary

Benchmark items: 106

## Concept Tagging

- items: 36
- micro_precision: 0.795
- micro_recall: 0.795
- micro_f1: 0.795
- macro_precision: 0.874
- macro_recall: 0.739
- macro_f1: 0.751
- mean_jaccard: 0.491
- label_type: keyword-derived silver labels

## Retrieval

- concept_filtered: Success@5=1.0, MRR@5=1.0
- exam_only: Success@5=0.887, MRR@5=0.694
- lecture_only: Success@5=0.675, MRR@5=0.558
- lexical: Success@5=0.9, MRR@5=0.802

## RAG Support

- queries: 40
- supported_rate: 0.975
- mean_support_score: 0.945

## Agent Metrics

- tasks: 144
- format_compliance_rate: 1
- concept_attribution_rate: 0.833
- hint_no_full_solution_rate: 1
- groundedness_proxy_rate: 0.826
- api_error_count: 17
- completed_response_rate: 0.882

## IRT Simulation

- random: {'weak_concept_coverage': 0.771, 'difficulty_match_error': 1.051, 'concept_diversity': 14.5, 'prerequisite_violation_rate': 0.833}
- difficulty_only: {'weak_concept_coverage': 0.521, 'difficulty_match_error': 0.363, 'concept_diversity': 9.25, 'prerequisite_violation_rate': 0.208}
- graph_only: {'weak_concept_coverage': 1.0, 'difficulty_match_error': 1.328, 'concept_diversity': 14.25, 'prerequisite_violation_rate': 0.979}
- graph_irt: {'weak_concept_coverage': 1.0, 'difficulty_match_error': 1.268, 'concept_diversity': 14.75, 'prerequisite_violation_rate': 0.896}

## Ablation

- {'condition': 'Full system', 'concept_f1': 0.795, 'retrieval_mrr': 1.0, 'rag_support': 0.945, 'agent_quality': 0.886, 'adaptive_score': 1.0}
- {'condition': 'No concept graph', 'concept_f1': 0.795, 'retrieval_mrr': 0.802, 'rag_support': 0.865, 'agent_quality': 0.633, 'adaptive_score': 0.521}
- {'condition': 'No concept filter', 'concept_f1': 0.795, 'retrieval_mrr': 0.802, 'rag_support': 0.8949999999999999, 'agent_quality': 0.726, 'adaptive_score': 1.0}
- {'condition': 'No RAG grounding', 'concept_f1': 0.795, 'retrieval_mrr': 0.0, 'rag_support': 0.0, 'agent_quality': 0.75, 'adaptive_score': 1.0}
- {'condition': 'No IRT adaptation', 'concept_f1': 0.795, 'retrieval_mrr': 1.0, 'rag_support': 0.945, 'agent_quality': 0.916, 'adaptive_score': 1.0}
