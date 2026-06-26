# MIT Linear Algebra Finals Preprocessing README

本 README 专门用于处理 `mit linear algebra.zip` 中的 MIT 18.06 Linear Algebra 历年 final exam 材料。  
这份材料应主要定位为 **external examination benchmark corpus**，即“外部考试评测集”，用于支持论文中的系统级评估、自动批改一致性测试、题目难度匹配测试、考纲对齐测试和消融实验。

与 Hefferon slides 和 flipped-classroom materials 不同，这份 MIT final 材料不建议作为主要训练题库，而应优先作为 **外部 benchmark** 使用。

---

## 1. Source Description

原始压缩包：

```text
mit linear algebra.zip
```

解压后大致结构为：

```text
mit linear algebra/
├── fall1999/
├── fall2000/
├── fall2001...
├── ...
├── spring2022/
└── fall2022/
```

每个 semester 文件夹通常包含：

```text
final exam PDF
solution PDF
```

例如：

```text
fall2022/final.pdf
fall2022/finalsol.pdf

spring2022/final.pdf
spring2022/finalsol.pdf

fall2019/Final.pdf
fall2019/Final Solutions.pdf
```

部分年份只有试卷，没有答案；部分文件名中包含乱码，这是由于原文件夹名包含中文提示，例如“没找到答案”。

---

## 2. Recommended Role in the Paper

这份 MIT finals 最适合用于论文第 12 节的评估部分。

推荐定位：

```text
external benchmark
external final-exam benchmark
out-of-distribution examination benchmark
course-scope alignment benchmark
automatic grading benchmark
```

不推荐定位：

```text
primary course corpus
training exercise bank
course lecture material
```

原因：

1. MIT final 题目不一定完全匹配目标课程考纲。
2. 题目难度可能高于普通工科线性代数期末。
3. 某些题目包含目标课程未覆盖的知识点。
4. 如果作为训练题库，会降低后续外部评估的可信度。

---

## 3. Relationship with Other Data Sources

建议与前两份材料这样分工：

| Data Source | Recommended Role |
|---|---|
| `slides.zip` | RAG 讲解语料、定义、定理、证明、概念解释 |
| `flipped.zip` | 课堂练习、作业题库、midterm/final 内部 benchmark |
| `mit linear algebra.zip` | 外部 final exam benchmark、泛化测试、超纲检测 |
| 用户自己的讲义 | primary course corpus |
| 用户自己的配套习题 | primary exercise bank |

MIT finals 应放在数据体系的评估端，而不是训练端。

---

## 4. Target Output Datasets

最终建议生成以下文件：

```text
data_processed/mit_finals/
├── mit_finals_manifest.csv
├── mit_final_problem_bank_raw.jsonl
├── mit_final_benchmark_in_scope.jsonl
├── mit_final_benchmark_out_of_scope.jsonl
├── mit_final_solution_pairs.jsonl
├── mit_final_no_solution_set.jsonl
├── mit_final_visual_assets_manifest.csv
└── mit_final_metadata_summary.json
```

---

## 5. Dataset Roles

---

### 5.1 MIT Finals Manifest

File:

```text
mit_finals_manifest.csv
```

Purpose:

```text
记录所有年份、学期、试卷文件、答案文件、文件状态、是否可用于 benchmark。
```

Recommended fields:

```csv
semester_id,year,term,exam_file,solution_file,has_solution,file_status,use_type,notes
```

Example:

```csv
fall2022,2022,fall,fall2022/final.pdf,fall2022/finalsol.pdf,true,paired_pdf,external_benchmark,
spring2022,2022,spring,spring2022/final.pdf,spring2022/finalsol.pdf,true,paired_pdf,external_benchmark,
fall2000,2000,fall,fall2000/final-fall-00.pdf,,false,exam_only,no_solution_set,no official solution found
fall2012,2012,fall,fall2012/final-with-sol.pdf,fall2012/final-with-sol.pdf,true,combined_exam_solution,external_benchmark,exam and solution are in one PDF
```

