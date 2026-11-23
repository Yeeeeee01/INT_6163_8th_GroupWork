# INT6163 第8组：银行定期存款营销分析

本项目使用 UCI 银行营销数据集（Bank Marketing），研究如何在外呼工时有限时，为待联系记录排序并评估名单效率。分析是历史数据回放，不是实际部署，也不能据此推断电话导致订阅或提高总体签约量。

## 项目概要

- **数据与切分：**原始数据共 41,188 行、21 列；按原行序分为训练集 24,712 行、验证集 8,238 行、测试集 8,238 行，不打乱顺序。
- **主模型：**逻辑回归，使用通话前可知的 14 项特征；排除通话后才知道的 `duration`，主模型也不含五项宏观指标。
- **评价方式：**使用平均精确率（AP）、前 K 名单精确率（Precision@K）、前 K 名单召回率（Recall@K）及混淆矩阵；所有模型在相同测试集及相同预算下比较。
- **行动建议：**按风险分排序，结合人工复核和联系上限；联系限制只作事后回放，不代表真实业务规则或已部署流程。

## 主要结果

测试集有 8,238 条记录，其中 2,540 条后来订阅。主工作点为 30% 预算，即联系名单上限 `K = 2,472`。

- 主逻辑回归模型的 AP 为 **0.448274**，前 K 名单精确率为 **48.54%**，前 K 名单召回率为 **47.24%**，命中 1,200 条订阅。
- 相比“上次营销成功优先”的规则基线，同样预算下多命中 **276** 条订阅，少联系 **276** 条未订阅记录；这两项是同一名单变化的两种表达，不应相加。
- 主名单漏掉 **1,340** 条后来订阅的记录。结果反映名单排序效率，不代表电话带来的因果增益。
- 含 `duration` 的模型仅作泄漏消融：该字段在电话结束后才可知，不能用于真实预测。

数据存在明显时间漂移，测试集订阅率高于训练集。结果只适用于本次历史留出期，不应直接外推到其他时期、银行或渠道。

## 项目流程

| 阶段 | 内容 | 主要产出 |
|---|---|---|
| A：数据质量 | 核对数据来源、字段、缺失标签、重复记录和原行序切分 | `data/README_data.md`、T1、数据字典、`split_v1.csv`、F1/F1b/F2 |
| B：模型训练 | 训练基线、逻辑回归、决策树和随机森林；只用验证集选参 | `02_models.py`、`scores.csv`、T2、系数表 |
| C：最终评价 | 在冻结测试集上一次性评价、分析误差切片和预算敏感性 | `metrics.json`、T3/T4/T5、F3/F4 |
| D：报告与行动 | 整合报告证据，回放固定联系限制并绘制建议流程 | `report.docx`、T6、F5、章节—图表对应表 |

T5 将报告中的数字对应到 `metrics.json` 键和报告页码，用于追溯与校对。`metrics.json` 是正式数字源。

## 运行项目

建议使用 Python 3.9 或更新版本，并按仓库声明安装依赖。在项目根目录执行：

```bash
python -m pip install -r requirements.txt
python scripts/reproduce_all.py --check-only
python scripts/reproduce_all.py
```

完整入口会从原始 CSV 在新工作区依次运行 A → B → C → D01 → D02，并核对报告登记的 107 个数字。检查通过后，可在 `runs/latest_run.txt` 指向的运行目录查看 `RUN_RESULTS.md` 和 `publication/`。运行结果不会覆盖仓库中的正式报告或公开结果。

如需单独运行 A、B、C：

```bash
python 01_data_quality.py
python 02_models.py
python 03_eval.py
```

也可使用 `python scripts/reproduce_abc.py` 单独重建 A—C。运行顺序、结果目录及字体说明以本 README 和各脚本输出为准。`--check-only` 只做输入与环境预检，不会重新训练模型。

## 文件结构

下表和目录树涵盖当前项目中的代码、数据、报告及正式结果。运行后才生成的 `runs/`、`local_review/` 和虚拟环境目录不属于固定交付文件，详见“运行项目”。

