<!-- README_D整理：以下D04_03技术说明原字节完整保留，当前发布范围以新导航为准 -->

> 当前提交到 `report` 分支的清单为 **20文件**，详见[README_D.md](README_D.md)与[CONTRIBUTIONS.md](CONTRIBUTIONS.md)。报告及D04-03技术重跑均已用户通过；E/PPT与T5后续修改暂缓。下文18文件清单和待阅读状态属于D04_03历史范围，原科学入口仍适用。

<!-- D04_02 原README完整保留
&lt;!-- D04_01 原P01 README逐行保留；嵌套注释标记转义，原字节另存本地归档
&lt;!-- P01整理前README原文保留
# INT_6163_8th_GroupWork

INT6163 (02P) Advanced Data Analytics — Group 8, Bank Marketing project.


--&gt;
&lt;!-- B01 原README说明开始
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
B01 原README说明结束 --&gt;
&lt;!-- B01 修订说明开始 --&gt;
&lt;!-- P01整理前README原文保留

## Reproduce Part A and Part B

Use Python 3.9 or newer, with the unchanged requirements.txt. From the repository root:

```powershell
python -m pip install -r requirements.txt
python 01_data_quality.py
python 02_models.py --output-root local_review/B01_candidate
```

Part A validates and preserves the frozen split. B01 keeps the original models,
features, seed, preprocessing and Validation-only selection, and writes candidates
under local_review/B01_candidate/outputs. The original root outputs/scores.csv,
T2 and C metrics remain paired and unchanged.

Candidate scores, T2, selection pool and coefficients retain their original
formats. B_run_manifest.json records declared versus observed environment and
input/output fingerprints. B_legacy_comparison.json records score differences
without reading Test labels or choosing models using Test performance.


--&gt;
&lt;!-- B01 验收口径修订：澄清流程复刻标准
See [B01 repair and reproduction guide](docs/B01_FIX_GUIDE.md). Historical exact
retraining is not established from the incomplete upstream environment record;
the observed local environment is not a new project standard.
--&gt;
&lt;!-- P01整理前README原文保留


See [B01 repair and reproduction guide](docs/B01_FIX_GUIDE.md). Reproduction is
judged under the GitHub-declared requirements, without requiring an identical
original machine. Record observed dependencies and output differences; use paired
outputs from the same complete A/B/C run. The observed local environment is not
a new project standard.


--&gt;
&lt;!-- B01 修订说明结束 --&gt;
&lt;!-- C01旧C说明保留
## Reproduce Part C: final evaluation and number guardrails


--&gt;
&lt;!-- B01 原C入口说明开始
After Parts A and B have produced `outputs/split_v1.csv` and
`outputs/scores.csv`, run from the repository root:
B01 原C入口说明结束 --&gt;
&lt;!-- C01旧C说明保留


The existing Part C command below evaluates the original root frozen scores.
B01 candidates are isolated and are not automatically substituted into C.
During the B01 stage, do not treat this command as evaluation of the new candidate;
candidate integration and metric version pairing are reserved for the C repair stage.

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



--&gt;
&lt;!-- P01整理前README原文保留


## Reproduce Part C and the complete A/B/C pipeline

C01 evaluates the same B01 run and writes isolated paired results. See the
[C01 repair and reproduction guide](docs/C01_FIX_GUIDE.md) for exact repair
locations, before/after differences and member instructions.

```bash
python scripts/reproduce_abc.py
```

The complete entry creates a fresh workspace from raw CSV, source and config;
no cached outputs are copied. It runs A, B and C in order under the original
GitHub requirements. The final [ABC_REPRODUCED] line gives the paired metrics
path; local_review/ABC_reproduction/latest_run.txt locates the latest run.
Observed transitive versions are recorded, without requiring the original
author's undeclared environment or turning local versions into project rules.

For existing A output and default B01 candidates:

```bash
python 02_models.py
python 03_eval.py
```

C reads local_review/B01_candidate and writes local_review/C01_candidate.
The original root scores/metrics stay paired and unchanged. C freezes the new
metrics.json first, then renders all tables and figures from it; full slice,
case, Validation, coefficient, budget and PR data are registered. T5_all_numbers.csv
indexes every numeric value. Original Test protocol, K=2472, AP/Top-K formulas,
models and Validation-only selection are preserved. Historical numeric differences
are disclosed; the duration model remains an ablation, not the main model.