---

### 5.2 Raw MIT Final Problem Bank

File:

```text
mit_final_problem_bank_raw.jsonl
```

Purpose:

```text
保存所有从 MIT final PDF 中解析出的题目，不立即决定是否纳入最终 benchmark。
```

This is an intermediate dataset.

---

### 5.3 In-Scope MIT Final Benchmark

File:

```text
mit_final_benchmark_in_scope.jsonl
```

Purpose:

```text
保存与目标课程考纲一致的 MIT final 题，用于系统级评估。
```

Example use:

```text
automatic grading evaluation
concept attribution evaluation
RAG-supported explanation evaluation
difficulty matching evaluation
ablation experiments
```

---

### 5.4 Out-of-Scope MIT Final Benchmark

File:

```text
mit_final_benchmark_out_of_scope.jsonl
```

Purpose:

```text
保存超出目标课程考纲的 MIT final 题，用于考纲对齐和超纲检测实验。
```

This dataset is valuable because the paper claims that the system is syllabus-aligned.  
The out-of-scope set can test whether the system can identify and handle problems outside the target final review scope.

---

### 5.5 Solution Pair Records

File:

```text
mit_final_solution_pairs.jsonl
```

Purpose:

```text
记录每道题和标准答案之间的配对关系。
```

This is important because many semesters have separate exam and solution PDFs.

---

### 5.6 No-Solution Set

File:

```text
mit_final_no_solution_set.jsonl
```

Purpose:

```text
保存没有官方答案的年份或题目。
```

These problems can still be used for:

```text
concept tagging evaluation
scope filtering evaluation
difficulty estimation
manual benchmark construction
```

But should not be used for automatic grading evaluation unless solutions are manually created and verified.

---

## 6. Recommended Folder Structure

```text
mit_finals_preprocessing/
│
├── README.md
│
├── data_raw/
│   └── mit_linear_algebra/
│       ├── fall1999/
│       ├── spring1999/
│       ├── ...
│       └── fall2022/
│
├── data_intermediate/
│   ├── extracted_pages/
│   ├── cleaned_pages/
│   ├── exam_problem_candidates/
│   ├── solution_candidates/
│   ├── aligned_problem_solution_candidates/
│   ├── scope_filtering_candidates/
│   └── duplicate_candidates/
│
├── data_processed/
│   ├── mit_finals_manifest.csv
│   ├── mit_final_problem_bank_raw.jsonl
│   ├── mit_final_benchmark_in_scope.jsonl
│   ├── mit_final_benchmark_out_of_scope.jsonl
│   ├── mit_final_solution_pairs.jsonl
│   ├── mit_final_no_solution_set.jsonl
│   ├── mit_final_visual_assets_manifest.csv
│   └── mit_final_metadata_summary.json
│
├── quality_check/
│   ├── missing_solution_report.csv
│   ├── solution_alignment_review.csv
│   ├── low_confidence_concept_tags.csv
│   ├── out_of_scope_review.csv
│   ├── duplicate_problem_candidates.csv
│   ├── benchmark_manual_review_samples.csv
│   └── leakage_check_report.csv
│
├── scripts/
│   ├── 01_unzip_and_manifest.py
│   ├── 02_classify_exam_solution_files.py
│   ├── 03_extract_pdf_text.py
│   ├── 04_clean_exam_text.py
│   ├── 05_parse_exam_problems.py
│   ├── 06_parse_solution_files.py
│   ├── 07_align_exam_solution.py
│   ├── 08_tag_concepts.py
│   ├── 09_scope_filtering.py
│   ├── 10_estimate_difficulty_irt.py
│   ├── 11_build_rubrics.py
│   ├── 12_deduplicate_and_leakage_check.py
│   ├── 13_quality_check.py
│   └── 14_export_benchmarks.py
│
└── prompts/
    ├── exam_problem_parsing_prompt.md
    ├── solution_alignment_prompt.md
    ├── concept_tagging_prompt.md
    ├── scope_filtering_prompt.md
    ├── difficulty_estimation_prompt.md
    └── rubric_generation_prompt.md
```

