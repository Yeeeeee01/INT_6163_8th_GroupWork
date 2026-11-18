# README_D：D部分工作与整合查阅入口

本项目为INT6163第8组Bank Marketing外呼分析。`report`分支以**main的完整项目**为基础，整合ABC修复与D报告成果；不把其他成员的资料改成D的附属材料。修复后的文件在原路径直接替代main版本，原版可在main及Git历史查阅。

先读本页了解文件和修改，再按[README.md](README.md)运行全项目；成员职责见[CONTRIBUTIONS.md](CONTRIBUTIONS.md)。

## 1. D需要查阅的三个直接交付物

| 小组分工D“交什么” | 当前直接文件 | 内容 |
|---|---|---|
| 报告 | [report.docx](report.docx) | 已填写定稿；六章正文、六图、三张科学表、GenAI与成员贡献、参考资料 |
| F5行动闭环 | [outputs/F5_行动闭环.png](outputs/F5_行动闭环.png)、[SVG](outputs/F5_行动闭环.svg) | 预算→联系限制→复核→外呼→留痕；图内数字来自同次回放 |
| 报告章节—图表对应表 | [outputs/章节_图表_数字对应表.md](outputs/章节_图表_数字对应表.md) | 报告实际六章、嵌入图表、对应文件和20组关键证据 |

三个交付物均直接可见，不放在分析结果压缩包内。报告第7页含GenAI和成员贡献，第8页含19条参考资料及可点击引用；无需再拆出重复的引用或AI说明文件。

## 2. 按作业要求完成了什么

| 要求来源 | 内容 | 对应文件 |
|---|---|---|
| `INT6163_Group_Project.pdf`第1页 | 约2400中文字报告（不含封面、参考文献），数据说明、分析文件、主要结果和引用 | 报告、data/、ABC代码与Notebook、outputs/及figures/ |
| 同PDF第2页报告提交检查 | 可运行代码、执行顺序README、引用、素材来源与GenAI说明 | README、完整入口、报告第7—8页、本页来源说明 |
| `INT6163_第8组_小组分工.docx`的D | 六章报告、F5、章节—图表表、行动代价、限制与责任 | 上述三个直接交付物、T6、统一metrics |
| 同DOCX“材料整合” | 依赖、顺序、随机种子、UCI取得方式；独立CONTRIBUTIONS.md | README、本页第6节、CONTRIBUTIONS.md |
| 同DOCX的ABC | 数据说明、字典、切分、分数、指标、T1—T5及F1—F4 | 原项目标准目录中的直接文件，详见第4节 |

D整合了ABC证据，复核报告数字、引用和图表来源；补充固定联系限制的事后回放，将额外漏报与原模型漏报分开；绘制F5并整理行动责任、隐私及外推限制。完整入口可从原始CSV重建ABC与D分析，核对定稿报告107处数字，不重新生成或覆盖已手工填写的报告。

课程最终整包要求与仓库资源展示是不同环节：此分支以直接文件供组员查阅；最终课程打包按课程提交方式处理。文件清单只登记实际存在的材料，不用占位PPT或虚构页码表示已完成。

## 3. report与main的关系及修改边界

main基线为`bfdfedb3e6cf82ea59254279a5352af4f2a395e8`。本分支保留main全部32个路径，修复和新结果沿用原路径；没有另建“main旧版”和“修复版”两套公开文件。原始CSV、原说明、requirements、features配置与冻结切分方案保留。

当前完整项目57个文件：7个沿用main、25个原路径修订、25个新增。这里是完整分支文件数，不是需要在已有仓库中重复上传所有文件的意思。分类按LF规范化文本内容比较；其中split_v1.csv仅规范换行，行号和分段与main相同，Git仍可能将其显示为修改。

| 范围 | main原状或旧整合方式 | report当前处理与原因 |
|---|---|---|
| A入口、字典及说明 | Notebook依赖__file__，脚本缺少README生成；字段用途与实际配置有矛盾 | 同一脚本供两入口调用，修正用途、unknown和隐私表述；核对输入、切分与来源 |
| B训练 | 可训练，但缺少可核验的环境、来源、输出及新旧差异说明 | 保持训练和Validation选参，新增同次清单与候选输出保护，不用Test选参 |
| C评价 | 指标已计算，来源绑定、完整数字与报告索引、离散PR等不足 | 保持AP/TopK业务计算，补来源核验、独立核对、全量索引与图表可追溯性 |
| 原outputs/与figures/ | 仍是历史结果，而报告使用重建结果，容易混读 | 用同次重建结果在原路径更新，表、分数、图与报告统一；逐项用途见下表 |
| metrics与T5 | main只有原C结果，页码未绑定当前报告 | 统一保留C科学键，追加D01和report_evidence；T5绑定107处报告数字及实际页码 |
| README | main以ABC为主体 | 以main原文结构维护ABC说明，再补完整运行与D总结；D详细导航集中在本页 |
| ABC修复指南 | 独立docs/ABC_FIX_GUIDE.md，与本页重复导航 | 46点全部并入本页第5节；独立指南撤下，旧稿仅在本地及Git历史保留 |
| 分析结果ZIP | 新旧结果包与根目录产物并存，需解压查找D成果 | 撤下新增ABCD结果ZIP，直接发布到data/、outputs/、figures/；原main的UCI下载存档不属于分析结果包 |
| 完整入口及默认读取 | 旧发布模块生成ZIP，D01默认读取ZIP | 生成run/publication直接目录；D01默认取最新新运行ABC，可显式指定--abc-run |

