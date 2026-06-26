# AILinearReview

An exam-syllabus-driven methodological framework for adaptive linear algebra review with a concept graph, retrieval-augmented grounding, dialogue-agent feedback, a learner-facing UI prototype, and IRT-based item selection.

## Overview

AILinearReview studies how linear algebra final-review materials can be converted into a closed-loop adaptive review workflow. The framework includes:

- Layer 1: PDF-to-Markdown corpus construction and audit
- Layer 2: Concept graph construction and prerequisite-aware review paths
- Layer 3: Concept-filtered retrieval and evidence-grounded feedback
- Layer 4: Dialogue-agent grading, hinting, and tutoring actions
- Layer 5: Learner-state tracking and IRT-based adaptive item selection
- Layer 6: Browser-based learner-facing interface

The current release is a research prototype and automatic-benchmark package. It does not claim classroom learning gains or human-subject validation.

## Repository Structure

```text
AILinearReview/
├── src/                         # Experiment and analysis scripts
│   ├── run_full_experiments.py
│   ├── run_concept_tagging_expanded.py
│   ├── run_true_ablation.py
│   ├── run_irt_sensitivity.py
│   └── compute_concept_tagging_diagnostics.py
├── data/
│   ├── full_experiment_outputs/ # Saved benchmark metrics and rows
│   ├── concept_graph_seed.md
│   ├── evaluation_corpus_notes.md
│   └── material_index.md
├── ui_prototype/                # Local web UI and Python back end
├── docs/                        # Workflow and preprocessing notes
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the UI prototype:

```bash
cd ui_prototype
python3 server.py
```

Then open:

```text
http://127.0.0.1:8765
```

To enable live agent calls, copy `.env.example` to `.env` and add a valid `ZHIPUAI_API_KEY`.

## Reproducing Experiments

The saved outputs used in the paper are under `data/full_experiment_outputs/`.

Representative commands:

```bash
python3 src/run_full_experiments.py
python3 src/run_concept_tagging_expanded.py
python3 src/run_irt_sensitivity.py
python3 src/run_true_ablation.py
```

Some scripts expect the converted Markdown corpora to be present locally. The converted full-text corpora are not redistributed in this repository; see `docs/` for preprocessing notes and source information.

## Data Sources

The project uses public linear algebra teaching resources:

- Jim Hefferon's Linear Algebra materials: https://hefferon.net/linearalgebra/
- MIT 18.06 Linear Algebra archive: https://web.mit.edu/18.06/www/

For licensing and redistribution reasons, this repository does not include the original PDFs or converted full-text Markdown corpora. It includes code, manuscript files, UI prototype files, experiment summaries, and benchmark output tables.

## Key Results

- 200 converted Markdown files audited locally
- 106 benchmark items extracted from converted materials
- Expanded concept-tagging diagnostics over 80 completed API-labeled items
- Retrieval benchmark with 160 review queries
- RAG support evaluation over 40 grounded explanation queries
- Agent interaction diagnostics over 144 tasks
- Executable ablation analysis across major system components
- IRT sensitivity analysis for graph-constrained adaptive selection

## Citation

If you use this repository, please cite the accompanying manuscript:

```text
waiting for accept
```

## License

Code and documentation in this repository are released under the MIT License. The manuscript text is not included in this repository. External educational materials remain subject to the licenses and permissions of their original sources.

## Contact

```text
waiting for details
```