---

## 7. File Classification

The first key step is to classify each PDF as one of the following:

```text
exam_pdf
solution_pdf
combined_exam_solution_pdf
exam_only_no_solution
visual_solution_asset
unknown
```

---

### 7.1 Classification Rules

Use filename patterns:

```text
If filename contains "sol", "solution", "solutions", "answer", "answers", "ans":
    solution_pdf

If filename contains "with-sol":
    combined_exam_solution_pdf

If filename contains "final" and not solution pattern:
    exam_pdf

If file extension is .png:
    visual_solution_asset
```

Examples:

```text
fall2022/final.pdf                         -> exam_pdf
fall2022/finalsol.pdf                      -> solution_pdf
fall2019/Final Solutions.pdf               -> solution_pdf
spring2010/18.06-Final-Answers-Sp2010.pdf  -> solution_pdf
fall2012/final-with-sol.pdf                -> combined_exam_solution_pdf
spring2011/sol-1.png                       -> visual_solution_asset
```

---

## 8. Manifest Construction

Generate:

```text
mit_finals_manifest.csv
```

Recommended columns:

```csv
semester_id,year,term,folder_name,exam_file,solution_file,has_solution,solution_format,file_status,use_type,notes
```

Example:

```csv
fall2022,2022,fall,fall2022,fall2022/final.pdf,fall2022/finalsol.pdf,true,pdf,paired_pdf,external_benchmark,
spring2011,2011,spring,spring2011,spring2011/spring 2011 final exam.pdf,spring2011/sol-1.png|spring2011/sol-2.png|spring2011/sol-3.png,true,png,exam_pdf_with_image_solutions,manual_review_required
fall1995,1995,fall,1995n1993...,1995n1993.../final-95.pdf,,false,,exam_only,no_solution_set,no official solution found
fall1993,1993,fall,1995n1993...,1995n1993.../final-93.pdf,,false,,exam_only,no_solution_set,no official solution found
```

---

## 9. Text Extraction

Extract every PDF page into JSONL records.

Output:

```text
data_intermediate/extracted_pages/
```

Page record schema:

```json
{
  "page_id": "mit_fall2022_exam_p001",
  "semester_id": "fall2022",
  "year": 2022,
  "term": "fall",
  "file_path": "fall2022/final.pdf",
  "file_role": "exam_pdf",
  "page": 1,
  "raw_text": "...",
  "text_length": 1450,
  "extraction_status": "success",
  "image_required": false
}
```

For scanned pages or image-heavy pages:

```json
{
  "extraction_status": "visual_or_low_text",
  "image_required": true
}
```

---

## 10. Cleaning Rules

Clean PDF text while preserving mathematical structure.

Recommended cleaning:

```text
1. Remove repeated headers and footers.
2. Remove standalone page numbers.
3. Normalize whitespace.
4. Preserve problem numbers.
5. Preserve subproblem labels: (a), (b), (c), etc.
6. Preserve point values.
7. Preserve matrix/vector notation as much as possible.
8. Preserve "Solution", "Answer", and "Final Answer" labels.
9. Merge broken lines caused by PDF extraction.
10. Do not remove theorem names or instructions.
```

Do not remove:

```text
problem number
subproblem label
matrix entries
equation system
point values
solution steps
exam instructions that affect grading
```

---

## 11. Problem Parsing

Each final exam should be parsed into one problem record per numbered problem.

Output intermediate file:

```text
mit_final_problem_bank_raw.jsonl
```

Recommended schema:

