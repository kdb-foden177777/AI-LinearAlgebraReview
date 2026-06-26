# 论文写作逻辑与实验数据说明

本文档用于解释当前论文 `paper_work/mdpi_manuscript/main.tex` 的写作逻辑，以及论文中各项实验数据是如何获得的。它不是论文正文，而是供我们理解、检查和后续修改论文时使用的“内部说明书”。

## 1. 论文整体写作逻辑

### 1.1 论文核心问题

这篇论文解决的问题不是“做一个普通聊天机器人帮助学生学线性代数”，而是：

> 如何把线性代数期末复习材料、知识概念图谱、检索增强生成、自动批改、对话 Agent 和 IRT 难度自适应组合成一个可追踪、可解释、可评估的闭环复习系统。

因此文章的重点是一个系统架构和自动实验验证，而不是一个已经完成真实课堂随机对照试验的教育干预研究。

### 1.2 文章主线

论文按照以下逻辑展开：

1. 线性代数期末复习有特殊困难：概念多、依赖关系强、题目往往跨多个知识点。
2. 静态讲义和题库不能自动回答三个关键问题：学生错在哪里、下一步该复习什么、下一题难度该如何选择。
3. LLM 可以解释和生成内容，但如果没有课程材料和知识图谱约束，容易出现幻觉、偏离大纲、只给流畅但不可靠的反馈。
4. 因此系统需要一个闭环：材料转 Markdown 语料库，构建概念图谱，检索相关证据，生成或选择题目，批改答案，归因错误，更新学生状态，再推荐下一步。
5. 论文通过多个模块实验检查这个闭环的关键部件是否可运行、是否有数据支撑、哪里还不可靠。

### 1.3 当前论文结构

当前 `main.tex` 已经被整理成类似 MDPI `Applied Sciences` 论文的框架：

- `Introduction`：说明问题、动机、贡献和研究边界。
- `Related Work`：综述智能教学系统、知识图谱、RAG、IRT、LLM 教育反馈。
- `Materials and Methods`：描述系统方法，包括问题定义、系统架构、UI、语料库、概念图谱、RAG、出题批改、错误归因、对话 Agent、IRT、实验设计。
- `Results`：报告实验结果，包括概念标注、检索、RAG 支持度、Agent 交互、IRT 仿真、消融实验。
- `Discussion`：解释结果含义、与相关研究比较、局限和启示。
- `Conclusion`：总结系统贡献和未来工作。

### 1.4 UI 在论文中的角色

UI 交互界面不是独立的人类用户实验数据来源。它的角色是系统的前端落地形态，也就是把后端模块变成学生可以实际操作的复习界面。

UI 承载以下功能：

- 展示学生复习状态、弱概念和推荐路径。
- 显示当前题目、难度、概念标签和证据片段。
- 支持学生提交答案、请求提示、进入对话。
- 把学生输入发送给本地 Agent 服务。
- 展示 Agent 返回的批改、提示、概念归因和下一步建议。

因此 UI 与实验的关系是：Table 8 的 Agent interaction evaluation 最接近 UI，因为它测试的是 UI 中会发生的 grading、hint 和 dialogue 三类交互。但当前论文没有声称 UI 已经经过真实学生可用性测试或学习效果测试。

## 2. 材料来源与数据基础

### 2.1 原始材料

论文使用的材料来自三个 Markdown 文件夹：

| 文件夹 | 文件数 | 行数 | 字符数 | 近似 token 数 | 主要作用 |
|---|---:|---:|---:|---:|---|
| `slides_md` | 54 | 22,873 | 1,309,998 | 327,500 | 课程范围、定义、定理、讲义内容 |
| `flipped_md` | 81 | 4,679 | 192,308 | 48,077 | 翻转课堂活动、练习、少量考试和答案 |
| `mit_linear_algebra_md` | 65 | 10,280 | 676,584 | 169,146 | MIT 18.06 final exam 与 solution 参考 |
| 总计 | 200 | 37,832 | 2,178,890 | 544,723 | 完整实验语料库 |

