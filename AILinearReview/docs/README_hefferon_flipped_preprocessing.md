# Hefferon Flipped-Classroom Materials Preprocessing README

本 README 专门用于处理 `flipped.zip` 中的 Jim Hefferon flipped-classroom materials。  
这份材料与 lecture slides 不同，它更适合被处理成 **结构化习题库、课堂练习库、作业题库、midterm benchmark 和 final benchmark**，用于支持论文中的自适应出题、自动批改、错题归因、IRT 难度自适应和系统评估。

---

## 1. Source Description

原始压缩包：

```text
flipped.zip
```

解压后大致结构为：

```text
flipped/
├── handin/
│   ├── handin-1.pdf
│   ├── handin-2.pdf
│   ├── handin-2-ans.pdf
│   ├── ...
│   ├── handin-11.pdf
│   ├── midterm.pdf
│   └── final.pdf
│
└── inclass/
    ├── schedule.pdf
    ├── linear-systems/
    ├── vector-spaces/
    ├── map/
    ├── determinants/
    └── jc/
```

该材料包应定位为：

```text
open-source auxiliary exercise and assessment corpus
```

即“开源辅助习题与评测语料”。

---

## 2. Difference from Slides Preprocessing

`slides.zip` 主要用于：

```text
RAG 讲解
定义、定理、证明检索
知识点复习材料
```

而 `flipped.zip` 主要用于：

```text
题库构建
课堂练习解析
作业题解析
自动批改 rubric 构建
midterm / final benchmark 构建
系统评估
```

因此，`flipped.zip` 的核心预处理任务不是 lecture block chunking，而是：

```text
problem parsing
solution alignment
rubric construction
concept tagging
difficulty labeling
benchmark splitting
scope filtering
```

---

## 3. Target Output Datasets

最终建议生成以下数据文件：

```text
data_processed/hefferon_flipped/
├── hefferon_flipped_manifest.csv
├── hefferon_schedule_metadata.json
├── hefferon_inclass_exercise_bank.jsonl
├── hefferon_handin_exercise_bank.jsonl
├── hefferon_midterm_benchmark.jsonl
├── hefferon_final_benchmark.jsonl
├── hefferon_visual_assets_manifest.csv
└── hefferon_flipped_metadata_summary.json
```

---

## 4. Recommended Folder Structure

建议为 flipped materials 单独建立处理目录：

```text
hefferon_flipped_preprocessing/
│
├── README.md
│
├── data_raw/
│   └── flipped/
│       ├── handin/
│       └── inclass/
│
├── data_intermediate/
│   ├── raw_manifest.csv
│   ├── extracted_pages/
│   ├── cleaned_pages/
│   ├── parsed_problem_candidates/
│   ├── solution_alignment_candidates/
│   ├── rubric_candidates/
│   └── scope_filtering_candidates/
│
├── data_processed/
│   ├── hefferon_schedule_metadata.json
│   ├── hefferon_inclass_exercise_bank.jsonl
│   ├── hefferon_handin_exercise_bank.jsonl
│   ├── hefferon_midterm_benchmark.jsonl
│   ├── hefferon_final_benchmark.jsonl
│   ├── hefferon_visual_assets_manifest.csv
│   └── hefferon_flipped_metadata_summary.json
│
├── quality_check/
│   ├── missing_solution_report.csv
│   ├── low_confidence_tags.csv
│   ├── rubric_review_required.csv
│   ├── out_of_scope_problems.csv
│   ├── duplicate_problem_candidates.csv
│   └── manual_review_samples.csv
│
├── scripts/
│   ├── 01_unzip_and_manifest.py
│   ├── 02_extract_pdf_text.py
│   ├── 03_clean_problem_text.py
│   ├── 04_parse_inclass_worksheets.py
│   ├── 05_parse_handin_assignments.py
│   ├── 06_parse_midterm_final.py
│   ├── 07_align_solutions.py
│   ├── 08_tag_concepts.py
│   ├── 09_generate_rubrics.py
│   ├── 10_estimate_difficulty_irt.py
│   ├── 11_scope_filtering.py
│   ├── 12_quality_check.py
│   └── 13_export_datasets.py
│
└── prompts/
    ├── problem_parsing_prompt.md
    ├── solution_alignment_prompt.md
    ├── concept_tagging_prompt.md
    ├── rubric_generation_prompt.md
    ├── difficulty_estimation_prompt.md
    └── scope_filtering_prompt.md
```

