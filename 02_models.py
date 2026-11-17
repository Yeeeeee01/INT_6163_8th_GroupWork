# -*- coding: utf-8 -*-
# [B01-01 原代码开始] 明确环境依据、候选输出和原冻结结果保护
# """Part B: fit comparable baselines and models using the frozen Part A split."""
# [B01-01 原代码结束]
# [B01-01 修订代码开始]
"""Part B B01：保持GitHub训练方案，补充环境核对、候选隔离及来源记录。

环境按GitHub README Python3.9+与原requirements；本机实测版本只作记录。
默认写入local_review/B01_candidate，保留与C冻结指标配对的根目录原scores。
命令：python 02_models.py --output-root local_review/B01_candidate
"""
# [B01-01 修订代码结束]

from __future__ import annotations

import json

# [B01-02 新增] 增加追溯所需标准库，不改变模型依赖版本
import argparse
import hashlib
import importlib.metadata
import platform
import shutil
import sys
from datetime import datetime
from math import isfinite
# [B01-02 新增结束]
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
# [B01-03 原代码开始] 新训练候选不覆盖与原C指标配对的预测文件
# OUTPUT = ROOT / "outputs"
# [B01-03 原代码结束]
# [B01-03 修订代码开始]
LEGACY_OUTPUT = ROOT / "outputs"
OUTPUT = ROOT / "local_review" / "B01_candidate" / "outputs"
# [B01-03 修订代码结束]
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


# [B01-04 新增] 运行记录与候选隔离；模型实现保留

GITHUB_BASE_COMMIT = "bfdfedb3e6cf82ea59254279a5352af4f2a395e8"
GITHUB_EXPECTED_REQUIREMENTS = {"pandas": "2.2.3", "scikit-learn": "1.6.1", "PyYAML": "6.0.2", "matplotlib": "3.9.4"}
GITHUB_NORMALIZED_HASHES = {'data/raw/bank-additional-full.csv': '233e260d5d1d506a2c10381da5b8c2f75f2c08d1b373ca7b825e39ebe1bd30df', 'outputs/split_v1.csv': 'a6a452d080788aae533dd043e44dced2a9eac95e7ec4a2b39248394b83eaa0aa', 'configs/features.yaml': '09fd5282d67dd90331b243ee2128addb88936f9bbc4882d68897968fe33457bd', 'requirements.txt': 'd0de5273259b4ba63cfd0ad9aa260a78ed80fbc0acc2e10f7d895de560695d1f', 'outputs/scores.csv': 'b354c6cb35d3c6ef2f39d2b6b66a3c136319e072bc62770f5aecc615735cc2bc'}


def file_evidence(path):
    """Return actual bytes and LF-normalized fingerprints without rewriting input."""
    content = path.read_bytes()
    normalized = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "lf_normalized_sha256": hashlib.sha256(normalized).hexdigest()}