--&gt;
&lt;!-- DOCS-SPLIT 新增：仅添加组员修复指南入口，原环境与运行说明保留。 --&gt;
&lt;!-- P01整理前README原文保留

## A01 修订说明与复现指引

Part A的修复位置、修复前后区别、原因及组员本地操作步骤见 [A01修复指南](docs/A01_FIX_GUIDE.md)。请将该指南与带A01修改标记的源码一起使用。

--&gt;
&lt;!-- DOCS-SPLIT 新增结束 --&gt;

# INT6163 第8组银行外呼分析

本仓库用通话前信息生成订阅倾向排序，并在固定历史留出数据上比较名单效率。A01/B01/C01修复已分别通过用户28项、33项、36项技术重跑。当前为本地待发布整理版，尚未推送GitHub；D报告、F5和联系限制策略代价尚未制作。

## 从原始数据完整运行

使用GitHub已声明的Python3.9+和原requirements.txt，不额外规定某台电脑的精确Python或间接依赖版本。在已有本仓库原始数据及configs/features.yaml的项目根目录：

```powershell
python -m pip install -r requirements.txt
python scripts/reproduce_abc.py
```

依次出现PASS A、PASS B、PASS C及[ABC_REPRODUCED]表示完整运行成功。入口复制源码、配置及原CSV到新工作区，不复制已有outputs/figures，也不从发布快照读取缓存。实际环境、输入来源、输出与本次耗时保存在新运行清单中。

```text
local_review/ABC_reproduction/<本次编号>/
  input_manifest.json
  run_manifest.json
  A.log / B.log / C.log
  workspace/outputs/
  workspace/local_review/B01_candidate/outputs/
  workspace/local_review/C01_candidate/outputs/
  workspace/local_review/C01_candidate/figures/
```

local_review/ABC_reproduction/latest_run.txt保存最新运行目录。完整入口使用原始CSV，不联网获取新版本数据。

## 查看已验收结果

完整结果统一保存在[results/ABC_C01_verified.zip](results/ABC_C01_verified.zip)。解压后先看snapshot.json及其成员指纹，再看workspace/local_review/C01_candidate/outputs/metrics.json。表图与数据说明也在同一快照中，保留原工作区相对路径与输入/输出清单。

本轮Test为8238条，K=2472；主模型AP约0.448274、命中1200，规则基线命中924，多命中276、无效联系少276、漏报1340。两个276是同一固定K变化的两种表达，不相加。10%预算下规则命中536而主模型417，不能声称所有预算胜出。

根目录原有outputs/figures及data/README_data.md属于保留的历史产物，本轮发布没有逐个替换这些文件；查看修订后的统计、说明和图表请使用上述ZIP或重新运行。旧分数与旧metrics仍成套保留，不能与新结果混用。

## 修复说明和分步入口

三份共享修复指南已合并为[docs/ABC_FIX_GUIDE.md](docs/ABC_FIX_GUIDE.md)，包含46个修复点、源码行号、前后区别、原因、原环境声明和组员操作步骤。原被替换代码继续保留为注释，科学源代码未因打包重写。

若需要逐步检查，在项目根目录按顺序执行：

```powershell
python 01_data_quality.py
python 02_models.py
python 03_eval.py
```

A核对并沿用正确冻结切分；B默认写local_review/B01_candidate；C读取同次B清单并写local_review/C01_candidate。A/C Notebook调用同一权威脚本；首次运行C Notebook前先完成A、B。推荐完整入口，它在独立工作区中处理全部产物。

## 复现和解释边界

原requirements保持pandas2.2.3、scikit-learn1.6.1、PyYAML6.0.2、matplotlib3.9.4。Train内拟合预处理与模型，Validation选参，C对固定方案作Test最终评价。重复执行用于复现，不按Test重新调参；历史数值差异如实记录，不要求找回原作者未声明环境或追平旧概率。

