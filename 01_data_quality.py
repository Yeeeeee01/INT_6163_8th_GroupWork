# -*- coding: utf-8 -*-
"""
INT6163 高级数据分析 · 第8组 · Part A：问题界定与数据质量
=========================================================
运行方式（在本文件所在目录打开命令行）：
    python 01_data_quality.py

作用：一次性产出 Part A 的全部交付物
    data/README_data.md          数据说明（问题陈述五字段 / 21 列字典 / 来源许可 / 隐私）
    outputs/split_v1.csv         按行序 60/20/20 的切分（row_id, fold），只生成一次
    outputs/data_dictionary.csv  21 列数据字典（机器可读）
    outputs/T1_数据质量表.md      数据质量表 T1
    outputs/A_summary.json       实测数字汇总，供 C 填 metrics.json
    figures/F1_通话前后字段分界图.png
    figures/F2_数据血缘图.png

依赖：pip install pandas matplotlib
注意：split_v1.csv 已存在时默认不重新生成（分工稿要求「只生成一次」）；
      确需重建时运行 python 01_data_quality.py --force
"""

# %% 1. 环境与路径
from pathlib import Path
import sys
import json
import hashlib
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 不弹窗口，直接存图
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "bank-additional-full.csv"
DATA_DIR = ROOT / "data"
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
for d in (DATA_DIR, OUT, FIG):
    d.mkdir(parents=True, exist_ok=True)

RAW_DOWNLOAD_DATE = "2026-11-11"   # 原始数据落到本项目的日期
SPLIT_ID = "v1"
SEP = ";"                          # UCI 官方说明：分号分隔
SEED_NOTE = "SEED=42 只用于 B 的模型随机性；A 的切分不用任何随机性"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

if not RAW.exists():
    raise FileNotFoundError(
        f"找不到原始数据：{RAW}\n"
        "请从 UCI #222 下载 bank+marketing.zip，解压出 "
        "bank-additional/bank-additional-full.csv 放到 data/raw/ 下。"
    )

# %% 2. 读取原始数据并留证（数据血缘的起点）
raw_bytes = RAW.read_bytes()
raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
raw_file_bytes = len(raw_bytes)

# 关键：sep=";"，用默认逗号会读成一整列
df = pd.read_csv(RAW, sep=SEP)
n_rows, n_columns = df.shape
print(f"[读取] {RAW.name}  {n_rows} 行 × {n_columns} 列  |  {raw_file_bytes:,} bytes")
print(f"[留证] sha256 = {raw_sha256}")

# %% 3. 清洗前统计：先看清楚数据长什么样
before = {
    "行数": n_rows,
    "列数": n_columns,
    "NaN 单元格数": int(df.isna().sum().sum()),
    "完全重复行数": int(df.duplicated().sum()),
}
unknown_before = (df == "unknown").sum()
unknown_before = unknown_before[unknown_before > 0].astype(int).to_dict()
n_pdays_999_before = int((df["pdays"] == 999).sum())
y_counts = df["y"].value_counts()
n_positive = int(y_counts.get("yes", 0))
n_negative = int(y_counts.get("no", 0))
positive_rate = n_positive / n_rows

print(f"[标签] y=yes {n_positive} 行（{positive_rate*100:.4f}%） / y=no {n_negative} 行")
print(f"[缺失] NaN {before['NaN 单元格数']} 个；unknown 分布：{unknown_before}")
print(f"[哨兵] pdays=999 共 {n_pdays_999_before} 行")
print(f"[重复] 完全重复行 {before['完全重复行数']} 行")

# %% 4. 清洗决定：本项目不删行、不改值，只做「显式标注」
# 理由：unknown 在 UCI 官方说明里被编码成一个真实类别，删除/插补会抹掉信息；
#       pdays=999 是「从未被联系」的哨兵，不是 999 天；
#       12 行完全重复，因数据没有客户 ID，无法判断是录入重复还是不同 campaign 的独立联系记录，保留。
# 因此清洗前后行数不变，变化的是「记录口径」——全部写进 T1，每个决定都能查到影响行数。
CLEAN_ACTIONS = [
    ("unknown 视为真实类别，不删除、不插补", "各列 unknown 计数（见 T1）", 0, "保留信息，避免伪造分布"),
    ("pdays=999 标记为「从未联系」哨兵，不改原值", f"{n_pdays_999_before} 行", 0, "不当 999 天解释，避免数值误导"),
    ("完全重复行保留", f"{before['完全重复行数']} 行", 0, "无客户 ID，无法判定是重复录入还是独立联系记录"),
    ("NaN 处理：无 NaN，无需处理", "0 个", 0, "缺失已被编码为 unknown"),
    ("duration / y 排除出主模型特征清单", "2 列", 0, "防泄漏；duration 只做含/不含消融，y 只作真值"),
    ("新增 row_id 作为行标识（不进模型）", f"{n_rows} 行", 0, "数据无客户 ID，需要稳定主键供切分与核对"),
]
after = {
    "行数": n_rows,
    "列数": n_columns,
    "NaN 单元格数": 0,
    "完全重复行数": before["完全重复行数"],
}
unknown_after = unknown_before.copy()
n_pdays_999_after = n_pdays_999_before