```json
{
  "problem_id": "mit_fall2022_q001",
  "corpus_name": "mit_18_06_finals",
  "source_role": "external_benchmark",
  "source_type": "final_exam",
  "semester_id": "fall2022",
  "year": 2022,
  "term": "fall",
  "file_path": "fall2022/final.pdf",
  "page_start": 1,
  "page_end": 1,
  "problem_number": "1",
  "subproblem_label": null,
  "problem_text": "...",
  "raw_points": "10",
  "solution": "",
  "final_answer": "",
  "solution_source": "not_aligned_yet",
  "concept_tags": [],
  "prerequisite_tags": [],
  "problem_type": "",
  "difficulty_level": null,
  "irt": {},
  "in_course_scope": null,
  "use_type": "candidate_external_benchmark",
  "verified": false
}
```

---

### 11.1 Subproblem Handling

If a problem contains several subparts:

Option A: Keep as one mixed problem.

```json
{
  "problem_type": "mixed",
  "subproblem_label": null
}
```

Option B: Split into subproblem records.

```json
{
  "problem_id": "mit_fall2022_q003_a",
  "parent_problem_id": "mit_fall2022_q003",
  "subproblem_label": "a"
}
```

Recommended:

```text
For grading evaluation:
    split subproblems when each subpart has a clear answer.

For concept coverage evaluation:
    keep parent-level problem and record multiple concept_tags.
```

---

## 12. Solution Parsing and Alignment

Many MIT exams have separate solution PDFs.  
Therefore, solution alignment is one of the most important steps.

---

### 12.1 Pairing Level

First pair at the semester level:

```text
fall2022/final.pdf <-> fall2022/finalsol.pdf
spring2022/final.pdf <-> spring2022/finalsol.pdf
fall2019/Final.pdf <-> fall2019/Final Solutions.pdf
```

Then pair at the problem level:

```text
Question 1 <-> Solution 1
Question 2 <-> Solution 2
...
```

---

### 12.2 Solution Pair Record

File:

```text
mit_final_solution_pairs.jsonl
```

Schema:

```json
{
  "pair_id": "mit_fall2022_q001_pair",
  "problem_id": "mit_fall2022_q001",
  "semester_id": "fall2022",
  "exam_file": "fall2022/final.pdf",
  "solution_file": "fall2022/finalsol.pdf",
  "problem_number": "1",
  "solution_text": "...",
  "final_answer": "...",
  "alignment_confidence": 0.95,
  "alignment_method": "problem_number_matching",
  "requires_manual_review": false
}
```

---

### 12.3 Alignment Rules

```text
1. Match by problem number first.
2. Use subproblem labels if present.
3. If solution PDF has different numbering, use text similarity.
4. If solution is embedded in the same file, split by "Solution" labels.
5. If solution is image-only, mark image_required = true.
6. Low confidence alignment must be manually reviewed.
```

Low-confidence cases:

```text
alignment_confidence < 0.85
```

should enter:

```text
solution_alignment_review.csv
```

---

## 13. Concept Tagging

Every MIT problem must be mapped to the target course concept graph.

Required fields:

```json
{
  "concept_tags": [],
  "prerequisite_tags": []
}
```

---

### 13.1 Recommended Concept Tag Set

Use the same concept IDs as the main course concept graph:

```text
linear_systems
gaussian_elimination
row_reduction
reduced_echelon_form
matrix_rank
solution_structure
vector_space
subspace
linear_independence
basis
dimension
orthogonality
orthogonal_projection
least_squares
determinant_properties
determinant_geometry
laplace_expansion
linear_transformation
kernel
range
matrix_representation
matrix_operations
inverse_matrix
change_of_basis
similarity
eigenvalues
eigenvectors
diagonalization
symmetric_matrix
quadratic_form
positive_definite_matrix
singular_value_decomposition
markov_matrix
fourier_series
differential_equations
complex_vector_space
```

