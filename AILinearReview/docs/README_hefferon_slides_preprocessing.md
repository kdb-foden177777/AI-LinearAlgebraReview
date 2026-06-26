# Hefferon Linear Algebra Slides Preprocessing README

本 README 专门用于处理 `slides.zip` 中的 Jim Hefferon Linear Algebra slides。  
这些 slides 可作为论文系统中的 **open-source auxiliary lecture corpus**，即“开源辅助线性代数讲义语料”，用于支持 RAG 检索、知识点讲解、证明补充和快速复习。

本 README 的目标不是简单地把 slides 转成文本，而是将其处理成适合自适应复习系统使用的三层结构化语料库：

1. **Main Corpus**：普通 slides，用于常规讲解与 RAG 检索  
2. **Summary Corpus**：handout slides，用于快速复习与路径推荐  
3. **Proof Corpus**：allproofs slides，用于定理证明与深度解释  

---

## 1. Source Description

原始压缩包：

```text
slides.zip
```

该压缩包包含 Jim Hefferon 线性代数 slides，文件大致分为五个章节组：

```text
one/
two/
three/
four/
five/
```

每个 unit 通常有三种版本：

```text
unit.pdf
unit_handout.pdf
unit_allproofs.pdf
```

例如：

```text
one/one_i.pdf
one/one_i_handout.pdf
one/one_i_allproofs.pdf
```

三种版本的作用不同：

| Variant | Example | Role |
|---|---|---|
| main | `one_i.pdf` | 标准 lecture slides，作为主 RAG 语料 |
| handout | `one_i_handout.pdf` | 精简版 slides，作为 summary-level 语料 |
| allproofs | `one_i_allproofs.pdf` | 包含更多证明，作为 proof-oriented 语料 |

---

## 2. Why Special Processing Is Needed

这套 slides 不能直接全部混合进一个 RAG 数据库，原因有三点：

### 2.1 Three File Variants Cause Heavy Duplication

普通版、handout 版和 allproofs 版之间存在大量重复内容。  
如果直接混合，RAG 检索时会重复召回相同内容，降低答案质量。

### 2.2 Slides Are Page-Based, Not Textbook-Paragraph-Based

slides 的内容按页组织，常见情况包括：

```text
一页一个定义
连续几页一个例题
连续几页一个证明
一页只有图或几何解释
```

因此不适合简单按照固定 token 数切块。

### 2.3 The Slides Are Auxiliary Materials

这些 slides 不是目标课程的原始讲义，除非你的课程确实采用 Hefferon 作为教材。  
在论文中建议称为：

```text
open-source auxiliary linear algebra slide corpus
```

不要直接称为：

```text
course lecture notes
```

除非它确实是课程指定材料。

---

## 3. Target Output Datasets

最终建议生成以下三个 corpus 文件：

```text
data_processed/hefferon_slides/
├── hefferon_course_knowledge_corpus.jsonl
├── hefferon_summary_corpus.jsonl
├── hefferon_proof_corpus.jsonl
└── hefferon_metadata_summary.json
```

---

### 3.1 Main Corpus

文件：

```text
hefferon_course_knowledge_corpus.jsonl
```

来源：

```text
普通版 slides，例如 one_i.pdf, two_ii.pdf, five_ii.pdf
```

用途：

```text
RAG 常规讲解
知识点总结
例题检索
错题讲解
复习路径资料推荐
```

---

### 3.2 Summary Corpus

文件：

```text
hefferon_summary_corpus.jsonl
```

来源：

```text
*_handout.pdf
```

用途：

```text
快速复习
章节概要
考前 checklist
复习路径生成
低 token 成本检索
```

---

### 3.3 Proof Corpus

文件：

```text
hefferon_proof_corpus.jsonl
```

来源：

```text
*_allproofs.pdf
```

用途：

```text
定理证明
证明题讲解
学生追问“为什么”
深度概念解释
```

注意：  
`allproofs` 中与普通版重复的内容应删除或标记为 duplicate，只保留新增证明内容。

---

## 4. Recommended Folder Structure

建议为 slides 单独建立处理目录：

