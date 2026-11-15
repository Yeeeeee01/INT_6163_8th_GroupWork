# INT_6163_8th_GroupWork

INT6163 (02P) Advanced Data Analytics — Group 8, Bank Marketing project.

## Reproduce Part A and Part B

Use Python 3.9 or newer. From the repository root:

```bash
python -m pip install -r requirements.txt
python 01_data_quality.py
python 02_models.py
```

Part A creates and freezes `outputs/split_v1.csv`. Part B reads that split without
changing it, fits preprocessing only on the training fold, and uses validation
PR-AUC to select model hyperparameters. It writes:

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

After Parts A and B have produced `outputs/split_v1.csv` and
`outputs/scores.csv`, run from the repository root:

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

Part C writes:

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