---

## 5. Dataset Roles

---

### 5.1 Schedule Metadata

Source:

```text
flipped/inclass/schedule.pdf
```

Output:

```text
hefferon_schedule_metadata.json
```

Purpose:

```text
建立 Hefferon 章节与课程知识点图之间的映射
辅助判断每份 worksheet 的主题
辅助 problem concept tagging
辅助 course-scope filtering
```

Recommended schema:

```json
{
  "course_source": "Hefferon flipped classroom materials",
  "schedule_items": [
    {
      "week_or_order": 1,
      "section_ref": "One.I",
      "section_title": "Solving Linear Systems",
      "folder": "inclass/linear-systems",
      "concept_tags": ["linear_systems", "gaussian_elimination"],
      "expected_scope": "core"
    }
  ]
}
```

---

### 5.2 In-Class Exercise Bank

Source:

```text
flipped/inclass/
```

Output:

```text
hefferon_inclass_exercise_bank.jsonl
```

Purpose:

```text
课堂练习题库
例题库
系统训练题库
错题讲解样本
自适应出题候选池
```

Typical input files:

```text
inclass/linear-systems/*.pdf
inclass/vector-spaces/*.pdf
inclass/map/*.pdf
inclass/determinants/*.pdf
inclass/jc/*.pdf
```

Each problem should be parsed into one JSON record.

---

### 5.3 Handin Exercise Bank

Source:

```text
flipped/handin/handin-*.pdf
```

Output:

```text
hefferon_handin_exercise_bank.jsonl
```

Purpose:

```text
作业题库
训练题库
rubric 批改样本
IRT 冷启动题库
```

Important note:

```text
handin-2-ans.pdf should be aligned with handin-2.pdf.
```

If other handin files do not have official answers, their solution fields can be left empty or generated later with a verified flag set to false.

---

### 5.4 Midterm Benchmark

Source:

```text
flipped/handin/midterm.pdf
```

Output:

```text
hefferon_midterm_benchmark.jsonl
```

Purpose:

```text
内部 benchmark
模块级评估
自动批改一致性测试
错因归因测试
```

Recommended use:

```text
Do not use midterm problems for training if they are used for evaluation.
```

---

### 5.5 Final Benchmark

Source:

```text
flipped/handin/final.pdf
```

Output:

```text
hefferon_final_benchmark.jsonl
```

Purpose:

```text
final examination benchmark
系统级评估
消融实验测试集
出题对齐度评估
批改准确率评估
难度匹配评估
```

This is one of the most valuable files in `flipped.zip` for the paper evaluation section.

---

### 5.6 Visual Assets Manifest

Source:

```text
flipped/inclass/**/asy/*.pdf
```

Output:

```text
hefferon_visual_assets_manifest.csv
```

Purpose:

```text
图像素材记录
几何解释素材
未来多模态扩展
```

These files should not enter the first version of the text-only RAG or problem bank unless their text content is meaningful.

Recommended schema:

```csv
asset_id,file_path,related_unit,related_concepts,image_required,use_type
visual_001,inclass/vector-spaces/asy/vs000.pdf,vector-spaces,vector_space,true,future_multimodal_extension
```

---

## 6. Step-by-Step Workflow

---

# Step 1: Unzip and Build Manifest

Generate:

```text
data_processed/hefferon_flipped/hefferon_flipped_manifest.csv
```

Recommended fields:

```csv
file_path,top_folder,sub_folder,file_name,file_type,source_type,role,include_in_mvp
```