这些数据来自之前用 marker-master 将 PDF 转换成 Markdown 的结果。论文中的语料规模表来自：

- `paper_work/full_experiment_outputs/corpus_audit.json`
- `paper_work/full_experiment_outputs/corpus_audit.md`

### 2.2 Benchmark item 来源

系统从 200 个 Markdown 文件中抽取了 106 个 benchmark items。它们来自 exam、activity、lecture、handout 等不同材料角色。

按材料角色：

| 来源角色 | item 数 |
|---|---:|
| activity | 20 |
| exam | 68 |
| lecture | 11 |
| handout | 7 |

按文件夹：

| 文件夹 | item 数 |
|---|---:|
| `flipped_md` | 21 |
| `mit_linear_algebra_md` | 67 |
| `slides_md` | 18 |

这些数据来自：

- `paper_work/full_experiment_outputs/benchmark_items.jsonl`
- `paper_work/full_experiment_outputs/benchmark_summary.json`

## 3. 论文中各实验的来源与含义

### 3.1 Corpus and Benchmark Scale

论文中的 corpus scale 和 benchmark scale 表不是模型生成的，而是脚本对本地 Markdown 文件直接统计得到的。

统计内容包括：

- 文件数；
- 行数；
- 字符数；
- 近似 token 数；
- source role；
- benchmark item 数量；
- item 对应的概念标签。

这些结果用于证明：论文不是凭空讨论一个系统，而是基于一个真实转换出来的线性代数材料库。

对应文件：

- `paper_work/full_experiment_outputs/corpus_audit.json`
- `paper_work/full_experiment_outputs/benchmark_summary.json`

### 3.2 Concept Tagging Experiment

这部分对应论文中的 Table 6 和 Table 7。

实验目的：

> 检查 LLM 能否把线性代数题目自动映射到概念图谱中的知识点。

实验方法：

1. 从 benchmark items 中选取 80 个目标 item。
2. 每个 item 本身有一组 keyword-derived silver labels，也就是用关键词和概念别名规则自动生成的“银标签”。
3. 调用 LLM，让它基于给定概念词表为 item 打标签。
4. 将 LLM 标签与银标签比较。
5. 计算 micro precision、micro recall、micro F1、macro F1、Jaccard、平均标签数量等指标。

最终结果：

| 指标 | 值 |
|---|---:|
| completed items | 80 |
| API error items | 0 |
| micro precision | 0.377 |
| micro recall | 0.377 |
| micro F1 | 0.377 |
| macro precision | 0.551 |
| macro recall | 0.523 |
| macro F1 | 0.348 |
| mean Jaccard | 0.324 |
| mean silver labels/item | 5.088 |
| mean predicted labels/item | 14.287 |
| mean extra labels/item | 9.588 |
| over-label rate | 0.912 |

重要解释：

这个实验的结果并不高，原因是 LLM 明显倾向于过度标注。也就是说，它经常把一个题目关联到很多可能相关的概念，而 keyword-derived silver labels 比较保守。这就是为什么论文中不能说“LLM 概念标注非常准确”，而应该说：

> 原始 LLM 概念标注可以作为候选信号，但不能直接作为最终诊断；需要概念图谱、检索证据和 syllabus filter 进一步约束。

对应文件：

- `paper_work/full_experiment_outputs/concept_tagging_predictions_expanded.csv`
- `paper_work/full_experiment_outputs/concept_tagging_metrics_expanded.json`
- `paper_work/full_experiment_outputs/concept_tagging_diagnostics_expanded.json`
- `paper_work/full_experiment_outputs/concept_tagging_per_concept_expanded.csv`

### 3.3 Retrieval Benchmark

这部分对应论文中的 retrieval benchmark table。

实验目的：

> 检查概念过滤后的检索是否比普通词法检索、只检索讲义、只检索考试材料更适合复习场景。

实验方法：

1. 构造 160 个 review queries。
2. Query 类型包括：
   - direct concept question；
   - exam fragment；
   - misconception prompt；
   - multi-concept review；
   - vague student question；
   - worked example request。