```text
hefferon_slides_preprocessing/
│
├── README.md
│
├── data_raw/
│   └── slides/
│       ├── one/
│       ├── two/
│       ├── three/
│       ├── four/
│       └── five/
│
├── data_intermediate/
│   ├── raw_manifest.csv
│   ├── page_text/
│   │   ├── one_i_main.jsonl
│   │   ├── one_i_handout.jsonl
│   │   ├── one_i_allproofs.jsonl
│   │   └── ...
│   │
│   ├── cleaned_pages/
│   │   ├── one_i_main_cleaned.jsonl
│   │   └── ...
│   │
│   ├── semantic_blocks/
│   │   ├── main_blocks_raw.jsonl
│   │   ├── handout_blocks_raw.jsonl
│   │   └── allproofs_blocks_raw.jsonl
│   │
│   └── duplicate_candidates.csv
│
├── data_processed/
│   ├── slide_unit_metadata.json
│   ├── hefferon_course_knowledge_corpus.jsonl
│   ├── hefferon_summary_corpus.jsonl
│   ├── hefferon_proof_corpus.jsonl
│   └── hefferon_metadata_summary.json
│
├── quality_check/
│   ├── low_confidence_tags.csv
│   ├── out_of_scope_blocks.csv
│   ├── duplicate_report.csv
│   ├── image_required_blocks.csv
│   └── manual_review_samples.csv
│
├── scripts/
│   ├── 01_unzip_and_manifest.py
│   ├── 02_extract_page_text.py
│   ├── 03_clean_slide_text.py
│   ├── 04_merge_semantic_blocks.py
│   ├── 05_assign_coarse_tags.py
│   ├── 06_refine_concept_tags.py
│   ├── 07_scope_filtering.py
│   ├── 08_deduplicate_variants.py
│   ├── 09_quality_check.py
│   └── 10_export_corpora.py
│
└── prompts/
    ├── block_type_classification_prompt.md
    ├── concept_tagging_prompt.md
    ├── scope_filtering_prompt.md
    └── deduplication_check_prompt.md
```

---

## 5. Step-by-Step Workflow

---

# Step 1: Unzip and Build File Manifest

首先解压 `slides.zip`，保留原始目录结构：

```text
data_raw/slides/
├── one/
├── two/
├── three/
├── four/
└── five/
```

然后生成文件清单：

```text
data_intermediate/raw_manifest.csv
```

每个 PDF 一行。

推荐字段：

```csv
file_path,chapter_group,unit,variant,role,pages,include_in_mvp
```

示例：

```csv
one/one_i.pdf,one,one_i,main,main_rag,54,true
one/one_i_handout.pdf,one,one_i,handout,summary,false
one/one_i_allproofs.pdf,one,one_i,allproofs,proof,false
five/five_ii.pdf,five,five_ii,main,main_rag,48,true
```

---

## 5.1 Variant Detection Rules

根据文件名自动识别版本：

```text
if filename contains "_handout":
    variant = "handout"
elif filename contains "_allproofs":
    variant = "allproofs"
else:
    variant = "main"
```

对应 role：

```text
main       -> main_rag
handout    -> summary
allproofs  -> proof
```

---

# Step 2: Build Slide Unit Metadata

为每个 unit 建立粗粒度主题标签。  
这个文件非常重要，因为后续 block 级 concept tagging 可以先继承 unit 级粗标签，再细化。

输出：

```text
data_processed/slide_unit_metadata.json
```

推荐内容：