Some MIT final problems may include advanced or extra topics.  
These should be tagged, but may later be marked out of scope.

---

## 14. Scope Filtering

MIT 18.06 coverage may not match the target course.  
Therefore, scope filtering is mandatory.

---

### 14.1 Output Fields

```json
{
  "in_course_scope": true,
  "matched_course_concepts": ["eigenvalues", "diagonalization"],
  "out_of_scope_concepts": [],
  "course_scope_reason": "The problem tests eigenvalues and diagonalization, which are included in the target syllabus."
}
```

Out-of-scope example:

```json
{
  "in_course_scope": false,
  "matched_course_concepts": [],
  "out_of_scope_concepts": ["singular_value_decomposition"],
  "course_scope_reason": "The problem requires singular value decomposition, which is not included in the target final review syllabus."
}
```

---

### 14.2 In-Scope Criteria

A problem is in scope if:

```text
1. Its main tested concept appears in the target concept graph.
2. Its solution uses methods covered by the target course.
3. It is suitable for final review in the target course.
4. It does not require advanced tools absent from the syllabus.
```

---

### 14.3 Out-of-Scope Criteria

A problem is out of scope if:

```text
1. It requires SVD if SVD is not in target syllabus.
2. It requires differential equations if not covered.
3. It requires Markov chains if not covered.
4. It requires Fourier analysis or signal-processing interpretation.
5. It uses complex vector spaces if the target course is real-only.
6. It relies on abstract linear maps beyond course scope.
```

---

## 15. Benchmark Splitting

After scope filtering, split MIT problems into:

```text
mit_final_benchmark_in_scope.jsonl
mit_final_benchmark_out_of_scope.jsonl
mit_final_no_solution_set.jsonl
```

---

### 15.1 In-Scope Benchmark

Use for:

```text
system-level evaluation
automatic grading evaluation
difficulty matching evaluation
ablation testing
RAG explanation quality testing
```

Required fields:

```text
problem_id
problem_text
solution
final_answer
concept_tags
problem_type
difficulty_level
rubric
in_course_scope = true
use_type = external_benchmark
exclude_from_training = true
```

---

### 15.2 Out-of-Scope Benchmark

Use for:

```text
syllabus alignment evaluation
out-of-scope detection
over-generation control
LLM hallucination control
```

Required fields:

```text
problem_id
problem_text
concept_tags
out_of_scope_concepts
course_scope_reason
in_course_scope = false
use_type = out_of_scope_detection
exclude_from_training = true
```

---

### 15.3 No-Solution Set

Use for:

```text
scope filtering only
concept tagging only
manual extension
future benchmark construction
```

Do not use for:

```text
automatic grading accuracy evaluation
```

unless manually verified solutions are added.

---

## 16. Problem Type Labeling

Use a fixed set of problem types:

```text
multiple_choice
fill_blank
true_false
calculation
proof
conceptual_explanation
mixed
```

MIT finals are often:

```text
calculation
proof
mixed
conceptual_explanation
```

---

## 17. Difficulty and IRT Cold Start

Use the same 1–5 difficulty scale as the rest of the project.

```text
1 = very easy
2 = easy
3 = medium
4 = hard
5 = very hard
```

Mapping to 2PL IRT difficulty:

```text
difficulty_level = 1 -> b = -2.0
difficulty_level = 2 -> b = -1.0
difficulty_level = 3 -> b = 0.0
difficulty_level = 4 -> b = 1.0
difficulty_level = 5 -> b = 2.0
```

Default discrimination:

```text
a = 1.0
```

Adjustments:

```text
a = 1.1 or 1.2 for diagnostic multi-step problems
a = 0.8 or 0.9 for shallow, recognition-based, or guessing-prone problems
```

Record:

```json
{
  "irt": {
    "a": 1.1,
    "b": 1.0,
    "parameter_source": "cold_start_mapping_from_difficulty_level"
  }
}
```

---

