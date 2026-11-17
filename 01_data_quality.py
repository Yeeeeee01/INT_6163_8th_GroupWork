# -*- coding: utf-8 -*-
# [A01-01 原代码开始] 环境与运行说明以GitHub为依据，保留原模块说明
# """
# INT6163 高级数据分析 · 第8组 · Part A：问题界定与数据质量
# =========================================================
# 运行方式（在本文件所在目录打开命令行）：
#     python 01_data_quality.py
# 
# 作用：一次性产出 Part A 的全部交付物
#     data/README_data.md          数据说明（问题陈述五字段 / 21 列字典 / 来源许可 / 隐私）
#     outputs/split_v1.csv         按行序 60/20/20 的切分（row_id, fold），只生成一次
#     outputs/data_dictionary.csv  21 列数据字典（机器可读）
#     outputs/T1_数据质量表.md      数据质量表 T1
#     outputs/A_summary.json       实测数字汇总，供 C 填 metrics.json
#     figures/F1_通话前后字段分界图.png
#     figures/F2_数据血缘图.png
# 
# 依赖：pip install pandas matplotlib
# 注意：split_v1.csv 已存在时默认不重新生成（分工稿要求「只生成一次」）；
#       确需重建时运行 python 01_data_quality.py --force
# """
# [A01-01 原代码结束]
# [A01-01 修订代码开始]
"""
INT6163 第8组 Part A 数据质量 A01 修订
环境依据：GitHub README 的 Python 3.9+ 与仓库 requirements.txt 原有版本。
运行：python 01_data_quality.py
可选隔离输出：python 01_data_quality.py --output-root 项目内目录
修改处保留原代码注释；既有生成文件运行前备份，Markdown另保留原文注释。
原始数据和既定60/20/20切分不改变；已有切分必须先通过校验。
"""
# [A01-01 修订代码结束]

# %% 1. 环境与路径
from pathlib import Path
import sys

# [A01-02 新增] 增加参数、GitHub依赖核对与生成件备份所需标准库
import argparse
import importlib.metadata
import shutil
# [A01-02 新增结束]
import json
import hashlib
from datetime import datetime

import pandas as pd

# [A01-03 新增] 读取GitHub已有features.yaml，统一入模字段说明
import yaml
# [A01-03 新增结束]
import matplotlib
matplotlib.use("Agg")  # 不弹窗口，直接存图
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "bank-additional-full.csv"
# [A01-04 原代码开始] 保留原输出接口，增加隔离输出、环境核对和生成件留痕
# DATA_DIR = ROOT / "data"
# OUT = ROOT / "outputs"
# FIG = ROOT / "figures"
# for d in (DATA_DIR, OUT, FIG):
#     d.mkdir(parents=True, exist_ok=True)
# [A01-04 原代码结束]
# [A01-04 修订代码开始]
parser = argparse.ArgumentParser(description="Part A A01，依据GitHub声明环境运行")
parser.add_argument("--output-root", type=Path, default=ROOT)
parser.add_argument("--force", action="store_true", help="显式重建切分；旧生成件仍先备份")
args = parser.parse_args()
OUTPUT_ROOT = args.output_root.resolve()
if OUTPUT_ROOT != ROOT and ROOT not in OUTPUT_ROOT.parents:
    raise ValueError("输出目录必须是本项目或其子目录，避免写入其他项目")
DATA_DIR = OUTPUT_ROOT / "data"
OUT = OUTPUT_ROOT / "outputs"
FIG = OUTPUT_ROOT / "figures"
for d in (DATA_DIR, OUT, FIG):
    d.mkdir(parents=True, exist_ok=True)

# GitHub没有声明精确Python补丁版本或完整间接依赖；这里不补造这些要求。
if sys.version_info < (3, 9):
    raise RuntimeError("GitHub README 要求 Python 3.9 或以上")
declared_dependencies = {}
for dependency_line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
    dependency_line = dependency_line.strip()
    if not dependency_line or dependency_line.startswith("#"):
        continue
    package, required_version = dependency_line.split("==", 1)
    actual_version = importlib.metadata.version(package)
    if actual_version != required_version:
        raise RuntimeError(f"GitHub依赖不符：{package} 要求 {required_version}，实际 {actual_version}")
    declared_dependencies[package] = required_version
FEATURES_CONFIG = ROOT / "configs" / "features.yaml"
feature_config = yaml.safe_load(FEATURES_CONFIG.read_text(encoding="utf-8"))
main_features = feature_config["feature_sets"]["main"]
if not isinstance(main_features, list) or len(main_features) != len(set(main_features)):
    raise ValueError("主特征配置必须是无重复字段的列表")
if {"duration", "y", "row_id"}.intersection(main_features):
    raise ValueError("通话后字段、标签和技术行号不得进入主特征配置")