```json
{
  "one_i": {
    "chapter_group": "one",
    "title": "Linear Systems",
    "coarse_concept_tags": [
      "linear_systems",
      "gaussian_elimination",
      "row_reduction"
    ],
    "expected_scope": "core"
  },
  "one_ii": {
    "chapter_group": "one",
    "title": "Geometry of Linear Systems",
    "coarse_concept_tags": [
      "geometry_of_linear_systems",
      "solution_sets"
    ],
    "expected_scope": "core"
  },
  "one_iii": {
    "chapter_group": "one",
    "title": "Reduced Echelon Form",
    "coarse_concept_tags": [
      "reduced_echelon_form",
      "gauss_jordan_elimination"
    ],
    "expected_scope": "core"
  },
  "two_i": {
    "chapter_group": "two",
    "title": "Vector Spaces",
    "coarse_concept_tags": [
      "vector_space",
      "subspace"
    ],
    "expected_scope": "core_or_optional"
  },
  "two_ii": {
    "chapter_group": "two",
    "title": "Linear Independence",
    "coarse_concept_tags": [
      "linear_independence",
      "linear_dependence"
    ],
    "expected_scope": "core"
  },
  "two_iii": {
    "chapter_group": "two",
    "title": "Basis and Dimension",
    "coarse_concept_tags": [
      "basis",
      "dimension"
    ],
    "expected_scope": "core"
  },
  "three_i": {
    "chapter_group": "three",
    "title": "Isomorphism",
    "coarse_concept_tags": [
      "isomorphism",
      "coordinate_representation"
    ],
    "expected_scope": "optional_or_out_of_scope"
  },
  "three_ii": {
    "chapter_group": "three",
    "title": "Homomorphism and Linear Maps",
    "coarse_concept_tags": [
      "homomorphism",
      "linear_transformation",
      "kernel",
      "range"
    ],
    "expected_scope": "optional_or_out_of_scope"
  },
  "three_iii": {
    "chapter_group": "three",
    "title": "Matrix Representation",
    "coarse_concept_tags": [
      "matrix_representation",
      "linear_map_matrix"
    ],
    "expected_scope": "core_or_optional"
  },
  "three_iv": {
    "chapter_group": "three",
    "title": "Matrix Operations",
    "coarse_concept_tags": [
      "matrix_operations",
      "matrix_multiplication",
      "inverse_matrix"
    ],
    "expected_scope": "core"
  },
  "three_v": {
    "chapter_group": "three",
    "title": "Change of Basis",
    "coarse_concept_tags": [
      "change_of_basis",
      "similarity"
    ],
    "expected_scope": "core_or_optional"
  },
  "three_vi": {
    "chapter_group": "three",
    "title": "Orthogonal Projection",
    "coarse_concept_tags": [
      "orthogonal_projection",
      "least_squares"
    ],
    "expected_scope": "core_or_optional"
  },
  "four_i": {
    "chapter_group": "four",
    "title": "Determinants",
    "coarse_concept_tags": [
      "determinant_definition",
      "determinant_properties"
    ],
    "expected_scope": "core"
  },
  "four_ii": {
    "chapter_group": "four",
    "title": "Geometry of Determinants",
    "coarse_concept_tags": [
      "determinant_geometry",
      "orientation",
      "volume_scaling"
    ],
    "expected_scope": "core_or_optional"
  },
  "four_iii": {
    "chapter_group": "four",
    "title": "Laplace Expansion",
    "coarse_concept_tags": [
      "laplace_expansion",
      "cofactor_expansion"
    ],
    "expected_scope": "core"
  },
  "five_i": {
    "chapter_group": "five",
    "title": "Complex Vector Spaces",
    "coarse_concept_tags": [
      "complex_vector_space"
    ],
    "expected_scope": "optional_or_out_of_scope"
  },
  "five_ii": {
    "chapter_group": "five",
    "title": "Similarity and Eigenvalues",
    "coarse_concept_tags": [
      "eigenvalues",
      "eigenvectors",
      "similarity",
      "diagonalization"
    ],
    "expected_scope": "core"
  },
  "five_ii_a": {
    "chapter_group": "five",
    "title": "Geometric Interpretation of Eigenvectors",
    "coarse_concept_tags": [
      "eigenvectors",
      "geometric_interpretation",
      "diagonalization"
    ],
    "expected_scope": "core_or_optional"
  }
}
```

---

# Step 3: Extract Text Page by Page

每个 PDF 先按页提取，而不是直接切成 chunk。

输出：

```text
data_intermediate/page_text/{unit}_{variant}.jsonl
```

每页一条记录。

示例：

```json
{
  "page_id": "hefferon_one_i_main_p012",
  "source_id": "hefferon_one_i_main",
  "source_title": "Jim Hefferon Linear Algebra Slides",
  "file_path": "one/one_i.pdf",
  "chapter_group": "one",
  "unit": "one_i",
  "variant": "main",
  "page": 12,
  "raw_text": "...",
  "text_length": 684,
  "extraction_status": "success",
  "image_required": false
}
```

---

## 5.3 Extraction Notes

如果某页几乎没有文字，只有图形或动画解释，应标记：

```json
{
  "image_required": true,
  "extraction_status": "visual_or_low_text"
}
```

后续纯文本 RAG 可以暂时排除这些页，但它们可作为未来多模态扩展材料。

---

# Step 4: Clean Slide Text

slides 中常见噪声包括：

```text
页码
重复页眉
重复页脚
课程名
版权声明
单独出现的章节标题
空白符
断行
```

清洗后输出：

```text
data_intermediate/cleaned_pages/{unit}_{variant}_cleaned.jsonl
```