## 18. Rubric Construction

Rubrics are needed for automatic grading evaluation.

---

### 18.1 Which MIT Problems Need Rubrics

Need rubrics:

```text
calculation
proof
conceptual_explanation
mixed
```

Optional:

```text
multiple_choice
fill_blank
true_false
```

---

### 18.2 Rubric Schema

```json
[
  {
    "step_id": 1,
    "description": "Correctly set up the characteristic polynomial.",
    "points": 2,
    "related_concepts": ["eigenvalues"]
  },
  {
    "step_id": 2,
    "description": "Solve the eigenvalues correctly.",
    "points": 2,
    "related_concepts": ["eigenvalues"]
  },
  {
    "step_id": 3,
    "description": "Find the corresponding eigenvectors.",
    "points": 3,
    "related_concepts": ["eigenvectors"]
  },
  {
    "step_id": 4,
    "description": "Conclude diagonalizability correctly.",
    "points": 3,
    "related_concepts": ["diagonalization"]
  }
]
```

---

### 18.3 Rubric Rules

```text
1. Use original point values if available.
2. Otherwise normalize to 10 points.
3. Each step must be checkable.
4. Each step should be linked to related concept tags.
5. Do not use benchmark solutions in model prompts during evaluation.
6. Rubric may be created from official solution before evaluation, but must be hidden from the system being tested.
7. All benchmark rubrics should be manually reviewed.
```

---

## 19. Duplicate and Leakage Check

MIT finals may overlap with:

```text
Hefferon final benchmark
Hefferon handin assignments
MIT OCW practice problems
course exercise bank
generated questions
```

Before using MIT finals as external benchmark, detect duplicates.

---

### 19.1 Leakage Rules

If a MIT problem appears in training bank:

```text
remove it from training bank
or mark exclude_from_training = true
```

If a generated question is based on a MIT benchmark problem:

```text
exclude it from evaluation
```

---

### 19.2 Duplicate Metadata

Recommended fields:

```json
{
  "dedup_group_id": "mit_fall2022_q003_cluster",
  "is_duplicate": false,
  "duplicate_of": null,
  "duplicate_similarity": 0.0,
  "exclude_from_training": true
}
```

All MIT benchmark problems should have:

```json
{
  "exclude_from_training": true
}
```

---

## 20. Quality Check

---

### 20.1 File-Level Quality Check

```text
[ ] All valid files are included in mit_finals_manifest.csv.
[ ] __MACOSX files are ignored.
[ ] .DS_Store files are ignored.
[ ] PDF files are correctly classified as exam/solution/combined.
[ ] PNG solution files are recorded as visual_solution_asset.
[ ] Semesters without official solutions are marked has_solution = false.
```

---

### 20.2 Problem-Level Quality Check

```text
[ ] Every problem has a unique problem_id.
[ ] Every problem has semester_id.
[ ] Every problem has year and term.
[ ] Every problem has problem_number.
[ ] Every problem has problem_text.
[ ] Every problem has source_type = final_exam.
[ ] Every problem has concept_tags.
[ ] Every problem has problem_type.
[ ] Every problem has difficulty_level.
[ ] Every problem has in_course_scope.
[ ] Every benchmark problem has exclude_from_training = true.
```

---

### 20.3 Solution Quality Check

```text
[ ] Every paired semester has problem-solution alignment.
[ ] Alignment confidence is recorded.
[ ] Low-confidence alignments are manually reviewed.
[ ] Image-only solutions are marked image_required = true.
[ ] No-solution exams are excluded from grading evaluation.
```

---

### 20.4 Benchmark Quality Check

```text
[ ] In-scope benchmark problems are manually reviewed.
[ ] Out-of-scope benchmark labels are manually reviewed.
[ ] Rubrics for benchmark problems are manually reviewed.
[ ] Duplicates with training banks are detected.
[ ] Benchmark solutions are hidden from system prompts during evaluation.
```

