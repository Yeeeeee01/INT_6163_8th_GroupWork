# README_D：项目文件用途与提交说明

本项目为INT6163第8组银行定期存款外呼分析。本说明回答三个问题：作业要求交什么、`report`分支需要哪些文件、哪些材料只在本地保留。2026年11月18日，报告已由用户确认通过；D04-03用户实际重跑39项全部通过。E的PPT及T5后续修改按用户指示暂缓，本轮保留已验收报告与现有T5。

## 1. 按哪两份要求整理

| 依据 | 明确要求 | 当前对应材料 |
|---|---|---|
| `INT6163_Group_Project.pdf`第1页 | 约2,400中文字报告（不含封面与参考文献），同时提交数据说明、代码或分析文件、主要结果和引用 | `report.docx`、分析源码/Notebook、原数据说明与统一结果ZIP |
| 同PDF第2页“报告提交检查” | 可运行代码/Notebook/分析文件、说明执行顺序的README、参考文献、素材来源和GenAI使用说明 | `README.md`、运行入口、报告第7页GenAI及第8页参考资料、下述来源清单 |
| `INT6163_第8组_小组分工.docx`的D“材料整合” | README写清依赖/执行顺序/随机种子/UCI取得方式；独立`CONTRIBUTIONS.md`按“文件→负责人→图表”说明贡献 | `README.md`、本说明第7节、`CONTRIBUTIONS.md` |
| 同DOCX的A/B/C/D“交什么” | 数据说明、字典、切分、分数、指标、T1—T5、F1—F5及报告章节—图表对应表 | 按同次结果统一收录在`results/ABCD_verified.zip`，具体位置见第4节 |

课程要求的是完整材料及可复现证据，没有规定必须提交所有本地审计日志、虚拟环境、旧稿或每次检查产生的目录。`README_D.md`是为组员和教师查阅补充的导航文件，课程原文没有点名这个文件名；`CONTRIBUTIONS.md`则是小组分工原文明确点名的交付物。

小组分工还要求最终课程材料打成一个ZIP；当前`ABCD_verified.zip`是分析结果包。最终课程整包的组装按后续安排处理，E/PPT不在本轮工作范围内。原要求没有强制另交PDF，本轮报告保持已通过的`report.docx`。

## 2. 当前提交范围：20个改动文件，目标report分支

原已验收清单是18文件；本次新增本说明和原文要求的独立贡献表，合计20文件，即6个覆盖、14个新增。原清单中16文件保持原字节，包括全部科学实现、报告、结果包；README和共享指南仅在开头补充当前导航，旧文完整保留。新增文档不改变模型、数据、阈值或任何科学结果。

| 仓库内相对路径 | 作用与提交依据 | 操作 |
|---|---|---|
| `report.docx` | D明确交付；用户已通过的报告，含引用、GenAI和成员信息 | 新增 |
| `README.md` | 原文明确要求的项目依赖与运行说明 | 覆盖 |
| `README_D.md` | 本次新增的文件分类、提交与结果导航 | 新增 |
| `CONTRIBUTIONS.md` | 小组分工明确要求的文件—负责人—图表贡献表 | 新增 |
| `01_data_quality.py` | A的权威计算入口，支持数据说明和质量证据重建 | 覆盖 |
| `01_data_quality.ipynb` | A明确交付的Notebook，调用同一权威脚本 | 覆盖 |
| `02_models.py` | B明确交付的模型训练与Validation选参入口 | 覆盖 |
| `03_eval.py` | C的权威评价入口 | 覆盖 |
| `03_eval.ipynb` | C明确交付的Notebook，调用同一权威脚本 | 覆盖 |
| `c01_support.py` | 当前C入口依赖的公共核验与数字登记实现 | 新增 |
| `scripts/reproduce_abc.py` | 原CSV到ABC的完整复现入口 | 新增 |
| `scripts/d01_contact_policy.py` | 联系限制固定规则的事后回放，支撑T6和行动代价 | 新增 |
| `scripts/d02_report_assets.py` | 生成F5及章节—图表—数字对应表 | 新增 |
| `scripts/reproduce_all.py` | 公开统一入口，运行A→B→C→D01→D02并核对报告 | 新增 |
| `scripts/result_bundle.py` | 统一数字索引与同次结果ZIP生成，供统一入口调用 | 新增 |
| `docs/ABC_FIX_GUIDE.md` | 46项ABC修复的位置、前后区别、原因与组员操作 | 新增 |
| `docs/REPORT_EVIDENCE.json` | 报告数字/图像身份、规则和实际报告页码登记 | 新增 |
| `results/ABCD_verified.zip` | 课程要求的主要结果，集中包含A/B/C/D已验收同次产物 | 新增 |
| `.gitattributes` | 本项目采用的Git换行及Word/ZIP二进制保护规则 | 新增 |
| `.gitignore` | 本项目采用的本地环境、缓存、运行及审计目录排除规则 | 新增 |