含duration模型只作泄漏消融；本项目没有部署、因果/uplift或提高总体订阅率的证据。联系限制规则的额外损失尚未计算，现有1340个名单漏报不能代替该策略代价。GenAI确用于本轮代码修复、核验和材料整理；完整作业的引用、贡献与GenAI披露由D后续如实汇总。

## 本轮精简提交范围

本轮只提交源码/Notebook/入口、README、.gitattributes、.gitignore、合并指南和结果ZIP，共12个新增或修改文件。原始数据、requirements.txt、configs/features.yaml及其他原有文件继续保留。虚拟环境、编辑器设置、审计备份、本机日志及原三份独立指南不上传。本包不是最终报告或学校提交整包。

D04_01 原README保留结束 --&gt;

# INT6163第8组：银行外呼名单分析

本项目在通话前对记录排序，在同一联系预算下比较订阅命中、无效联系和漏报；补充固定联系限制的事后回放及建议责任流程。报告为手工定稿[report.docx](report.docx)，运行分析不会将它替换为模板。当前D04_01候选只整合公开运行入口与证据检查，尚未完成最终结果ZIP和学校整包。

## 环境

沿用原声明：Python 3.9或以上，安装[requirements.txt](requirements.txt)的四项固定依赖。原作者未声明的精确补丁版本不是新增要求。每次运行会记录实际Python和已安装分发包，记录不替代原环境标准。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/reproduce_all.py
```

其他系统激活对应虚拟环境后运行`python scripts/reproduce_all.py`。在VS Code中选择该虚拟环境解释器，从项目根目录执行。无需安装Codex、python-docx、PDF库或Office，即可重建全部分析并核对报告证据。查看和编辑Word可使用自己的文档软件。

A图及F5包含中文，系统需要可用CJK字体。F5默认依次尝试Microsoft YaHei、SimHei、Noto Sans CJK SC、WenQuanYi Micro Hei；如需指定：

```powershell
python scripts/reproduce_all.py --font-family "Noto Sans CJK SC"
```

不附带有版权限制的系统字体。字体不同可能导致图像字节不同；不得将这种差异说成科学结果改变。缺少覆盖字体时绘图明确停止。

A沿用原已验收字体配置Microsoft YaHei / SimHei；`--font-family`仅控制F5。只安装Noto字体不自动适配A。其他系统须具备原图配置支持的中文字体，字体适配和跨机结果应按实际运行核对；本阶段实测为记录的Windows环境。

## 统一入口做什么

1. 核对声明环境、原始CSV规范化内容、配置和代码、报告及其六幅嵌图。
2. 在runs/下创建全新的工作区，仅复制原数据、分析代码和配置；不复制既有outputs、figures、切分、模型分数或结果ZIP。
3. 从原始CSV运行A→B→C，再把同次ABC结果传入D01固定规则回放和D02图表生成。
4. 对照[REPORT_EVIDENCE.json](docs/REPORT_EVIDENCE.json)，检查全部科学结果、固定规则、F5数字结构和报告107处数字。整数与文本精确相同，浮点只允许绝对1e-12的舍入差异。
5. 记录每阶段日志、环境、输入和全部产物指纹；报告不重生成、不覆盖。

输出不覆盖根目录历史结果。为兼容已验收代码，内部新工作区会生成名为local_review的中间目录；不需要预先提交、复制或下载开发机器原local_review。

运行前可仅检查输入：

```powershell
python scripts/reproduce_all.py --check-only
```

成功末行包含：

```text
[ABCD_REPRODUCED] .../RUN_RESULTS.md
[REPORT_EVIDENCE] 107/107 matched; authored report unchanged
```

读取runs/latest_run.txt中的项目相对路径，打开该运行目录的RUN_RESULTS.md。该页指向本次统一metrics、Test比较表、T6和F5；artifact_index.json登记全部实际文件。不要用根目录历史outputs/figures替换本次结果。

## 报告及结果边界

- report.docx来自用户填写和修订的原稿；仅有已核对的提交副本，不要求成员重建空白模板。修改报告后须重新核对并更新证据登记，不自动改写旧报告数字。
- 主模型为原通话前Logistic；主工作点30%，Test比较不能回用于选参。duration仅为泄漏消融；低预算规则优于主模型的反例保留。
- 联系规则固定为previous≥3且poutcome=failure；主情景不递补，递补仅作预设对照。Test此前已看过，这是事后描述性回放，不是银行政策、真实人工放行或部署成效。
- 重建目标为原声明依赖下的同次科学结果；不承诺任意兼容系统逐位恢复旧GitHub训练分数。路径、时间、包记录和CSV原字节换行元数据单列，不冒充科学差异。
- 旧[ABC_C01_verified.zip](results/ABC_C01_verified.zip)与[ABC修复指南](docs/ABC_FIX_GUIDE.md)作为P01历史对照保留。统一入口不读取这个ZIP。完整D补充结果统一包、正式T5报告/PPT页码及最终白名单还在后续整合范围，当前候选不是学校完整最终包。

## 文件清单与阶段来源

| 文件 | 作用 |
|---|---|
| 01_data_quality.py / .ipynb | A数据质量、字段与切分 |
| 02_models.py、configs/features.yaml | B训练、Validation选参及特征配置 |
| 03_eval.py / .ipynb、c01_support.py | C留出评价、统一数字源与图表 |
| scripts/d01_contact_policy.py | 固定规则补充回放，科学实现沿用已验收版本 |
| scripts/d02_report_assets.py | F5与素材索引，科学图形实现沿用已验收版本 |
| scripts/reproduce_all.py | 本轮新增的无缓存统一调度与报告证据检查 |
| scripts/reproduce_abc.py | ABC内部从原始数据重建入口 |
| docs/REPORT_EVIDENCE.json | 报告科学参考、107数字及嵌图指纹；不含开发机绝对路径 |
| report.docx | 已填写的正式报告副本 |

原数据及许可见data/raw/bank-additional-names.txt、A生成的数据说明和报告参考资料。GenAI与成员贡献采用report.docx的实际声明；本次使用AI辅助材料整合及核验，未生成新实验结论。后续完整发布时再统一审查声明与材料范围。

## D04_01相对P01的新增与修订

| 文件与位置 | 原状态 | 本轮状态及原因 |
|---|---|---|
| scripts/reproduce_all.py / main | 只有ABC的分步重建入口 | 新增A→B→C→D01→D02统一调度；短运行ID加一层ABC工作区，避免Windows嵌套长路径。D04_01-01注释保留首版实现。 |
| scripts/reproduce_all.py / preflight、scientific、compare | 没有报告与完整补充回放的统一核对 | 固定输入与入口自身指纹，核对原声明环境、手工报告107个数字和完整科学参考。仅舍弃时间、路径等元数据，保留科学值及CSV规范化内容身份。 |
| docs/REPORT_EVIDENCE.json | P01未收录D报告证据 | 新增从已验收同次结果提取的参考、报告嵌图身份、固定规则及F5数字结构；它只用于重建后的比较，不被复制进训练工作区作为计算结果。 |
| README.md、.gitignore | 仅P01/ABC运行说明 | 补充公开统一命令、字体条件和手工报告边界；runs/排除提交。原README逐行注释保留，科学入口源码和旧46点指南未改。 |
| report.docx、scripts/d01_contact_policy.py、scripts/d02_report_assets.py | 尚未纳入P01的12文件方案 | 将已验收原件纳入本轮候选；三份文件均按原字节复制，不重新写报告或更改政策计算。 |

这17个拟新增或修改文件是D04_01入口候选；另有4个仓库原有必要输入。最终结果ZIP及材料白名单仍在后续整合，不能把此数目当作已经封版的学校提交清单。

D04_02 原README完整保留 END -->

# INT6163第8组：银行外呼名单分析

在通话前对记录排序，在同一联系预算下比较订阅命中、无效联系与漏报，并补充固定联系限制的事后回放和建议行动流程。正式报告为已填写的[report.docx](report.docx)；运行分析只核对报告证据，不生成或覆盖报告。

## 安装与运行

沿用原声明Python 3.9+与[requirements.txt](requirements.txt)中的pandas 2.2.3、scikit-learn 1.6.1、PyYAML 6.0.2、matplotlib 3.9.4。在VS Code选择项目虚拟环境，从项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/reproduce_all.py
```