### 历史分数与复现范围

原main表与重建表的个别分数存在细微差异，原仓库未声明完整的原训练环境，不能仅凭旧CSV判定唯一成因。公开运行以原requirements声明为环境依据，不要求与作者未声明的环境完全相同，也不为追平旧数修改训练、切分或评价。

例如Test主Logistic AP：main为`0.44827597373273753`，本次重建为`0.44827396573339506`；两者同K命中均为1200。报告采用本分支同次重建的整套结果，不能混用main旧分数或旧图。

已在仅按原requirements安装的隔离环境中，从原CSV完整重建并核对报告；这说明本方案可在声明环境基础上完整执行。并不承诺所有未来Python、间接依赖或字体组合都产生历史CSV逐字节相同的文件。入口记录实际环境，核对科学值与107处报告数字；数值不匹配时停止并保留报告，不静默把旧参考值当计算结果。时间戳、运行路径和字体像素不等同于科学值。

<a id="snapshot"></a>
## 4. 完整文件清单、用途与提交依据

保留下列完整目录结构。报告、ABC源代码/Notebook、数据说明、主要表图和贡献表属于作业材料；复现脚本、证据契约及运行清单是本实现保证可运行、可核验所需的支持文件，课程未逐一点名这些辅助文件名。Git规则是协作配置；main原缓存仅为继承资源。

### 项目说明与报告

| 文件 | 相对main | 用途 |
|---|---|---|
| [README.md](README.md) | 原路径修订 | 从main项目说明继续维护的ABC执行顺序与D总结，项目总入口 |
| [README_D.md](README_D.md) | 新增 | D必读入口、完整文件清单、main差异及46项修复 |
| [CONTRIBUTIONS.md](CONTRIBUTIONS.md) | 新增 | 作业点名的文件→负责人→图表贡献表 |
| [report.docx](report.docx) | 新增 | D报告定稿；含六章、引用、GenAI和已填写成员信息 |

### 代码、Notebook与证据登记

| 文件 | 相对main | 用途 |
|---|---|---|
| [01_data_quality.ipynb](01_data_quality.ipynb) | 原路径修订 | A Notebook，定位项目后调用相同脚本，旧代码格注释保留 |
| [01_data_quality.py](01_data_quality.py) | 原路径修订 | A权威计算入口；来源、质量、字典、切分与三张图 |
| [02_models.py](02_models.py) | 原路径修订 | B训练、Validation选参、分数和运行清单 |
| [03_eval.ipynb](03_eval.ipynb) | 原路径修订 | C Notebook，调用同一评价入口 |
| [03_eval.py](03_eval.py) | 原路径修订 | C固定Test评价、误差、消融、案例及预算分析 |
| [c01_support.py](c01_support.py) | 新增 | C输入核验、AP核对、完整数字索引与清单支持 |
| [docs/REPORT_EVIDENCE.json](docs/REPORT_EVIDENCE.json) | 新增 | 原输入内容、报告身份、107数字/页码、六图、规则及章节证据契约 |
| [scripts/d01_contact_policy.py](scripts/d01_contact_policy.py) | 新增 | 固定联系限制事后回放；无模型拟合或阈值搜索 |
| [scripts/d02_report_assets.py](scripts/d02_report_assets.py) | 新增 | 从同次指标绘制F5及阶段证据素材 |
| [scripts/reproduce_abc.py](scripts/reproduce_abc.py) | 新增 | 原CSV→ABC全新工作区执行入口 |
| [scripts/reproduce_all.py](scripts/reproduce_all.py) | 新增 | 原CSV→ABC→D01→D02统一入口，核对107处报告数字 |
| [scripts/result_bundle.py](scripts/result_bundle.py) | 新增 | 统一入口依赖；名称沿用，但当前发布直接目录、正式T5和章节表，不生成结果ZIP |

### 依赖、配置与数据