3. 对每个 query，在四种检索条件下检索：
   - lexical：全库 TF-IDF 检索；
   - lecture-only：只检索讲义材料；
   - exam-only：只检索考试材料；
   - concept-filtered：先用 active concept metadata 限定候选池，再做词法排序。
4. 计算 Success@1、Success@5、MRR@5、nDCG@5。

最终结果：

| Condition | Queries | Success@1 | Success@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|---:|---:|
| Lexical | 160 | 0.669 | 0.875 | 0.751 | 0.771 |
| Lecture-only | 160 | 0.362 | 0.650 | 0.456 | 0.509 |
| Exam-only | 160 | 0.600 | 0.825 | 0.690 | 0.712 |
| Concept-filtered | 160 | 1.000 | 1.000 | 1.000 | 1.000 |

重要解释：

concept-filtered 的 1.000 不是说系统拥有完美自然语言理解能力，而是因为这个实验条件使用了 benchmark 已知的 active concept metadata。它更像是在回答：

> 如果系统已经知道当前复习概念，那么用概念先过滤材料，会不会显著提高证据检索质量？

答案是会。因此论文中把它解释为 concept-aware retrieval upper bound，而不是无限夸大为真实开放场景下永远 100% 准确。

对应文件：

- `paper_work/full_experiment_outputs/retrieval_results_expanded.csv`
- `paper_work/full_experiment_outputs/retrieval_metrics_expanded.json`
- `paper_work/full_experiment_outputs/retrieval_metrics_by_type_expanded.csv`

### 3.4 RAG Support Evaluation

实验目的：

> 检查系统生成的解释是否被检索到的材料支持。

实验方法：

1. 从扩展 retrieval query 中抽取 40 个 grounded explanation queries。
2. 系统先检索相关 context。
3. LLM 基于检索 context 生成回答。
4. 再用一次模型判断回答是否被 retrieved chunks 支持。
5. 计算 supported rate 和 mean support score。

最终结果：

| 指标 | 值 |
|---|---:|
| queries | 40 |
| supported rate | 0.975 |
| mean support score | 0.945 |

重要解释：

这是真实脚本和模型调用得到的自动评估结果，但它仍然是 automatic judge，不是人工专家逐条审阅。因此论文中说它是 support proxy 或 automatic support evaluation，而不是最终数学正确性证明。

有一个低支持案例：用户想要 determinant worked example，但检索结果主要是 determinant definitions and lemmas。这说明系统未来需要更强的 material-type filtering，例如区分 definition、worked example、exam solution。

对应文件：

- `paper_work/full_experiment_outputs/rag_answer_rows.csv`
- `paper_work/full_experiment_outputs/rag_support_metrics.json`
- `paper_work/full_experiment_outputs/rag_failure_cases.md`

### 3.5 Agent Interaction Evaluation

这部分对应论文中的 Agent interaction table，也是与 UI 最相关的实验。

实验目的：

> 检查 UI 中会发生的三类 Agent 行为是否可用：grading、hint、dialogue。

实验方法：

1. 覆盖 16 个线性代数概念节点。
2. 每个概念生成 9 个任务：
   - 3 个 grading；
   - 3 个 hint；
   - 3 个 dialogue。
3. 总任务数为 16 × 9 = 144。
4. 调用 LLM Agent 生成反馈。
5. 对输出做自动检查：
   - 是否完成响应；
   - 是否显式提到或接近 paraphrase 目标概念；
   - 是否有 evidence-linked / grounding proxy；
   - grading 是否符合 rubric format；
   - hint 是否避免直接给完整答案。

最终结果：

| Task type | Tasks | Concept-linked | Evidence-linked | Task-specific |
|---|---:|---:|---:|---:|
| Grading | 48 | 47 | 47 | 48 |
| Hint | 48 | 42 | 41 | 48 |
| Dialogue | 48 | 48 | 48 | -- |
| Overall | 144 | 137 | 136 | -- |

额外指标文件中也记录了比例：