# %% 5. 21 列数据字典（语义 / 类型 / 是否通话前可知 / 是否进主模型）
# 「通话前可知」是本题防泄漏的核心判据：这一通电话拨出去之前拿不拿得到。
DICTS = [
    ("age", "客户年龄", "数值", "是", "是", ""),
    ("job", "职业类别", "类别", "是", "是", "含 unknown；敏感属性，不单独作为联系依据"),
    ("marital", "婚姻状况", "类别", "是", "是", "含 unknown；敏感属性"),
    ("education", "教育程度", "类别", "是", "是", "含 unknown；敏感属性"),
    ("default", "是否有信用违约记录", "类别", "是", "是", "unknown 8,597 行，保留为类别"),
    ("housing", "是否有住房贷款", "类别", "是", "是", "含 unknown"),
    ("loan", "是否有个人贷款", "类别", "是", "是", "含 unknown"),
    ("contact", "本次联系的通讯方式（手机/固话）", "类别", "是", "是", "仅作误差切片，不作主结论"),
    ("month", "本次联系所在月份", "类别", "是", "是", "仅作误差切片；无精确日期列"),
    ("day_of_week", "本次联系所在星期", "类别", "是", "是", "仅作误差切片；无精确日期列"),
    ("duration", "本次通话时长（秒）", "数值", "否", "否", "泄漏特征！通话结束才知道；UCI 官方要求剔除，仅用于含/不含消融"),
    ("campaign", "本轮 campaign 中该客户被联系次数（含本次）", "数值", "是", "是", "历史联系记录"),
    ("pdays", "距上次 campaign 联系的天数", "数值", "是", "是", "999 = 从未联系，哨兵值"),
    ("previous", "本轮之前该客户被联系次数", "数值", "是", "是", "历史联系记录"),
    ("poutcome", "上次营销活动结果", "类别", "是", "是", "简单规则基线按它排序"),
    ("emp.var.rate", "就业变动率（季度宏观指标）", "数值", "是", "是", "2008 金融危机期间可能漂移，时间留出能暴露"),
    ("cons.price.idx", "消费者价格指数（月度）", "数值", "是", "是", "宏观指标，同上"),
    ("cons.conf.idx", "消费者信心指数（月度）", "数值", "是", "是", "宏观指标，同上"),
    ("euribor3m", "欧元同业拆借 3 月利率（日度）", "数值", "是", "是", "宏观指标，同上"),
    ("nr.employed", "就业人数（季度）", "数值", "是", "是", "宏观指标，同上"),
    ("y", "客户是否订阅定期存款", "类别", "否", "否", "真值 / 标签，只用来对答案，绝不进模型"),
]
dict_df = pd.DataFrame(
    DICTS, columns=["字段名", "语义", "类型", "通话前可知", "进主模型", "备注"]
)
dict_df.insert(0, "序号", range(1, len(dict_df) + 1))
dict_df.to_csv(OUT / "data_dictionary.csv", index=False, encoding="utf-8-sig")

pre_cols = dict_df[dict_df["通话前可知"] == "是"]["字段名"].tolist()
post_cols = dict_df[dict_df["通话前可知"] == "否"]["字段名"].tolist()
print(f"[字典] 21 列已写出：通话前可知 {len(pre_cols)} 列 / 通话后或标签 {len(post_cols)} 列")

# %% 6. F1「通话前 / 通话后字段分界图」
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis("off")
ax.set_title("F1  通话前 / 通话后字段分界图", fontsize=16, pad=14)

