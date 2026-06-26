# Full Experiment Flowchart for the Linear Algebra Adaptive Review Paper

This document is the controlling workflow for the full paper experiments. Future
experimental scripts, result tables, and manuscript revisions should follow this
flowchart closely.

## Goal

Produce a complete experimental evidence package for the paper:

1. Corpus-scale characterization and benchmark construction.
2. Concept graph and concept-tagging evaluation.
3. Retrieval and RAG grounding evaluation.
4. Agent grading, hinting, and dialogue evaluation.
5. Adaptive item-selection and IRT simulation.
6. Ablation experiments.
7. Final paper-ready tables, figures, and result narratives.

## Complete Flowchart

```mermaid
flowchart TD
    A[Start: Available Materials] --> A1[slides_md]
    A --> A2[flipped_md]
    A --> A3[mit_linear_algebra_md]
    A --> A4[outline.docx and MDPI template]
    A --> A5[UI prototype and local agent server]

    A1 --> B[Corpus Audit and Cleaning]
    A2 --> B
    A3 --> B

    B --> B1[Count files, lines, tokens, topics]
    B --> B2[Detect duplicate slide fragments]
    B --> B3[Detect corrupted or empty conversions]
    B --> B4[Split materials by role]

    B4 --> C[Benchmark Construction]
    C --> C1[Course-scope corpus: slides_md]
    C --> C2[Practice corpus: flipped_md]
    C --> C3[Exam benchmark: mit_linear_algebra_md]
    C --> C4[Question/snippet extraction]
    C4 --> C5[Benchmark JSONL]

    C5 --> D[Concept Graph Construction]
    D --> D1[Seed nodes from syllabus units]
    D --> D2[Prerequisite edges]
    D --> D3[Concept aliases and keywords]
    D --> D4[Node weights from slides, flipped tasks, exams]
    D --> D5[Machine-readable concept graph JSON]

    C5 --> E[Concept Tagging Evaluation]
    D5 --> E
    E --> E1[LLM concept labels]
    E --> E2[Keyword/silver labels]
    E --> E3[Human-check subset if available]
    E --> E4[Precision, recall, F1, Jaccard]
    E --> E5[Confusion/error analysis]

    C5 --> F[Retrieval Benchmark]
    D5 --> F
    F --> F1[Build chunk index]
    F --> F2[Queries from concept probes and exam tasks]
    F --> F3[Baseline lexical retrieval]
    F --> F4[Concept-filtered retrieval]
    F --> F5[Hybrid or reranked retrieval if implemented]
    F --> F6[Success@k, MRR@k, nDCG@k]

    F6 --> G[RAG Answer Support Evaluation]
    E1 --> G
    G --> G1[Generate grounded explanations]
    G --> G2[Judge support against retrieved chunks]
    G --> G3[Measure supported rate and support score]
    G --> G4[Analyze unsupported or drifting answers]

    C5 --> H[Agent Interaction Evaluation]
    D5 --> H
    F1 --> H
    H --> H1[Grading tasks]
    H --> H2[Hint-generation tasks]
    H --> H3[Dialogue tutoring tasks]
    H1 --> H4[Rubric format compliance]
    H1 --> H5[Concept attribution quality]
    H2 --> H6[Hint usefulness and no-full-solution rate]
    H3 --> H7[Groundedness, continuity, action quality]

    C5 --> I[Adaptive Selection and IRT Simulation]
    D5 --> I
    I --> I1[Assign initial item difficulty]
    I --> I2[Simulate learner profiles]
    I --> I3[Select next items with graph + IRT]
    I --> I4[Compare to non-adaptive baselines]
    I --> I5[Coverage, difficulty match, remediation efficiency]

    E4 --> J[Ablation Experiments]
    F6 --> J
    G3 --> J
    H4 --> J
    I5 --> J
    J --> J1[Full system]
    J --> J2[No concept graph]
    J --> J3[No concept filter in retrieval]
    J --> J4[No RAG grounding]
    J --> J5[No rubric structure]
    J --> J6[No IRT adaptation]
    J --> J7[Ablation result table]

    J7 --> K[Paper Evidence Package]
    E5 --> K
    G4 --> K
    H7 --> K
    I5 --> K
    K --> K1[Tables]
    K --> K2[Figures]
    K --> K3[Result paragraphs]
    K --> K4[Limitations]
    K --> K5[Reproducibility notes]

    K --> L[Update MDPI Manuscript]
    L --> M[Compile PDF]
    M --> N[Final human text revision]
```