其他系统使用对应环境的`python scripts/reproduce_all.py`。分析与打包不需要Codex、python-docx、PDF库或Office；查看Word可使用自己的文档软件。原作者未声明的精确系统补丁版本不是新增要求；运行清单如实记录实际版本。

A图沿用Microsoft YaHei / SimHei字体配置。F5依次尝试Microsoft YaHei、SimHei、Noto Sans CJK SC和WenQuanYi Micro Hei，也可用`--font-family`指定已安装字体。该参数只控制F5；只安装Noto不自动适配A。本阶段实测为记录的Windows环境；其他系统需具备A支持的中文字体。字体差异可能改变图像字节，科学数字仍须匹配；不附带系统字体。

## 查看结果

直接查阅已验收报告对应的[ABCD_verified.zip](results/ABCD_verified.zip)，解压后先打开README_RESULTS.md。本次只提供一个合并结果ZIP，包含49个文件：

| 包内位置 | 用途 |
|---|---|
| report/metrics.json | 正式数字源；原C及D01键值全部保留，仅增加report_evidence文档登记 |
| report/T5_数字核对表.md | 报告107处科学数字与实际报告页码 |
| report/T5_all_numbers.csv | 全部33,612个数值叶子索引；区分正文、图源、未引用值和元数据 |
| report/T5_report_claims.json | 可机读的107条报告引用及页码 |
| report/D01_policy_registration.json | 原计算前规则登记的共享摘录及原登记指纹 |
| workspace/ | 同次A、B、C、D01、D02原始输出与阶段清单，保持原字节 |
| run/、snapshot.json | 实际运行、输入输出指纹及包内路径映射 |