```text
.
├── .gitattributes
├── .gitignore
├── 01_data_quality.ipynb
├── 01_data_quality.py
├── 02_models.py
├── 03_eval.ipynb
├── 03_eval.py
├── c01_support.py
├── CONTRIBUTIONS.md
├── README.md
├── requirements.txt
├── report.docx
├── __pycache__/
│   └── 01_data_quality.cpython-314.pyc
├── configs/
│   └── features.yaml
├── data/
│   ├── README_data.md
│   └── raw/
│       ├── bank-additional-full.csv
│       ├── bank-additional-names.txt
│       └── bank-additional.zip
├── docs/
│   └── REPORT_EVIDENCE.json
├── figures/
│   ├── F1_通话前后字段分界图.png
│   ├── F1b_时间漂移证据.png
│   ├── F2_数据血缘图.png
│   ├── F3_PR曲线.png
│   └── F4_预算收益曲线.png
├── outputs/
│   ├── A_summary.json
│   ├── B_run_manifest.json
│   ├── C_run_manifest.json
│   ├── C_测试集模型比较表.md
│   ├── D01_policy_registration.json
│   ├── D01_policy_spec.json
│   ├── D01_run_manifest.json
│   ├── D01_逐记录审计.csv
│   ├── F5_行动闭环.png
│   ├── F5_行动闭环.svg
│   ├── T1_数据质量表.md
│   ├── T2_模型对比表.csv
│   ├── T2_模型对比表.md
│   ├── T3_误差切片表.md
│   ├── T4_duration消融表.md
│   ├── T5_all_numbers.csv
│   ├── T5_report_claims.json
│   ├── T5_数字核对表.md
│   ├── T6_联系限制补充评价.md
│   ├── data_dictionary.csv
│   ├── logistic_coefficients.csv
│   ├── metrics.json
│   ├── model_selection_pool.csv
│   ├── publication_manifest.json
│   ├── scores.csv
│   ├── split_v1.csv
│   └── 章节_图表_数字对应表.md
└── scripts/
    ├── d01_contact_policy.py
    ├── d02_report_assets.py
    ├── reproduce_abc.py
    ├── reproduce_all.py
    └── result_bundle.py
```

### 根目录文件

| 文件 | 用途 |
|---|---|
| `.gitattributes` | 规定文本文件换行格式和二进制文件类型。 |
| `.gitignore` | 排除虚拟环境、运行产物、缓存及本地检查文件。 |
| `README.md` | 项目概述、结果摘要、运行步骤与完整文件说明。 |
| `CONTRIBUTIONS.md` | 记录成员分工及各自负责的项目产出。 |
| `requirements.txt` | 声明分析代码所需的 Python 依赖版本。 |
| `report.docx` | 六章项目报告，含图表、参考资料、生成式人工智能使用说明和成员贡献。 |
| `01_data_quality.py` | A 阶段入口：检查数据、生成字段字典、冻结切分并输出数据质量材料。 |
| `01_data_quality.ipynb` | A 阶段交互式笔记本，调用与脚本相同的数据处理逻辑。 |
| `02_models.py` | B 阶段入口：拟合基线和候选模型，只用训练集拟合、验证集选参。 |
| `03_eval.py` | C 阶段入口：读取冻结分数，在测试集进行最终评价并生成表图。 |
| `03_eval.ipynb` | C 阶段交互式笔记本，调用与脚本相同的评价逻辑。 |
| `c01_support.py` | C 阶段共用的输入核验、指标复核和结果登记辅助代码。 |
| `__pycache__/01_data_quality.cpython-314.pyc` | 已跟踪的 Python 字节码缓存；不是运行依赖，可从交付包中排除。 |

### 配置、数据与证据

| 路径 | 用途 |
|---|---|
| `configs/features.yaml` | 冻结主模型特征，以及宏观指标和 `duration` 消融特征清单。 |
| `data/README_data.md` | 数据来源、许可、字段含义、质量处理、隐私限制及切分协议。 |
| `data/raw/bank-additional-full.csv` | 项目使用的 UCI 完整原始数据，保持原始行序。 |
| `data/raw/bank-additional-names.txt` | UCI 随附的数据集说明、变量定义和来源信息。 |
| `data/raw/bank-additional.zip` | 原始数据下载存档；实际分析直接读取同目录 CSV。 |
| `docs/REPORT_EVIDENCE.json` | 报告身份、已登记数字、页码、图表及对应证据的机器可读契约。 |

### 图表目录

| 文件 | 用途 |
|---|---|
| `figures/F1_通话前后字段分界图.png` | 区分电话拨出前可知信息与 `duration`、标签等事后信息。 |
| `figures/F1b_时间漂移证据.png` | 展示按原始行序分组后的订阅率变化。 |
| `figures/F2_数据血缘图.png` | 展示原始数据、处理、切分与评价之间的数据流程。 |
| `figures/F3_PR曲线.png` | 比较各模型在测试集上的精确率—召回率表现。 |
| `figures/F4_预算收益曲线.png` | 展示不同联系预算下的命中订阅数量。 |
| `outputs/F5_行动闭环.png`、`outputs/F5_行动闭环.svg` | 展示名单排序、规则筛查、人工复核、联系执行和结果留痕的建议流程。 |

### `outputs/` 结果目录

