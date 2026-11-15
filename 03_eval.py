# -*- coding: utf-8 -*-
"""
INT6163 高级数据分析 · 第8组 · Part C：实验设计与评价 + 数字守门
=================================================================
运行方式（在项目根目录打开命令行）：
    python 03_eval.py

设计原则：
1. Test 标签只在本脚本中读取一次，用于最终评价，不参与 A 的切分或 B 的选模。
2. 所有模型使用同一个 K、同一个排序规则和同一套指标。
3. 业务增益相对简单规则基线 poutcome_success 计算；no_skill 只作对照。
4. 所有最终数字统一写入 outputs/metrics.json，写完后锁定只读。

产物：
    outputs/metrics.json
    outputs/T3_误差切片表.md
    outputs/T4_duration消融表.md
    outputs/T5_数字核对表.md
    outputs/C_测试集模型比较表.md
    figures/F3_PR曲线.png
    figures/F4_预算收益曲线.png
"""

from __future__ import annotations

import importlib.util
import json
import os
from datetime import datetime
from math import ceil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_curve


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "bank-additional-full.csv"
SPLIT = ROOT / "outputs" / "split_v1.csv"
SCORES = ROOT / "outputs" / "scores.csv"
A_SUMMARY = ROOT / "outputs" / "A_summary.json"
T2 = ROOT / "outputs" / "T2_模型对比表.csv"
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
METRICS = OUT / "metrics.json"

POSITIVE_LABEL = "yes"
NEGATIVE_LABEL = "no"
MAIN_MODEL = "logistic"
RULE_BASELINE = "poutcome_success"
NO_SKILL = "no_skill"
ABLATION = "logistic_duration_ablation"
WORK_FRACTION = 0.30
SENSITIVITY_FRACTIONS = tuple(x / 100 for x in range(10, 101, 10))
MIN_SLICE_N = 100
MODEL_ORDER = (
    NO_SKILL,
    RULE_BASELINE,
    MAIN_MODEL,
    "logistic_macro_control",
    "decision_tree",
    "random_forest",
    ABLATION,
)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9


def load_split() -> pd.DataFrame:
    if not SPLIT.exists():
        raise FileNotFoundError(f"缺少 Part A 冻结切分：{SPLIT}")
    split = pd.read_csv(SPLIT)
    if split.columns.tolist() != ["row_id", "fold"]:
        raise ValueError("split_v1.csv 必须只有 row_id, fold 两列")
    test_rows = split.loc[split["fold"].eq("test"), "row_id"].tolist()
    if len(test_rows) != 8238 or test_rows != list(range(32950, 41188)):
        raise ValueError("split_v1.csv 与 A 的冻结 Test 段不一致")
    return split


def load_test_labels() -> pd.DataFrame:
    # 唯一一次读取 Test 标签：只给 C 的最终评价使用。
    labels = pd.read_csv(
        RAW,
        sep=";",
        usecols=[
            "y",
            "poutcome",
            "contact",
            "job",
            "campaign",
            "previous",
            "pdays",
        ],
    )
    labels.insert(0, "row_id", range(len(labels)))
    test = labels.loc[labels["row_id"].between(32950, 41187)].copy()
    if len(test) != 8238:
        raise ValueError("Test 标签行数应为 8238")
    if not set(test["y"].unique()).issubset({POSITIVE_LABEL, NEGATIVE_LABEL}):
        raise ValueError("Test 标签包含非预期类别")
    return test


def load_scores(test_labels: pd.DataFrame) -> pd.DataFrame:
    scores = pd.read_csv(SCORES)
    test_scores = scores.loc[scores["fold"].eq("test")].copy()
    if set(test_scores["model"].unique()) != set(MODEL_ORDER):
        raise ValueError("scores.csv 的 Test 模型集合不符合 B 的冻结清单")
    counts = test_scores.groupby("model").size().to_dict()
    if counts != {model: len(test_labels) for model in MODEL_ORDER}:
        raise ValueError(f"Test 分数行数不一致：{counts}")

    expected_ids = test_labels["row_id"].tolist()
    for model in MODEL_ORDER:
        model_ids = test_scores.loc[test_scores["model"].eq(model), "row_id"].tolist()
        if model_ids != expected_ids:
            raise ValueError(f"{model} 的 Test row_id 与标签未逐行对齐")
    return test_scores