“原文明确点名”与“当前实现运行所需”均在上表注明；辅助脚本和Git规则不冒称课程逐个指定的文件名。提交时保留`docs/`、`scripts/`、`results/`层级，将20个文件放入仓库对应位置。

## 3. 原仓库已有、完整运行必须保留的4个输入

| 文件 | 用途 | 本次处理 |
|---|---|---|
| `requirements.txt` | 原GitHub声明的分析依赖 | 保留原版，未添加文档工具或锁定本机额外包 |
| `configs/features.yaml` | 主特征、消融配置及既定协议 | 保留原版 |
| `data/raw/bank-additional-full.csv` | 重建所用原始数据快照 | 保留内容与原行序，由入口核对规范化指纹 |
| `data/raw/bank-additional-names.txt` | 原始字段解释、来源及资料说明 | 保留原版 |

它们已存在于原仓库，所以无需作为本次新增/修改重复提交；制作离线可运行代码包时仍必须包含。这20个改动文件加上述4个输入构成24文件最小运行材料；原Git其余历史文件继续保留。单独复制本次改动文件时，还需同时取得原仓库输入。

## 4. 作业必需结果已放在统一ZIP的哪里

先解压`results/ABCD_verified.zip`并打开其中`README_RESULTS.md`。下表路径都相对该ZIP的解压根目录，不是需要另建的第二套提交文件。

| 原文要求/用途 | ZIP内实际文件或目录 |
|---|---|
| 数据说明、许可与21列字典说明 | `workspace/data/README_data.md` |
| 字段字典 | `workspace/outputs/data_dictionary.csv` |
| 冻结切分 | `workspace/outputs/split_v1.csv` |
| T1质量表及A统计 | `workspace/outputs/T1_数据质量表.md`、`workspace/outputs/A_summary.json` |
| F1字段分界、F1b行序漂移证据、F2血缘 | `workspace/figures/`内三张PNG |
| B分数与T2模型比较 | `workspace/local_review/B01_candidate/outputs/scores.csv`、同目录`T2_模型对比表.csv`及`.md` |
| 系数与选参证据 | 同一B目录的`logistic_coefficients.csv`、`model_selection_pool.csv` |
| C Test模型比较、T3切片、T4消融 | `workspace/local_review/C01_candidate/outputs/`中的对应表 |
| F3 PR曲线与F4预算曲线 | `workspace/local_review/C01_candidate/figures/` |
| 正式统一数字源 | `report/metrics.json`；保留原C/D01全部键值，只增加文档登记节 |
| 正式T5及完整数字索引 | `report/T5_数字核对表.md`、`report/T5_all_numbers.csv`、`report/T5_report_claims.json` |
| F5行动闭环与报告章节—图表对应表 | `workspace/local_review/D02_candidate/outputs/F5_行动闭环.png`、`.svg`及`章节_图表_数字对应表.md` |
| 联系限制代价T6与逐记录审计 | `workspace/local_review/D01_candidate/outputs/T6_联系限制补充评价.md`、`D01_逐记录审计.csv` |
| 原始阶段指标、运行清单与归档映射 | 各阶段`metrics.json`和运行清单、`run/`、`snapshot.json` |

正式T5已登记107处报告数字及8页报告的实际页码；现有内容保留，PPT页码未登记。包内早期C/D阶段T5及素材提示是当时记录，当前报告核对采用`report/`下的正式文件。49个ZIP成员及完整数值索引均已核验。

特别区分：ZIP成员名包含`workspace/local_review/`，是为了保留已验收产物及其原始来源结构；这些成员属于必须提供的结果内容，保留在ZIP中。下面第5节所说“仅供本地”的，是工作区根目录的开发审计目录，不能据同名路径删掉ZIP内的结果。

## 5. 仅供项目本地使用的材料

| 本地位置/文件 | 用途与处理 |
|---|---|
| `.venv/`、本地独立验证环境 | 本机解释器和依赖安装；他人按requirements新建环境，不上传环境副本 |
| `.vscode/` | 本机VS Code解释器与编辑器设置 |
| `.git/` | 本机Git元数据；不作为作业附件复制 |
| `__pycache__/`、`*.pyc` | Python运行缓存 |
| 工作区根目录`local_review/` | 审计、候选、旧稿、逐阶段重跑、失败诊断、字节备份和验收记录；整目录留在本地 |
| `local_review/D03_candidate/report_填写版.docx` | 用户已填写和修改的本地原稿；当前与提交版同字节，后续修改需重新核对并同步 |
| `local_review/D03_candidate/report.docx` | 旧自动生成稿的回归基线；保留原路径支持已验收检查 |
| `local_review/repairs/`、`checks/`、`before/`、旧修订目录 | 故障诊断、旧实现、源文件备份和历史核验，不逐份上传 |
| `local_review/publish_compact/P01/`、`publish_D04/D04_01`至`D04_03` | 旧12/17/18文件方案和已通过阶段的冻结记录，继续保留 |
| `local_review/publish_D04/report_branch_release/` | 本次20文件准备区；只取其`upload_files/`内文件放到仓库相对路径，准备区容器和清单日志留本地 |
| `runs/` | 他人执行公开入口后在自己的电脑生成的全新结果和日志，默认不逐次上传 |
| `scripts/d03_build_report.py`及Word/PDF渲染、核验辅助程序 | 本地文档制作工具；报告已经手工填写并通过，不要求组员重建空白模板 |
| `docs/PROGRESS.md`、`docs/ABC_FIX_LOG.md`、旧A/B/C独立指南、`PROJECT_GUIDE.md`、本地计划/审计说明 | 阶段进度和历史导航；当前共享修订依据为`docs/ABC_FIX_GUIDE.md`与本说明 |