| 文件 | 相对main | 用途 |
|---|---|---|
| [configs/features.yaml](configs/features.yaml) | 沿用main | main原14项主特征与macro/duration消融方案 |
| [data/README_data.md](data/README_data.md) | 原路径修订 | A实际生成的数据说明、许可、质量、字段与切分协议 |
| [data/raw/bank-additional-full.csv](data/raw/bank-additional-full.csv) | 沿用main | main原始41188条数据，保留原行序 |
| [data/raw/bank-additional-names.txt](data/raw/bank-additional-names.txt) | 沿用main | UCI原始说明、字段解释与数据覆盖期 |
| [data/raw/bank-additional.zip](data/raw/bank-additional.zip) | 沿用main | main原有UCI下载存档；CSV已直接提供，无需解压查阅结果 |
| [requirements.txt](requirements.txt) | 沿用main | main原四项固定依赖；没有加入Word/PDF或Codex工具 |

### 表、指标、分数与数字索引

| 文件 | 相对main | 用途 |
|---|---|---|
| [outputs/A_summary.json](outputs/A_summary.json) | 原路径修订 | A结构化统计、字段配置和双指纹 |
| [outputs/B_run_manifest.json](outputs/B_run_manifest.json) | 新增 | 同次B源码、环境、输入和原始输出指纹 |
| [outputs/C_run_manifest.json](outputs/C_run_manifest.json) | 新增 | 同次C清单及与B来源配对 |
| [outputs/C_测试集模型比较表.md](outputs/C_测试集模型比较表.md) | 原路径修订 | 7模型相同Test、相同K的AP/TopK比较 |
| [outputs/D01_policy_registration.json](outputs/D01_policy_registration.json) | 新增 | 计算前规则登记，说明非Test阈值寻优 |
| [outputs/D01_policy_spec.json](outputs/D01_policy_spec.json) | 新增 | 固定示例闸门、主情景与对照口径 |
| [outputs/D01_run_manifest.json](outputs/D01_run_manifest.json) | 新增 | D01输入、ABC来源和原始阶段输出指纹 |
| [outputs/D01_逐记录审计.csv](outputs/D01_逐记录审计.csv) | 新增 | 两分段共16476条原名单/限制/递补审计 |
| [outputs/F5_行动闭环.png](outputs/F5_行动闭环.png) | 新增 | D点名交付F5；可直接预览的行动建议流程 |
| [outputs/F5_行动闭环.svg](outputs/F5_行动闭环.svg) | 新增 | 同一F5矢量格式，供报告排版或放大 |
| [outputs/T1_数据质量表.md](outputs/T1_数据质量表.md) | 原路径修订 | 缺失标签、重复、哨兵及漂移证据摘要 |
| [outputs/T2_模型对比表.csv](outputs/T2_模型对比表.csv) | 原路径修订 | Validation模型比较，可读取表格 |
| [outputs/T2_模型对比表.md](outputs/T2_模型对比表.md) | 原路径修订 | Validation模型比较，供直接查阅 |
| [outputs/T3_误差切片表.md](outputs/T3_误差切片表.md) | 原路径修订 | 21切片，包含分母、混淆数、误报及小样本提醒 |
| [outputs/T4_duration消融表.md](outputs/T4_duration消融表.md) | 原路径修订 | duration泄漏诊断，不能用作部署主模型 |
| [outputs/T5_all_numbers.csv](outputs/T5_all_numbers.csv) | 新增 | 完整33612个数值叶子、类型、用途分类及页码状态 |
| [outputs/T5_report_claims.json](outputs/T5_report_claims.json) | 新增 | 107处报告数字的值、格式和页码结构化登记 |
| [outputs/T5_数字核对表.md](outputs/T5_数字核对表.md) | 原路径修订 | 107处报告数字→JSON键→报告实际页码 |
| [outputs/T6_联系限制补充评价.md](outputs/T6_联系限制补充评价.md) | 新增 | 不递补和递补情景、联系数、命中及额外漏报 |
| [outputs/data_dictionary.csv](outputs/data_dictionary.csv) | 原路径修订 | 21列字典，入模标记取自实际features配置 |
| [outputs/logistic_coefficients.csv](outputs/logistic_coefficients.csv) | 原路径修订 | 标准化及编码后的Logistic系数，只解释条件关联 |
| [outputs/metrics.json](outputs/metrics.json) | 原路径修订 | 统一数字源；C原科学键+D01补充+report_evidence文档登记 |
| [outputs/model_selection_pool.csv](outputs/model_selection_pool.csv) | 原路径修订 | Validation全部候选参数及AP，不含Test选参 |
| [outputs/publication_manifest.json](outputs/publication_manifest.json) | 新增 | 同次公开文件内容指纹、原阶段路径→公开路径及指标增补映射 |
| [outputs/scores.csv](outputs/scores.csv) | 原路径修订 | 7模型×Validation/Test概率；C与D的同次预测输入 |
| [outputs/split_v1.csv](outputs/split_v1.csv) | 沿用main | 原行序60/20/20冻结切分 |
| [outputs/章节_图表_数字对应表.md](outputs/章节_图表_数字对应表.md) | 新增 | D点名交付章节—图表表；对应实际六章、六图、三表及20组证据 |