def box(x, y, w, h, title, lines, face, edge):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.12",
                                facecolor=face, edgecolor=edge, linewidth=1.2))
    ax.text(x + w/2, y + h - 0.42, title, ha="center", va="center", fontsize=13, fontweight="bold")
    for i, line in enumerate(lines):
        ax.text(x + 0.25, y + h - 1.0 - i*0.42, line, ha="left", va="center", fontsize=9.6)

left_lines = [
    "客户属性：age / job / marital / education / default / housing / loan",
    "本次安排：contact / month / day_of_week（仅作误差切片）",
    "历史联系：campaign / pdays / previous / poutcome",
    "宏观指标：emp.var.rate / cons.price.idx / cons.conf.idx",
    "          euribor3m / nr.employed",
    f"共 {len(pre_cols)} 列 → 主模型可用",
]
right_lines = [
    "duration：通话时长（秒）",
    "y：是否订阅（真值）",
    "",
    "共 2 列，主模型不可用",
    "duration 仅用于消融",
    "y 只用于留出期对答案",
]
box(0.25, 1.15, 7.2, 5.1, "通话前就可知道", left_lines, "#E6F1FB", "#185FA5")
box(8.9, 1.15, 2.85, 5.1, "通话后才知道", right_lines, "#FCEBEB", "#A32D2D")
ax.annotate("", xy=(8.82, 3.7), xytext=(7.52, 3.7),
            arrowprops=dict(arrowstyle="->", lw=1.8, color="#5F5E5A"))
ax.text(8.17, 4.15, "这一通外呼", ha="center", va="center", fontsize=10.5, color="#444441")
ax.text(6.0, 0.55, "判据：这一通电话拨出去之前，这个信息拿不拿得到？拿不到就不能进主模型。",
        ha="center", fontsize=10, color="#444441")
fig.savefig(FIG / "F1_通话前后字段分界图.png", dpi=170, bbox_inches="tight")
plt.close(fig)

# %% 7. F2「数据血缘图」
fig, ax = plt.subplots(figsize=(12.8, 3.6))
ax.set_xlim(0, 13); ax.set_ylim(0, 3.6); ax.axis("off")
ax.set_title("F2  数据血缘图（来源 → 抽取 → 清洗 → 特征 → 切分）", fontsize=15, pad=12)
steps = [
    ("UCI #222 官方 zip", "bank+marketing.zip\nCC BY 4.0"),
    ("抽取原始表", "bank-additional-full.csv\n41,188 行 × 21 列"),
    ("质量检查 / 标注", "unknown、pdays=999\n重复行留证，不删行"),
    ("字段分界", "F1 分界图\n21 列数据字典"),
    ("按行序切分", "split_v1.csv\n60 / 20 / 20，只读"),
]
w, gap = 2.32, 0.28
for i, (title, sub) in enumerate(steps):
    x = 0.18 + i * (w + gap)
    ax.add_patch(FancyBboxPatch((x, 0.9), w, 1.65,
                                boxstyle="round,pad=0.08,rounding_size=0.1",
                                facecolor="#E1F5EE" if i < 4 else "#FAEEDA",
                                edgecolor="#0F6E56" if i < 4 else "#854F0B", linewidth=1.1))
    ax.text(x + w/2, 2.15, title, ha="center", fontsize=10.5, fontweight="bold")
    ax.text(x + w/2, 1.45, sub, ha="center", fontsize=8.6)
    if i < 4:
        ax.annotate("", xy=(x + w + gap - 0.04, 1.72), xytext=(x + w + 0.03, 1.72),
                    arrowprops=dict(arrowstyle="->", lw=1.4, color="#5F5E5A"))
ax.text(6.5, 0.4, "每一步的产物都落在 data/ 或 outputs/ 下；sha256 与实测统计见 A_summary.json / T1。",
        ha="center", fontsize=9.4, color="#444441")
fig.savefig(FIG / "F2_数据血缘图.png", dpi=170, bbox_inches="tight")
plt.close(fig)

# %% 7b. 加分图：按行序十等分的正类率（时间漂移的实证）
decile = []
for i in range(10):
    lo, hi = i * n_rows // 10, (i + 1) * n_rows // 10
    s = df.iloc[lo:hi]
    decile.append({
        "bucket": f"{i*10}-{(i+1)*10}%",
        "n": len(s),
        "n_positive": int((s["y"] == "yes").sum()),
        "positive_rate": round(float((s["y"] == "yes").mean()), 6),
    })
