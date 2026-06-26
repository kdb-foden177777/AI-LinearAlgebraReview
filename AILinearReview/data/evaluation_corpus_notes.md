# Evaluation Corpus Notes

This file turns the converted materials into a concrete evaluation plan for
the paper outline.

## Corpus Partition

### Course-aligned corpus

Use:

- `slides_md`
- `flipped_md`

Purpose:

- build the concept graph
- construct the RAG corpus
- sample in-course exercises
- derive rubric and error-attribution examples

This corpus should be treated as the system's "course material." Outputs from
the adaptive review system should be constrained to this corpus when claiming
course alignment.

### External exam benchmark

Use:

- `mit_linear_algebra_md`

Purpose:

- evaluate exam-style question coverage
- test concept tagging on unseen finals
- provide item-level examples for IRT difficulty adaptation
- evaluate answer/solution retrieval when solution files are available

This corpus should be treated as an external benchmark, not as the course
syllabus.

## Candidate Evaluation Tasks

### Task 1. Concept Tagging

Input: exam question text.

Output: one or more concept graph nodes.

Example labels:

- `rank`
- `nullspace`
- `determinant`
- `eigenvalue`
- `orthogonal_projection`
- `least_squares`
- `svd`

Metrics:

- exact match for single-label questions
- micro/macro F1 for multi-label tagging
- human audit on a small sample

Materials:

- MIT finals with solutions
- flipped final and midterm

### Task 2. Retrieval Quality

Input: a concept or student question.

Output: relevant slide/exercise chunks with citations.

Metrics:

- recall@k
- citation accuracy
- rate of unsupported statements

Materials:

- `slides_md` for theory
- `flipped_md` for exercises and worked examples

### Task 3. Rubric-Based Grading

Input: question, solution rubric, student answer.

Output: score, feedback, error type.

Metrics:

- score agreement with reference solution
- absolute score error
- error-type classification accuracy

Materials:

- flipped hand-ins with solutions
- MIT exam/solution pairs

### Task 4. Adaptive Selection

Input: student model with mastery scores and IRT ability estimate theta.

Output: next question and explanation for why it was selected.

Metrics:

- difficulty match: `abs(b - theta)`
- high-weight weak-concept coverage
- avoidance of repeated concepts
- interpretability of selection reason

Materials:

- MIT exam items as candidate item pool
- concept graph from `slides_md`

### Task 5. Ablation Evaluation

Compare:

- full system
- no concept graph
- no RAG
- no mastery update
- no prerequisite propagation
- no IRT selection

Expected observations:

- removing concept graph increases out-of-scope or weakly aligned outputs
- removing RAG increases unsupported explanations
- removing mastery update makes the system one-shot rather than closed-loop
- removing prerequisite propagation reduces upstream remediation quality
- removing IRT worsens difficulty matching

## Recommended Benchmark Table

The paper can report a corpus table like this:

| Source | Count | Role | Notes |
|---|---:|---|---|
| Hefferon slides | 54 Markdown files | concept graph and explanations | repeated slide text requires deduplication |
| Hefferon flipped material | 81 Markdown files | exercises, hand-ins, exams | includes in-class tasks and assessments |
| MIT 18.06 finals | 65 Markdown files | external benchmark and IRT item pool | multiple years with solution availability varying |

## Quality Control Rules

Before using a Markdown file as evidence:

1. Check whether it contains the main question or theorem text.
2. Ignore blank answer regions, scrap paper, page headers, and score boxes.
3. For MIT files, treat layout loss as acceptable if the mathematical question
   and solution text are preserved.
4. If a file has suspiciously short content, compare it against the original
   PDF before using it in a benchmark.
5. Do not count duplicated progressive slide fragments as separate concepts.

## Paper Placement

Use this information in:

- Section 6.1: corpus construction
- Section 7.1: question generation strategies
- Section 7.2: grading and rubric design
- Section 10.4: IRT item parameter estimation
- Section 12.1: evaluation benchmark
- Section 12.4: ablation settings