### ABC图

| 文件 | 相对main | 用途 |
|---|---|---|
| [figures/F1_通话前后字段分界图.png](figures/F1_通话前后字段分界图.png) | 原路径修订 | A：通话前可知19列、主模型实际14列及禁用字段 |
| [figures/F1b_时间漂移证据.png](figures/F1b_时间漂移证据.png) | 原路径修订 | A：原行序分段正类率；无精确Test日期或单调宣称 |
| [figures/F2_数据血缘图.png](figures/F2_数据血缘图.png) | 原路径修订 | A：原始数据、处理与留出评价的血缘 |
| [figures/F3_PR曲线.png](figures/F3_PR曲线.png) | 原路径修订 | C：7模型Test PR与AP，含离散/常数基线 |
| [figures/F4_预算收益曲线.png](figures/F4_预算收益曲线.png) | 原路径修订 | C：10%—100%固定预算收益，保留规则优于主模型的预算点 |

### Git规则与main原有缓存

| 文件 | 相对main | 用途 |
|---|---|---|
| [.gitattributes](.gitattributes) | 新增 | Git文本LF及Word/PNG/原数据ZIP二进制规则 |
| [.gitignore](.gitignore) | 新增 | 忽略后续生成的环境、运行、缓存与本地审计 |
| [__pycache__/01_data_quality.cpython-314.pyc](__pycache__/01_data_quality.cpython-314.pyc) | 沿用main | main已跟踪的历史运行缓存，原样继承；不是运行依赖或D新增成果 |

### 如何读清单与来源

[publication_manifest.json](outputs/publication_manifest.json)绑定本次公开文件及其内容指纹；文本跨系统换行可比较`lf_normalized_sha256`，Word/PNG应比较原字节。它不包含自身的自引用指纹，也不将README等协作文档冒充为训练输入。

B、C、D01运行清单保留原阶段记录，其相对路径指向同次运行工作区。`stage_to_public`登记阶段结果到本页公开路径的映射；`original_stage_artifacts`保留原输出指纹。统一metrics在C结果上追加D01和文档节，正式T5与章节表也经过发布整理，因此不把这些增强文件冒称为某个原阶段文件的逐字节副本。成员直接读标准目录，复核原始阶段时查看自己重建run中的清单。

<a id="abc-repairs"></a>
## 5. ABC相对main修复的全部46点

原版在main，修复版在本分支相同文件路径。以下保留A01/B01/C01编号、源码位置、前后区别及原因，合并自原ABC_FIX_GUIDE；按编号可在源码内搜索。Python被替换实现已注释保留，Notebook旧格保留为注释；无需额外上传旧代码文件。

<a id="a01"></a>
<details>
<summary>A：数据质量与入口，21点</summary>