Example:

```csv
handin/final.pdf,handin,,final.pdf,pdf,final_exam,benchmark,true
handin/midterm.pdf,handin,,midterm.pdf,pdf,midterm_exam,benchmark,true
handin/handin-2.pdf,handin,,handin-2.pdf,pdf,handin_assignment,exercise_bank,true
handin/handin-2-ans.pdf,handin,,handin-2-ans.pdf,pdf,handin_solution,solution_key,true
inclass/schedule.pdf,inclass,,schedule.pdf,pdf,schedule,metadata,true
inclass/linear-systems/One-I-3.pdf,inclass,linear-systems,One-I-3.pdf,pdf,inclass_worksheet,exercise_bank,true
inclass/vector-spaces/asy/vs000.pdf,inclass,vector-spaces/asy,vs000.pdf,pdf,visual_asset,visual_manifest,false
```

---

## 6.1 Source Type Rules

Use these labels:

```text
schedule
inclass_worksheet
handin_assignment
handin_solution
midterm_exam
final_exam
visual_asset
unknown
```

---

# Step 2: Extract PDF Text

Extract each PDF page into a JSONL record.

Output folder:

```text
data_intermediate/extracted_pages/
```

Example page record:

```json
{
  "page_id": "hefferon_final_p001",
  "file_path": "handin/final.pdf",
  "source_type": "final_exam",
  "page": 1,
  "raw_text": "...",
  "text_length": 1432,
  "extraction_status": "success",
  "image_required": false
}
```

If a page contains mostly diagrams or little text:

```json
{
  "image_required": true,
  "extraction_status": "visual_or_low_text"
}
```

---

# Step 3: Clean Extracted Text

Clean the extracted text before problem parsing.

Recommended cleaning:

```text
1. Remove repeated headers and footers.
2. Remove page numbers if they appear as standalone lines.
3. Normalize whitespace.
4. Preserve problem numbers.
5. Preserve subproblem markers such as (a), (b), (c).
6. Preserve mathematical expressions.
7. Preserve matrices and vector notation as much as possible.
8. Merge lines broken by PDF extraction.
9. Do not delete solution labels.
10. Do not delete point values if they exist.
```

Do not remove:

```text
Problem numbers
Subproblem labels
Solution text
Answer labels
Point values
Matrix notation
Vector notation
Theorem references
```

---

# Step 4: Parse Schedule

Parse:

```text
inclass/schedule.pdf
```

into:

```text
hefferon_schedule_metadata.json
```

Recommended fields:

```json
{
  "section_ref": "One.I",
  "section_title": "Solving Linear Systems",
  "source_folder": "linear-systems",
  "related_files": ["One-I-3.pdf"],
  "concept_tags": ["linear_systems", "gaussian_elimination"],
  "expected_scope": "core"
}
```

This file is useful because many worksheet filenames correspond to Hefferon chapter-section references.

---

# Step 5: Parse In-Class Worksheets

Input:

```text
flipped/inclass/**/*.pdf
```

Exclude:

```text
flipped/inclass/**/asy/*.pdf
```

unless needed for future multimodal processing.

Output:

```text
hefferon_inclass_exercise_bank.jsonl
```

---

## 5.1 In-Class Problem Schema

Each problem should be one JSON record:

```json
{
  "problem_id": "hefferon_inclass_linear_systems_one_i_3_q001",
  "corpus_name": "hefferon_flipped",
  "source_role": "open_source_auxiliary",
  "source_type": "inclass_worksheet",
  "file_path": "inclass/linear-systems/One-I-3.pdf",
  "chapter_ref": "One.I.3",
  "page_start": 1,
  "page_end": 1,
  "problem_number": "1",
  "subproblem_label": null,
  "problem_text": "...",
  "solution": "",
  "final_answer": "",
  "concept_tags": ["linear_systems", "gaussian_elimination"],
  "prerequisite_tags": [],
  "problem_type": "calculation",
  "difficulty_level": 2,
  "estimated_time_minutes": 5,
  "rubric": [],
  "irt": {
    "a": 1.0,
    "b": -1.0,
    "parameter_source": "cold_start_mapping_from_difficulty_level"
  },
  "in_course_scope": true,
  "course_scope_reason": "The problem practices solving linear systems, which is included in the target syllabus.",
  "use_type": "training_bank",
  "has_official_solution": false,
  "verified": false
}
```

