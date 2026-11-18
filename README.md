# INT_6163_8th_GroupWork

INT6163 (02P) Advanced Data Analytics — Group 8, Bank Marketing project.

This `report` branch integrates the complete `main` project, repaired A/B/C
entries and matching results, and Part D. Read [README_D.md](README_D.md) for
the file inventory, the 46 repair points, and differences from `main`.

Part D deliverables are directly available:

- [report.docx](report.docx): approved report, references, GenAI statement and contributions.
- [F5 action loop PNG](outputs/F5_行动闭环.png) / [SVG](outputs/F5_行动闭环.svg).
- [Report chapter–figure–file map](outputs/章节_图表_数字对应表.md).

## Reproduce the integrated A–D project

Use Python 3.9 or newer and the original [requirements.txt](requirements.txt).
From the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/reproduce_all.py --check-only
python scripts/reproduce_all.py
```

The entry runs A → B → C → D01 → D02 from the original CSV in a new workspace.
Read `runs/latest_run.txt` and that run's `RUN_RESULTS.md`; its `publication/`
contains directly browsable `data/`, `outputs/`, `figures/` and a byte-identical
copy of the authored report. No result archive or old predictions are used as
training inputs. Repository results and `report.docx` are not overwritten.
The report's 107 registered numbers and action-diagram values are checked
against the newly computed results. An evidence mismatch stops the run.

The public result files below are one matching rebuilt set. Individual A/B/C
entries remain available for inspection; the unified entry is the recommended
way to recreate the complete public set.

## Reproduce Part A and Part B

Use Python 3.9 or newer. From the repository root:

```bash
python -m pip install -r requirements.txt
python 01_data_quality.py
python 02_models.py
```

Part A creates and freezes `outputs/split_v1.csv`. Part B reads that split without
changing it, fits preprocessing only on the training fold, and uses validation
average precision (AP) to select model hyperparameters. The B entry writes
to `local_review/B01_candidate/outputs/`; the matching published files are:

- `outputs/scores.csv`: Validation and final Test-fold probabilities in a
  consistent `row_id, fold, model, risk` format. Part B does not read Test
  labels; Part C aligns scores to labels for the one-time final evaluation.
- `outputs/T2_模型对比表.md` and `.csv`: Validation-only model comparison.
- `outputs/model_selection_pool.csv`: tested Logistic C values and candidate
  model results on Validation.
- `outputs/logistic_coefficients.csv`: selected Logistic model's encoded
  feature coefficients (associations, not causal effects).
- `configs/features.yaml`: frozen pre-call feature list and separate
  macro-control and `duration` ablation feature lists. The selected main model
  excludes five macroeconomic indicators; their Logistic control is retained
  for the Validation comparison.

The `no_skill` model always predicts `no`. `logistic_duration_ablation` is
included only to measure leakage and must not be used as the main model.
Part C should use the Test scores only for its final evaluation; no Test metrics
are used for Part B model selection. See [data/README_data.md](data/README_data.md)
for the dataset, data-quality decisions, and split protocol.

## Reproduce Part C: final evaluation and number guardrails

After running the A and B entries above, run from the repository root.
The repaired C entry loads the matching B candidate and its manifest:

```bash
python 03_eval.py
```

Part C reads the frozen Test labels only for the one-time final evaluation.
Every model is compared at the same budget:

- Test rows: 8,238.
- Main working point: `K = ceil(30% x 8,238) = 2,472`.
- Ranking rule: `risk` descending, with `row_id` ascending as the deterministic
  tie-breaker.
- Main model: `logistic`, excluding `duration` and the five macroeconomic
  indicators.

The C entry writes to `local_review/C01_candidate/outputs/` and `figures/`.
The consolidated published paths are:

- `outputs/metrics.json`: the single source of truth for reported numbers.
- `outputs/T3_误差切片表.md`: Test error slices.
- `outputs/T4_duration消融表.md`: leakage ablation for `duration`.
- `outputs/T5_数字核对表.md`: number-to-JSON-key audit table.
- `outputs/C_测试集模型比较表.md`: Test comparison at the shared budget.
- `figures/F3_PR曲线.png`: precision-recall curves.
- `figures/F4_预算收益曲线.png`: budget sensitivity from 10% to 100%.

The duration model is an ablation only and must not be presented as the main
model. Results are based on one historical Test period and support ranking
evaluation, not causal or uplift claims.

## Part D: report, action and integration

Part D assembles the six-chapter report and its evidence, defines a proposed
contact-review loop, and replays a fixed illustrative contact restriction
(`previous >= 3` and `poutcome == failure`). The main scenario does not refill
removed contacts. Its extra missed subscriptions are separated from the
original model's missed subscriptions; a refill scenario is reported separately.
This is a retrospective replay, with no causal, deployment or real human-release
claim. [T6](outputs/T6_联系限制补充评价.md) and [F5](outputs/F5_行动闭环.png)
show the calculation and proposed workflow.

[outputs/metrics.json](outputs/metrics.json) is the unified numeric source;
[T5](outputs/T5_数字核对表.md) links the approved report's 107 numbers to JSON
keys and actual pages. [CONTRIBUTIONS.md](CONTRIBUTIONS.md) records responsibilities.
All result tables and figures are available in their normal project directories.

The data source, download instructions, random seed (42), row-order 60/20/20
split, font requirements and repair details are in [README_D.md](README_D.md).
Environment authority remains the original requirements; observed installation
versions are recorded in each run. Historical `main` scores are not promised to
be bit-identical to retraining in every compatible environment. The unified
entry verifies the new science against the registered report and preserves
the report when a comparison fails.