# CSV/JSON/图片不能加入代码注释；在重生成之前保留逐字节备份与清单。
generated_paths = [
    "data/README_data.md", "outputs/A_summary.json", "outputs/data_dictionary.csv",
    "outputs/T1_数据质量表.md", "outputs/split_v1.csv",
    "figures/F1_通话前后字段分界图.png", "figures/F1b_时间漂移证据.png",
    "figures/F2_数据血缘图.png",
]
existing_generated = [name for name in generated_paths if (OUTPUT_ROOT / name).is_file()]
if existing_generated:
    archive = OUTPUT_ROOT / "local_review" / "repairs" / "A01" / "generated_before" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    archive.mkdir(parents=True, exist_ok=False)
    archived_hashes = {}
    for relative in existing_generated:
        src = OUTPUT_ROOT / relative
        dest = archive / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        archived_hashes[relative] = hashlib.sha256(src.read_bytes()).hexdigest()
    (archive / "manifest.json").write_text(json.dumps(archived_hashes, ensure_ascii=False, indent=2), encoding="utf-8")

def write_review_markdown(path, content):
    """保留首次被替换的原Markdown注释，后续运行不反复堆叠相同旧稿。"""
    begin = "<!-- A01_ORIGINAL_MARKDOWN_BEGIN\n"
    end = "\nA01_ORIGINAL_MARKDOWN_END -->\n"
    if path.exists():
        previous = path.read_text(encoding="utf-8")
        if previous.startswith(begin) and end in previous:
            prefix = previous.split(end, 1)[0] + end
        else:
            if "-->" in previous:
                raise ValueError(f"旧Markdown含嵌套注释，已备份；需人工核对后生成：{path}")
            prefix = begin + previous + end
    else:
        prefix = begin + "本次从原始数据新生成，无被替换旧文。" + end
    path.write_text(prefix + "\n" + content, encoding="utf-8")
# [A01-04 修订代码结束]

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

# [A01-05 新增] 解释LF/CRLF差异并校验GitHub冻结数据内容
# 同时记录真实字节指纹和明确定义的LF内容指纹，不修改原始CSV。
normalized_raw_bytes = raw_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
raw_normalized_sha256 = hashlib.sha256(normalized_raw_bytes).hexdigest()
expected_normalized_sha256 = "233e260d5d1d506a2c10381da5b8c2f75f2c08d1b373ca7b825e39ebe1bd30df"
if raw_normalized_sha256 != expected_normalized_sha256:
    raise ValueError("原始数据内容与GitHub冻结快照不一致；不继续生成结果")
# [A01-05 新增结束]

# 关键：sep=";"，用默认逗号会读成一整列
df = pd.read_csv(RAW, sep=SEP)
n_rows, n_columns = df.shape

# [A01-06 新增] 先核对已有冻结切分，阻止带错切分继续生成A产物
if (n_rows, n_columns) != (41188, 21):
    raise ValueError("本项目冻结数据应为41188行、21列")
if not set(main_features).issubset(df.columns):
    raise ValueError("features.yaml 含原始数据中不存在的字段")

def validate_frozen_split(frame):
    """核对字段、行号与既定连续60/20/20切分，不根据标签重划分。"""
    if frame.columns.tolist() != ["row_id", "fold"]:
        raise ValueError("冻结切分必须仅含 row_id, fold")
    n_train_expected = int(n_rows * 0.60)
    n_validation_end = int(n_rows * 0.80)
    expected_folds = (["train"] * n_train_expected
                      + ["validation"] * (n_validation_end - n_train_expected)
                      + ["test"] * (n_rows - n_validation_end))
    if frame["row_id"].tolist() != list(range(n_rows)) or frame["fold"].tolist() != expected_folds:
        raise ValueError("冻结切分与GitHub既定原始行序60/20/20协议不一致")

if (OUT / "split_v1.csv").exists() and not args.force:
    validate_frozen_split(pd.read_csv(OUT / "split_v1.csv"))