---

## 5.2 In-Class Parsing Rules

```text
1. Treat each numbered item as a separate problem.
2. If a problem has subparts (a), (b), (c), either:
   - keep them as one mixed problem, or
   - split them into separate records with a shared parent_problem_id.
3. Keep original problem numbering.
4. Preserve matrices and systems of equations.
5. If solution is absent, leave solution empty.
6. Do not invent official solutions.
7. If using LLM-generated solution later, mark solution_source = "generated_unverified".
```

Recommended subproblem format:

```json
{
  "problem_id": "hefferon_inclass_two_ii_q003_b",
  "parent_problem_id": "hefferon_inclass_two_ii_q003",
  "subproblem_label": "b"
}
```

---

# Step 6: Parse Handin Assignments

Input:

```text
flipped/handin/handin-*.pdf
```

Exclude from assignment bank:

```text
midterm.pdf
final.pdf
```

Output:

```text
hefferon_handin_exercise_bank.jsonl
```

---

## 6.1 Handin Problem Schema

```json
{
  "problem_id": "hefferon_handin_02_q001",
  "corpus_name": "hefferon_flipped",
  "source_role": "open_source_auxiliary",
  "source_type": "handin_assignment",
  "file_path": "handin/handin-2.pdf",
  "assignment_id": "handin-2",
  "page_start": 1,
  "page_end": 1,
  "problem_number": "1",
  "problem_text": "...",
  "solution": "...",
  "final_answer": "...",
  "solution_source": "official_solution",
  "concept_tags": ["linear_independence"],
  "prerequisite_tags": ["vector_space"],
  "problem_type": "proof",
  "difficulty_level": 3,
  "estimated_time_minutes": 10,
  "rubric": [],
  "irt": {
    "a": 1.0,
    "b": 0.0,
    "parameter_source": "cold_start_mapping_from_difficulty_level"
  },
  "in_course_scope": true,
  "use_type": "training_bank",
  "verified": false
}
```

---

## 6.2 Solution Alignment

Some files may have separate answer files, such as:

```text
handin-2.pdf
handin-2-ans.pdf
```

In this case, align problems by:

```text
assignment_id
problem_number
subproblem_label
similarity between problem references
```

If official solution is aligned:

```json
{
  "has_official_solution": true,
  "solution_source": "official_solution"
}
```

If not:

```json
{
  "has_official_solution": false,
  "solution_source": "missing"
}
```

---

# Step 7: Parse Midterm and Final

Input:

```text
flipped/handin/midterm.pdf
flipped/handin/final.pdf
```

Outputs:

```text
hefferon_midterm_benchmark.jsonl
hefferon_final_benchmark.jsonl
```

---

## 7.1 Benchmark Problem Schema

```json
{
  "problem_id": "hefferon_final_2021_spring_q001",
  "corpus_name": "hefferon_flipped",
  "source_role": "open_source_auxiliary",
  "source_type": "final_exam",
  "file_path": "handin/final.pdf",
  "exam_name": "Final",
  "exam_term": "2021-Spring",
  "page_start": 1,
  "page_end": 1,
  "problem_number": "1",
  "subproblem_label": null,
  "problem_text": "...",
  "solution": "...",
  "final_answer": "...",
  "solution_source": "official_solution_or_embedded_solution",
  "concept_tags": ["eigenvalues", "diagonalization"],
  "prerequisite_tags": ["determinant_properties"],
  "problem_type": "calculation",
  "difficulty_level": 4,
  "estimated_time_minutes": 12,
  "rubric": [],
  "irt": {
    "a": 1.1,
    "b": 1.0,
    "parameter_source": "cold_start_mapping_from_difficulty_level"
  },
  "in_course_scope": true,
  "use_type": "benchmark",
  "benchmark_split": "final",
  "verified": false
}
```