保留原始页码和 source metadata。

---

## 5.4 Cleaning Rules

建议清洗：

```text
1. 删除重复页眉和页脚
2. 删除只有页码的行
3. 合并被换行切断的普通句子
4. 保留数学表达式
5. 保留矩阵、向量、行列式相关符号
6. 删除明显重复的 slide title
7. 标记空白页
```

不要删除：

```text
definition
theorem
proof
example
equation
matrix
problem statement
solution step
geometric interpretation
```

---

# Step 5: Merge Pages into Semantic Blocks

slides 的基本单位是页，但最终 RAG 的基本单位应该是 semantic block。

输出：

```text
data_intermediate/semantic_blocks/main_blocks_raw.jsonl
data_intermediate/semantic_blocks/handout_blocks_raw.jsonl
data_intermediate/semantic_blocks/allproofs_blocks_raw.jsonl
```

---

## 5.5 Recommended Block Types

```text
definition
theorem
proof
example
solution
remark
summary
formula
exercise_prompt
visual_explanation
transition
metadata
```

---

## 5.6 Merging Rules

### Main slides

普通版 slides 建议按以下规则合并：

```text
1. 一页一个完整定义：单独成 block
2. 定理页 + 后续解释页：合并为 theorem block
3. 例题题干 + 解答步骤：合并为 example 或 solution block
4. 证明如果较短：合并成 proof block
5. 一个主题超过 5 页：按小标题再次切分
6. 纯目录页、过渡页：标记为 metadata 或 transition
```

---

### Handout slides

handout 版可以切得更粗：

```text
1. 按小节或主题切分
2. 每个 block 可以覆盖 2–5 页
3. block_type 多为 summary / formula / example
```

---

### Allproofs slides

allproofs 版应主要保留 proof：

```text
1. 只保留 proof、theorem、proof-related remark
2. 与 main slides 重复的定义和例题可删除
3. 一个证明对应一个 proof block
4. 如果证明很长，可以按 proof step 切分
```

---

# Step 6: Assign Coarse Concept Tags

每个 block 先继承 unit 级粗标签。

示例：

```json
{
  "block_id": "hefferon_five_ii_main_b003",
  "unit": "five_ii",
  "coarse_concept_tags": [
    "eigenvalues",
    "eigenvectors",
    "similarity",
    "diagonalization"
  ]
}
```

这一阶段不要求精确，只是提供初始标签候选。

---

# Step 7: Refine Concept Tags

在 coarse tags 的基础上，为每个 block 生成精确知识点标签。

输入：

```text
1. semantic block
2. slide_unit_metadata.json
3. target course concept_graph.json
```

输出：

```json
{
  "concept_tags": ["eigenvalues", "eigenvectors"],
  "prerequisite_tags": ["determinant_properties", "characteristic_polynomial"],
  "concept_tag_confidence": {
    "eigenvalues": 0.96,
    "eigenvectors": 0.91
  }
}
```

---

## 7.1 Tagging Principles

```text
1. concept_tags 只标当前 block 主要讲的知识点
2. prerequisite_tags 标使用但不是重点讲解的前置知识
3. 不要把 unit 里的所有 coarse tags 全部无脑复制到每个 block
4. 每个 block 最好 1–3 个 concept_tags
5. 超过 4 个 concept_tags 的 block 应考虑重新切分
```

---

# Step 8: Course Scope Filtering

因为 Hefferon slides 是开源辅助材料，不一定与目标课程完全一致，所以每个 block 都需要判断是否在课程范围内。

输出字段：

```json
{
  "in_course_scope": true,
  "course_scope_reason": "This block explains eigenvalues, which are included in the target syllabus."
}
```

如果超纲：

```json
{
  "in_course_scope": false,
  "course_scope_reason": "This block focuses on complex vector spaces, which are not included in the target final review syllabus."
}
```

---

## 8.1 High-Risk Units for Scope Filtering

以下 unit 需要特别检查：

```text
three_i      isomorphism
three_ii     homomorphism and abstract linear maps
three_v      change of basis
three_vi     orthogonal projection / least squares
five_i       complex vector spaces
five_ii_a    geometric interpretation of eigenvectors
```

其中：

```text
three_i, three_ii, five_i
```

最可能超出普通工科线性代数期末复习范围。

---

# Step 9: Deduplicate Across Variants

这是处理这套 slides 最关键的一步。