| 指标 | 值 |
|---|---:|
| completed tasks | 144 |
| API error count | 0 |
| completed response rate | 1.000 |
| concept attribution rate | 0.951 |
| groundedness proxy rate | 0.944 |
| hint no-full-solution rate | 1.000 |

重要解释：

这组数据是真实 API 调用后保存下来的输出，不是手填的。之前曾有 API error，但后来对失败行进行了重跑，最终 `api_error_count = 0`，所以论文里不写 API error。

为什么论文里用 count 而不是只用比例？因为 48 个任务中错 1 个就是 47/48 = 0.979，容易让表格出现很多看似奇怪的 0.979 或 1.000。改成 count 更透明，也更容易理解。

对应文件：

- `paper_work/full_experiment_outputs/agent_interaction_rows.csv`
- `paper_work/full_experiment_outputs/agent_metrics.json`
- `paper_work/rerun_agent_api_errors.py`

### 3.6 IRT Simulation

这部分对应论文中的 IRT/adaptive selection simulation，以及后来新增的 IRT sensitivity analysis。

实验目的：

> 在没有真实学生作答记录的情况下，模拟比较不同选题策略的行为。

重要边界：

这不是学生实验，也不是从真实学生 response log 校准出来的 IRT 参数。它是 simulation-based evaluation。

实验方法：

1. 构造 4 个模拟学习者 profile：
   - weak linear systems；
   - mid-level spectral review；
   - advanced orthogonality review；
   - broad final review。
2. 比较 4 种选题策略：
   - random；
   - difficulty-only；
   - graph-only；
   - graph+IRT。
3. 每个 profile 下选择一系列 item。
4. 计算：
   - weak-concept coverage；
   - difficulty match error；
   - concept diversity；
   - prerequisite risk flag。

最终结果：

| Condition | Weak coverage | Difficulty error | Concept div. | Prereq. risk flag |
|---|---:|---:|---:|---:|
| Random | 0.771 | 1.051 | 14.50 | 0.833 |
| Difficulty-only | 0.521 | 0.363 | 9.25 | 0.208 |
| Graph-only | 1.000 | 1.328 | 14.25 | 0.979 |
| Graph+IRT | 1.000 | 1.268 | 14.75 | 0.896 |

重要解释：

这个实验说明一个 trade-off：

- difficulty-only 最会匹配难度，但不一定覆盖弱概念；
- graph-only 最会覆盖弱概念，但难度匹配差；
- graph+IRT 保持弱概念覆盖，同时比 graph-only 稍微改善 difficulty error。

`prerequisite risk flag` 不是人工确认的违规，而是自动代理指标。它表示某个 item 含有高级概念，而模拟 profile 中一些先修概念仍弱。由于线性代数期末题本来经常跨多个概念，所以这个指标偏高。论文中不能把它写成“确定的教学错误”，只能写成 automatic proxy / risk flag。

为了更清楚地检验 IRT 的作用，后来又新增了一个固定弱概念目标的 sensitivity experiment。这个实验先固定学生当前要复习的弱概念，然后只在同一概念候选题池里比较不同选题策略。这样可以避免 IRT 效果被概念覆盖率掩盖。

新增 IRT sensitivity 结果：

| Policy | Trials | Weak cov. | Hit@0.5 | Hit@0.75 | Diff. error | Mean info |
|---|---:|---:|---:|---:|---:|---:|
| Random within target | 26 | 1.000 | 0.077 | 0.077 | 1.250 | 0.171 |
| Syllabus-ranked | 26 | 1.000 | 0.231 | 0.269 | 0.964 | 0.195 |
| Difficulty-only | 26 | 1.000 | 0.615 | 0.731 | 0.459 | 0.233 |
| Graph+IRT | 26 | 1.000 | 0.538 | 0.731 | 0.512 | 0.230 |

这个新实验更适合说明 IRT 的价值：Graph+IRT 相比 syllabus-ranked，把 Hit@0.5 从 0.231 提升到 0.538，把 difficulty error 从 0.964 降到 0.512。纯 difficulty-only 仍然在难度匹配上略好，但它不考虑图谱和大纲约束。因此论文中的解释应是：IRT 适合作为“概念诊断之后的 second-stage selector”，而不是整个复习路径的唯一主导机制。

