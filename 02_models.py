# -*- coding: utf-8 -*-
"""Part B: fit comparable baselines and models using the frozen Part A split."""

from __future__ import annotations

import json
from math import ceil
from pathlib import Path

import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "bank-additional-full.csv"
SPLIT = ROOT / "outputs" / "split_v1.csv"
CONFIG = ROOT / "configs" / "features.yaml"
OUTPUT = ROOT / "outputs"
SEED = 42
POSITIVE_LABEL = "yes"
MODEL_ORDER = (
    "no_skill",
    "poutcome_success",
    "logistic",
    "logistic_macro_control",
    "decision_tree",
    "random_forest",
    "logistic_duration_ablation",
)

NUMERIC_FEATURES = [
    "age",
    "campaign",
    "pdays",
    "previous",
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
]
CATEGORICAL_FEATURES = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]
MACRO_FEATURES = [
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
]


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, dict]:
    if not RAW.exists():
        raise FileNotFoundError(f"找不到原始数据：{RAW}")
    if not SPLIT.exists():
        raise FileNotFoundError(f"找不到 Part A 冻结切分：{SPLIT}")
    if not CONFIG.exists():
        raise FileNotFoundError(f"找不到特征配置：{CONFIG}")

    split = pd.read_csv(SPLIT)
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    if config["split_id"] != "v1":
        raise ValueError(f"特征配置 split_id 必须为 v1，实际为 {config['split_id']!r}")
    fold_counts = split["fold"].value_counts().to_dict()
    if fold_counts != {"train": 24712, "validation": 8238, "test": 8238}:
        raise ValueError("split_v1.csv 的分段与 Part A 冻结协议不一致")
    all_features = list(dict.fromkeys([*NUMERIC_FEATURES, *CATEGORICAL_FEATURES, "duration"]))
    data = pd.read_csv(RAW, sep=";", usecols=all_features)
    if len(data) != len(split) or split["row_id"].tolist() != list(range(len(data))):
        raise ValueError("split_v1.csv 必须与原始数据逐行对齐，row_id 从 0 连续递增")

    n_train_validation = fold_counts["train"] + fold_counts["validation"]
    expected_folds = (
        ["train"] * fold_counts["train"]
        + ["validation"] * fold_counts["validation"]
        + ["test"] * fold_counts["test"]
    )
    if split["fold"].tolist() != expected_folds:
        raise ValueError("split_v1.csv 不是 Part A 的连续按行序时间留出切分")
    # Read labels only through the end of Validation; Test labels are reserved for C.
    labels = pd.read_csv(RAW, sep=";", usecols=["y"], nrows=n_train_validation)["y"]
    if len(labels) != n_train_validation or labels.isna().any():
        raise ValueError("Train/Validation 标签行数不符或包含缺失值")
    if not set(labels.unique()).issubset({"yes", "no"}):
        raise ValueError("Train/Validation 标签包含非预期类别")
    data.insert(0, "row_id", range(len(data)))
    labels.index = range(n_train_validation)
    return data, split, labels, config


def get_features(config: dict, feature_set: str) -> list[str]:
    features = config["feature_sets"][feature_set]
    if "y" in features or "row_id" in features:
        raise ValueError(f"{feature_set} 特征集不得包含标签 y 或 row_id")
    if feature_set == "main" and "duration" in features:
        raise ValueError("主模型特征集不得包含通话后才知道的 duration")
    return features


def make_pipeline(
    features: list[str], estimator: object
) -> Pipeline:
    numeric = [column for column in NUMERIC_FEATURES + ["duration"] if column in features]
    categorical = [column for column in CATEGORICAL_FEATURES if column in features]
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ],
        remainder="drop",
    )
    return Pipeline([("preprocess", preprocessor), ("model", estimator)])


def top_k_metrics(y_true: pd.Series, risk: pd.Series, fraction: float = 0.30) -> dict:
    """Measure top-K using row_id ascending as the deterministic tie-breaker."""
    n = len(y_true)
    k = ceil(n * fraction)
    ranked = pd.DataFrame(
        {"row_id": y_true.index, "y_true": y_true.to_numpy(), "risk": risk.to_numpy()}
    ).sort_values(
        ["risk", "row_id"], ascending=[False, True], kind="mergesort"
    )
    hits = int(ranked.head(k)["y_true"].sum())
    total_positive = int(y_true.sum())
    return {
        "k": k,
        "precision_at_30pct": hits / k,
        "recall_at_30pct": hits / total_positive if total_positive else 0.0,
        "hits_at_30pct": hits,
    }