---

## 7.2 Benchmark Rules

```text
1. Do not mix final benchmark problems into the training bank.
2. Do not use benchmark solutions in prompts during system testing.
3. Keep official solutions for scoring and evaluation only.
4. Label all benchmark problems with benchmark_split.
5. Keep midterm and final as separate evaluation sets.
```

Recommended split:

```text
midterm -> development benchmark / module-level evaluation
final   -> final benchmark / system-level evaluation
```

---

# Step 8: Concept Tagging

Every problem must be mapped to the target course concept graph.

Required fields:

```json
{
  "concept_tags": [],
  "prerequisite_tags": []
}
```

---

## 8.1 Recommended Concept Tags

Use the same concept IDs as the main course concept graph.

Examples:

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
linear_transformation
kernel
range
matrix_representation
matrix_operations
inverse_matrix
change_of_basis
orthogonality
orthogonal_projection
least_squares
determinant_properties
determinant_geometry
laplace_expansion
eigenvalues
eigenvectors
similarity
diagonalization
complex_vector_space
```

---

## 8.2 Tagging Rules

```text
1. concept_tags should represent the main skill tested by the problem.
2. prerequisite_tags should represent supporting knowledge used in solving.
3. Do not assign too many tags.
4. Most problems should have 1–3 concept_tags.
5. If a problem has more than 4 concept_tags, consider splitting it into subproblems.
6. Use only concept IDs from the concept graph.
```

---

# Step 9: Problem Type Labeling

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

Typical mapping:

```text
Solving a system              -> calculation
Prove a subspace property     -> proof
Find eigenvalues              -> calculation
Explain why a statement holds -> conceptual_explanation
Problem with a, b, c parts    -> mixed
```

---

# Step 10: Difficulty and IRT Cold Start

Because there may be no real student response data, use cold-start difficulty estimation.

---

## 10.1 Difficulty Scale

```text
1 = very easy
2 = easy
3 = medium
4 = hard
5 = very hard
```

---

## 10.2 Suggested Difficulty Criteria

Consider:

```text
number of solution steps
number of concepts involved
calculation complexity
proof requirement
abstraction level
presence of traps
expected time
```

---

## 10.3 IRT Parameter Mapping

Use 2PL IRT:

```text
P(correct | θ) = 1 / (1 + exp(-a(θ - b)))
```

Initial difficulty mapping:

```text
difficulty_level = 1 -> b = -2.0
difficulty_level = 2 -> b = -1.0
difficulty_level = 3 -> b = 0.0
difficulty_level = 4 -> b = 1.0
difficulty_level = 5 -> b = 2.0
```

Initial discrimination:

```text
a = 1.0 by default
a = 1.1 or 1.2 for strong diagnostic problems
a = 0.8 or 0.9 for shallow or guessing-prone problems
```

Record parameter source:

```json
{
  "irt": {
    "a": 1.0,
    "b": 0.0,
    "parameter_source": "cold_start_mapping_from_difficulty_level"
  }
}
```

---

# Step 11: Rubric Construction

Rubrics are critical for automatic grading.

---

## 11.1 Which Problems Need Rubrics

Need rubric:

```text
calculation
proof
conceptual_explanation
mixed
```

Rubric optional:

```text
multiple_choice
fill_blank
true_false
```

---

## 11.2 Rubric Schema

```json
[
  {
    "step_id": 1,
    "description": "Correctly set up the augmented matrix.",
    "points": 2,
    "related_concepts": ["linear_systems", "row_reduction"]
  },
  {
    "step_id": 2,
    "description": "Perform valid elementary row operations.",
    "points": 3,
    "related_concepts": ["gaussian_elimination"]
  },
  {
    "step_id": 3,
    "description": "Identify the solution set correctly.",
    "points": 3,
    "related_concepts": ["solution_structure"]
  },
  {
    "step_id": 4,
    "description": "State the final answer in the required form.",
    "points": 2,
    "related_concepts": ["solution_structure"]
  }
]
```

---

## 11.3 Rubric Rules

```text
1. Total score should usually be 10 unless original problem has points.
2. Each step should correspond to a checkable action.
3. Each step should have points.
4. Each step should be linked to related_concepts if possible.
5. Do not combine too many actions into one step.
6. Do not create a rubric if the solution is missing and unverified.
7. If the rubric is LLM-generated, mark rubric_source = "generated_unverified".
8. If manually checked, set verified = true.
```

---

# Step 12: Scope Filtering

Every problem should be checked against the target course concept graph and syllabus.

Fields:

```json
{
  "in_course_scope": true,
  "course_scope_reason": ""
}
```

Out-of-scope example:

```json
{
  "in_course_scope": false,
  "course_scope_reason": "This problem requires complex vector spaces, which are not included in the target syllabus."
}
```

---

## 12.1 Scope Filtering Rules

In scope if:

```text
1. Main concept exists in the course concept graph.
2. Required methods are covered by the course lecture notes.
3. Problem can be solved using target course methods.
4. Problem difficulty is reasonable for final review.
```

Out of scope if:

```text
1. Main concept is not in the syllabus.
2. Requires advanced or abstract material not covered.
3. Requires external theorem not in course notes.
4. Problem belongs to a different course level.
```

---

# Step 13: Duplicate Detection

There may be overlap between:

```text
inclass worksheets
handin assignments
midterm
final
slides examples
MIT finals
```

Duplicate detection is useful to avoid training-test leakage.

---

## 13.1 Important Rule

If a problem appears in both training bank and benchmark:

```text
Remove it from training bank
or
mark it as duplicate_of benchmark and exclude from training
```

---

## 13.2 Duplicate Metadata

Recommended fields:

```json
{
  "dedup_group_id": "linear_system_row_reduction_001",
  "is_duplicate": false,
  "duplicate_of": null,
  "duplicate_similarity": 0.0,
  "exclude_from_training": false
}
```

If duplicate:

```json
{
  "is_duplicate": true,
  "duplicate_of": "hefferon_final_2021_spring_q003",
  "duplicate_similarity": 0.91,
  "exclude_from_training": true
}
```

---

# Step 14: Quality Check

Quality check is essential because problem parsing errors directly damage grading and benchmark validity.

---

## 14.1 Required Checks

### File-level checks

```text
[ ] All PDFs are included in hefferon_flipped_manifest.csv.
[ ] schedule.pdf is parsed separately.
[ ] midterm.pdf and final.pdf are not mixed into training bank.
[ ] asy visual PDFs are excluded from text-only problem parsing.
```

### Problem-level checks

```text
[ ] Every problem has a unique problem_id.
[ ] Every problem has source_type.
[ ] Every problem has file_path.
[ ] Every problem has problem_text.
[ ] Every problem has concept_tags.
[ ] Every problem has problem_type.
[ ] Every problem has difficulty_level.
[ ] Every problem has in_course_scope.
[ ] Every benchmark problem has benchmark_split.
```

### Solution checks

```text
[ ] Official solutions are aligned when available.
[ ] Missing solutions are clearly marked.
[ ] Generated solutions are not mistaken for official solutions.
[ ] Benchmark solutions are kept for scoring only.
```

### Rubric checks

```text
[ ] Calculation, proof, conceptual, and mixed problems have rubrics.
[ ] Rubric point totals are valid.
[ ] Rubric steps are checkable.
[ ] Rubric source is recorded.
[ ] Unverified rubrics are marked verified = false.
```

### Leakage checks

```text
[ ] Benchmark problems are excluded from training.
[ ] Duplicates between handin and final are detected.
[ ] Duplicates between inclass and final are detected.
[ ] duplicate_problem_candidates.csv is generated.
```

---

## 14.2 Manual Review Priority

Prioritize manual review for:

```text
1. final benchmark problems
2. midterm benchmark problems
3. problems with official solutions
4. proof problems
5. mixed problems
6. low-confidence concept tags
7. high difficulty problems
8. possible duplicates between training and benchmark
```

Recommended manual review ratio:

```text
final benchmark: 100%
midterm benchmark: 100%
handin assignments: at least 30%
inclass worksheets: at least 20%
rubrics: all benchmark rubrics
```

---

# Step 15: Metadata Summary

Generate:

```text
hefferon_flipped_metadata_summary.json
```

Example:

```json
{
  "source_name": "Jim Hefferon flipped-classroom materials",
  "source_role": "open_source_auxiliary_exercise_corpus",
  "num_pdf_files": 81,
  "num_inclass_files": 0,
  "num_handin_files": 0,
  "num_visual_asset_files": 0,
  "num_inclass_problems": 0,
  "num_handin_problems": 0,
  "num_midterm_problems": 0,
  "num_final_problems": 0,
  "num_problems_with_official_solution": 0,
  "num_rubric_problems": 0,
  "num_in_scope_problems": 0,
  "num_out_of_scope_problems": 0,
  "num_excluded_from_training": 0,
  "manual_review_ratio": {
    "final": 1.0,
    "midterm": 1.0,
    "handin": 0.3,
    "inclass": 0.2
  },
  "notes": "Counts should be filled after preprocessing."
}
```

---

## 16. Minimal Viable Processing Plan

If time is limited, do not process everything at once.

---

### 16.1 MVP Files

Prioritize:

```text
flipped/inclass/schedule.pdf
flipped/handin/final.pdf
flipped/handin/midterm.pdf
flipped/handin/handin-1.pdf
flipped/handin/handin-2.pdf
flipped/handin/handin-2-ans.pdf
flipped/inclass/linear-systems/
flipped/inclass/vector-spaces/
flipped/inclass/determinants/
```

Delay:

```text
flipped/inclass/**/asy/
flipped/inclass/jc/
low-relevance worksheets
files without parseable text
```

---

### 16.2 MVP Outputs

Generate first:

```text
hefferon_final_benchmark.jsonl
hefferon_midterm_benchmark.jsonl
hefferon_handin_exercise_bank_mvp.jsonl
hefferon_inclass_exercise_bank_mvp.jsonl
hefferon_schedule_metadata.json
```

---

### 16.3 MVP Required Fields

For every problem:

```text
problem_id
source_type
file_path
problem_number
problem_text
concept_tags
problem_type
difficulty_level
in_course_scope
use_type
```

For benchmark problems:

```text
solution
final_answer
benchmark_split
rubric
exclude_from_training = true
```

---

# Step 17: Suggested Processing Order

Recommended practical order:

```text
1. 解压 flipped.zip
2. 生成 manifest
3. 单独解析 schedule.pdf
4. 解析 final.pdf，生成 final benchmark
5. 解析 midterm.pdf，生成 midterm benchmark
6. 解析 handin assignments，生成 handin exercise bank
7. 对 handin-2 与 handin-2-ans 做答案配对
8. 解析 inclass worksheets，生成 inclass exercise bank
9. 排除 asy visual assets
10. 给所有题目打 concept_tags
11. 标 difficulty_level
12. 建立 rubric
13. 做 scope filtering
14. 做 duplicate detection，防止训练-测试泄漏
15. 人工审核 benchmark
16. 导出 metadata summary
```

---

# Step 18: How to Use These Datasets in the System

Recommended usage:

```text
inclass_exercise_bank:
    low-stakes practice, examples, adaptive training questions