fig, ax = plt.subplots(figsize=(10, 4.2))
xs = [d["bucket"] for d in decile]
ys = [d["positive_rate"] * 100 for d in decile]
bars = ax.bar(xs, ys, color=["#B5D4F4"]*6 + ["#FAC775"]*2 + ["#F09595"]*2,
              edgecolor="#5F5E5A", linewidth=0.6)
ax.axhline(positive_rate * 100, ls="--", lw=1.2, color="#A32D2D",
           label=f"全量均值 {positive_rate*100:.2f}%")
for b, v in zip(bars, ys):
    ax.text(b.get_x() + b.get_width()/2, v + 0.8, f"{v:.1f}", ha="center", fontsize=9)
ax.set_ylabel("订阅率 (%)")
ax.set_xlabel("按原始行序十等分（≈ 时间先后）")
ax.set_title("F1b  时间漂移证据：越靠后的记录，真实订阅率越高", fontsize=14, pad=12)
ax.set_ylim(0, max(ys) * 1.18)
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
plt.xticks(rotation=30, ha="right", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "F1b_时间漂移证据.png", dpi=170, bbox_inches="tight")
plt.close(fig)
print("[图] F1 / F2 / F1b 已生成")

# %% 8. 按行序时间留出 60/20/20，生成一次 split_v1.csv
# 关键：数据本身已按日期排序（2008-05 → 2010-11），随机切分会「用未来预测过去」，所以绝不 shuffle。
n_train = int(n_rows * 0.60)
n_val = int(n_rows * 0.80) - n_train
n_test = n_rows - n_train - n_val
folds = (["train"] * n_train) + (["validation"] * n_val) + (["test"] * n_test)
split_path = OUT / "split_v1.csv"

if split_path.exists() and "--force" not in sys.argv:
    print(f"[切分] {split_path.name} 已存在，跳过生成（只生成一次；需重建请加 --force）")
else:
    split_df = pd.DataFrame({"row_id": range(n_rows), "fold": folds})
    split_df.to_csv(split_path, index=False, encoding="utf-8")
    print(f"[切分] 已写出 {split_path.name}：train {n_train} / validation {n_val} / test {n_test}")

split_df = pd.read_csv(split_path)
fold_counts = split_df["fold"].value_counts().to_dict()
pos_by_fold = {
    f: int(((df["y"] == "yes") & (split_df["fold"] == f)).sum())
    for f in ["train", "validation", "test"]
}
pos_rate_by_fold = {
    f: round(pos_by_fold[f] / fold_counts[f], 6)
    for f in ["train", "validation", "test"]
}
print(f"[切分] 三段行数 {fold_counts}；各段正类 {pos_by_fold}；各段正类率 {pos_rate_by_fold}")