---

## 9.1 Deduplication Priority

保留优先级：

```text
main > handout > allproofs
```

但三类文件不完全一样，不能简单删掉 handout 或 allproofs。

---

## 9.2 Deduplication Rules

### For main corpus

```text
普通版 main 是默认主语料。
保留所有通过质量检查的 main blocks。
```

---

### For handout corpus

```text
即使 handout 内容与 main 重复，也可以保留。
但它进入 summary_corpus，不进入 main_corpus。
```

原因：

```text
handout 的作用是快速复习，而不是详细讲解。
```

---

### For allproofs corpus

```text
allproofs 中与 main 高度重复的 block 应删除或标记为 duplicate。
只保留 main 中没有的证明、证明细节、证明补充说明。
```

---

## 9.3 Duplicate Metadata

每个 block 建议包含：

```json
{
  "dedup_group_id": "eigenvalue_definition_001",
  "is_duplicate": false,
  "duplicate_of": null,
  "duplicate_similarity": 0.0
}
```

如果是重复块：

```json
{
  "dedup_group_id": "eigenvalue_definition_001",
  "is_duplicate": true,
  "duplicate_of": "hefferon_five_ii_main_b004",
  "duplicate_similarity": 0.93
}
```

---

## 9.4 Similarity Thresholds

建议阈值：

```text
similarity >= 0.90:
    duplicate
0.75 <= similarity < 0.90:
    candidate_for_manual_review
similarity < 0.75:
    keep
```

注意：  
数学文本短块容易误判，应人工检查高相似度的定理和公式。

---

# Step 10: Export Final JSONL Corpora

---

## 10.1 Main Corpus Schema

文件：

```text
data_processed/hefferon_slides/hefferon_course_knowledge_corpus.jsonl
```

示例：

```json
{
  "block_id": "hefferon_three_vi_main_b008",
  "corpus_name": "hefferon_slides",
  "source_role": "open_source_auxiliary",
  "source_title": "Jim Hefferon Linear Algebra Slides",
  "file_path": "three/three_vi.pdf",
  "chapter_group": "three",
  "unit": "three_vi",
  "variant": "main",
  "retrieval_layer": "main",
  "page_start": 8,
  "page_end": 10,
  "block_type": "example",
  "title": "Projection onto a subspace",
  "text": "...",
  "latex": "...",
  "concept_tags": ["orthogonal_projection"],
  "prerequisite_tags": ["inner_product", "orthogonality"],
  "coarse_concept_tags": ["orthogonal_projection", "least_squares"],
  "in_course_scope": true,
  "course_scope_reason": "Orthogonal projection is included in the target linear algebra syllabus.",
  "importance": 0.75,
  "dedup_group_id": "projection_example_001",
  "is_duplicate": false,
  "duplicate_of": null,
  "image_required": false,
  "verified": false
}
```

---

## 10.2 Summary Corpus Schema

文件：

```text
data_processed/hefferon_slides/hefferon_summary_corpus.jsonl
```

示例：

```json
{
  "block_id": "hefferon_two_iii_handout_b002",
  "corpus_name": "hefferon_slides",
  "source_role": "open_source_auxiliary",
  "source_title": "Jim Hefferon Linear Algebra Slides",
  "file_path": "two/two_iii_handout.pdf",
  "unit": "two_iii",
  "variant": "handout",
  "retrieval_layer": "summary",
  "page_start": 3,
  "page_end": 5,
  "block_type": "summary",
  "title": "Basis and Dimension Summary",
  "text": "...",
  "concept_tags": ["basis", "dimension"],
  "in_course_scope": true,
  "is_duplicate": false,
  "image_required": false,
  "verified": false
}
```

---

## 10.3 Proof Corpus Schema

文件：

```text
data_processed/hefferon_slides/hefferon_proof_corpus.jsonl
```

示例：

```json
{
  "block_id": "hefferon_five_ii_allproofs_b011",
  "corpus_name": "hefferon_slides",
  "source_role": "open_source_auxiliary",
  "source_title": "Jim Hefferon Linear Algebra Slides",
  "file_path": "five/five_ii_allproofs.pdf",
  "unit": "five_ii",
  "variant": "allproofs",
  "retrieval_layer": "proof",
  "page_start": 32,
  "page_end": 35,
  "block_type": "proof",
  "title": "Proof of Diagonalization Criterion",
  "text": "...",
  "concept_tags": ["diagonalization"],
  "prerequisite_tags": ["eigenvectors", "linear_independence"],
  "in_course_scope": true,
  "dedup_group_id": "diagonalization_criterion_proof_001",
  "is_duplicate": false,
  "duplicate_of": null,
  "image_required": false,
  "verified": false
}
```