def validation_metrics(y_true: pd.Series, risk: pd.Series) -> dict:
    top_k = top_k_metrics(y_true, risk)
    predicted = risk >= 0.5
    positives = y_true.astype(bool)
    tp = int((predicted & positives).sum())
    fp = int((predicted & ~positives).sum())
    fn = int((~predicted & positives).sum())
    tn = int((~predicted & ~positives).sum())
    return {
        "pr_auc": float(average_precision_score(y_true, risk)),
        **top_k,
        "accuracy_at_0_5": (tp + tn) / len(y_true),
        "precision_at_0_5": tp / (tp + fp) if tp + fp else 0.0,
        "recall_at_0_5": tp / (tp + fn) if tp + fn else 0.0,
    }


def fit_best(
    train_x: pd.DataFrame,
    train_y: pd.Series,
    validation_x: pd.DataFrame,
    validation_y: pd.Series,
    features: list[str],
    candidates: list[dict],
    model_kind: str,
) -> tuple[Pipeline, dict, pd.Series, list[dict]]:
    best: tuple[float, Pipeline, dict, pd.Series] | None = None
    candidate_rows: list[dict] = []
    for params in candidates:
        if model_kind == "logistic":
            estimator = LogisticRegression(
                C=params["C"],
                max_iter=1000,
                solver="liblinear",
                random_state=SEED,
            )
        elif model_kind == "tree":
            estimator = DecisionTreeClassifier(random_state=SEED, **params)
        elif model_kind == "forest":
            estimator = RandomForestClassifier(
                n_estimators=150,
                max_features="sqrt",
                n_jobs=-1,
                random_state=SEED,
                **params,
            )
        else:
            raise ValueError(f"未知模型类型：{model_kind}")

        model = make_pipeline(features, estimator)
        model.fit(train_x[features], train_y)
        risk = positive_probabilities(model, validation_x[features])
        score = float(average_precision_score(validation_y, risk))
        metrics = validation_metrics(validation_y, risk)
        candidate_rows.append(
            {
                "model_family": model_kind,
                "feature_set": ",".join(features),
                "parameters": json.dumps(params, sort_keys=True),
                "validation_pr_auc": score,
                "precision_at_30pct": metrics["precision_at_30pct"],
                "recall_at_30pct": metrics["recall_at_30pct"],
                "hits_at_30pct": metrics["hits_at_30pct"],
            }
        )
        if best is None or score > best[0]:
            best = (score, model, params, risk)

    if best is None:
        raise ValueError(f"{model_kind} 没有候选超参数")
    return best[1], best[2], best[3], candidate_rows


def positive_probabilities(model: Pipeline, features: pd.DataFrame) -> pd.Series:
    classifier = model.named_steps["model"]
    classes = list(classifier.classes_)
    print(f"[classes_] {type(classifier).__name__}: {classes}")
    if POSITIVE_LABEL not in classes:
        raise ValueError(f"模型 classes_ 中不存在正类 {POSITIVE_LABEL!r}: {classes}")
    positive_index = classes.index(POSITIVE_LABEL)
    return pd.Series(model.predict_proba(features)[:, positive_index], index=features.index)