def ranked_frame(y_true: pd.Series, risk: pd.Series) -> pd.DataFrame:
    ranking = pd.DataFrame(
        {
            "row_id": y_true.index.to_numpy(dtype=int),
            "y_true": y_true.to_numpy(dtype=int),
            "risk": risk.to_numpy(dtype=float),
        }
    )
    return ranking.sort_values(
        ["risk", "row_id"], ascending=[False, True], kind="mergesort"
    ).reset_index(drop=True)


def top_k_metrics(y_true: pd.Series, risk: pd.Series, fraction: float) -> dict:
    n = len(y_true)
    k = ceil(n * fraction)
    ranking = ranked_frame(y_true, risk)
    selected = ranking.head(k)
    hits = int(selected["y_true"].sum())
    positives = int(y_true.sum())
    negatives = n - positives
    precision = hits / k
    recall = hits / positives if positives else 0.0
    threshold = float(ranking.iloc[k - 1]["risk"])
    tp = hits
    fp = k - tp
    fn = positives - tp
    tn = negatives - fp
    return {
        "contact_fraction": float(fraction),
        "k": k,
        "threshold_at_kth_risk": threshold,
        "hits_at_k": hits,
        "precision_at_k": precision,
        "recall_at_k": recall,
        "invalid_calls_at_k": fp,
        "missed_subscriptions_at_k": fn,
        "confusion_at_budget": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
    }


def full_metrics(y_true: pd.Series, risk: pd.Series, fraction: float) -> dict:
    top = top_k_metrics(y_true, risk, fraction)
    return {
        "pr_auc": float(average_precision_score(y_true, risk)),
        **top,
    }


def evaluate_models(test_labels: pd.DataFrame, scores: pd.DataFrame) -> dict:
    y = test_labels.set_index("row_id")["y"].eq(POSITIVE_LABEL).astype(int)
    result: dict[str, dict] = {}
    for model in MODEL_ORDER:
        risk = (
            scores.loc[scores["model"].eq(model)]
            .set_index("row_id")["risk"]
            .reindex(y.index)
        )
        if risk.isna().any():
            raise ValueError(f"{model} 存在无法对齐的风险分数")
        result[model] = full_metrics(y, risk, WORK_FRACTION)
    return result