本地准备区位于`local_review/`下，是为了隔离发布版与开发历史；其中选定的20个文件是待提交内容，准备区目录本身仍只在本地使用。

根目录`outputs/`、`figures/`、`data/README_data.md`及旧`results/ABC_C01_verified.zip`保留原Git或前阶段历史，供对照和回归。本次不额外覆盖它们；当前报告的数字和图表来源按第4节或本次运行的`RUN_RESULTS.md`查阅。原Git已跟踪的缓存/历史文件也不在本轮擅自删除。

## 6. 贡献、引用与GenAI材料

成员职责与可核验文件对应见[CONTRIBUTIONS.md](CONTRIBUTIONS.md)，姓名沿用已通过报告的贡献表；成员学号保留在报告中。E只登记既有分工，按本轮约定暂缓PPT及相关页码工作。

[report.docx](report.docx)第7页已有实际GenAI声明与成员贡献，第8页有19项参考资料及可点击引用。引用和GenAI不需要仅为凑文件数再拆成新的REFERENCES或GENAI文件。AI工具为Codex，模型按用户确认填写GPT-6.1 Sol；实际用途与核验采用报告已通过的声明。

| 素材/依据 | 来源及本项目使用方式 |
|---|---|
| 银行数据及原始字段说明 | [UCI Bank Marketing #222](https://archive.ics.uci.edu/dataset/222/bank+marketing)，[数据DOI](https://doi.org/10.24432/C5K306)，CC BY 4.0；采用bank-additional-full版本 |
| 研究背景文献 | Moro, Cortez & Rita (2014), Decision Support Systems 62:22—31，[DOI](https://doi.org/10.1016/j.dss.2014.03.001)；本轮沿用已核对书目信息，不声称重新取得或通读全文 |
| AP指标实现依据 | [scikit-learn 1.6 average_precision_score文档](https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.average_precision_score.html)及实际C代码 |
| F1/F1b/F2 | 由A脚本依据本项目数据和字段字典生成 |
| F3/F4 | 由C脚本依据同次评价数据生成 |
| F5 | 由D02脚本依据固定规则和冻结数字源生成，表示建议流程 |
| 外部软件依赖 | 原requirements中的pandas、scikit-learn、PyYAML、matplotlib；具体使用见对应脚本和报告参考资料 |

原课程PDF和小组分工DOCX用于核对要求，保留原位置；它们不是本次新增上传的项目分析成果。

## 7. 复现入口与本地整理方式

以下命令在已取得原仓库、并合并本次20文件后的仓库根目录执行。原工作根目录为了保留历史验收路径，未被准备区版本批量覆盖；本地查阅发布版时以20文件准备区为准。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/reproduce_all.py --check-only
.\.venv\Scripts\python.exe scripts/reproduce_all.py
```

依赖仍以原GitHub的Python 3.9+及四项固定包版本为依据；模型随机种子42，按原行序60/20/20切分，切分本身不随机。需要恢复原始快照时，在UCI页面下载bank-additional.zip并选用bank-additional-full.csv及其names说明，放到`data/raw/`，保留原行序；入口自动检查数据内容指纹。

A图沿用Microsoft YaHei/SimHei字体配置，F5支持README中列出的CJK字体。本次已在Windows/Python3.12.14的新环境中实测；本机实际包版本不取代原依赖声明。分析不需要Word、PDF工具或Codex运行时。

统一入口从原CSV依次运行A/B/C/D01/D02，生成新结果并核对报告107处数字。读取`runs/latest_run.txt`并打开对应`RUN_RESULTS.md`。当前图表、T5和ZIP不靠旧缓存复制生成，手工定稿报告保持原字节。每台机器和未来依赖解析仍由公开入口实际核对。

本次整理采用“保留原件＋明确当前提交入口”的方式，没有重命名或搬移原数据、脚本、报告、冻结产物或历史验收目录。当前20文件清单、原验收科学文件保持证明和本地整理记录保存在`local_review/publish_D04/report_branch_release/`；旧18文件方案继续归档。目标分支为`report`，本轮没有提交或推送。