def main() -> None:
    data, split, labels, config = load_inputs()
    main_features = get_features(config, "main")
    macro_control_features = get_features(config, "macro_control")
    ablation_features = get_features(config, "duration_ablation")
    if set(main_features) != set(NUMERIC_FEATURES + CATEGORICAL_FEATURES) - set(MACRO_FEATURES):
        raise ValueError("主模型特征集应包含 14 个通话前非宏观字段")
    if set(macro_control_features) != set(main_features) | set(MACRO_FEATURES):
        raise ValueError("宏观对照特征集应为主模型特征加 5 个宏观字段")
    if ablation_features != main_features + ["duration"]:
        raise ValueError("duration 消融特征必须仅在主模型特征后增加 duration")

    train_mask = split["fold"].eq("train")
    validation_mask = split["fold"].eq("validation")
    train = data.loc[train_mask]
    validation = data.loc[validation_mask]
    train_y = labels.loc[train.index]
    validation_y = labels.loc[validation.index].eq(POSITIVE_LABEL).astype(int)
    test_features = list(dict.fromkeys([*macro_control_features, "duration"]))
    test = data.loc[split["fold"].eq("test"), ["row_id", *test_features]]

    # Confirm the target-probability column before scoring; all preprocessing
    # is fit inside each pipeline on train only.
    selected: dict[str, tuple[Pipeline, dict, pd.Series]] = {}
    candidate_pool: list[dict] = []
    logistic_candidates = [{"C": c} for c in (0.1, 1.0, 3.0, 10.0, 30.0, 100.0)]
    for model_name, feature_set, candidates, model_kind in [
        ("logistic", main_features, logistic_candidates, "logistic"),
        (
            "logistic_macro_control",
            macro_control_features,
            logistic_candidates,
            "logistic",
        ),
        (
            "decision_tree",
            main_features,
            [
                {"max_depth": depth, "min_samples_leaf": leaf}
                for depth in (3, 5, 8)
                for leaf in (50, 100)
            ],
            "tree",
        ),
        (
            "random_forest",
            main_features,
            [
                {"max_depth": depth, "min_samples_leaf": leaf}
                for depth in (10, None)
                for leaf in (20, 50)
            ],
            "forest",
        ),
        (
            "logistic_duration_ablation",
            ablation_features,
            logistic_candidates,
            "logistic",
        ),
    ]:
        model, params, validation_risk, candidate_rows = fit_best(
            train[feature_set],
            train_y,
            validation[feature_set],
            validation_y,
            feature_set,
            candidates,
            model_kind,
        )
        for row in candidate_rows:
            row["model"] = model_name
        candidate_pool.extend(candidate_rows)
        selected[model_name] = (model, params, validation_risk)
        print(
            f"[Validation 选参] {model_name}: AP="
            f"{average_precision_score(validation_y, validation_risk):.6f}; {params}"
        )

    score_frames: list[pd.DataFrame] = []
    summary_rows: list[dict] = []
    for fold_name, part in (("validation", validation), ("test", test)):
        y_true = validation_y if fold_name == "validation" else None
        for model_name in MODEL_ORDER:
            if model_name == "no_skill":
                risk = pd.Series(0.0, index=part.index)
            elif model_name == "poutcome_success":
                risk = part["poutcome"].eq("success").astype(float)
            else:
                model, _, validation_risk = selected[model_name]
                if fold_name == "validation":
                    risk = validation_risk
                else:
                    feature_set = (
                        ablation_features
                        if model_name == "logistic_duration_ablation"
                        else macro_control_features
                        if model_name == "logistic_macro_control"
                        else main_features
                    )
                    risk = positive_probabilities(model, part[feature_set])

            frame = pd.DataFrame(
                {
                    "row_id": part["row_id"].astype(int).to_numpy(),
                    "fold": fold_name,
                    "model": model_name,
                    "risk": risk.to_numpy(dtype=float),
                }
            )
            score_frames.append(frame)
            if fold_name == "validation":
                assert y_true is not None
                metrics = validation_metrics(y_true, risk)
                summary_rows.append(
                    {
                        "model": model_name,
                        "validation_pr_auc": metrics["pr_auc"],
                        "precision_at_30pct": metrics["precision_at_30pct"],
                        "recall_at_30pct": metrics["recall_at_30pct"],
                        "hits_at_30pct": metrics["hits_at_30pct"],
                        "accuracy_at_0_5": metrics["accuracy_at_0_5"],
                        "precision_at_0_5": metrics["precision_at_0_5"],
                        "recall_at_0_5": metrics["recall_at_0_5"],
                        "selected_parameters": (
                            json.dumps(selected[model_name][1], sort_keys=True)
                            if model_name in selected
                            else "{}"
                        ),
                        "selection_basis": (
                            "validation PR-AUC"
                            if model_name in selected
                            else "fixed baseline"
                        ),
                    }
                )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    scores = pd.concat(score_frames, ignore_index=True)
    scores["model"] = pd.Categorical(scores["model"], categories=MODEL_ORDER, ordered=True)
    scores["fold"] = pd.Categorical(
        scores["fold"], categories=["validation", "test"], ordered=True
    )
    scores = scores.sort_values(["fold", "model", "row_id"])
    scores["model"] = scores["model"].astype(str)
    scores["fold"] = scores["fold"].astype(str)
    scores.to_csv(OUTPUT / "scores.csv", index=False, float_format="%.10g")

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUTPUT / "T2_模型对比表.csv", index=False, float_format="%.6f")
    lines = [
        "# T2 模型对比表（Validation）",
        "",
        "> 仅用 Part A 的 `split_v1`；所有处理器仅在 Train 拟合，树/森林/Logistic 参数仅按 Validation PR-AUC 选择。此表不含 Test 指标，Test 分数仅供 C 在最终评价时使用。",
        "> Precision@30% / Recall@30% 采用 K=ceil(0.30×Validation 行数)，分数并列时按 row_id 升序稳定排序，与 C 的名单生成口径一致。",
        "",
        "| 模型 | Validation PR-AUC | Precision@30% | Recall@30% | 命中数@30% | Accuracy@0.5 | Precision@0.5 | Recall@0.5 | 选定参数 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        params = row["selected_parameters"].replace("|", "\\|")
        lines.append(
            f"| {row['model']} | {row['validation_pr_auc']:.6f} | "
            f"{row['precision_at_30pct']:.6f} | {row['recall_at_30pct']:.6f} | "
            f"{row['hits_at_30pct']} | {row['accuracy_at_0_5']:.6f} | "
            f"{row['precision_at_0_5']:.6f} | {row['recall_at_0_5']:.6f} | `{params}` |"
        )
    lines.extend(
        [
            "",
            "说明：`no_skill` 恒输出 0 分，Accuracy@0.5 是全猜 no 的准确率，不能代表名单排序能力；`logistic_macro_control` 只用于检验宏观指标的时间漂移，`logistic_duration_ablation` 只用于泄漏消融，两者均非主模型。",
            "",
            "模型取舍：Validation 选择不含宏观指标的 Logistic（L2，"
            f"C={selected['logistic'][1]['C']:g}）。其 PR-AUC "
            f"{summary.loc[summary['model'].eq('logistic'), 'validation_pr_auc'].iloc[0]:.6f} "
            "高于规则基线 "
            f"{summary.loc[summary['model'].eq('poutcome_success'), 'validation_pr_auc'].iloc[0]:.6f}；"
            "30% 预算命中数 "
            f"{summary.loc[summary['model'].eq('logistic'), 'hits_at_30pct'].iloc[0]:.0f} "
            "也高于规则基线 "
            f"{summary.loc[summary['model'].eq('poutcome_success'), 'hits_at_30pct'].iloc[0]:.0f}。"
            "`logistic_macro_control` 是同算法、同切分、同调参流程的对照。该结论是 Validation 选型结果，须由 C 在 Test 上一次性确认，不能提前声称测试集全面胜出。",
            "",
            "固定预算按 K=ceil(30%×Validation 行数) 计算；分数并列时以 row_id 升序作稳定决胜规则。Test 标签不参与 B 的训练、模型选择或指标计算，仅输出 Test 风险分数供 C 一次性评价。",
            "",
            "完整 Logistic C 网格结果见 `outputs/model_selection_pool.csv`。主模型不含 `duration`；该字段仅用于单独消融。",
            "",
        ]
    )
    (OUTPUT / "T2_模型对比表.md").write_text("\n".join(lines), encoding="utf-8")
    logistic = selected["logistic"][0]
    feature_names = logistic.named_steps["preprocess"].get_feature_names_out()
    coefficients = logistic.named_steps["model"].coef_[0]
    coefficient_table = pd.DataFrame(
        {
            "encoded_feature": feature_names,
            "coefficient_log_odds": coefficients,
        }
    )
    coefficient_table["abs_coefficient"] = coefficient_table[
        "coefficient_log_odds"
    ].abs()
    coefficient_table = coefficient_table.sort_values(
        "abs_coefficient", ascending=False
    )
    coefficient_table.to_csv(
        OUTPUT / "logistic_coefficients.csv", index=False, float_format="%.8f"
    )
    pd.DataFrame(candidate_pool).sort_values(
        ["model", "validation_pr_auc"], ascending=[True, False]
    ).to_csv(OUTPUT / "model_selection_pool.csv", index=False, float_format="%.8f")
    print(f"[完成] {OUTPUT / 'scores.csv'}（{len(scores):,} 行）")
    print(f"[完成] {OUTPUT / 'T2_模型对比表.md'}")
    print(f"[完成] {OUTPUT / 'logistic_coefficients.csv'}")
    print(f"[完成] {OUTPUT / 'model_selection_pool.csv'}")


if __name__ == "__main__":
    main()