正式T5的报告页码绑定当前8页report.docx指纹，来自此前实际渲染与验收；分析脚本不重新分页Word。图源数据不冒称每个数值都在正文出现；未引用数字不编报告页码。PPT尚未登记，PPT页码全部保留“待E实际PPT核对”。包内早期阶段T5保留当时原稿，正式核对以report/为准。原始CSV、源码、配置和报告不重复装入ZIP。

## 从原始数据完整重建

统一入口先核对环境、原始CSV规范化内容、配置、源码、报告六图及107条数字登记，再在runs/创建全新工作区，运行A→B→C→D01→D02。计算不使用既有分数、切分、metrics或结果ZIP；科学重建通过后才生成正式T5和新ZIP。

```powershell
python scripts/reproduce_all.py --check-only
python scripts/reproduce_all.py
```

完整运行成功末尾包含：

```text
[RESULTS_PACKAGED] .../results/ABCD_verified.zip
[ABCD_REPRODUCED] .../RUN_RESULTS.md
[REPORT_EVIDENCE] 107/107 matched; authored report unchanged
```

读取runs/latest_run.txt中的相对路径，打开对应RUN_RESULTS.md。正式metrics、T5、ZIP、Test比较表、T6、F5及全部实际产物均由该页定位。报告和根目录历史outputs/figures不会被覆盖。内部local_review目录由本次运行新建，不需要开发机器的原local_review。

对已成功的一次运行可重复打包，不重新训练：

```powershell
python scripts/reproduce_all.py --package-run runs/<运行ID>
```

同一运行输入与输出未变时ZIP字节相同；若来源或产物改变则拒绝。不同新运行保留各自时间和来源元数据，不承诺ZIP字节相同。CSV的LF/CRLF会改变原字节SHA和字节大小；规范化内容指纹、样本与科学结果仍须一致。

## 解释边界

Train拟合，Validation选参，C只评价固定方案。主模型Logistic、30%预算与14个通话前特征保持；duration只用于泄漏消融。Test低预算规则优于主模型的反例保留。整数与文本精确一致；科学浮点核对的绝对容差为1e-12，不承诺任意兼容机器逐位追平旧训练分数。

联系限制固定previous≥3且poutcome=failure，主情景不递补，递补仅作固定对照。Test此前已暴露，补充结果是事后描述性回放，没有真实人工放行、部署或因果成效证据。原名单漏报1340、全段触发订阅42与额外漏报3分别登记，不能互相替代。