| 文件 | 用途 |
|---|---|
| `A_summary.json` | A 阶段数据规模、标签、字段、切分和来源指纹摘要。 |
| `B_run_manifest.json` | B 阶段代码、输入、环境和输出的运行记录。 |
| `C_run_manifest.json` | C 阶段输入、评价来源及与 B 阶段结果的配对记录。 |
| `C_测试集模型比较表.md` | 各模型在同一测试集和相同联系预算下的比较结果。 |
| `D01_policy_registration.json` | 固定联系限制规则的事前登记记录。 |
| `D01_policy_spec.json` | 联系限制规则、主情景及对照情景的定义。 |
| `D01_run_manifest.json` | D01 回放所用输入、来源和结果指纹。 |
| `D01_逐记录审计.csv` | 逐条记录原名单、限制条件和递补情景的审计结果。 |
| `T1_数据质量表.md` | 缺失标签、重复记录、特殊取值及漂移等数据质量摘要。 |
| `T2_模型对比表.md`、`T2_模型对比表.csv` | 验证集模型比较表，分别供阅读和表格处理。 |
| `T3_误差切片表.md` | 按客群与联系特征划分的测试误差及样本量。 |
| `T4_duration消融表.md` | 比较是否使用通话时长的结果，仅用于展示泄漏影响。 |
| `T5_数字核对表.md` | 将报告数字对应到 `metrics.json` 键及报告页码。 |
| `T5_all_numbers.csv` | `metrics.json` 中全部数值的键、类型、用途和报告页码索引。 |
| `T5_report_claims.json` | 报告中逐项引用数字的机器可读登记。 |
| `T6_联系限制补充评价.md` | 联系限制回放的联系量、命中数及额外漏报等补充结果。 |
| `data_dictionary.csv` | 机器可读的数据字段、含义和入模信息。 |
| `logistic_coefficients.csv` | 主逻辑回归模型的编码特征系数；表示条件关联，不表示因果。 |
| `metrics.json` | 正式数字源，供报告核对、图表生成和结果追溯。 |
| `model_selection_pool.csv` | 验证集上测试过的模型和参数候选结果。 |
| `publication_manifest.json` | 正式发布文件与运行阶段产物之间的映射和指纹记录。 |
| `scores.csv` | 模型在验证集和测试集上的记录级风险分数。 |
| `split_v1.csv` | 冻结的原行序训练、验证和测试集划分。 |
| `章节_图表_数字对应表.md` | 报告章节、实际图表、配套分析文件和证据的对应关系。 |

### `scripts/` 运行与发布工具

| 文件 | 用途 |
|---|---|
| `scripts/reproduce_abc.py` | 从原始数据在新工作区重建 A、B、C 阶段。 |
| `scripts/d01_contact_policy.py` | 执行固定联系限制的事后回放，不训练模型或搜索阈值。 |
| `scripts/d02_report_assets.py` | 根据已登记结果生成 F5 图及报告证据素材。 |
| `scripts/result_bundle.py` | 整合并发布表格、图形、指标和报告证据索引。 |
| `scripts/reproduce_all.py` | 统一执行 A、B、C、D01、D02，并核对报告登记数字。 |

完整重跑会在 `runs/` 下创建新的运行目录；A/B/C 单阶段候选结果写入 `local_review/`。这两个目录用于运行与审查，不是固定源文件。`.venv/`、编辑器配置和新生成的缓存也属于本地环境，不是项目分析输入。

## 数据、方法与限制

- 数据来自 [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)，许可为 CC BY 4.0，DOI：[10.24432/C5K306](https://doi.org/10.24432/C5K306)。引用资料见报告及 [data/README_data.md](data/README_data.md)。
- 随机种子为 42；切分按原始行序进行，测试集只用于最终评价，不用于模型选择。
- `unknown` 保留为独立编码类别；`pdays = 999` 表示此前没有相应营销联系记录。`row_id` 仅用于追踪原始行，不是客户编号。
- 数据没有未拨打对照组，且没有客户 ID 和精确日期；不能据此估计因果效果，也无法保证不同数据折之间没有同一客户。
- 年龄、职业、婚姻和教育等属性需谨慎处理，不应单独作为联系或排除客户的依据；真实使用前应设置人工复核、权限控制和后续监测。
- 固定联系限制 `previous >= 3` 且 `poutcome == failure` 是本作业的示例假设。回放结果不是已验证的银行政策或真实人工复核效果。

## 项目整合说明

当前分支整合 A、B、C 分析修订及 D 报告成果。相较原 `main`，主要整理包括：统一交互式笔记本与脚本入口、核对特征配置和数据说明、补充运行来源记录、加强测试集与指标核验、统一图表和报告数字来源，以及补充报告证据索引。历史版本与修改细节可在 Git 历史中查看；本 README 保留项目运行和交付所需的概要信息。

重跑结果可能因 Python、依赖或字体环境与历史文件存在非科学数字层面的差异；完整入口会记录运行环境，并在报告证据不匹配时停止，不会静默替换报告数字。