---

## 21. Manual Review Priority

Highest priority:

```text
1. final benchmark in-scope problems
2. final benchmark out-of-scope problems
3. solution alignment pairs
4. all benchmark rubrics
5. old exams with unclear formatting
6. semesters with combined exam-solution PDFs
7. PNG/image solution files
```

Recommended manual review ratio:

```text
in-scope benchmark: 100%
out-of-scope benchmark: 100%
solution alignment: 100% for low confidence, 20% for high confidence
rubrics: 100% for benchmark problems
no-solution set: optional
```

---

## 22. Metadata Summary

Generate:

```text
mit_final_metadata_summary.json
```

Example:

```json
{
  "source_name": "MIT 18.06 Linear Algebra Finals",
  "source_role": "external_examination_benchmark",
  "num_total_files": 69,
  "num_pdf_files": 66,
  "num_png_files": 3,
  "num_semester_folders": 37,
  "num_exam_pdfs": 0,
  "num_solution_pdfs": 0,
  "num_combined_exam_solution_pdfs": 0,
  "num_semesters_with_solution": 0,
  "num_semesters_without_solution": 0,
  "num_raw_problems": 0,
  "num_in_scope_benchmark_problems": 0,
  "num_out_of_scope_benchmark_problems": 0,
  "num_no_solution_problems": 0,
  "num_rubric_problems": 0,
  "manual_review_ratio": {
    "benchmark": 1.0,
    "rubrics": 1.0,
    "low_confidence_solution_alignment": 1.0
  },
  "notes": "Counts should be filled after full preprocessing."
}
```

---

## 23. Minimal Viable Processing Plan

If time is limited, do not process all years at once.

---

### 23.1 MVP Years

Prioritize recent paired years:

```text
fall2022
spring2022
spring2021
fall2019
spring2019
fall2018
spring2018 if available
fall2017
spring2017
spring2016
```

From the observed archive, good initial candidates include:

```text
fall2022/final.pdf + fall2022/finalsol.pdf
spring2022/final.pdf + spring2022/finalsol.pdf
spring2021/Final.pdf + spring2021/Final Solutions.pdf
fall2019/Final.pdf + fall2019/Final Solutions.pdf
spring2019/final.pdf + spring2019/finalsol.pdf
fall2018/final.pdf + fall2018/finalsol.pdf
fall2017/final.pdf + fall2017/final-sol.pdf
spring2017/final.pdf + spring2017/final-sol.pdf
spring2016/final.pdf + spring2016/final_solns.pdf
```

---

### 23.2 MVP Outputs

Generate first:

```text
mit_final_benchmark_in_scope_mvp.jsonl
mit_final_benchmark_out_of_scope_mvp.jsonl
mit_final_solution_pairs_mvp.jsonl
mit_finals_manifest_mvp.csv
```

---

### 23.3 MVP Required Fields

For each problem:

```text
problem_id
semester_id
year
term
file_path
problem_number
problem_text
solution
concept_tags
problem_type
difficulty_level
in_course_scope
use_type
exclude_from_training
```

Optional but recommended:

```text
rubric
irt
final_answer
prerequisite_tags
matched_course_concepts
out_of_scope_concepts
```

---

## 24. Recommended Processing Order

```text
1. 解压 mit linear algebra.zip
2. 删除或忽略 __MACOSX 和 .DS_Store
3. 生成 mit_finals_manifest.csv
4. 自动分类 exam_pdf / solution_pdf / combined_exam_solution_pdf
5. 先选择 8–10 个 recent paired semesters 做 MVP
6. 按页提取 exam 和 solution 文本
7. 解析 exam problems
8. 解析 solution problems
9. 对齐 problem-solution pairs
10. 做 concept tagging
11. 做 scope filtering
12. 分成 in-scope benchmark 和 out-of-scope benchmark
13. 为 in-scope benchmark 建立 rubric
14. 标 difficulty_level 与 IRT cold-start 参数
15. 检查与训练题库的重复，防止 leakage
16. 人工审核 benchmark 和 rubrics
17. 导出 metadata summary
```