# [A01-06 新增结束]
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
# [A01-07 原代码开始] 修正缺失编码的语义说明，保留既定处理方法
# # 理由：unknown 在 UCI 官方说明里被编码成一个真实类别，删除/插补会抹掉信息；
# [A01-07 原代码结束]
# [A01-07 修订代码开始]
# 理由：unknown 是缺失值标签；本项目选择保留为独立类别，不删除或插补。
# [A01-07 修订代码结束]
#       pdays=999 是「从未被联系」的哨兵，不是 999 天；
#       12 行完全重复，因数据没有客户 ID，无法判断是录入重复还是不同 campaign 的独立联系记录，保留。
# 因此清洗前后行数不变，变化的是「记录口径」——全部写进 T1，每个决定都能查到影响行数。
CLEAN_ACTIONS = [
# [A01-08 原代码开始] 处理方法不变，修正unknown文案
#     ("unknown 视为真实类别，不删除、不插补", "各列 unknown 计数（见 T1）", 0, "保留信息，避免伪造分布"),
# [A01-08 原代码结束]
# [A01-08 修订代码开始]
    ("unknown 缺失标签保留为独立类别，不删除、不插补", "各列 unknown 计数（见 T1）", 0, "保留缺失信息，避免伪造分布"),
# [A01-08 修订代码结束]
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
# [A01-09 原代码开始] 字段备注与GitHub实际特征配置一致
#     ("contact", "本次联系的通讯方式（手机/固话）", "类别", "是", "是", "仅作误差切片，不作主结论"),
# [A01-09 原代码结束]
# [A01-09 修订代码开始]
    ("contact", "本次联系的通讯方式（手机/固话）", "类别", "是", "是", "进入主模型；不单独作为联系依据"),
# [A01-09 修订代码结束]
# [A01-10 原代码开始] 字段备注与GitHub实际特征配置一致
#     ("month", "本次联系所在月份", "类别", "是", "是", "仅作误差切片；无精确日期列"),
# [A01-10 原代码结束]
# [A01-10 修订代码开始]
    ("month", "本次联系所在月份", "类别", "是", "是", "进入主模型；无精确日期列"),
# [A01-10 修订代码结束]
# [A01-11 原代码开始] 字段备注与GitHub实际特征配置一致
#     ("day_of_week", "本次联系所在星期", "类别", "是", "是", "仅作误差切片；无精确日期列"),
# [A01-11 原代码结束]
# [A01-11 修订代码开始]
    ("day_of_week", "本次联系所在星期", "类别", "是", "是", "进入主模型；无精确日期列"),
# [A01-11 修订代码结束]
    ("duration", "本次通话时长（秒）", "数值", "否", "否", "泄漏特征！通话结束才知道；UCI 官方要求剔除，仅用于含/不含消融"),
    ("campaign", "本轮 campaign 中该客户被联系次数（含本次）", "数值", "是", "是", "历史联系记录"),
    ("pdays", "距上次 campaign 联系的天数", "数值", "是", "是", "999 = 从未联系，哨兵值"),
    ("previous", "本轮之前该客户被联系次数", "数值", "是", "是", "历史联系记录"),
    ("poutcome", "上次营销活动结果", "类别", "是", "是", "简单规则基线按它排序"),
    ("emp.var.rate", "就业变动率（季度宏观指标）", "数值", "是", "否", "通话前可知；Validation 宏观对照，主模型排除以降低时间漂移风险"),
    ("cons.price.idx", "消费者价格指数（月度）", "数值", "是", "否", "通话前可知；Validation 宏观对照，主模型排除以降低时间漂移风险"),
    ("cons.conf.idx", "消费者信心指数（月度）", "数值", "是", "否", "通话前可知；Validation 宏观对照，主模型排除以降低时间漂移风险"),
    ("euribor3m", "欧元同业拆借 3 月利率（日度）", "数值", "是", "否", "通话前可知；Validation 宏观对照，主模型排除以降低时间漂移风险"),
    ("nr.employed", "就业人数（季度）", "数值", "是", "否", "通话前可知；Validation 宏观对照，主模型排除以降低时间漂移风险"),
    ("y", "客户是否订阅定期存款", "类别", "否", "否", "真值 / 标签，只用来对答案，绝不进模型"),
]
dict_df = pd.DataFrame(
    DICTS, columns=["字段名", "语义", "类型", "通话前可知", "进主模型", "备注"]
)
dict_df.insert(0, "序号", range(1, len(dict_df) + 1))

# [A01-12 新增] 入模标记统一从features.yaml生成，不维护第二份人工清单
dict_df["进主模型"] = dict_df["字段名"].map(lambda name: "是" if name in main_features else "否")
# [A01-12 新增结束]
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
# [A01-13 原代码开始] F1与实际入模配置保持一致
#     "本次安排：contact / month / day_of_week（仅作误差切片）",
# [A01-13 原代码结束]
# [A01-13 修订代码开始]
    "本次安排：contact / month / day_of_week（主模型使用）",
# [A01-13 修订代码结束]
    "历史联系：campaign / pdays / previous / poutcome",
    "宏观指标：emp.var.rate / cons.price.idx / cons.conf.idx",
    "          euribor3m / nr.employed",
# [A01-14 原代码开始] 明确可用字段数与实际入模字段数的区别
#     f"共 {len(pre_cols)} 列通话前可知 → 主模型按验证集筛选",
# [A01-14 原代码结束]
# [A01-14 修订代码开始]
    f"通话前可知 {len(pre_cols)} 列；实际主模型使用 {len(main_features)} 列",
# [A01-14 修订代码结束]
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
# [A01-21 原代码开始] 图题描述总体分布变化，避免暗示逐段单调上升
# ax.set_title("F1b  时间漂移证据：越靠后的记录，真实订阅率越高", fontsize=14, pad=12)
# [A01-21 原代码结束]
# [A01-21 修订代码开始]
ax.set_title("F1b  行序分布变化：后段总体正类率更高", fontsize=14, pad=12)
# [A01-21 修订代码结束]
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