handin_exercise_bank:
    structured training bank, rubric grading, IRT cold-start pool

midterm_benchmark:
    module-level evaluation and development benchmark

final_benchmark:
    final system-level evaluation and ablation testing

schedule_metadata:
    concept mapping and course alignment

visual_assets_manifest:
    future multimodal extension
```

---

## 18.1 Avoid Training-Test Leakage

The following must not be used as training questions if they are used for evaluation:

```text
hefferon_midterm_benchmark.jsonl
hefferon_final_benchmark.jsonl
```

If a similar problem exists in the training bank:

```text
mark exclude_from_training = true
```

---

# Step 19: How This Supports the Paper

This preprocessing supports the following paper modules:

| Output | Paper Module | Function |
|---|---|---|
| `hefferon_inclass_exercise_bank.jsonl` | M3 / M4 | 自适应练习、错题归因 |
| `hefferon_handin_exercise_bank.jsonl` | M3 / E2 | 训练题库、rubric 批改、IRT |
| `hefferon_midterm_benchmark.jsonl` | Section 12 | 模块级评估 |
| `hefferon_final_benchmark.jsonl` | Section 12 | 系统级评估与消融 |
| `hefferon_schedule_metadata.json` | M1 / M2 | 章节—知识点映射 |
| `hefferon_visual_assets_manifest.csv` | Future Work | 多模态扩展 |

---

# Step 20: Suggested Paper Wording

You can describe the flipped materials preprocessing in the paper as follows:

> The Hefferon flipped-classroom materials were processed as an auxiliary exercise and assessment corpus. Unlike the lecture slide corpus, which was used primarily for retrieval-based explanation, the flipped materials were parsed into structured problem records. In-class worksheets were used to construct a practice exercise bank, hand-in assignments were used as a structured training bank, and the midterm and final examinations were reserved as benchmark datasets. Each problem record contains source metadata, problem text, solution information when available, concept tags, problem type, difficulty level, cold-start IRT parameters, and grading rubrics for subjective problems. Visual-only assets were excluded from the text-only pipeline and retained in a separate manifest for future multimodal extensions.

中文说明：

> 我们将 Hefferon flipped-classroom materials 处理为辅助习题与评测语料。不同于主要用于检索讲解的 lecture slide corpus，flipped materials 被解析为结构化题目记录。课堂 worksheets 用于构建练习题库，hand-in assignments 用作结构化训练题库，midterm 与 final exams 被保留为 benchmark 数据集。每道题记录来源信息、题干、可用答案、知识点标签、题型、难度等级、冷启动 IRT 参数，以及主观题评分 rubric。纯图像类素材不进入第一版文本处理流程，而是作为未来多模态扩展保存在 visual asset manifest 中。

---

# Step 21: Final Checklist

```text
[ ] flipped.zip 已解压
[ ] hefferon_flipped_manifest.csv 已生成
[ ] schedule.pdf 已单独解析
[ ] inclass worksheets 已排除 asy visual assets
[ ] inclass exercise bank 已生成
[ ] handin assignments 已解析
[ ] handin-2 与 handin-2-ans 已对齐
[ ] midterm benchmark 已生成
[ ] final benchmark 已生成
[ ] benchmark 未混入 training bank
[ ] 每道题有 problem_id
[ ] 每道题有 source_type
[ ] 每道题有 problem_text
[ ] 每道题有 concept_tags
[ ] 每道题有 problem_type
[ ] 每道题有 difficulty_level
[ ] 主观题有 rubric
[ ] 每道题有 in_course_scope
[ ] 每道题有 use_type
[ ] 训练-测试重复题已检查
[ ] benchmark problems 已 100% 人工审核
[ ] metadata summary 已生成
```

---

## 22. Practical Recommendation

实际执行时建议先处理：

```text
1. final.pdf
2. midterm.pdf
3. handin-2.pdf + handin-2-ans.pdf
4. inclass/linear-systems/
5. inclass/vector-spaces/
6. inclass/determinants/
```

这样你可以最快得到论文最需要的部分：

```text
final benchmark
midterm benchmark
带答案的作业样本
基础章节练习题库
```

其余 worksheet 和 visual assets 可以作为后续扩展。