对应文件：

- `paper_work/full_experiment_outputs/irt_simulation_rows.csv`
- `paper_work/full_experiment_outputs/irt_simulation_metrics.json`
- `paper_work/full_experiment_outputs/irt_sensitivity_rows.csv`
- `paper_work/full_experiment_outputs/irt_sensitivity_metrics.json`
- `paper_work/full_experiment_outputs/irt_sensitivity_summary.md`

### 3.7 Ablation Analysis

这部分对应论文中的 ablation table。

实验目的：

> 检查移除某些系统组件后，目标指标会如何变化。

消融条件：

| Condition | 移除内容 |
|---|---|
| A0 full system | 无 |
| A1 no syllabus alignment | 移除 syllabus alignment |
| A2 no mastery loop | 移除 mastery loop |
| A3 no concept-filtered retrieval | 移除 concept-filtered retrieval，退化为 lexical retrieval |
| A4 no dependency propagation | 移除 prerequisite propagation |
| A5 no IRT adaptation | 移除 IRT weighting |
| A6 fixed dialogue flow | 移除 dialogue agent 的灵活对话流程 |

论文采用的是 primary-metric ablation，而不是把所有列都放进去。原因是不同组件本来影响的指标不同，强行把每个 condition 放在所有指标上，会产生很多不变值，看起来像“假实验”。现在的表格只报告每个消融最应该影响的目标指标。

最终结果：

| Condition | Removed component | Target metric | Full | Ablated | Change |
|---|---|---|---:|---:|---:|
| A1 no syllabus alignment | M1 syllabus alignment | Alignment score ↑ | 0.472 | 0.469 | -0.003 |
| A2 no mastery loop | M4 mastery loop | Weak-concept coverage ↑ | 0.979 | 0.604 | -0.375 |
| A3 no concept-filtered retrieval | M2 concept filter | Retrieval MRR@5 ↑ | 1.000 | 0.751 | -0.249 |
| A4 no dependency propagation | Prerequisite propagation | Prerequisite risk flag ↓ | 0.854 | 0.896 | +0.042 |
| A5 no IRT adaptation | E2 IRT weighting | Difficulty hit@0.5 ↑ | 0.538 | 0.231 | -0.307 |
| A6 fixed dialogue flow | E1 dialogue agent | Dialogue flexibility ↑ | 0.915 | 0.250 | -0.665 |

重要解释：

这不是人工填出来的表，而是脚本重算后的结果。每个 condition 通过改变配置，然后重新计算对应指标。后来为了避免 A3 使用“无检索必然为 0”的过严指标，论文主表把 A3 改成了更合理的非平凡对照：从 concept-filtered retrieval 退化为 lexical retrieval。这样比较的是“是否使用概念过滤”的增益，而不是“有没有检索工具”的必然差异。

不过也要注意：

- A1 的影响很小，说明当前自动指标对 syllabus alignment 不够敏感。
- A3 仍然显示检索模块重要，但现在解释为 concept filter 的增益：MRR@5 从 lexical retrieval 的 0.751 提升到 concept-filtered retrieval 的 1.000。
- A2 影响明显，说明 mastery loop 对弱概念覆盖很重要。
- A5 在固定弱概念目标的 sensitivity analysis 中影响明显，说明 IRT 对第二阶段难度匹配有价值。
- A6 影响明显，说明固定流程不能很好支持多类对话行为。

对应文件：

- `paper_work/run_true_ablation.py`
- `paper_work/full_experiment_outputs/ablation_results.csv`
- `paper_work/full_experiment_outputs/ablation_delta_results.csv`
- `paper_work/full_experiment_outputs/ablation_summary.md`
- `paper_work/full_experiment_outputs/ablation_retrieval_rows.csv`
- `paper_work/full_experiment_outputs/ablation_selection_rows.csv`
- `paper_work/full_experiment_outputs/ablation_dialogue_rows.csv`

## 4. 哪些数据是真实的，哪些是代理指标或仿真