# [A01-15 原代码开始] 已有切分先验证后沿用；新切分也验证后再写出
# if split_path.exists() and "--force" not in sys.argv:
#     print(f"[切分] {split_path.name} 已存在，跳过生成（只生成一次；需重建请加 --force）")
# else:
#     split_df = pd.DataFrame({"row_id": range(n_rows), "fold": folds})
#     split_df.to_csv(split_path, index=False, encoding="utf-8")
#     print(f"[切分] 已写出 {split_path.name}：train {n_train} / validation {n_val} / test {n_test}")
# 
# split_df = pd.read_csv(split_path)
# [A01-15 原代码结束]
# [A01-15 修订代码开始]
if split_path.exists() and not args.force:
    split_df = pd.read_csv(split_path)
    validate_frozen_split(split_df)
    print(f"[切分] {split_path.name} 已验证，沿用原冻结内容，不重写")
else:
    split_df = pd.DataFrame({"row_id": range(n_rows), "fold": folds})
    validate_frozen_split(split_df)
    split_df.to_csv(split_path, index=False, encoding="utf-8")
    print(f"[切分] 已写出 {split_path.name}：train {n_train} / validation {n_val} / test {n_test}")
# [A01-15 修订代码结束]
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

# [A01-16 新增] 补充可追溯字段；未声明的Python精确版本与间接依赖不伪造为标准
        "raw_normalized_sha256": raw_normalized_sha256,
        "raw_normalization": "bytes: CRLF -> LF, then CR -> LF; source file unchanged",
        "main_features": main_features,
        "main_feature_count": len(main_features),
        "environment_authority": "GitHub README.md Python 3.9+ and requirements.txt",
        "github_declared_dependencies": declared_dependencies,