def sensitivity_table(test_labels: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    y = test_labels.set_index("row_id")["y"].eq(POSITIVE_LABEL).astype(int)
    rows: list[dict] = []
    for model in (MAIN_MODEL, RULE_BASELINE, NO_SKILL):
        risk = (
            scores.loc[scores["model"].eq(model)]
            .set_index("row_id")["risk"]
            .reindex(y.index)
        )
        for fraction in SENSITIVITY_FRACTIONS:
            metrics = full_metrics(y, risk, fraction)
            rows.append(
                {
                    "model": model,
                    "contact_fraction": fraction,
                    "contacted": metrics["k"],
                    "hits": metrics["hits_at_k"],
                    "precision": metrics["precision_at_k"],
                    "recall": metrics["recall_at_k"],
                    "invalid_calls": metrics["invalid_calls_at_k"],
                    "missed_subscriptions": metrics["missed_subscriptions_at_k"],
                }
            )
    return pd.DataFrame(rows)


def business_summary(models: dict) -> dict:
    main = models[MAIN_MODEL]
    rule = models[RULE_BASELINE]
    no_skill = models[NO_SKILL]
    total_positive = main["hits_at_k"] + main["missed_subscriptions_at_k"]
    extra_vs_rule = main["hits_at_k"] - rule["hits_at_k"]
    invalid_avoided_vs_rule = rule["invalid_calls_at_k"] - main["invalid_calls_at_k"]
    extra_vs_no_skill = main["hits_at_k"] - no_skill["hits_at_k"]
    return {
        "primary_comparator": RULE_BASELINE,
        "definitions": {
            "extra_hits_vs_rule": "主模型@K命中数 - poutcome_success规则基线@K命中数",
            "invalid_calls_avoided_vs_rule": "规则基线@K的无效电话数 - 主模型@K的无效电话数",
            "missed_subscriptions_at_k": "Test真实订阅总数 - 主模型@K命中数",
            "extra_hits_vs_no_skill": "主模型@K命中数 - no_skill@K命中数（仅对照）",
        },
        "k": main["k"],
        "test_positive_rows": total_positive,
        "main_hits_at_k": main["hits_at_k"],
        "rule_baseline_hits_at_k": rule["hits_at_k"],
        "no_skill_hits_at_k": no_skill["hits_at_k"],
        "extra_hits_vs_rule": extra_vs_rule,
        "invalid_calls_avoided_vs_rule": invalid_avoided_vs_rule,
        "missed_subscriptions_at_k": main["missed_subscriptions_at_k"],
        "extra_hits_vs_no_skill": extra_vs_no_skill,
    }


def build_slice_frame(
    test_labels: pd.DataFrame, scores: pd.DataFrame, selected_model: str
) -> pd.DataFrame:
    model_scores = (
        scores.loc[scores["model"].eq(selected_model)]
        .set_index("row_id")["risk"]
        .reindex(test_labels["row_id"])
    )
    ranked = ranked_frame(
        test_labels.set_index("row_id")["y"].eq(POSITIVE_LABEL).astype(int),
        model_scores,
    )
    k = ceil(len(test_labels) * WORK_FRACTION)
    selected_ids = set(ranked.head(k)["row_id"].tolist())

    frame = test_labels.copy()
    frame["selected_at_k"] = frame["row_id"].isin(selected_ids)
    frame["is_positive"] = frame["y"].eq(POSITIVE_LABEL)

    def campaign_bucket(value: int) -> str:
        if value <= 1:
            return "1次"
        if value <= 3:
            return "2-3次"
        if value <= 6:
            return "4-6次"
        return "7次及以上"

    frame["campaign_bucket"] = frame["campaign"].map(campaign_bucket)
    dimensions = [
        ("poutcome", "上次活动结果", frame["poutcome"].astype(str)),
        ("contact", "联系方式", frame["contact"].astype(str)),
        ("job", "职业", frame["job"].astype(str)),
        ("campaign", "本轮联系次数", frame["campaign_bucket"]),
    ]
    rows: list[dict] = []
    for dimension, dimension_label, series in dimensions:
        for level, group in frame.groupby(series, dropna=False):
            tp = int((group["selected_at_k"] & group["is_positive"]).sum())
            fp = int((group["selected_at_k"] & ~group["is_positive"]).sum())
            fn = int((~group["selected_at_k"] & group["is_positive"]).sum())
            tn = int((~group["selected_at_k"] & ~group["is_positive"]).sum())
            positives = tp + fn
            negatives = fp + tn
            rows.append(
                {
                    "dimension": dimension,
                    "dimension_label": dimension_label,
                    "level": str(level),
                    "sample_n": len(group),
                    "positives": positives,
                    "selected_n": tp + fp,
                    "tp": tp,
                    "fp": fp,
                    "fn": fn,
                    "tn": tn,
                    "recall": tp / positives if positives else 0.0,
                    "false_positive_rate": fp / negatives if negatives else 0.0,
                    "precision": tp / (tp + fp) if tp + fp else 0.0,
                    "small_sample_flag": len(group) < MIN_SLICE_N,
                }
            )
    return pd.DataFrame(rows)


def select_failure_cases(
    test_labels: pd.DataFrame, scores: pd.DataFrame
) -> pd.DataFrame:
    model_scores = (
        scores.loc[scores["model"].eq(MAIN_MODEL)]
        .set_index("row_id")["risk"]
        .reindex(test_labels["row_id"])
    )
    frame = test_labels.copy()
    frame["risk"] = model_scores.to_numpy()
    frame["is_positive"] = frame["y"].eq(POSITIVE_LABEL)
    ranked = frame.sort_values(["risk", "row_id"], ascending=[False, True])
    k = ceil(len(frame) * WORK_FRACTION)
    selected_ids = set(ranked.head(k)["row_id"].tolist())
    frame["selected_at_k"] = frame["row_id"].isin(selected_ids)

    missed = (
        frame.loc[frame["is_positive"] & ~frame["selected_at_k"]]
        .sort_values(["risk", "row_id"], ascending=[False, True])
        .head(2)
        .copy()
    )
    false_alarm = (
        frame.loc[~frame["is_positive"] & frame["selected_at_k"]]
        .sort_values(["risk", "row_id"], ascending=[False, True])
        .head(1)
        .copy()
    )
    cases = pd.concat([missed, false_alarm], ignore_index=True)
    case_types = ["漏报：真实订阅但未进名单", "漏报：真实订阅但未进名单", "误报：进入名单但未订阅"]
    cases["case_type"] = case_types
    cases["risk"] = cases["risk"].round(6)
    return cases[
        [
            "case_type",
            "row_id",
            "risk",
            "selected_at_k",
            "poutcome",
            "contact",
            "job",
            "campaign",
            "previous",
            "pdays",
            "y",
        ]
    ]


def write_model_table(models: dict) -> None:
    lines = [
        "# C 测试集模型比较表（最终评价，一次性）",
        "",
        "> Test 标签仅在 `03_eval.py` 的最终评价中读取一次；本表所有模型共用 "
        "`K=ceil(30%×8,238)=2,472`，分数并列按 `row_id` 升序。",
        "",
        "| 模型 | Test PR-AUC | Precision@K | Recall@K | 命中数@K | 无效电话@K | 漏报订阅@K |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model in MODEL_ORDER:
        row = models[model]
        lines.append(
            f"| {model} | {row['pr_auc']:.6f} | {row['precision_at_k']:.6f} | "
            f"{row['recall_at_k']:.6f} | {row['hits_at_k']} | "
            f"{row['invalid_calls_at_k']} | {row['missed_subscriptions_at_k']} |"
        )
    lines.extend(
        [
            "",
            "说明：`no_skill` 的分数全为 0，名单只能按 row_id 决胜，因此仅作对照，不能代表有意义的业务排序。"
            "`logistic_macro_control` 只检验宏观指标的时间漂移，"
            "`logistic_duration_ablation` 只检验 duration 泄漏，二者均非主模型。",
            "",
        ]
    )
    (OUT / "C_测试集模型比较表.md").write_text("\n".join(lines), encoding="utf-8")


def write_slice_table(slices: pd.DataFrame, cases: pd.DataFrame) -> None:
    lines = [
        "# T3 误差切片表（Test，主模型 logistic，K=2,472）",
        "",
        f"> 切片用于检查主模型在哪类客群失灵，不用于决定“只联系哪一类人”。"
        f"样本量小于 {MIN_SLICE_N} 的分桶标为“小样本”，解释时需谨慎。",
        "> 召回率 = TP/(TP+FN)；误报率 = FP/(FP+TN)；样本口径均为 Test 全量 8,238 行。",
        "",
        "| 维度 | 分桶 | 样本量 | 真实订阅数 | 名单人数 | TP | FP | FN | TN | 召回率 | 误报率 | 切片精度 | 标记 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in slices.itertuples(index=False):
        flag = "小样本" if row.small_sample_flag else ""
        lines.append(
            f"| {row.dimension_label} | {row.level} | {row.sample_n} | {row.positives} | "
            f"{row.selected_n} | {row.tp} | {row.fp} | {row.fn} | {row.tn} | "
            f"{row.recall:.4f} | {row.false_positive_rate:.4f} | "
            f"{row.precision:.4f} | {flag} |"
        )

    lines.extend(
        [
            "",
            "## 切片读数",
            "",
            "- `poutcome=failure` 的召回率仅 14.37%（480 个真实订阅中漏掉 411 个），是当前名单最明显的失灵区；不能据此永久排除该客群，反而应对高 `previous` 且多次失败者设联系上限并保留人工复核。",
            "- `campaign=4-6次` 与 `7次及以上` 的召回率分别为 29.74% 和 33.33%，低于 1-3 次组，说明反复外呼客群需要单独审计。",
            "- `job=blue-collar` 与 `housemaid` 的召回率较低（31.48%、28.36%），但职业是敏感属性，只能用于解释误差与人工复核，不能变成单一排除规则。",
            "- `job=unknown` 只有 64 行，虽显示召回率 36.36%，但已标为小样本，不作为稳定结论。",

            "## 失败案例",
            "",
            "| 类型 | row_id | 风险分 | 是否进名单 | poutcome | contact | job | campaign | previous | pdays | y |",
            "|---|---:|---:|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in cases.itertuples(index=False):
        lines.append(
            f"| {row.case_type} | {row.row_id} | {row.risk:.6f} | "
            f"{'是' if row.selected_at_k else '否'} | {row.poutcome} | {row.contact} | "
            f"{row.job} | {row.campaign} | {row.previous} | {row.pdays} | {row.y} |"
        )
    lines.extend(
        [
            "",
            "案例解释口径：漏报案例是“真实订阅但未进入预算名单”，误报案例是“进入名单但没有订阅”。"
            "两者都应回到具体切片与行动规则中解释，不能把单一案例当成模型总体结论。",
            "",
        ]
    )
    (OUT / "T3_误差切片表.md").write_text("\n".join(lines), encoding="utf-8")


def write_ablation_table(models: dict, validation: pd.DataFrame) -> None:
    validation_main = validation.loc[validation["model"].eq(MAIN_MODEL)].iloc[0]
    validation_ablation = validation.loc[validation["model"].eq(ABLATION)].iloc[0]
    main = models[MAIN_MODEL]
    ablated = models[ABLATION]
    rows = [
        (
            "Validation",
            float(validation_main["validation_pr_auc"]),
            int(validation_main["hits_at_30pct"]),
            float(validation_ablation["validation_pr_auc"]),
            int(validation_ablation["hits_at_30pct"]),
        ),
        (
            "Test",
            main["pr_auc"],
            main["hits_at_k"],
            ablated["pr_auc"],
            ablated["hits_at_k"],
        ),
    ]
    lines = [
        "# T4 duration 泄漏消融表",
        "",
        "> 主模型与消融模型只差 `duration`。消融模型仅用于量化泄漏，不得作为最终模型。",
        "",
        "| 数据段 | 不含 duration PR-AUC | 不含 duration 命中数 | 含 duration PR-AUC | 含 duration 命中数 | PR-AUC 绝对差 | 命中数绝对差 | PR-AUC 相对膨胀 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for fold, main_ap, main_hits, duration_ap, duration_hits in rows:
        ap_diff = duration_ap - main_ap
        hits_diff = duration_hits - main_hits
        relative = ap_diff / main_ap if main_ap else 0.0
        lines.append(
            f"| {fold} | {main_ap:.6f} | {main_hits} | {duration_ap:.6f} | "
            f"{duration_hits} | {ap_diff:+.6f} | {hits_diff:+d} | {relative:+.2%} |"
        )
    lines.extend(
        [
            "",
            "结论：加入 `duration` 后指标明显变好，但这不表示模型更有业务价值，而是因为该字段在电话结束后才可得。"
            "UCI 官方说明原文：\"should be discarded if the intention is to have a realistic predictive model\"。",
            "",
            "因此，最终模型必须使用不含 `duration` 的 `logistic`；含 `duration` 版本只保留为泄漏证据。",
            "",
        ]
    )
    (OUT / "T4_duration消融表.md").write_text("\n".join(lines), encoding="utf-8")


def write_t5(models: dict, business: dict, metrics: dict) -> None:
    main = models[MAIN_MODEL]
    ablation = models[ABLATION]
    rows = [
        ("Test 行数", metrics["protocol"]["test_rows"], "protocol.test_rows"),
        ("Test 真实订阅数", metrics["protocol"]["test_positive_rows"], "protocol.test_positive_rows"),
        ("主工作点 K", metrics["protocol"]["k_at_30pct"], "protocol.k_at_30pct"),
        ("主模型 Test PR-AUC", f"{main['pr_auc']:.6f}", "models.logistic.pr_auc"),
        ("主模型 Precision@K", f"{main['precision_at_k']:.6f}", "models.logistic.precision_at_k"),
        ("主模型 Recall@K", f"{main['recall_at_k']:.6f}", "models.logistic.recall_at_k"),
        ("主模型命中数@K", main["hits_at_k"], "models.logistic.hits_at_k"),
        ("相对规则基线多命中订阅", business["extra_hits_vs_rule"], "business.extra_hits_vs_rule"),
        (
            "相对规则基线少打无效电话",
            business["invalid_calls_avoided_vs_rule"],
            "business.invalid_calls_avoided_vs_rule",
        ),
        ("预算名单漏报订阅", business["missed_subscriptions_at_k"], "business.missed_subscriptions_at_k"),
        (
            "含 duration 的 Test PR-AUC",
            f"{ablation['pr_auc']:.6f}",
            "models.logistic_duration_ablation.pr_auc",
        ),
        (
            "duration 造成的 PR-AUC 绝对差",
            f"{ablation['pr_auc'] - main['pr_auc']:+.6f}",
            "ablation.test_pr_auc_absolute_difference",
        ),
    ]
    lines = [
        "# T5 数字核对表",
        "",
        "> 唯一数字真值源为 `outputs/metrics.json`。报告与 PPT 只能引用表中的 json 键名；"
        "页码由 D / E 回填，页码未填前不得宣称整稿数字已核对。",
        "",
        "| 指标 | 数字 | metrics.json 键名 | 报告/PPT 页码 |",
        "|---|---:|---|---|",
    ]
    for label, value, key in rows:
        lines.append(f"| {label} | {value} | `{key}` | 待 D/E 回填 |")
    lines.extend(
        [
            "",
            "锁定状态：`outputs/metrics.json` 由 C 生成后设为只读；E 只转录核对，不修改口径或数值。",
            "",
        ]
    )
    (OUT / "T5_数字核对表.md").write_text("\n".join(lines), encoding="utf-8")


def plot_pr_curves(test_labels: pd.DataFrame, scores: pd.DataFrame) -> None:
    y = test_labels.set_index("row_id")["y"].eq(POSITIVE_LABEL).astype(int)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    colors = {
        MAIN_MODEL: "#185FA5",
        RULE_BASELINE: "#0F6E56",
        NO_SKILL: "#777777",
        ABLATION: "#A32D2D",
    }
    labels = {
        MAIN_MODEL: "Logistic（主模型）",
        RULE_BASELINE: "poutcome_success 规则",
        NO_SKILL: "全猜不订阅",
        ABLATION: "Logistic + duration（仅消融）",
    }
    for model in (MAIN_MODEL, RULE_BASELINE, NO_SKILL, ABLATION):
        risk = (
            scores.loc[scores["model"].eq(model)]
            .set_index("row_id")["risk"]
            .reindex(y.index)
        )
        precision, recall, _ = precision_recall_curve(y, risk)
        ap = average_precision_score(y, risk)
        ax.plot(
            recall,
            precision,
            label=f"{labels[model]}  AP={ap:.3f}",
            color=colors[model],
            linewidth=2 if model == MAIN_MODEL else 1.4,
        )
    prevalence = y.mean()
    ax.axhline(
        prevalence,
        linestyle="--",
        linewidth=1,
        color="#A32D2D",
        label=f"Test 正类率 {prevalence:.1%}",
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("F3  Test PR 曲线：名单排序能力")
    ax.grid(alpha=0.22)
    ax.legend(frameon=False, fontsize=8.2, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG / "F3_PR曲线.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_budget_curve(sensitivity: pd.DataFrame) -> None:
    labels = {
        MAIN_MODEL: "Logistic（主模型）",
        RULE_BASELINE: "poutcome_success 规则",
        NO_SKILL: "全猜不订阅",
    }
    colors = {MAIN_MODEL: "#185FA5", RULE_BASELINE: "#0F6E56", NO_SKILL: "#777777"}
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for model in (MAIN_MODEL, RULE_BASELINE, NO_SKILL):
        part = sensitivity.loc[sensitivity["model"].eq(model)]
        ax.plot(
            part["contact_fraction"] * 100,
            part["hits"],
            marker="o",
            markersize=4,
            linewidth=2 if model == MAIN_MODEL else 1.5,
            color=colors[model],
            label=labels[model],
        )
    main_at_30 = sensitivity.loc[
        sensitivity["model"].eq(MAIN_MODEL)
        & np.isclose(sensitivity["contact_fraction"], WORK_FRACTION)
    ].iloc[0]
    ax.axvline(30, color="#A32D2D", linestyle="--", linewidth=1)
    ax.scatter(
        [30],
        [main_at_30["hits"]],
        s=55,
        color="#A32D2D",
        zorder=5,
    )
    ax.annotate(
        f"主工作点 30%: {int(main_at_30['hits'])} 次命中",
        xy=(30, main_at_30["hits"]),
        xytext=(36, main_at_30["hits"] - 120),
        arrowprops={"arrowstyle": "->", "color": "#A32D2D", "lw": 1},
        fontsize=9,
        color="#A32D2D",
    )
    ax.set_xlabel("联系预算占 Test 名单比例 (%)")
    ax.set_ylabel("名单中命中的真实订阅数")
    ax.set_title("F4  预算-收益曲线：同样名单规模下命中多少订阅")
    ax.set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    ax.grid(alpha=0.22)
    ax.legend(frameon=False, fontsize=8.4, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "F4_预算收益曲线.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_metrics_json(metrics: dict) -> None:
    if METRICS.exists():
        os.chmod(METRICS, 0o666)
    METRICS.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.chmod(METRICS, 0o444)


def build_metrics(
    models: dict,
    business: dict,
    slices: pd.DataFrame,
    sensitivity: pd.DataFrame,
    a_summary: dict,
    validation: pd.DataFrame,
) -> dict:
    main = models[MAIN_MODEL]
    ablation = models[ABLATION]
    return {
        "schema_version": "1.0",
        "generated_by": "C",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_files": {
            "split": "outputs/split_v1.csv",
            "scores": "outputs/scores.csv",
            "labels": "data/raw/bank-additional-full.csv",
            "validation_model_comparison": "outputs/T2_模型对比表.csv",
            "part_a_summary": "outputs/A_summary.json",
        },
        "protocol": {
            "split_id": a_summary["split_id"],
            "split_method": a_summary["data"]["split_method"],
            "label": "y",
            "positive_label": POSITIVE_LABEL,
            "test_row_id_min": 32950,
            "test_row_id_max": 41187,
            "test_rows": int(a_summary["data"]["n_test"]),
            "test_positive_rows": int(a_summary["data"]["n_positive_by_fold"]["test"]),
            "test_positive_rate": float(a_summary["data"]["positive_rate_by_fold"]["test"]),
            "work_fraction": WORK_FRACTION,
            "k_at_30pct": main["k"],
            "ranking_rule": "risk descending; row_id ascending as deterministic tie-breaker",
            "k_rule": "ceil(work_fraction * test_rows)",
            "test_used_for_final_evaluation_only": True,
            "test_label_read_location": "03_eval.py / load_test_labels()",
        },
        "selected_model": MAIN_MODEL,
        "models": models,
        "business": business,
        "ablation": {
            "compared_models": [MAIN_MODEL, ABLATION],
            "test_pr_auc_main": main["pr_auc"],
            "test_pr_auc_with_duration": ablation["pr_auc"],
            "test_pr_auc_absolute_difference": ablation["pr_auc"] - main["pr_auc"],
            "test_pr_auc_relative_inflation": (
                (ablation["pr_auc"] - main["pr_auc"]) / main["pr_auc"]
            ),
            "test_hits_main": main["hits_at_k"],
            "test_hits_with_duration": ablation["hits_at_k"],
            "test_hits_absolute_difference": ablation["hits_at_k"] - main["hits_at_k"],
            "validation_pr_auc_main": float(
                validation.loc[validation["model"].eq(MAIN_MODEL), "validation_pr_auc"].iloc[0]
            ),
            "validation_pr_auc_with_duration": float(
                validation.loc[validation["model"].eq(ABLATION), "validation_pr_auc"].iloc[0]
            ),
            "uci_decision": (
                "duration should be discarded if the intention is to have a realistic predictive model"
            ),
        },
        "error_slices": {
            "dimensions": ["poutcome", "contact", "job", "campaign_bucket"],
            "minimum_reported_slice_n": MIN_SLICE_N,
            "rows": int(len(slices)),
            "small_sample_rows": int(slices["small_sample_flag"].sum()),
            "table": "outputs/T3_误差切片表.md",
        },
        "sensitivity": {
            "fractions": list(SENSITIVITY_FRACTIONS),
            "models": [MAIN_MODEL, RULE_BASELINE, NO_SKILL],
            "rows": int(len(sensitivity)),
            "interpretation": "K changes across fractions; 30% is the primary budget, others are sensitivity only.",
        },
        "artifacts": {
            "pr_curve": "figures/F3_PR曲线.png",
            "budget_curve": "figures/F4_预算收益曲线.png",
            "slice_table": "outputs/T3_误差切片表.md",
            "duration_ablation_table": "outputs/T4_duration消融表.md",
            "number_audit_table": "outputs/T5_数字核对表.md",
            "model_comparison_table": "outputs/C_测试集模型比较表.md",
        },
        "guardrails": {
            "single_source_of_truth": "outputs/metrics.json",
            "metrics_json_locked_read_only": True,
            "no_causal_claim": True,
            "no_uplift_claim": True,
            "does_not_claim_increase_subscription_rate": True,
            "does_not_deploy_or_call_customers": True,
            "sensitive_attributes_not_used_as_single_contact_rule": True,
            "test_metrics_not_used_for_model_selection": True,
            "duration_ablation_not_used_as_main_model": True,
            "limitations": [
                "Historical replay only; no untreated control group.",
                "Observational associations, not causal effects.",
                "Performance reflects one chronological Test period and should not be generalized across banks or periods.",
                "The Test positive rate is 30.83%, materially higher than Train 4.81%, so absolute hit counts must not be attributed to the model alone.",
            ],
        },
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    for required in (A_SUMMARY, T2):
        if not required.exists():
            raise FileNotFoundError(f"缺少 Part A/B 产物：{required}")

    split = load_split()
    test_labels = load_test_labels()
    scores = load_scores(test_labels)
    a_summary = json.loads(A_SUMMARY.read_text(encoding="utf-8"))
    validation = pd.read_csv(T2)
    models = evaluate_models(test_labels, scores)
    business = business_summary(models)
    slices = build_slice_frame(test_labels, scores, MAIN_MODEL)
    cases = select_failure_cases(test_labels, scores)
    sensitivity = sensitivity_table(test_labels, scores)
    metrics = build_metrics(
        models, business, slices, sensitivity, a_summary, validation
    )

    write_model_table(models)
    write_slice_table(slices, cases)
    write_ablation_table(models, validation)
    write_t5(models, business, metrics)
    plot_pr_curves(test_labels, scores)
    plot_budget_curve(sensitivity)
    write_metrics_json(metrics)

    print("[协议] Test 8,238 行；真实订阅 2,540；K=2,472；row_id 升序稳定决胜")
    print(f"[主模型] PR-AUC={models[MAIN_MODEL]['pr_auc']:.6f}；"
          f"命中={models[MAIN_MODEL]['hits_at_k']}；"
          f"Precision@K={models[MAIN_MODEL]['precision_at_k']:.6f}；"
          f"Recall@K={models[MAIN_MODEL]['recall_at_k']:.6f}")
    print(f"[业务] 相对规则基线多命中 {business['extra_hits_vs_rule']}；"
          f"少打无效电话 {business['invalid_calls_avoided_vs_rule']}；"
          f"预算名单漏报 {business['missed_subscriptions_at_k']}")
    print(f"[消融] 不含 duration AP={models[MAIN_MODEL]['pr_auc']:.6f}；"
          f"含 duration AP={models[ABLATION]['pr_auc']:.6f}")
    print(f"[完成] {METRICS}（只读锁定）")
    print(f"[完成] {OUT / 'T3_误差切片表.md'}")
    print(f"[完成] {OUT / 'T4_duration消融表.md'}")
    print(f"[完成] {OUT / 'T5_数字核对表.md'}")
    print(f"[完成] {FIG / 'F3_PR曲线.png'}")
    print(f"[完成] {FIG / 'F4_预算收益曲线.png'}")


if __name__ == "__main__":
    main()