## Stage-by-Stage Specification

### Stage 1. Corpus Audit and Cleaning

Purpose: verify that the converted Markdown folders are usable and quantify the
available materials.

Inputs:

- `slides_md`
- `flipped_md`
- `mit_linear_algebra_md`

Outputs:

- `paper_work/full_experiment_outputs/corpus_audit.json`
- `paper_work/full_experiment_outputs/corpus_audit.md`
- Optional: `paper_work/full_experiment_outputs/conversion_quality_flags.csv`

Required measurements:

- number of Markdown files by folder
- line count, character count, approximate token count
- empty or very short files
- repeated-fragment rate for slides
- source-role labels: lecture, activity, exam, solution, handout

Paper use:

- Corpus table
- Data-preparation paragraph
- Limitations about PDF-to-Markdown conversion quality

### Stage 2. Benchmark Construction

Purpose: create a stable benchmark from the available materials.

Inputs:

- audited Markdown corpus
- source-role labels

Outputs:

- `paper_work/full_experiment_outputs/benchmark_items.jsonl`
- `paper_work/full_experiment_outputs/benchmark_summary.md`

Benchmark item fields:

- `id`
- `source_path`
- `source_role`
- `unit`
- `text`
- `question_text`
- `solution_text` if available
- `expected_concepts`
- `difficulty_seed`
- `has_solution`
- `split`: development, evaluation, or case_study

Sampling principle:

- Use `slides_md` mainly for explanations and concept scope.
- Use `flipped_md` for practice and classroom-style tasks.
- Use `mit_linear_algebra_md` for final-exam benchmark items.

Paper use:

- Benchmark construction subsection
- Evaluation setup table

### Stage 3. Concept Graph Construction

Purpose: convert the current seed concept graph into an executable graph.

Inputs:

- `paper_work/concept_graph_seed.md`
- benchmark items
- corpus keyword statistics

Outputs:

- `paper_work/full_experiment_outputs/concept_graph.json`
- `paper_work/full_experiment_outputs/concept_graph_table.csv`
- `paper_work/full_experiment_outputs/concept_edges.csv`

Required contents:

- concept node IDs
- labels
- aliases
- unit labels
- prerequisite edges
- syllabus weights
- exam weights
- remediation templates

Paper use:

- Concept graph table
- Graph construction method
- Remediation path examples

### Stage 4. Concept Tagging Evaluation

Purpose: evaluate whether benchmark items can be mapped to concept nodes.

Inputs:

- `benchmark_items.jsonl`
- `concept_graph.json`
- ZhipuAI API through `.env`

Outputs:

- `paper_work/full_experiment_outputs/concept_tagging_predictions.csv`
- `paper_work/full_experiment_outputs/concept_tagging_metrics.json`
- `paper_work/full_experiment_outputs/concept_tagging_error_analysis.md`

Conditions:

- keyword/silver baseline
- LLM zero-shot tagging
- LLM with concept aliases and graph context
- optional manually checked subset

Metrics:

- micro precision, recall, F1
- macro precision, recall, F1
- mean Jaccard
- per-concept support
- common confusions

Paper use:

- Concept tagging result table
- Error analysis paragraph

### Stage 5. Retrieval Benchmark

Purpose: measure whether the system retrieves relevant materials for concepts,
questions, and errors.

Inputs:

- benchmark queries
- corpus chunks
- concept graph

Outputs:

- `paper_work/full_experiment_outputs/retrieval_results.csv`
- `paper_work/full_experiment_outputs/retrieval_metrics.json`
- `paper_work/full_experiment_outputs/retrieval_examples.md`

Conditions:

- lexical retrieval baseline
- concept-filtered lexical retrieval
- source-role-aware retrieval
- optional hybrid retrieval if implemented

Metrics:

- Success@1, Success@3, Success@5
- MRR@5
- nDCG@5 if graded relevance is available
- source-role accuracy

Paper use:

- Retrieval result table
- RAG setup description

### Stage 6. RAG Answer Support Evaluation

Purpose: test whether generated explanations are supported by retrieved
materials.

Inputs:

- retrieval results
- benchmark queries
- retrieved context packs
- ZhipuAI API

Outputs:

- `paper_work/full_experiment_outputs/rag_answer_rows.csv`
- `paper_work/full_experiment_outputs/rag_support_metrics.json`
- `paper_work/full_experiment_outputs/rag_failure_cases.md`

Conditions:

- answer without retrieval
- answer with retrieval
- answer with concept-filtered retrieval

Metrics:

- supported rate
- mean support score
- unsupported claim rate
- citation/source-use consistency
- answer completeness score

Paper use:

- RAG result table
- Grounding and hallucination discussion

### Stage 7. Agent Interaction Evaluation

Purpose: evaluate the usable agent functions exposed by the UI.

Inputs:

- UI item pool
- benchmark items
- learner-state scenarios
- ZhipuAI API

Outputs:

- `paper_work/full_experiment_outputs/agent_grading_rows.csv`
- `paper_work/full_experiment_outputs/agent_hint_rows.csv`
- `paper_work/full_experiment_outputs/agent_dialogue_rows.csv`
- `paper_work/full_experiment_outputs/agent_metrics.json`

Tasks:

- grade a student answer
- generate a hint
- answer a dialogue question
- update or recommend next action

Metrics:

- format compliance rate
- score plausibility
- concept attribution rate
- groundedness score
- hint no-full-solution rate
- dialogue continuity score
- recommended-action validity

Paper use:

- Agent evaluation table
- UI and agent implementation subsection
- Case study

### Stage 8. Adaptive Selection and IRT Simulation

Purpose: evaluate the proposed IRT and graph-constrained adaptation without
claiming real student calibration.

Inputs:

- benchmark item pool
- concept labels
- initial difficulty estimates
- simulated learner profiles

Outputs:

- `paper_work/full_experiment_outputs/irt_simulation_rows.csv`
- `paper_work/full_experiment_outputs/irt_simulation_metrics.json`
- `paper_work/full_experiment_outputs/adaptive_paths.md`

Conditions:

- random item selection
- difficulty-only selection
- graph-only remediation
- graph + IRT selection

Metrics:

- difficulty match error
- weak-concept coverage
- prerequisite violation rate
- estimated remediation efficiency
- item diversity

Paper use:

- IRT simulation table
- Adaptive path figure or example
- Limitations clarifying simulated rather than real learner data

### Stage 9. Ablation Experiments

Purpose: show which system components contribute to performance.

Inputs:

- metrics from Stages 4 to 8

Outputs:

- `paper_work/full_experiment_outputs/ablation_results.csv`
- `paper_work/full_experiment_outputs/ablation_summary.md`

Ablation conditions:

- Full system
- No concept graph
- No concept-filtered retrieval
- No RAG grounding
- No rubric structure
- No dialogue memory
- No IRT adaptation

Paper use:

- Main ablation table
- Discussion of which components matter most

### Stage 10. Paper Evidence Package

Purpose: convert all experiment outputs into manuscript-ready artifacts.

Inputs:

- all metrics JSON/CSV files
- failure-case notes
- representative examples

Outputs:

- `paper_work/full_experiment_outputs/paper_tables.md`
- `paper_work/full_experiment_outputs/paper_result_narrative.md`
- `paper_work/full_experiment_outputs/paper_limitations.md`
- optional figure files

Paper use:

- Update Methods, Results, Discussion, Limitations, and Conclusion.

## Final Required Paper Tables

The full paper should eventually contain at least these tables:

1. Corpus composition table.
2. Benchmark item distribution table.
3. Concept graph unit/node/edge summary table.
4. Concept tagging metrics table.
5. Retrieval metrics table.
6. RAG support metrics table.
7. Agent interaction metrics table.
8. IRT simulation/adaptive selection table.
9. Ablation table.

## Final Required Paper Figures

The full paper should eventually contain at least these figures:

1. System architecture figure.
2. Human-system interaction UI figure or schematic.
3. Concept graph overview or unit-level graph.
4. Adaptive review loop figure.
5. Optional: ablation bar chart or IRT path example.

## Execution Rule for Future Work

When continuing experiments, do not jump directly to the manuscript. Follow this
order:

1. Generate or update data artifacts.
2. Validate metrics.
3. Save result files.
4. Summarize result implications.
5. Only then update the MDPI manuscript.

If an experiment cannot be fully run, mark it explicitly as one of:

- `completed`
- `pilot_only`
- `simulated`
- `blocked`
- `not_claimed`

The manuscript must never describe a `pilot_only` or `simulated` result as a
full real-world learning outcome.