---

# Step 11: Quality Check

生成最终 corpus 前，必须做质量检查。

---

## 11.1 Required Checks

### File-level checks

```text
[ ] 所有 PDF 已进入 raw_manifest.csv
[ ] 每个 PDF 正确识别 variant
[ ] 每个 PDF 有 unit
[ ] 每个 unit 有 coarse_concept_tags
```

### Page-level checks

```text
[ ] 每页有 page_id
[ ] 每页保留 file_path
[ ] 每页保留 page number
[ ] 空白页已标记
[ ] 纯图页已标记 image_required
```

### Block-level checks

```text
[ ] 每个 block 有 block_id
[ ] 每个 block 有 block_type
[ ] 每个 block 有 page_start/page_end
[ ] 每个 block 有 concept_tags
[ ] 每个 block 有 in_course_scope
[ ] 每个 block 有 retrieval_layer
[ ] 每个 block 有 source_role
```

### Deduplication checks

```text
[ ] handout 不进入 main corpus
[ ] allproofs 与 main 重复内容已标记或删除
[ ] duplicate_report.csv 已生成
[ ] 高相似度但不同用途的 block 已人工检查
```

---

## 11.2 Manual Review Priority

优先人工检查：

```text
1. high-weight concept blocks
2. low-confidence concept tags
3. out-of-scope blocks
4. allproofs retained blocks
5. image_required blocks
6. duplicate similarity between 0.75 and 0.90
```

高权重知识点包括：

```text
linear_systems
matrix_rank
linear_independence
basis
dimension
inverse_matrix
determinant_properties
eigenvalues
eigenvectors
diagonalization
orthogonal_projection
least_squares
quadratic_form
positive_definite_matrix
```

---

# Step 12: Metadata Summary

最终生成：

```text
data_processed/hefferon_slides/hefferon_metadata_summary.json
```

示例：

```json
{
  "source_name": "Jim Hefferon Linear Algebra Slides",
  "source_role": "open_source_auxiliary",
  "num_pdf_files": 54,
  "num_units": 18,
  "num_main_pdfs": 18,
  "num_handout_pdfs": 18,
  "num_allproofs_pdfs": 18,
  "num_main_blocks": 0,
  "num_summary_blocks": 0,
  "num_proof_blocks": 0,
  "num_in_scope_blocks": 0,
  "num_out_of_scope_blocks": 0,
  "num_image_required_blocks": 0,
  "num_duplicate_blocks": 0,
  "manual_review_ratio": 0.1,
  "notes": "Counts should be filled after preprocessing."
}
```

---

## 13. Minimal Viable Processing Plan

如果时间有限，不建议一开始处理全部 54 个 PDF。  
可以先做 MVP。

---

### 13.1 MVP Input Files

先只处理普通版 slides 中最核心的 8 个文件：

```text
one/one_i.pdf
one/one_iii.pdf
two/two_ii.pdf
two/two_iii.pdf
three/three_iv.pdf
three/three_vi.pdf
four/four_i.pdf
five/five_ii.pdf
```

覆盖核心知识点：

```text
线性方程组
行最简形
线性无关
基与维数
矩阵运算
投影与最小二乘
行列式
特征值与对角化
```

---

### 13.2 MVP Output

先生成：

```text
hefferon_course_knowledge_corpus_mvp.jsonl
```

每个 block 至少包含：

```text
block_id
source_title
file_path
unit
variant
retrieval_layer
page_start
page_end
block_type
text
concept_tags
in_course_scope
source_role
```

---

### 13.3 What Can Be Delayed

MVP 阶段可以暂缓：

```text
handout corpus
proof corpus
复杂去重
精细 prerequisite_tags
image_required 多模态处理
完整人工审核
```

但必须保留：

```text
source metadata
concept_tags
in_course_scope
```

否则后续很难补。

---

## 14. How to Use the Three Corpora in the System

推荐检索逻辑：

```text
普通讲解问题:
    search main corpus

快速复习问题:
    search summary corpus first, then main corpus

证明类问题:
    search proof corpus first, then main corpus

错题讲解:
    search main corpus by concept_tags

复习路径推荐:
    use summary corpus for overview, main corpus for detailed references

超纲问题:
    check in_course_scope before retrieval or generation
```