# [A01-16 新增结束]
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
# [A01-17 原代码开始] 保留旧T1模板注释，修正哈希、缺失语义和超出证据的表述
# t1 = f"""# T1 数据质量表（Part A）
# 
# > 本表所有数字由 `01_data_quality.py` 实测生成，来源 `data/raw/bank-additional-full.csv`；
# > 原始文件 sha256：`{raw_sha256}`。清洗前后**行数不变**，变化的是记录口径。
# 
# ## 一、总体
# 
# | 检查项 | 清洗前 | 清洗后 | 说明 |
# |---|---|---|---|
# | 行数 | {n_rows} | {after['行数']} | 不删任何行 |
# | 列数（含 y） | {n_columns} | {after['列数']} | 20 输入 + 1 标签 |
# | 分隔符 | `;` | `;` | 用默认逗号读取会变成一整列 |
# | NaN 单元格 | {before['NaN 单元格数']} | {after['NaN 单元格数']} | 缺失已被编码为 `unknown` 类别 |
# | 完全重复行 | {before['完全重复行数']} | {after['完全重复行数']} | 无客户 ID，无法判定是否独立联系记录，保留 |
# | 正类 `y = yes` | {n_positive}（{positive_rate*100:.4f}%） | 同左 | 约 89% 外呼无效 → accuracy 不能当主指标 |
# | `pdays = 999` | {n_pdays_999_before} | {n_pdays_999_after} | 「从未联系」哨兵，不是 999 天 |
# 
# ## 二、unknown 逐列计数（保留为真实类别）
# 
# | 列 | 清洗前 | 清洗后 | 处理决定 | 影响行数 |
# |---|---|---|---|---|
# {unk_rows}
# 
# ## 三、处理决定与影响行数
# 
# | 处理决定 | 涉及范围 | 影响行数 | 理由 |
# |---|---|---|---|
# {action_rows}
# 
# ## 四、结构性事实（写进报告用）
# 
# - **无精确日期列**：只有 `month` / `day_of_week`，但官方说明文件明确「ordered by date (May 2008 → November 2010)」→ 按行序时间留出，不随机切分。
# - **无客户 ID**：一行 = 一个客户 × 某轮 campaign 的联系记录；自建 `row_id` 作主键，不进模型。
# - **敏感属性**：`age` / `job` / `marital` / `education` 不得单独作为联系依据，报告需写最小化使用与角色隔离。
# - **宏观五列**：`emp.var.rate` / `cons.price.idx` / `cons.conf.idx` / `euribor3m` / `nr.employed` 虽在通话前可知，但受时期变化影响；B 在 Train 拟合、Validation 对比含/不含宏观特征后，将其从最终主模型排除，并保留含宏观版本作对照。
# - **泄漏字段**：`duration` 通话结束后才知道，主模型剔除，只做含/不含消融；`y` 只作真值，绝不进模型。
# - **标签随时间漂移（实测，重要）**：按原始行序十等分，订阅率从首个 10% 的 {decile[0]['positive_rate']*100:.2f}% 升到末个 10% 的 {decile[-1]['positive_rate']*100:.2f}%（全量 {positive_rate*100:.4f}%）；三段正类率 Train {pos_rate_by_fold['train']*100:.2f}% / Validation {pos_rate_by_fold['validation']*100:.2f}% / Test {pos_rate_by_fold['test']*100:.2f}%。这不是切分错误，官方说明数据按日期排序、后期 campaign 命中率明显更高。三个含义：① 随机切分会掩盖漂移、让分数虚高，所以必须按行序留出；② Test 的命中数偏高是数据本身造成，**C 必须与两个基线同一切分比较**，不能拿绝对命中数当模型的功劳；③ 报告限制章要写「结论不外推到其他时期」。配图 `figures/F1b_时间漂移证据.png`。
# 
# ## 五、切分协议（交付给 B / C）
# 
# | 段 | 行数 | 正类行数 | 正类率 | 行号区间（0-based） |
# |---|---|---|---|---|
# | Train | {n_train} | {pos_by_fold['train']} | {pos_rate_by_fold['train']*100:.2f}% | 0 – {n_train-1} |
# | Validation | {n_val} | {pos_by_fold['validation']} | {pos_rate_by_fold['validation']*100:.2f}% | {n_train} – {n_train+n_val-1} |
# | Test | {n_test} | {pos_by_fold['test']} | {pos_rate_by_fold['test']*100:.2f}% | {n_train+n_val} – {n_rows-1} |
# 
# `outputs/split_v1.csv`（`row_id`, `fold`）只生成一次、之后只读；Test 只在最终评价时用一次。
# {SEED_NOTE}。
# """
# [A01-17 原代码结束]
# [A01-17 修订代码开始]
t1 = f"""# T1 数据质量表（Part A）

> 本表所有数字由 `01_data_quality.py` 实测生成，来源 `data/raw/bank-additional-full.csv`；
> 原始文件 sha256：`{raw_sha256}`；LF规范内容 sha256：`{raw_normalized_sha256}`。原文件不改写，清洗前后**行数不变**。

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

## 二、unknown 逐列计数（缺失标签保留为独立类别）

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
- **宏观五列**：`emp.var.rate` / `cons.price.idx` / `cons.conf.idx` / `euribor3m` / `nr.employed` 虽在通话前可知，但受时期变化影响；B 在 Train 拟合、Validation 对比含/不含宏观特征后，将其从最终主模型排除，并保留含宏观版本作对照。
- **泄漏字段**：`duration` 通话结束后才知道，主模型剔除，只做含/不含消融；`y` 只作真值，绝不进模型。
- **标签随行序变化（实测）**：首个10%的正类率为 {decile[0]['positive_rate']*100:.2f}%，末个10%为 {decile[-1]['positive_rate']*100:.2f}%；三段正类率为 Train {pos_rate_by_fold['train']*100:.2f}% / Validation {pos_rate_by_fold['validation']*100:.2f}% / Test {pos_rate_by_fold['test']*100:.2f}%。总体后段更高，并非逐段单调。行序留出用于模拟后续时期评价；本项目未做随机切分对照，也不能据此归因于经济危机。结果须在同一Test与基线比较，不外推到其他时期。配图 `figures/F1b_时间漂移证据.png`。

## 五、切分协议（交付给 B / C）

| 段 | 行数 | 正类行数 | 正类率 | 行号区间（0-based） |
|---|---|---|---|---|
| Train | {n_train} | {pos_by_fold['train']} | {pos_rate_by_fold['train']*100:.2f}% | 0 – {n_train-1} |
| Validation | {n_val} | {pos_by_fold['validation']} | {pos_rate_by_fold['validation']*100:.2f}% | {n_train} – {n_train+n_val-1} |
| Test | {n_test} | {pos_by_fold['test']} | {pos_rate_by_fold['test']*100:.2f}% | {n_train+n_val} – {n_rows-1} |

`outputs/split_v1.csv`（`row_id`, `fold`）只生成一次、之后只读；Test 只在最终评价时用一次。
{SEED_NOTE}。
"""
# [A01-17 修订代码结束]
# [A01-18 原代码开始] 生成Markdown时保留被替换原文的HTML注释
# (OUT / "T1_数据质量表.md").write_text(t1, encoding="utf-8")
# [A01-18 原代码结束]
# [A01-18 修订代码开始]
write_review_markdown(OUT / "T1_数据质量表.md", t1)
# [A01-18 修订代码结束]
print("[表] T1 已写出")