| 修改点 | 文件位置 | 修复前 | 修复后 | 原因 |
|---|---|---|---|---|
| A01-01 模块说明 | [A01-01 新实现](01_data_quality.py#L23-L32)；[旧实现注释](01_data_quality.py#L2) | 局部说明使用未固定版本的安装命令，未交代修订留痕。 | 说明环境按GitHub README及requirements；增加隔离输出与备份说明。 | 明确修复边界与运行依据。 |
| A01-02 标准库导入 | [A01-02 新实现](01_data_quality.py#L38-L42) | 没有参数解析、依赖版本核对和备份所需的辅助导入。 | 新增argparse、importlib.metadata、shutil。 | 支撑入口、核对和备份；不是新增分析方法。 |
| A01-03 配置读取支持 | [A01-03 新实现](01_data_quality.py#L49-L51) | A字段说明与B特征配置分开维护。 | 导入仓库已有依赖PyYAML，读取features.yaml。 | 让字段说明取自同一实际配置。 |
| A01-04 输出路径、环境检查与备份 | [A01-04 新实现](01_data_quality.py#L66-L136)；[旧实现注释](01_data_quality.py#L59) | 输出位置固定；已有产物通常直接被新产物覆盖。 | 支持项目内--output-root；核对GitHub已声明依赖；生成前备份；新增Markdown原文保留函数。 | 允许安全隔离重跑，记录修改前状态。 |
| A01-05 原始数据内容指纹 | [A01-05 新实现](01_data_quality.py#L158-L165) | 只有原始字节SHA256，换行改变时难以辨别内容是否变化。 | 保留原字节SHA，另外计算CRLF/CR转LF后的内容SHA；核对冻结内容。 | 解释跨系统换行差异，源CSV保持原字节。 |
| A01-06 提前校验冻结切分 | [A01-06 新实现](01_data_quality.py#L171-L191) | 已有split时未由A核对内容。 | 校验列名、连续row_id与原行序60/20/20分段。 | 错误切分在生成统计和图表前被拒绝。 |
| A01-07 unknown注释语义 | [A01-07 新实现](01_data_quality.py#L219-L221)；[旧实现注释](01_data_quality.py#L216) | 注释将unknown称为真实类别。 | 明确unknown是缺失标签，当前保留为独立类别。 | 描述真实处理，不改变编码选择。 |
| A01-08 清洗决定表述 | [A01-08 新实现](01_data_quality.py#L229-L231)；[旧实现注释](01_data_quality.py#L226) | CLEAN_ACTIONS将unknown写为真实类别。 | 改为缺失标签保留为独立类别，继续不删除、不插补。 | 表格说明与字段语义一致。 |
| A01-09 contact备注 | [A01-09 新实现](01_data_quality.py#L260-L262)；[旧实现注释](01_data_quality.py#L257) | 备注写“仅作误差切片”，实际进入B主模型。 | 改为进入主模型、不单独作为联系依据。 | 修正文案与实际使用的矛盾。 |
| A01-10 month备注 | [A01-10 新实现](01_data_quality.py#L266-L268)；[旧实现注释](01_data_quality.py#L263) | 备注写“仅作误差切片”，实际进入B主模型。 | 改为进入主模型，同时保留无精确日期的说明。 | 保持说明准确。 |
| A01-11 day_of_week备注 | [A01-11 新实现](01_data_quality.py#L272-L274)；[旧实现注释](01_data_quality.py#L269) | 备注写“仅作误差切片”，实际进入B主模型。 | 改为进入主模型，同时保留无精确日期的说明。 | 保持说明准确。 |
| A01-12 字典入模标记 | [A01-12 新实现](01_data_quality.py#L292-L294) | 入模与否是手工写入字典的另一份清单。 | 根据features.yaml的main集合生成进主模型列。 | 降低两份清单再次失步的可能。 |
| A01-13 F1字段用途文字 | [A01-13 新实现](01_data_quality.py#L318-L320)；[旧实现注释](01_data_quality.py#L315) | contact/month/day_of_week标成仅作切片。 | 图内改为主模型使用。 | 图、字典与B配置一致。 |
| A01-14 F1字段数量文字 | [A01-14 新实现](01_data_quality.py#L327-L329)；[旧实现注释](01_data_quality.py#L324) | 未清楚区分可用字段与实际输入数量。 | 明确19列通话前可知、实际主模型使用14列。 | 避免把可知字段全部解释为主模型输入。 |
| A01-15 split生成及沿用 | [A01-15 新实现](01_data_quality.py#L432-L442)；[旧实现注释](01_data_quality.py#L422) | 有文件就跳过生成，随后直接读取。 | 正确切分验证后沿用且不重写；新切分验证后写出。 | 保留既定划分并防止错误输入被静默沿用。 |
| A01-16 A_summary来源字段 | [A01-16 新实现](01_data_quality.py#L479-L486) | 汇总以原有数据统计为主。 | 增加规范化指纹、入模字段及数量、GitHub环境依据和声明依赖。 | 支持后续追溯；没有替换C冻结指标。 |
| A01-17 T1生成模板 | [A01-17 新实现](01_data_quality.py#L556-L606)；[旧实现注释](01_data_quality.py#L505) | 部分措辞混淆缺失语义、换行指纹，或超出已做实验。 | 补双指纹并修正unknown、漂移和外推表述。 | 结论与实际证据范围匹配。 |
| A01-18 T1写入 | [A01-18 新实现](01_data_quality.py#L610-L612)；[旧实现注释](01_data_quality.py#L607) | 重新生成直接写入当前Markdown。 | 改用保留原文HTML注释的写入函数。 | 组员可在编辑器核对旧文，GitHub渲染显示当前有效正文。 |
| A01-19 README生成步骤 | [A01-19 新实现](01_data_quality.py#L617-L813) | Python脚本止于T1；生成README的代码只在Notebook中。 | 把完整README生成补入权威脚本。 | 脚本和Notebook产生同样的A交付物。 |
| A01-20 README安装入口 | [A01-20 新实现](01_data_quality.py#L714-L811)；[旧实现注释](01_data_quality.py#L618) | 生成的README还使用pip install pandas matplotlib。 | 改为python -m pip install -r requirements.txt，并说明GitHub为环境依据。 | 组员不会按旧说明安装一套未固定的依赖。 |
| A01-21 F1b图题 | [A01-21 新实现](01_data_quality.py#L402-L404)；[旧实现注释](01_data_quality.py#L399) | “越靠后的记录越高”可能被理解为逐段单调。 | 改为“后段总体正类率更高”。 | 图题符合实际非单调的分段变化，柱形数值不变。 |

</details>

<a id="b01"></a>
<details>
<summary>B：训练产物与追溯，11点</summary>

| 修改点 | 文件位置 | 修复前 | 修复后 | 原因 |
|---|---|---|---|---|
| B01-01 说明与边界 | [新实现](02_models.py#L5-L12)；[原代码注释](02_models.py#L2) | 原说明没有交代候选与冻结版本的关系。 | 明确GitHub环境依据、新结果隔离和原结果保护。 | 防止把本机候选当作新标准。 |
| B01-02 辅助标准库 | [新实现](02_models.py#L18-L27) | 无运行记录、指纹和备份辅助导入。 | 增加argparse、hashlib、metadata、platform、shutil等标准库。 | 补足追溯，不新增模型依赖。 |
| B01-03 输出默认位置 | [新实现](02_models.py#L49-L52)；[原代码注释](02_models.py#L46) | 默认覆盖根outputs，可能使新scores与旧C指标不匹配。 | 原outputs作为只读参考；默认候选写到local_review/B01_candidate/outputs。 | 保持旧scores与C冻结结果配对。 |
| B01-04 环境与来源函数 | [新实现](02_models.py#L97-L275) | 缺少完整环境、输入、输出和旧预测对比记录。 | 按GitHub声明检查；另记实际环境；核对输入内容；隔离、备份、校验输出并生成运行清单。 | 未声明项保持缺失，不反推原机版本。 |
| B01-05 配置与切分校验 | [新实现](02_models.py#L288-L295) | 配置seed、标签或行号字段与代码不一致时可能未明确指出。 | 校验seed=42、yes、y、row_id，以及切分列名、缺失、重复和整数行号。 | 避免记录配置与实际执行协议失步。 |
| B01-06 特征清单结构 | [新实现](02_models.py#L329-L332) | 未明确检查列表类型与重复项。 | 先检查结构与重复，再执行原特征限制。 | 保持既定特征，提前报告错误输入。 |
| B01-07 main入口 | [新实现](02_models.py#L461-L469)；[原代码注释](02_models.py#L457) | 没有按次运行的环境与输入来源快照。 | 训练前解析输出位置、核对GitHub声明和输入指纹。 | 将本次输出绑定实际输入与源码。 |
| B01-08 候选旧版备份 | [新实现](02_models.py#L608-L611)；[原代码注释](02_models.py#L605) | 候选重复运行可能覆盖已有产物。 | 写出前逐字节备份候选文件并生成清单。 | 保留运行历史。 |
| B01-09 预测输出校验 | [新实现](02_models.py#L623-L626)；[原代码注释](02_models.py#L620) | 直接导出分数。 | 检查键唯一、概率有效、七模型两分段及逐行覆盖后再导出；仍保留原10位有效数字格式。 | 确保交给C的候选文件完整且可核对。 |
| B01-10 T2 Markdown | [新实现](02_models.py#L672-L674)；[原代码注释](02_models.py#L669) | 重新生成直接覆盖当前文字。 | 保留旧正文HTML注释，科学表格正文不改。 | 满足旧文保留约定。 |
| B01-11 完成记录 | [新实现](02_models.py#L701-L703) | 只打印文件位置，缺少整次运行清单。 | 输出B_run_manifest.json和B_legacy_comparison.json，明确候选状态与历史环境未恢复。 | 支持追溯与差异解释，避免虚报旧结果已精确重现。 |

</details>

<a id="c01"></a>
<details>
<summary>C：评价与数字核对，14点</summary>

| 修改点 | 文件位置 | 修复前 | 修复后 | 原因 |
|---|---|---|---|---|
| C01-01 说明 | [原文注释](03_eval.py#L2) / [新代码](03_eval.py#L26) | 默认根目录产物，未说明新旧运行关系。 | 说明GitHub环境标准、同次候选路径及完整入口。 | 明确复刻口径与候选位置 |
| C01-02 导入 | [原文注释](03_eval.py#L48) / [新代码](03_eval.py#L52) | 无统一登记/渲染模块。 | 增加c01_support模块，数值评价公式仍在03_eval.py。 | 共享数字登记和渲染辅助模块 |
| C01-03 输入输出路径 | [原文注释](03_eval.py#L60) / [新代码](03_eval.py#L69) | 固定读取根outputs/scores，写回旧metrics。 | 默认衔接B01_candidate，写C01_candidate；支持显式输入。 | 默认衔接同次B候选，避免覆盖原冻结分数和指标 |
| C01-04 切分检查 | [原文注释](03_eval.py#L104) / [新代码](03_eval.py#L117) | 仅核对Test行号。 | 核对全部41188个行号及Train/Validation/Test连续60/20/20。 | 核对全部连续切分，避免只检查Test遗漏Train或Validation错误 |
| C01-05 分数检查 | [原文注释](03_eval.py#L152) / [新代码](03_eval.py#L170) | 只校验Test模型和逐行对应。 | 检查7模型2分段115332行、唯一键、[0,1]有限概率和全部行号。 | 校验完整7模型两分段的唯一键与概率，拒绝损坏或错版分数 |
| C01-06 模型表 | [原文注释](03_eval.py#L421) / [新代码](03_eval.py#L451) | 直接从内存models写表。 | 先落盘metrics，再只从该JSON生成模型表。 | 模型表只读取已落盘的统一数字 |
| C01-07 切片和案例 | [原文注释](03_eval.py#L456) / [新代码](03_eval.py#L510) | JSON缺具体记录；解释写死百分比，直接建议联系上限。 | 登记全部切片/案例；说明随本次结果取数；联系上限尚未评价。 | 切片和案例纳入JSON；解释文字动态取数，不预先声称联系上限已评价 |
| C01-08 duration消融 | [原文注释](03_eval.py#L515) / [新代码](03_eval.py#L566) | 表从models和T2分别取数。 | Validation与Test先统一登记，再生成表；原计算口径不变。 | 消融表从统一登记的Validation和Test数值生成 |
| C01-09 T5核对 | [原文注释](03_eval.py#L571) / [新代码](03_eval.py#L622) | 仅12个常用数字。 | 扩展常用数字键，并新增所有数值叶节点CSV索引，页码待D/E填写。 | 扩展常用核对表和全部数值叶节点索引，供报告逐项引用 |
| C01-10 F3 PR曲线 | [原文注释](03_eval.py#L627) / [新代码](03_eval.py#L678) | PR点直线相连，图下面积易与AP混淆。 | 坐标入JSON，使用post阶梯；阶梯积分与average_precision_score一致。 | PR坐标纳入JSON；使用与AP一致的阶梯连接，避免离散基线梯形面积误读 |
| C01-11 F4预算曲线 | [原文注释](03_eval.py#L683) / [新代码](03_eval.py#L734) | 各点只在绘图用临时表中。 | 全部30点入JSON后再绘图，30%仍为主工作点。 | 全部预算点从JSON生成，保留10%至100%敏感性及30%主工作点 |
| C01-12 metrics写出 | [原文注释](03_eval.py#L739) / [新代码](03_eval.py#L750) | 写出并设只读，缺少本次配对来源。 | 保留只读，写出前拒绝NaN/Infinity，候选旧版先备份。 | 保持只读锁定，拒绝非有限数值，旧件先由configure逐字节备份 |
| C01-13 数字登记 | [原文注释](03_eval.py#L755) / [新代码](03_eval.py#L859) | 缺A质量统计、B完整验证/参数、C具体切片/案例/预算坐标。 | 补齐这些数字、系数、候选池、PR坐标及输入指纹；原模型指标不改。 | 补齐A统计、B验证与参数、C切片案例预算坐标和来源指纹 |
| C01-14 main流程 | [原文注释](03_eval.py#L866) / [新代码](03_eval.py#L914) | 先写表图，最后写metrics，不能证明都由冻结JSON生成。 | 核对B同次清单，评价一次，先冻结JSON，再读回生成所有表图并写C清单。 | 同次清单校验后先写统一JSON，再用其生成所有表图；不更改原评价公式 |

</details>

### Notebook与生成件的补充说明

| 文件 | main与当前的具体区别 |
|---|---|
| 01_data_quality.ipynb | main直接使用__file__，普通新内核会报错；现定位项目并runpy调用A脚本，13格原代码注释保留，不重复计算 |
| 03_eval.ipynb | 现调用同一C入口，默认配对同次B结果；两代码格可从新内核执行，原替换代码保留注释 |
| data/README_data.md、T1、字典、A_summary、F1/F1b | 由修复A生成；原科学统计不变，修正unknown、实际入模、隐私及总体漂移表述，补双指纹 |
| T2、选参池、系数、scores | 由修复B在声明环境重新训练产生，不手工把差异改成历史数字；T2仍只用Validation |
| C测试表、T3/T4、F3/F4 | 使用同次B分数重新评价；完整切片、失败案例和预算点可回溯，离散PR的阶梯面积与AP一致 |
| metrics、T5及数字CSV/JSON | C/D原科学结果完整保留，最终报告数字与页码索引统一；没有增加PPT页码或新的调参实验 |

## 6. 组员在自己的电脑如何运行

首次取得项目，使用report分支的完整仓库，避免只下载D文件漏掉ABC依赖：

```powershell
git clone --branch report https://github.com/Yeeeeee01/INT_6163_8th_GroupWork.git
cd INT_6163_8th_GroupWork
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/reproduce_all.py --check-only
.\.venv\Scripts\python.exe scripts/reproduce_all.py
```

已有克隆时，先保存自己的修改，再切换report并更新；不要覆盖未保存工作。分析依赖以main原声明为准：Python 3.9+，pandas 2.2.3、scikit-learn 1.6.1、PyYAML 6.0.2、matplotlib 3.9.4。Notebook界面和内核由各自编辑器提供；终端完整入口不需要Word、PDF工具或Codex运行时。

顺序为A（原CSV、质量及切分）→B（Train拟合、Validation选参）→C（固定Test评价）→D01（固定规则事后回放）→D02（F5及证据素材）→直接目录发布。随机种子42；原行序24712/8238/8238，即60/20/20留出，无shuffle。

终端成功应出现各阶段PASS、`[RESULTS_DIRECTORY]`、`[ABCD_REPRODUCED]`及`[REPORT_EVIDENCE] 107/107 matched`。打开`runs/latest_run.txt`指向运行中的`RUN_RESULTS.md`，其`publication/`是新计算的同结构结果。仓库根目录表图是提交展示，重跑不会自动覆盖；需要发布新结果时必须成套核对后更新，不能只替换一张表。

只重算ABC可用`python scripts/reproduce_abc.py`；单独A/B/C的候选输出语义见README。D01独立回放可用`--abc-run`指定同次ABC目录；当前默认读取最新完整运行的ABC，不依赖结果ZIP。对一个成功运行再次导出目录可用`python scripts/reproduce_all.py --publish-run runs/<运行ID>`；源或产物变化会被拒绝。

数据来源：[UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)，[数据DOI](https://doi.org/10.24432/C5K306)，CC BY 4.0。恢复数据时选bank-additional的`bank-additional-full.csv`与names说明，放入data/raw/并保留原行序。入口核对LF规范内容指纹；不要自行换版本或修改期望哈希。原始数据说明见[data/README_data.md](data/README_data.md)。

A沿用Microsoft YaHei/SimHei的中文字体；F5支持Microsoft YaHei、SimHei、Noto Sans CJK SC或WenQuanYi Micro Hei。可用`--font-family`明确F5字体，缺少可用字体会停止，避免生成乱码。字体选择会影响图像像素，不应改动图内科学数字。

## 7. 哪些只供本地使用

| 位置 | 用途与处理 |
|---|---|
| .venv/、.vscode/ | 本机环境和编辑器配置，不上传 |
| local_review/及其checks、before、旧候选、旧发布目录 | 阶段核验、日志、旧实现、回归和字节备份，整目录留本地 |
| local_review/D03_candidate/report_填写版.docx | 已填写本地原稿；提交report.docx是其同字节副本，后续以填写稿修改并重新核对 |
| runs/ | 每次从原CSV新建的运行工作区、原阶段清单及日志，不逐次上传 |
| 本地Word/PDF生成、渲染、核验辅助程序；scripts/d03_build_report.py | 文档制作和检查工具，不属于成员运行分析的依赖 |
| 旧结果ZIP、旧独立ABC指南及阶段验收记录 | 备份和历史参考，公开入口统一为本页和标准目录 |
| .git/、新产生的__pycache__/和*.pyc | Git元数据或运行缓存，不作为新增作业成果；main已跟踪的一个pyc仅原样继承 |
| 本地计划、PROJECT_GUIDE、PROGRESS及同步记录 | 开发状态与历史管理，不替代公开README |

这不表示可以删掉公开目录里的运行清单、规则登记或逐记录审计：它们是本实现的复现支持证据，已在第4节逐个列明。原main的data/raw/bank-additional.zip是原始下载存档，保留为main资源；不承担隐藏报告、图表或分析结果的作用。

## 8. 引用、素材与解释边界

数据与原说明来自UCI。研究背景书目信息为Moro、Cortez、Rita（2014），Decision Support Systems 62:22–31，[DOI](https://doi.org/10.1016/j.dss.2014.03.001)。AP实现依据[scikit-learn 1.6官方文档](https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.average_precision_score.html)。报告保留核对后的题录及实际文件来源，不冒称未取得的论文全文已经通读。

F1/F1b/F2由A基于项目原数据与配置生成，F3/F4由C基于同次分数生成，F5由D02基于D01固定规则和同次指标绘制。六幅报告图与根目录提交Word保持已确认身份。AI工具Codex、模型GPT-6.1 Sol及实际用途/核验范围，按已通过报告第7页披露。

Test只支持历史排序评价，不表示因果提升。联系限制`previous >= 3 且 poutcome == failure`为固定示例、事后回放，不是真实银行政策；不递补主情景额外漏报3，与原名单漏报1340、触发群体订阅42分开。递补对照净命中变化+8独立解释，不能用它替代主情景或声称真实人工复核已实施。