示例：

```text
Student: “Can you quickly summarize diagonalization?”
System:
    1. Search summary corpus for diagonalization
    2. Return concise explanation
    3. Attach main corpus references if needed
```

```text
Student: “Why does diagonalization require enough independent eigenvectors?”
System:
    1. Search proof corpus for diagonalization
    2. Search main corpus for supporting definitions
    3. Generate proof-oriented explanation
```

---

## 15. How This Supports the Paper

在论文中，这部分预处理可以支持以下内容：

| Output | Paper Module | Purpose |
|---|---|---|
| `hefferon_course_knowledge_corpus.jsonl` | M2 RAG | 常规课程讲解与引用检索 |
| `hefferon_summary_corpus.jsonl` | M4 Review Path | 快速复习材料推荐 |
| `hefferon_proof_corpus.jsonl` | E1 Agent | 支持追问与证明解释 |
| `slide_unit_metadata.json` | M1 / M2 | 粗粒度知识点映射 |
| `in_course_scope` labels | M1 / Evaluation | 考纲对齐与超纲过滤 |
| `duplicate_report.csv` | Data Quality | 语料去重与质量控制 |

---

## 16. Suggested Paper Wording

可以在论文中这样描述这套 slides 的处理：

> The open-source Hefferon linear algebra slide corpus was processed as an auxiliary instructional corpus rather than as the primary course material. The slides were organized into three retrieval layers according to their file variants: standard lecture slides, handout slides, and proof-enriched slides. Standard slides were used as the main retrieval corpus, handout slides were used as a summary-level review corpus, and proof-enriched slides were used as a proof-oriented auxiliary corpus. Each PDF was first parsed at the page level, cleaned to remove repeated headers and footers, and then merged into semantic learning blocks such as definitions, theorems, examples, proofs, and remarks. Each block was aligned with the course concept graph and assigned metadata including source file, page range, slide variant, retrieval layer, concept tags, prerequisite tags, scope labels, and duplicate identifiers.

中文说明：

> 我们将 Hefferon 开源线性代数 slides 作为辅助教学语料，而非目标课程的唯一课程材料。根据文件版本，slides 被组织为三层检索语料：普通 lecture slides 用作主检索语料，handout slides 用作摘要级复习语料，allproofs slides 用作证明导向的补充语料。每个 PDF 首先按页解析，并清除重复页眉页脚，然后合并为定义、定理、例题、证明、备注等语义学习块。每个学习块进一步映射到课程知识点图，并记录来源文件、页码范围、版本类型、检索层级、知识点标签、前置知识标签、考纲范围标签和去重标识。

---

## 17. Final Checklist

```text
[ ] slides.zip 已解压
[ ] raw_manifest.csv 已生成
[ ] 每个 PDF 正确识别 variant
[ ] slide_unit_metadata.json 已完成
[ ] 每页文本已提取
[ ] 重复页眉页脚已清理
[ ] 纯图页已标记 image_required
[ ] 普通版 slides 已合并为 semantic blocks
[ ] handout 版 slides 已进入 summary corpus
[ ] allproofs 版 slides 已去重并进入 proof corpus
[ ] 每个 block 有 concept_tags
[ ] 每个 block 有 in_course_scope
[ ] 每个 block 有 retrieval_layer
[ ] 每个 block 有 source_role = open_source_auxiliary
[ ] duplicate_report.csv 已生成
[ ] low_confidence_tags.csv 已生成
[ ] out_of_scope_blocks.csv 已生成
[ ] manual_review_samples.csv 已生成
[ ] hefferon_metadata_summary.json 已生成
```

---

## 18. Practical Recommendation

实际执行时，建议分两阶段：

### Phase 1: MVP

只处理 18 个普通版 slides，或者先处理 8 个核心普通版 slides。  
目标是尽快得到：

```text
hefferon_course_knowledge_corpus_mvp.jsonl
```

用于跑通 RAG 和知识点检索流程。

### Phase 2: Full Corpus

加入：

```text
handout slides -> summary corpus
allproofs slides -> proof corpus
```

并完成：

```text
跨版本去重
scope filtering
manual quality check
metadata summary
```

不要一开始就把 54 个 PDF 全部混入系统，否则重复内容会严重影响检索质量。