# [A01-19 新增] 将原Notebook独有的README生成逻辑补入统一脚本
# [A01-20 原代码开始] 将生成README中的旧安装命令统一为GitHub requirements入口
# dict_md = "\n".join(
#     f"| {r['序号']} | `{r['字段名']}` | {r['语义']} | {r['类型']} | {r['通话前可知']} | {r['进主模型']} | {r['备注']} |"
#     for _, r in dict_df.iterrows()
# )
# readme = f"""# Part A｜数据说明（README_data.md）
# 
# **负责人：A（问题界定与数据质量）** ｜ 生成方式：`python 01_data_quality.py` ｜ 切分版本：{SPLIT_ID}
# 
# ---
# 
# ## 1. 问题陈述五字段（报告第一段照此写，L13 p9）
# 
# | 字段 | 内容 |
# |---|---|
# | **对象** | 留出期一条待联系记录（客户 × 某轮 campaign；**无客户 ID**，用 `row_id` 标识） |
# | **预测点** | **这一通电话拨出之前**；只能用当时可知的客户属性、历史联系记录与宏观指标 |
# | **输出** | 订阅倾向分 `risk` + 按分排序的联系顺序 + 预算–收益曲线（**不是「某一类客户」**） |
# | **行动** | 按分数从高到低联系；对 `previous` 高且 `poutcome=failure` 的人设联系上限；人工复核后执行、结果留痕回流 |
# | **约束** | 外呼工时有限；`duration` 不可得；观察性数据无「未拨打」对照组；敏感属性不得单独作为联系依据 |
# 
# 配图：`figures/F1_通话前后字段分界图.png`。左侧 {len(pre_cols)} 列通话前可知 → 这一通外呼 → 右侧 `duration` / `y` 不可用。
# **不要画**「T-4 周预警」式时间窗——数据没有精确日期列。
# 
# ## 2. 数据来源与许可
# 
# | 项 | 内容 |
# |---|---|
# | 数据集 | UCI #222 Bank Marketing（**bank-additional-full.csv**，不是 10% 抽样的 bank-additional.csv） |
# | 规模 | 实测 **{n_rows} 行 × {n_columns} 列**（20 输入 + `y`） |
# | 时间跨度 | 2008-05 → 2010-11，官方说明「ordered by date」；只有 `month` / `day_of_week`，无精确日期列 |
# | 分隔符 | `;` |
# | 正类 | `y == "yes"` 实测 **{n_positive} 行（{positive_rate*100:.4f}%）**，约 89% 外呼无效 |
# | 许可 | **CC BY 4.0**，DOI 10.24432/C5K306 |
# | 引用 | Moro, S., Cortez, P. & Rita, P. (2014), *A Data-Driven Approach to Predict the Success of Bank Telemarketing*, Decision Support Systems 62:22–31 |
# | 本地快照 | `data/raw/bank-additional-full.csv`，{raw_file_bytes:,} bytes，sha256 `{raw_sha256}`，首次落盘日期 {RAW_DOWNLOAD_DATE} |
# | LF内容指纹 | sha256 `{raw_normalized_sha256}`；将CRLF/CR转为LF后计算，源文件不改写 |
# 
# > 数据集官方说明第 56 行原文："this input should only be included for benchmark purposes and should be discarded if the intention is to have a realistic predictive model." —— 这是 `duration` 必须剔除、只做含/不含消融的官方依据。
# 
# ## 3. 21 列数据字典
# 
# | # | 字段 | 语义 | 类型 | 通话前可知 | 进主模型 | 备注 |
# |---|---|---|---|---|---|---|
# {dict_md}
# 
# `row_id` 是我们自建的行标识（0-based，**不是原始字段**），只用于切分与核对，明确丢弃、不进模型。
# 机器可读版：`outputs/data_dictionary.csv`。
# 
# 实际主模型字段由 `configs/features.yaml` 决定，共 {len(main_features)} 列；19列通话前可知不代表全部进入主模型。五个宏观指标保留为验证对照。
# 
# ## 4. 数据质量摘要
# 
# 完整表格见 `outputs/T1_数据质量表.md`。要点：
# 
# - `unknown` 按列计数后**缺失标签保留为独立类别**，不删除不插补（{', '.join(f'`{k}` {v}' for k, v in unknown_before.items())}）；
# - `pdays = 999` 是「从未联系」哨兵，共 {n_pdays_999_before} 行，保留原值但不解释为 999 天；
# - 完全重复行 {before['完全重复行数']} 行，无客户 ID 无法判定，保留不删；
# - 无 NaN 单元格；清洗前后行数不变，所有处理决定与影响行数都在 T1 可查；
# - 类别不平衡 89:11 → 全猜 `no` 就有约 {(n_negative/n_rows)*100:.2f}% accuracy，**accuracy 不能当主指标**。
# - **实测发现：标签随时间漂移**。按原始行序十等分，订阅率从 {decile[0]['positive_rate']*100:.2f}% 升到 {decile[-1]['positive_rate']*100:.2f}%；三段正类率 Train {pos_rate_by_fold['train']*100:.2f}% / Validation {pos_rate_by_fold['validation']*100:.2f}% / Test {pos_rate_by_fold['test']*100:.2f}%（见 `F1b_时间漂移证据.png`）。这既解释了「为什么必须按行序留出、不能随机切分」，也提醒 C：Test 命中数偏高源于数据本身，必须与两个基线同一切分比较；报告限制章要写「结论不外推到其他时期」。
# 
# ## 5. 切分协议（交给 B / C）
# 
# 按**原始行序**时间留出，不 shuffle：Train {n_train} 行 / Validation {n_val} 行 / Test {n_test} 行。
# 按官方日期顺序留出以模拟后续时期；本项目未运行随机切分对照。`outputs/split_v1.csv`（`row_id`, `fold`）由本脚本**只生成一次**，之后只读；Test 只在最终评价时用一次。{SEED_NOTE}。
# 各段正类人数：{pos_by_fold}。
# 
# ## 6. 隐私与伦理（报告要写）
# 
# - 数据未提供直接客户ID，`row_id`仅为行号；不能据此保证重识别风险为零，也无法核验同一客户是否跨折出现。
# - `age` / `job` / `marital` / `education` 属敏感属性：**最小化使用**，不得单独作为联系或排除客户的依据；名单最终需人工复核后执行（见 D 的 F5 行动闭环）。
# - 角色隔离：A 只处理原始数据与切分，不接触模型评分；名单与评价由 B / C 在各自脚本内完成，避免同一人既定义口径又裁决结果。
# - 项目是**历史回放**，不部署、不真的打电话；结论只到「名单效率」，不声称提高订阅率或已经省钱。
# 
# ## 7. 交付清单与复现
# 
# | 文件 | 说明 |
# |---|---|
# | `01_data_quality.py` / `01_data_quality.ipynb` | 可运行代码（同一份逻辑） |
# | `data/README_data.md` | 本文件 |
# | `outputs/split_v1.csv` | 切分，只读 |
# | `outputs/data_dictionary.csv` | 21 列字典 |
# | `outputs/T1_数据质量表.md` | 质量表 T1 |
# | `outputs/A_summary.json` | 实测数字汇总，供 C 填 `metrics.json` |
# | `figures/F1_通话前后字段分界图.png` | F1 |
# | `figures/F2_数据血缘图.png` | F2 |
# | `figures/F1b_时间漂移证据.png` | 加分图：标签漂移实证，可直接进报告限制章 / PPT |
# 
# 复现：`pip install pandas matplotlib` → 保持 `data/raw/bank-additional-full.csv` 在原位 → 运行 `python 01_data_quality.py` →
# 比对 `A_summary.json` 的 {n_rows} 行 / 正类占比 / unknown 各列计数 / 21 列字典 / 三段行数，换台电脑应完全一致。
# """
# write_review_markdown(DATA_DIR / "README_data.md", readme)
# print("[文档] data/README_data.md 已写出")
# print("[A01_PASS] 数据、字典、F1/F2/F1b、T1、README和冻结切分校验完成")
# [A01-20 原代码结束]
# [A01-20 修订代码开始]
dict_md = "\n".join(
    f"| {r['序号']} | `{r['字段名']}` | {r['语义']} | {r['类型']} | {r['通话前可知']} | {r['进主模型']} | {r['备注']} |"
    for _, r in dict_df.iterrows()
)
readme = f"""# Part A｜数据说明（README_data.md）

**负责人：A（问题界定与数据质量）** ｜ 生成方式：`python 01_data_quality.py` ｜ 切分版本：{SPLIT_ID}

---

## 1. 问题陈述五字段（报告第一段照此写，L13 p9）

| 字段 | 内容 |
|---|---|
| **对象** | 留出期一条待联系记录（客户 × 某轮 campaign；**无客户 ID**，用 `row_id` 标识） |
| **预测点** | **这一通电话拨出之前**；只能用当时可知的客户属性、历史联系记录与宏观指标 |
| **输出** | 订阅倾向分 `risk` + 按分排序的联系顺序 + 预算–收益曲线（**不是「某一类客户」**） |
| **行动** | 按分数从高到低联系；对 `previous` 高且 `poutcome=failure` 的人设联系上限；人工复核后执行、结果留痕回流 |
| **约束** | 外呼工时有限；`duration` 不可得；观察性数据无「未拨打」对照组；敏感属性不得单独作为联系依据 |

配图：`figures/F1_通话前后字段分界图.png`。左侧 {len(pre_cols)} 列通话前可知 → 这一通外呼 → 右侧 `duration` / `y` 不可用。
**不要画**「T-4 周预警」式时间窗——数据没有精确日期列。

## 2. 数据来源与许可

| 项 | 内容 |
|---|---|
| 数据集 | UCI #222 Bank Marketing（**bank-additional-full.csv**，不是 10% 抽样的 bank-additional.csv） |
| 规模 | 实测 **{n_rows} 行 × {n_columns} 列**（20 输入 + `y`） |
| 时间跨度 | 2008-05 → 2010-11，官方说明「ordered by date」；只有 `month` / `day_of_week`，无精确日期列 |
| 分隔符 | `;` |
| 正类 | `y == "yes"` 实测 **{n_positive} 行（{positive_rate*100:.4f}%）**，约 89% 外呼无效 |
| 许可 | **CC BY 4.0**，DOI 10.24432/C5K306 |
| 引用 | Moro, S., Cortez, P. & Rita, P. (2014), *A Data-Driven Approach to Predict the Success of Bank Telemarketing*, Decision Support Systems 62:22–31 |
| 本地快照 | `data/raw/bank-additional-full.csv`，{raw_file_bytes:,} bytes，sha256 `{raw_sha256}`，首次落盘日期 {RAW_DOWNLOAD_DATE} |
| LF内容指纹 | sha256 `{raw_normalized_sha256}`；将CRLF/CR转为LF后计算，源文件不改写 |

> 数据集官方说明第 56 行原文："this input should only be included for benchmark purposes and should be discarded if the intention is to have a realistic predictive model." —— 这是 `duration` 必须剔除、只做含/不含消融的官方依据。

## 3. 21 列数据字典

| # | 字段 | 语义 | 类型 | 通话前可知 | 进主模型 | 备注 |
|---|---|---|---|---|---|---|
{dict_md}

`row_id` 是我们自建的行标识（0-based，**不是原始字段**），只用于切分与核对，明确丢弃、不进模型。
机器可读版：`outputs/data_dictionary.csv`。

实际主模型字段由 `configs/features.yaml` 决定，共 {len(main_features)} 列；19列通话前可知不代表全部进入主模型。五个宏观指标保留为验证对照。

## 4. 数据质量摘要

完整表格见 `outputs/T1_数据质量表.md`。要点：

- `unknown` 按列计数后**缺失标签保留为独立类别**，不删除不插补（{', '.join(f'`{k}` {v}' for k, v in unknown_before.items())}）；
- `pdays = 999` 是「从未联系」哨兵，共 {n_pdays_999_before} 行，保留原值但不解释为 999 天；
- 完全重复行 {before['完全重复行数']} 行，无客户 ID 无法判定，保留不删；
- 无 NaN 单元格；清洗前后行数不变，所有处理决定与影响行数都在 T1 可查；
- 类别不平衡 89:11 → 全猜 `no` 就有约 {(n_negative/n_rows)*100:.2f}% accuracy，**accuracy 不能当主指标**。
- **实测发现：标签随时间漂移**。按原始行序十等分，订阅率从 {decile[0]['positive_rate']*100:.2f}% 升到 {decile[-1]['positive_rate']*100:.2f}%；三段正类率 Train {pos_rate_by_fold['train']*100:.2f}% / Validation {pos_rate_by_fold['validation']*100:.2f}% / Test {pos_rate_by_fold['test']*100:.2f}%（见 `F1b_时间漂移证据.png`）。这既解释了「为什么必须按行序留出、不能随机切分」，也提醒 C：Test 命中数偏高源于数据本身，必须与两个基线同一切分比较；报告限制章要写「结论不外推到其他时期」。

## 5. 切分协议（交给 B / C）

按**原始行序**时间留出，不 shuffle：Train {n_train} 行 / Validation {n_val} 行 / Test {n_test} 行。
按官方日期顺序留出以模拟后续时期；本项目未运行随机切分对照。`outputs/split_v1.csv`（`row_id`, `fold`）由本脚本**只生成一次**，之后只读；Test 只在最终评价时用一次。{SEED_NOTE}。
各段正类人数：{pos_by_fold}。

## 6. 隐私与伦理（报告要写）

- 数据未提供直接客户ID，`row_id`仅为行号；不能据此保证重识别风险为零，也无法核验同一客户是否跨折出现。
- `age` / `job` / `marital` / `education` 属敏感属性：**最小化使用**，不得单独作为联系或排除客户的依据；名单最终需人工复核后执行（见 D 的 F5 行动闭环）。
- 角色隔离：A 只处理原始数据与切分，不接触模型评分；名单与评价由 B / C 在各自脚本内完成，避免同一人既定义口径又裁决结果。
- 项目是**历史回放**，不部署、不真的打电话；结论只到「名单效率」，不声称提高订阅率或已经省钱。

## 7. 交付清单与复现

| 文件 | 说明 |
|---|---|
| `01_data_quality.py` / `01_data_quality.ipynb` | 可运行代码（同一份逻辑） |
| `data/README_data.md` | 本文件 |
| `outputs/split_v1.csv` | 切分，只读 |
| `outputs/data_dictionary.csv` | 21 列字典 |
| `outputs/T1_数据质量表.md` | 质量表 T1 |
| `outputs/A_summary.json` | 实测数字汇总，供 C 填 `metrics.json` |
| `figures/F1_通话前后字段分界图.png` | F1 |
| `figures/F2_数据血缘图.png` | F2 |
| `figures/F1b_时间漂移证据.png` | 加分图：标签漂移实证，可直接进报告限制章 / PPT |

复现环境依GitHub README的Python3.9+及仓库requirements.txt，未声明项不由本机补成标准。

复现：`python -m pip install -r requirements.txt` → 保持 `data/raw/bank-additional-full.csv` 在原位 → 运行 `python 01_data_quality.py` →
比对 `A_summary.json` 的 {n_rows} 行 / 正类占比 / unknown 各列计数 / 21 列字典 / 三段行数，换台电脑应完全一致。
"""
write_review_markdown(DATA_DIR / "README_data.md", readme)
print("[文档] data/README_data.md 已写出")
print("[A01_PASS] 数据、字典、F1/F2/F1b、T1、README和冻结切分校验完成")
# [A01-20 修订代码结束]

# [A01-19 新增结束]