# %% 9. 实测数字汇总 A_summary.json（供 C 填 metrics.json，禁止手抄）
summary = {
    "_README": "Part A 实测数字，全部由 01_data_quality.py 运行产出；C 填 metrics.json 时从此处取，禁止照抄公开资料参考值。",
    "split_id": SPLIT_ID,
    "generated_by": "A",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "data": {
        "n_rows": n_rows,
        "n_columns": n_columns,
        "n_positive": n_positive,
        "n_negative": n_negative,
        "positive_rate": round(positive_rate, 6),
        "unknown_count_by_column": unknown_before,
        "n_pdays_999": n_pdays_999_before,
        "n_duplicated_rows": before["完全重复行数"],
        "n_nan_cells": before["NaN 单元格数"],
        "n_train": n_train,
        "n_validation": n_val,
        "n_test": n_test,
        "n_positive_by_fold": pos_by_fold,
        "positive_rate_by_fold": pos_rate_by_fold,
        "positive_rate_decile_by_row_order": decile,
        "raw_file_bytes": raw_file_bytes,
        "raw_sha256": raw_sha256,
        "raw_download_date": RAW_DOWNLOAD_DATE,
        "separator": SEP,
        "split_method": "chronological holdout by original row order, no shuffle",
        "seed_note": SEED_NOTE,
    },
}
(OUT / "A_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)

# %% 10. 质量表 T1
unk_rows = "\n".join(
    f"| `{c}` 列 unknown | {v} | {unknown_after.get(c, 0)} | 保留为真实类别，不删除不插补 | 0 |"
    for c, v in unknown_before.items()
)
action_rows = "\n".join(
    f"| {a} | {b} | {c} | {d} |" for a, b, c, d in CLEAN_ACTIONS
)
t1 = f"""# T1 数据质量表（Part A）

> 本表所有数字由 `01_data_quality.py` 实测生成，来源 `data/raw/bank-additional-full.csv`；
> 原始文件 sha256：`{raw_sha256}`。清洗前后**行数不变**，变化的是记录口径。

## 一、总体

| 检查项 | 清洗前 | 清洗后 | 说明 |
|---|---|---|---|
| 行数 | {n_rows} | {after['行数']} | 不删任何行 |
| 列数（含 y） | {n_columns} | {after['列数']} | 20 输入 + 1 标签 |
| 分隔符 | `;` | `;` | 用默认逗号读取会变成一整列 |
| NaN 单元格 | {before['NaN 单元格数']} | {after['NaN 单元格数']} | 缺失已被编码为 `unknown` 类别 |
| 完全重复行 | {before['完全重复行数']} | {after['完全重复行数']} | 无客户 ID，无法判定是否独立联系记录，保留 |
| 正类 `y = yes` | {n_positive}（{positive_rate*100:.4f}%） | 同左 | 约 89% 外呼无效 → accuracy 不能当主指标 |
| `pdays = 999` | {n_pdays_999_before} | {n_pdays_999_after} | 「从未联系」哨兵，不是 999 天 |

## 二、unknown 逐列计数（保留为真实类别）

| 列 | 清洗前 | 清洗后 | 处理决定 | 影响行数 |
|---|---|---|---|---|
{unk_rows}

## 三、处理决定与影响行数

| 处理决定 | 涉及范围 | 影响行数 | 理由 |
|---|---|---|---|
{action_rows}

## 四、结构性事实（写进报告用）

- **无精确日期列**：只有 `month` / `day_of_week`，但官方说明文件明确「ordered by date (May 2008 → November 2010)」→ 按行序时间留出，不随机切分。
- **无客户 ID**：一行 = 一个客户 × 某轮 campaign 的联系记录；自建 `row_id` 作主键，不进模型。
- **敏感属性**：`age` / `job` / `marital` / `education` 不得单独作为联系依据，报告需写最小化使用与角色隔离。
- **宏观五列**：`emp.var.rate` / `cons.price.idx` / `cons.conf.idx` / `euribor3m` / `nr.employed` 保留进模型，但 2008 金融危机期间可能漂移，时间留出正好能暴露。
- **泄漏字段**：`duration` 通话结束后才知道，主模型剔除，只做含/不含消融；`y` 只作真值，绝不进模型。
- **标签随时间漂移（实测，重要）**：按原始行序十等分，订阅率从首个 10% 的 {decile[0]['positive_rate']*100:.2f}% 升到末个 10% 的 {decile[-1]['positive_rate']*100:.2f}%（全量 {positive_rate*100:.4f}%）；三段正类率 Train {pos_rate_by_fold['train']*100:.2f}% / Validation {pos_rate_by_fold['validation']*100:.2f}% / Test {pos_rate_by_fold['test']*100:.2f}%。这不是切分错误，官方说明数据按日期排序、后期 campaign 命中率明显更高。三个含义：① 随机切分会掩盖漂移、让分数虚高，所以必须按行序留出；② Test 的命中数偏高是数据本身造成，**C 必须与两个基线同一切分比较**，不能拿绝对命中数当模型的功劳；③ 报告限制章要写「结论不外推到其他时期」。配图 `figures/F1b_时间漂移证据.png`。

## 五、切分协议（交付给 B / C）

| 段 | 行数 | 正类行数 | 正类率 | 行号区间（0-based） |
|---|---|---|---|---|
| Train | {n_train} | {pos_by_fold['train']} | {pos_rate_by_fold['train']*100:.2f}% | 0 – {n_train-1} |
| Validation | {n_val} | {pos_by_fold['validation']} | {pos_rate_by_fold['validation']*100:.2f}% | {n_train} – {n_train+n_val-1} |
| Test | {n_test} | {pos_by_fold['test']} | {pos_rate_by_fold['test']*100:.2f}% | {n_train+n_val} – {n_rows-1} |

`outputs/split_v1.csv`（`row_id`, `fold`）只生成一次、之后只读；Test 只在最终评价时用一次。
{SEED_NOTE}。
"""
(OUT / "T1_数据质量表.md").write_text(t1, encoding="utf-8")
print("[表] T1 已写出")