源数据说明与许可见[data/raw/bank-additional-names.txt](data/raw/bank-additional-names.txt)及包内workspace/data/README_data.md。实际成员贡献、Codex / GPT-6.1 Sol使用范围采用报告第7页声明。

## 源码、修订与提交范围

ABC七个入口保持已验收原字节；46项既有修复详见[ABC_FIX_GUIDE.md](docs/ABC_FIX_GUIDE.md)。D04-02只在D01默认快照、D02文件链接、统一入口与文档登记处调整衔接，未改模型、阈值、评价公式或原图。原替换代码在相应源码以D04_02编号注释保留。

| 文件与定位 | 原状态 | 当前状态及原因 |
|---|---|---|
| scripts/d01_contact_policy.py，D04_02-01 | 默认旧ABC快照 | 默认统一ABCD快照；单独回放也使用同批C来源 |
| scripts/d02_report_assets.py，D04_02-02 | 素材说明链接旧ZIP | 指向统一ABCD结果包，图形与数字计算不变 |
| scripts/reproduce_all.py，D04_02-03至10 | 只重建/比对，无正式包与页码 | 区分CSV字节元数据，校验页码登记，成功后调用打包器，支持同次重复打包 |
| scripts/result_bundle.py，numeric_documents / package_verified_run | 无统一归档器 | 新增完整索引、原产物指纹核对、确定性ZIP与安全路径检查 |
| docs/REPORT_EVIDENCE.json，report / claims / policy_registration | 无正式页码登记 | 绑定已验收报告及实际页码，PPT仍待实际稿；不作为训练输入 |
| README.md、docs/ABC_FIX_GUIDE.md | 旧阶段12/17文件及旧结果入口 | 更新当前结果入口，旧正文注释保留，46点修复仍可查阅 |
| .gitattributes、results/ABCD_verified.zip | 原旧结果包 | Word及ZIP按二进制处理；一个新合并ZIP替代候选中的旧ZIP |

<!-- D04_03 原状态段保留
当前候选为18个拟新增或修改文件，配合仓库原有4个必要输入（requirements.txt、features.yaml、原始CSV、原始数据说明）组成22文件运行集合。原P01和D04-01候选仍单独归档，不把它们的旧清单当本轮最终清单。当前尚待原GitHub基线覆盖组合验收和用户重跑；PPT、课程提交仍未完成，未推送。
D04_03 原状态段结束 -->

当前发布候选为18个拟新增或修改文件，配合仓库原有4个必要输入组成22文件最小运行集合。其他原仓库文件继续保留；根目录历史outputs/figures不作为本次结果来源。原P01及D04-01/D04-02候选单独归档。

原仓库基线为`bfdfedb3e6cf82ea59254279a5352af4f2a395e8`。D04-03按“原Git提交完整内容＋下列18文件”进行独立覆盖验收，并只按原requirements建立新虚拟环境；以实际验收结果为准，不把此措施说成任意系统/依赖解析都能逐位复原历史分数。运行输出保留早期阶段状态文字，当前发布状态以本说明和验收记录为准。候选仍待用户重跑和最终阅读，PPT与课程提交未完成，未推送。

### 需要新增或覆盖的18个文件

```text
.gitattributes
.gitignore
README.md
01_data_quality.py
01_data_quality.ipynb
02_models.py
03_eval.py
03_eval.ipynb
c01_support.py
scripts/reproduce_abc.py
scripts/d01_contact_policy.py
scripts/d02_report_assets.py
scripts/reproduce_all.py
scripts/result_bundle.py
docs/ABC_FIX_GUIDE.md
docs/REPORT_EVIDENCE.json
results/ABCD_verified.zip
report.docx
```

继续使用原仓库的`requirements.txt`、`configs/features.yaml`、`data/raw/bank-additional-full.csv`和`data/raw/bank-additional-names.txt`；无需上传它们的重复副本。保留原目录层级，勿把scripts/docs/results中的文件平铺到根目录。不上传.venv、runs、local_review、填写原稿或检查日志。报告仍以根目录report.docx提交副本为准；更改填写原稿后须重新核对与同步，不擅自拿旧证据对应新稿。

