# Material Index for the Linear Algebra Adaptive Review Paper

This file summarizes the usable Markdown corpus for the paper project. The
purpose is to separate primary evidence from auxiliary files before drafting
the paper.

## Scope

Primary materials are limited to the three converted Markdown folders:

| Folder | Markdown files | Size | Primary use in paper |
|---|---:|---:|---|
| `slides_md` | 54 | 8.8M | Course content, concept graph construction, topic boundaries |
| `flipped_md` | 81 | 1.3M | In-class tasks, hand-ins, exams, worked solutions, error-pattern examples |
| `mit_linear_algebra_md` | 65 | 1.9M | External final-exam benchmark, question bank, solution references, IRT examples |

Total available Markdown files: 200.

Total text scale: approximately 37,632 lines.

Other files in the repository are auxiliary. The original PDFs are useful only
for quality checks against Markdown conversion. `marker-master`,
`requirements.txt`, and preprocessing READMEs are implementation references,
not conceptual sources for the learning-system paper.

## Corpus Roles

### `slides_md`

Role: course-structure and concept-source corpus.

This folder contains lecture slide conversions organized into five units:

- `one`: solving linear systems
- `two`: vector spaces
- `three`: maps / linear transformations
- `four`: determinants
- `five`: complex vector spaces and later spectral material

Each unit usually has base slides, handouts, and all-proofs variants. For the
paper, the most useful signal is not every repeated slide line, but the topic
progression and the formal vocabulary. These files should anchor:

- concept node extraction
- prerequisite edge construction
- course-specific scope definition
- examples of lecture-aligned explanations

Quality note: slide conversions contain repeated fragments because progressive
slides repeat prior text. Downstream extraction should deduplicate repeated
definitions and theorem statements.

Representative files:

- `slides_md/one/one_i/one_i.md`
- `slides_md/two/two_i/two_i.md`
- `slides_md/three/three_i/three_i.md`
- `slides_md/four/four_i/four_i.md`
- `slides_md/five/five_i/five_i.md`

### `flipped_md`

Role: instructional activity and assessment corpus.

This folder contains in-class exercises, hand-ins, a midterm, and a final. It
is useful for grounding the system in realistic student-facing tasks rather
than only lecture exposition.

Major groups:

- `flipped_md/inclass/linear-systems`
- `flipped_md/inclass/vector-spaces`
- `flipped_md/inclass/map`
- `flipped_md/inclass/determinants`
- `flipped_md/inclass/jc`
- `flipped_md/handin`

Recommended uses:

- extract worked examples and small exercises for the RAG corpus
- collect typical answer formats for rubric design
- map hand-in/final questions to concept graph nodes
- derive examples for error attribution and mastery updates

Representative files:

- `flipped_md/handin/final/final.md`
- `flipped_md/handin/midterm/midterm.md`
- `flipped_md/inclass/linear-systems/One-III/One-III.md`
- `flipped_md/inclass/vector-spaces/Two-II/Two-II.md`
- `flipped_md/inclass/map/Three-I/Three-I.md`
- `flipped_md/inclass/determinants/Four-I/Four-I.md`

### `mit_linear_algebra_md`

Role: external benchmark and historical final-exam corpus.

This folder contains MIT 18.06 final exams and many solution files across
multiple semesters. It should not define the course scope by itself; instead it
is best used as an external benchmark for evaluation and as a source of
exam-style questions.

Coverage includes files from the late 1990s through 2022, with many paired
exam/solution sets. Some folders explicitly note missing answers in their
folder names.

Recommended uses:

- build a final-exam benchmark for system evaluation
- sample problems for knowledge-point tagging
- estimate item difficulty from problem structure
- compare generated questions against real exam style
- create case studies for IRT and adaptive selection

Representative files:

- `mit_linear_algebra_md/spring2014/Final_s14_draft/Final_s14_draft.md`
- `mit_linear_algebra_md/spring2014/Final_s14_sol/Final_s14_sol.md`
- `mit_linear_algebra_md/fall2017/final/final.md`
- `mit_linear_algebra_md/fall2017/final-sol/final-sol.md`
- `mit_linear_algebra_md/spring2022/final/final.md`
- `mit_linear_algebra_md/spring2022/finalsol/finalsol.md`

Quality note: MIT final exams are not the same course as the Hefferon slide
corpus. They should be treated as a benchmark and transfer corpus, not as the
authoritative syllabus.

## Keyword Signal

The following rough corpus-wide keyword counts were observed by simple text
search. They are not final statistics, but they help prioritize concept
coverage:

| Keyword | Approximate hits |
|---|---:|
| basis | 864 |
| eigen | 689 |
| determinant | 527 |
| rank | 416 |
| dimension | 397 |
| orthogonal | 311 |
| singular | 287 |
| nullspace | 205 |
| projection | 192 |
| column space | 155 |
| Jordan | 79 |
| linear transformation | 61 |
| positive definite | 55 |
| least squares | 40 |
| SVD | 24 |

These counts suggest that the paper should emphasize linear systems,
subspaces, basis/dimension, determinants, eigen-analysis, orthogonality,
projection, and spectral/SVD topics.

## How These Materials Map to the Outline

| Outline section | Primary material | How to use it |
|---|---|---|
| Section 5: Concept graph | `slides_md` | Extract nodes, prerequisite edges, and topic weights |
| Section 6: RAG | `slides_md`, `flipped_md` | Treat slides as explanations and flipped files as worked examples |
| Section 7: Question generation and grading | `flipped_md`, `mit_linear_algebra_md` | Extract problem types, answers, and rubric-like solution steps |
| Section 8: Error attribution | `flipped_md`, MIT solutions | Derive examples of wrong-step categories and prerequisite failures |
| Section 10: IRT | MIT finals | Use exam problems as item pool for difficulty/discrimination discussion |
| Section 12: Evaluation | MIT finals plus flipped exams | Use paired exam/solution files for benchmark and ablation examples |

## Immediate Next Use

The next working artifact should be a seed concept graph. It should be based
primarily on `slides_md`, then cross-checked against high-frequency topics from
`flipped_md` and `mit_linear_algebra_md`.