为了避免混淆，可以把论文数据分为三类。

### 4.1 真实本地统计

这些数据直接来自本地文件统计，不涉及模型主观判断：

- corpus 文件数、行数、字符数、近似 token 数；
- benchmark item 数量；
- item 来源角色；
- source folder 统计。

### 4.2 真实脚本/API 实验结果

这些数据是脚本运行和 API 调用后得到的，不是人工编造：

- concept tagging 的 LLM 标注结果；
- RAG answer rows；
- RAG support automatic judge；
- Agent grading/hint/dialogue responses；
- agent interaction metrics；
- rerun 后 API error count 为 0。

但是这些结果中的一部分是 automatic proxy，例如 support score、grounding proxy、concept-linked 检查。它们真实存在，但不等于人工专家最终判断。

### 4.3 仿真结果

IRT/adaptive selection 是仿真，不是真实学生数据。它真实地来自脚本运行，但模拟对象是我们设定的 learner profiles。

论文中必须保持这个边界：

- 可以说 simulation-based IRT evaluation；
- 不可以说 real learner calibration；
- 不可以说已经证明真实学生学习效果提升。

## 5. 当前论文最需要谨慎表达的地方

### 5.1 Concept-filtered retrieval 的 1.000

这个结果很高，但合理，因为它使用了已知 active concept metadata。它证明“如果概念识别可靠，概念过滤非常有帮助”，但不证明开放场景下端到端检索永远完美。

### 5.2 Concept tagging 的低 F1

低 F1 不是坏事，反而支持论文的设计论点：不能完全依赖 LLM 原始概念标注，需要图谱和证据约束。

### 5.3 Dialogue 的 48/48

Dialogue 高是因为 prompts 本身要求 concept-tied explanation，所以应谨慎解释为“在结构化提示下表现稳定”，而不是泛化成所有自由对话都完美。

### 5.4 IRT 不是课堂实验

IRT 目前只是模拟选题策略，不涉及真实学生成绩提升。未来如果要增强论文，需要真实学生 response logs 或小规模 user study。

### 5.5 UI 不是学习效果证据

UI 是系统原型和交互载体，不是证明系统提升学习效果的独立证据。要让 UI 成为强贡献，需要增加 usability study、任务完成时间、满意度问卷或交互日志分析。

## 6. 论文当前可以主张什么

当前论文可以比较稳妥地主张：

1. 已经构建了一个基于真实线性代数材料的 Markdown 语料库。
2. 已经从材料中抽取了 benchmark items 和概念图谱。
3. 已经实现了一个闭环系统架构，包括概念图谱、检索、RAG、批改、对话、IRT 仿真和 UI 原型。
4. 检索实验表明 concept-filtered retrieval 对复习场景有明显帮助。
5. RAG support 实验显示大多数生成回答能被检索证据支持。
6. Agent interaction 实验显示 grading、hint、dialogue 在结构化任务下可以稳定运行。
7. Concept tagging 实验显示 raw LLM labels 噪声较大，需要约束。
8. IRT 仿真显示 graph+IRT 在弱概念覆盖和难度匹配之间有折中价值。
9. 消融实验显示 retrieval、mastery loop 和 dialogue agent 是当前系统中影响最明显的组件。

当前论文不应该主张：

1. 已经证明真实学生学习成绩提升。
2. 已经完成真实课堂部署。
3. IRT 参数来自真实学生答题校准。
4. LLM 概念标注已经达到高准确率。
5. UI 本身已经通过用户研究证明有效。

## 7. 后续如果继续增强论文，最值得补的实验

如果后面继续优化，优先级建议如下：

1. 人工抽样验证 concept labels 和 agent feedback。
2. 小规模 UI usability study，例如 5-10 人试用，记录任务完成率和反馈。
3. 对 RAG support 做人工专家复核，至少抽样 20-30 条。
4. 收集少量真实学生 response logs，用于替代或补充 IRT 仿真。
5. 把当前 automatic proxy 指标和人工评分做相关性检查。

这些会显著增强论文的实证说服力。