def inspect_github_environment():
    """Check declared requirements; separately record, rather than prescribe, observations."""
    if sys.version_info < (3, 9):
        raise RuntimeError("GitHub README要求Python3.9或以上")
    declared = {}
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            name, version = line.strip().split("==", 1)
            declared[name] = version
    if declared != GITHUB_EXPECTED_REQUIREMENTS:
        raise RuntimeError("requirements与本次GitHub基线声明不同；请核实上游版本，不采用本机另定标准")
    for name, version in declared.items():
        installed = importlib.metadata.version(name)
        if installed != version:
            raise RuntimeError(f"GitHub依赖不符：{name}要求{version}，实际{installed}")
    observed = {}
    for name in [*declared, "numpy", "scipy", "joblib", "threadpoolctl"]:
        try:
            observed[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            observed[name] = None
    return {
        "authority": {"repository": "Yeeeeee01/INT_6163_8th_GroupWork", "baseline_commit": GITHUB_BASE_COMMIT,
                      "python_minimum": "3.9", "declared_requirements": declared},
        "not_provided_by_upstream": ["B_training_python_exact_version", "B_training_numpy_version",
                                     "B_training_scipy_version", "B_training_joblib_version",
                                     "B_training_threadpoolctl_version", "complete_original_environment_lock"],
        "observed_for_this_run_only": {"python": sys.version, "system": platform.system(),
                                       "machine": platform.machine(), "packages": observed},
        "observed_environment_is_project_standard": False,
    }


def inspect_inputs():
    """Bind this run to the frozen GitHub data, split and feature configuration."""
    result = {}
    for relative in ["data/raw/bank-additional-full.csv", "outputs/split_v1.csv", "configs/features.yaml", "requirements.txt"]:
        evidence = file_evidence(ROOT / relative)
        if evidence["lf_normalized_sha256"] != GITHUB_NORMALIZED_HASHES[relative]:
            raise ValueError(f"输入与GitHub冻结基线内容不一致：{relative}")
        result[relative] = evidence
    result["02_models.py"] = file_evidence(ROOT / "02_models.py")
    return result


def parse_b01_arguments():
    parser = argparse.ArgumentParser(description="B01：按GitHub方案训练并记录隔离候选")
    parser.add_argument("--output-root", type=Path, default=ROOT / "local_review" / "B01_candidate")
    args = parser.parse_args()
    args.output_root = args.output_root.resolve()
    if args.output_root == ROOT or ROOT not in args.output_root.parents:
        raise ValueError("B01候选输出必须在项目子目录内，不能覆盖根目录原scores与C冻结结果")
    return args


def archive_b_outputs():
    """Keep exact prior generated files before replacing candidate output."""
    names = ["scores.csv", "T2_模型对比表.csv", "T2_模型对比表.md", "model_selection_pool.csv",
             "logistic_coefficients.csv", "B_run_manifest.json", "B_legacy_comparison.json"]
    existing = [name for name in names if (OUTPUT / name).is_file()]
    if not existing:
        return
    archive = OUTPUT.parent / "B01_generated_before" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    archive.mkdir(parents=True, exist_ok=False)
    manifest = {}
    for name in existing:
        shutil.copy2(OUTPUT / name, archive / name)
        manifest[name] = hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest()
    (archive / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_candidate_scores(scores, split):
    """Check score schema, coverage and probability range without reading Test labels."""
    if scores.columns.tolist() != ["row_id", "fold", "model", "risk"]:
        raise ValueError("预测输出必须为row_id,fold,model,risk")
    if scores.duplicated(["row_id", "fold", "model"]).any():
        raise ValueError("预测输出存在重复键")
    if not scores["risk"].map(lambda x: isfinite(x) and 0 <= x <= 1).all():
        raise ValueError("预测分数含缺失、无穷或超出[0,1]的值")
    if set(scores["model"]) != set(MODEL_ORDER) or set(scores["fold"]) != {"validation", "test"}:
        raise ValueError("预测模型或分段集合不完整")
    for fold in ["validation", "test"]:
        ids = split.loc[split["fold"].eq(fold), "row_id"].tolist()
        for model in MODEL_ORDER:
            actual = scores.loc[scores["fold"].eq(fold) & scores["model"].eq(model), "row_id"].tolist()
            if actual != ids:
                raise ValueError(f"预测行号覆盖不一致：{fold}/{model}")


def write_b_markdown(path, content):
    """Preserve previous Markdown as a comment, with an exact backup made beforehand."""
    begin = "<!-- B01_ORIGINAL_MARKDOWN_BEGIN\n"
    end = "\nB01_ORIGINAL_MARKDOWN_END -->\n"
    if path.exists():
        old = path.read_text(encoding="utf-8")
        if old.startswith(begin) and end in old:
            prefix = old.split(end, 1)[0] + end
        elif "-->" not in old:
            prefix = begin + old + end
        else:
            raise ValueError("旧Markdown含其他注释，已保留备份；需核对后再生成")
    else:
        prefix = begin + "本次新生成，无被替换旧稿。" + end
    path.write_text(prefix + "\n" + content, encoding="utf-8")


def compare_legacy_scores():
    """Compare saved risk values only; never compute Test performance or read Test y."""
    reference = LEGACY_OUTPUT / "scores.csv"
    result = {"reference_commit": GITHUB_BASE_COMMIT, "test_labels_read": False,
              "status": "reference_not_available", "rows": [],
              "interpretation": "Differences are diagnostic; candidate scores do not replace the original frozen results."}
    if not reference.is_file():
        return result
    result["reference_fingerprint"] = file_evidence(reference)
    if result["reference_fingerprint"]["lf_normalized_sha256"] != GITHUB_NORMALIZED_HASHES["outputs/scores.csv"]:
        result["status"] = "reference_not_confirmed_as_original_github"
        return result
    old = pd.read_csv(reference)
    new = pd.read_csv(OUTPUT / "scores.csv")
    aligned = new.merge(old, on=["row_id", "fold", "model"], suffixes=("_candidate", "_original"), validate="one_to_one")
    if len(aligned) != len(old) or len(new) != len(old):
        raise ValueError("新旧预测键不一致，不能进行逐行比较")
    for (model, fold), group in aligned.groupby(["model", "fold"], sort=True):
        diff = (group["risk_candidate"] - group["risk_original"]).abs()
        result["rows"].append({"model": model, "fold": fold, "rows": len(group),
                               "different_risk_rows": int(diff.ne(0).sum()),
                               "max_abs_risk_difference": float(diff.max())})
    result["exact_numeric_prediction_match"] = all(row["different_risk_rows"] == 0 for row in result["rows"])
    result["status"] = "exact_prediction_match" if result["exact_numeric_prediction_match"] else "prediction_differences_recorded"
    result["historical_training_environment_recovered"] = False
    return result


def write_run_manifest(environment, inputs, split, selected, config):
    """Publish provenance for a complete candidate run, not a new project standard."""
    if inspect_inputs() != inputs:
        raise RuntimeError("训练期间输入或源码发生变化，拒绝将结果标为完整候选")
    comparison = compare_legacy_scores()
    comparison_path = OUTPUT / "B_legacy_comparison.json"
    comparison_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    generated = ["scores.csv", "T2_模型对比表.csv", "T2_模型对比表.md", "model_selection_pool.csv",
                 "logistic_coefficients.csv", "B_legacy_comparison.json"]
    manifest = {
        "schema_version": "B01-1.0", "stage": "B01", "generated_at": datetime.now().isoformat(timespec="seconds"),
        "release_status": "candidate_only_not_C_frozen", "environment": environment,
        "input_fingerprints": inputs,
        "protocol": {"split_id": config["split_id"], "fold_rows": split["fold"].value_counts().to_dict(),
                     "seed": SEED, "positive_label": POSITIVE_LABEL, "selection_fold": "validation",
                     "test_labels_used_by_B": False, "rank_rule": "risk descending; row_id ascending",
                     "validation_budget_fraction": 0.30, "model_order": list(MODEL_ORDER),
                     "feature_sets": config["feature_sets"]},
        "selected_parameters": {name: params for name, (_, params, _) in selected.items()},
        "output_fingerprints": {name: file_evidence(OUTPUT / name) for name in generated},
        "legacy_comparison_status": comparison["status"],
        "historical_exact_retraining_reproduction": "not_established_from_available_github_environment_information",
        "original_frozen_scores_replaced": False,
    }
    (OUTPUT / "B_run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[B01_LEGACY] {comparison['status']}；只记录差异，不改原冻结结果")
    print(f"[B01_PASS] 候选与追溯记录完整：{OUTPUT}；历史训练环境精确复原尚未证实")

# [B01-04 新增结束]

def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, dict]:
    if not RAW.exists():
        raise FileNotFoundError(f"找不到原始数据：{RAW}")
    if not SPLIT.exists():
        raise FileNotFoundError(f"找不到 Part A 冻结切分：{SPLIT}")
    if not CONFIG.exists():
        raise FileNotFoundError(f"找不到特征配置：{CONFIG}")

    split = pd.read_csv(SPLIT)
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

# [B01-05 新增] 避免配置与实际执行静默不一致，不重新选种子
    if split.columns.tolist() != ["row_id", "fold"] or split.isna().any().any():
        raise ValueError("切分字段必须为row_id,fold且不含缺失")
    if not pd.api.types.is_integer_dtype(split["row_id"]) or split["row_id"].duplicated().any():
        raise ValueError("切分row_id必须为无重复整数")
    if config.get("seed") != SEED or config.get("positive_label") != POSITIVE_LABEL or config.get("label") != "y" or config.get("row_id") != "row_id":
        raise ValueError("配置种子、正类、标签或行号与GitHub既定协议不一致")
# [B01-05 新增结束]

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

# [B01-06 新增] 特征清单先检查重复与结构，保留实际字段方案
    if not isinstance(features, list) or len(features) != len(set(features)):
        raise ValueError(f"{feature_set}必须是无重复字段的列表")
# [B01-06 新增结束]
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


# [B01-07 原代码开始] 训练前核对GitHub输入与环境，明确候选输出位置
# def main() -> None:
#     data, split, labels, config = load_inputs()
# [B01-07 原代码结束]
# [B01-07 修订代码开始]
def main() -> None:
    global OUTPUT
    args = parse_b01_arguments()
    OUTPUT = args.output_root / "outputs"
    environment = inspect_github_environment()
    input_fingerprints = inspect_inputs()
    data, split, labels, config = load_inputs()
# [B01-07 修订代码结束]
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

# [B01-08 原代码开始] 覆盖候选生成件之前保存原文件，不触及根目录冻结产物
#     OUTPUT.mkdir(parents=True, exist_ok=True)
# [B01-08 原代码结束]
# [B01-08 修订代码开始]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    archive_b_outputs()
# [B01-08 修订代码结束]
    scores = pd.concat(score_frames, ignore_index=True)
    scores["model"] = pd.Categorical(scores["model"], categories=MODEL_ORDER, ordered=True)
    scores["fold"] = pd.Categorical(
        scores["fold"], categories=["validation", "test"], ordered=True
    )
    scores = scores.sort_values(["fold", "model", "row_id"])
    scores["model"] = scores["model"].astype(str)
    scores["fold"] = scores["fold"].astype(str)
# [B01-09 原代码开始] 输出前校验完整性，保留原10位有效数字导出格式
#     scores.to_csv(OUTPUT / "scores.csv", index=False, float_format="%.10g")
# [B01-09 原代码结束]
# [B01-09 修订代码开始]
    validate_candidate_scores(scores, split)
    scores.to_csv(OUTPUT / "scores.csv", index=False, float_format="%.10g")
# [B01-09 修订代码结束]

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
# [B01-10 原代码开始] Markdown保留旧文注释，结构化输出则保留有效格式并备份
#     (OUTPUT / "T2_模型对比表.md").write_text("\n".join(lines), encoding="utf-8")
# [B01-10 原代码结束]
# [B01-10 修订代码开始]
    write_b_markdown(OUTPUT / "T2_模型对比表.md", "\n".join(lines))
# [B01-10 修订代码结束]
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

# [B01-11 新增] 完整输出后生成可核验的运行清单与原预测差异记录
    write_run_manifest(environment, input_fingerprints, split, selected, config)
# [B01-11 新增结束]


if __name__ == "__main__":
    main()