---

## 25. How to Use MIT Finals in the System Evaluation

Recommended evaluation uses:

```text
1. Grading accuracy:
   Use in-scope MIT benchmark with official solutions and rubrics.

2. Concept attribution:
   Check whether the system maps each answer or error to the correct concept_tags.

3. Difficulty matching:
   Compare selected problem difficulty b with learner ability θ.

4. Scope control:
   Use out-of-scope MIT benchmark to test whether the system avoids unsupported content.

5. Ablation:
   Compare full system vs no-RAG, no-concept-graph, no-IRT, no-learner-model settings.
```

---

## 26. Suggested Paper Wording

You can describe this dataset as follows:

> The MIT 18.06 final examination archive was processed as an external examination benchmark rather than as part of the training corpus. Each semester folder was first classified according to whether it contained an exam file, a solution file, or a combined exam-solution file. Exam PDFs were parsed into structured problem records, and solution PDFs were aligned at the problem level using problem numbers and subproblem labels. Each problem was annotated with concept tags, problem type, difficulty level, cold-start IRT parameters, course-scope labels, and grading rubrics when official solutions were available. Problems aligned with the target syllabus were retained as an in-scope external benchmark, while problems requiring topics outside the target course were reserved as an out-of-scope detection set. All benchmark problems were excluded from the training bank to avoid evaluation leakage.

中文说明：

> 我们将 MIT 18.06 历年 final exam 材料处理为外部考试评测集，而不是训练语料。首先根据每个学期文件夹中是否包含试卷、答案或试卷答案合并文件进行分类。随后将试卷 PDF 解析为结构化题目记录，并根据题号和小问标签对答案 PDF 进行题目级对齐。每道题进一步标注知识点、题型、难度等级、冷启动 IRT 参数、考纲范围标签，并在存在官方答案时建立评分 rubric。与目标课程考纲一致的题目被保留为考纲内外部 benchmark，超出目标课程范围的题目则保留为超纲检测集。所有 benchmark 题目均不进入训练题库，以避免评估泄漏。

---

## 27. Final Checklist

```text
[ ] mit linear algebra.zip 已解压
[ ] __MACOSX 文件已忽略
[ ] .DS_Store 文件已忽略
[ ] mit_finals_manifest.csv 已生成
[ ] exam_pdf / solution_pdf / combined_exam_solution_pdf 已分类
[ ] 无答案年份已标记
[ ] recent paired semesters MVP 已选定
[ ] exam PDFs 已解析成 problem records
[ ] solution PDFs 已解析成 solution records
[ ] problem-solution alignment 已完成
[ ] low-confidence alignment 已进入人工审核
[ ] 每道题有 concept_tags
[ ] 每道题有 problem_type
[ ] 每道题有 difficulty_level
[ ] 每道题有 in_course_scope
[ ] in-scope benchmark 已生成
[ ] out-of-scope benchmark 已生成
[ ] no-solution set 已生成
[ ] benchmark rubrics 已建立
[ ] benchmark 题目 exclude_from_training = true
[ ] 与其他训练题库重复题已检查
[ ] metadata summary 已生成
```

---

## 28. Practical Recommendation

For the paper MVP, the most efficient route is:

```text
1. Use recent paired semesters first:
   fall2022, spring2022, spring2021, fall2019, spring2019, fall2018, fall2017, spring2017.

2. Parse these into problem-solution pairs.

3. Split them into:
   - in-scope benchmark
   - out-of-scope benchmark

4. Manually verify all benchmark labels and rubrics.

5. Keep older exams and no-solution exams as optional expansion.
```

This gives the paper a strong and credible external benchmark without requiring full manual processing of every historical exam.
