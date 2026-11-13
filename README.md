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
