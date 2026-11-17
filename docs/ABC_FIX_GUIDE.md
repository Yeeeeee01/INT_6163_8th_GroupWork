<!-- README_D整理：原46点指南及旧阶段范围完整保留 -->

> 当前发布范围为 `report` 分支20文件，见[README_D.md](../README_D.md)。本指南保留46项ABC修复及D04_03技术说明；旧18文件数量和待验收文字属历史。科学源码、报告、结果ZIP与现有T5保持原字节。

<!-- D04_02 原共享指南导言完整保留
# ABC 修复说明与组员复现指南

本文件将原A01、B01、C01三份共享说明合并，保留46个修复编号、源码位置、前后区别、原因和组员本地操作步骤。源码及Notebook按原分工保留，科学计算没有因整理提交材料而改变。原三份独立说明仍在本机保存，本轮共享这一份。

环境依据仍为GitHub原README的Python3.9+及原requirements.txt四项固定依赖；不要求恢复原作者未声明的环境。A01/B01/C01已收到用户实际技术重跑28/0、33/0、36/0。P01只整理发布文件，正式报告与联系限制策略评价尚未开展。

本轮建议提交12个新增/修改文件：7个源码或Notebook/入口，README、.gitattributes、.gitignore、本指南及一个结果ZIP。仓库已有原始数据、requirements.txt、features.yaml和历史产物继续保留。请按提交清单选择文件；某些已生成的本地A产物仍会出现在Git差异中，不属于这次精简提交。

先阅读[项目运行说明](../README.md)，然后按需查阅[A01](#a01)、[B01](#b01)、[C01](#c01)。各节保留当时的独立修订范围，当前总体状态以上述验收记录为准。

<a id="snapshot"></a>
## 同次结果快照

下载并解压[ABC_C01_verified.zip](../results/ABC_C01_verified.zip)，先阅读snapshot.json。它选自用户已通过的C01验收中第一次完整原始数据运行，包含A八个结果、B七个结果、C九个结果和两份运行清单，另有快照索引。源CSV和源码不重复打包。

```text
snapshot.json
run/input_manifest.json
run/run_manifest.json
workspace/data/README_data.md
workspace/outputs/                    A的统计、切分、字典与T1
workspace/figures/                    A的F1/F1b/F2
workspace/local_review/B01_candidate/outputs/
workspace/local_review/C01_candidate/outputs/
workspace/local_review/C01_candidate/figures/
```

ZIP内保留原工作区相对目录，运行清单中的路径因此仍可对应。源码/原数据输入在仓库内，快照索引另列其内容指纹。跨系统换行时区分原字节与LF规范指纹；不要修改快照中的清单数值来适应解压目录。

以workspace/local_review/C01_candidate/outputs/metrics.json作为这次已验收结果的统一数字源；T2、T3—T5、PR图与预算图必须取同一快照。根目录历史outputs/figures及data/README_data.md未全部纳入本次更新，不作为本轮修订后的结果说明；本节和ZIP内文件是本轮查看入口。下方独立阶段说明涉及生成件的链接统一跳转本节，具体文件在上述目录中。

metrics在原运行时设为只读；解压工具可能不保留文件属性，内容以ZIP及成员指纹核验。需要重新计算时从项目根目录执行python scripts/reproduce_abc.py，它仍从原CSV建立全新工作区，不读取本ZIP作计算缓存。

## 合并范围

以下三节合并自原独立指南；旧稿仍保存在本机，源代码中的原修改注释全部保留。原独立文档名如在阶段文字中出现，均指本文件对应节。文件数量整理没有增加模型、改变参数或生成D行动策略损失。



D04_02 原共享指南导言完整保留 END -->

# ABC修复说明与组员复现指南

本指南保留A01的21项、B01的11项和C01的14项，共46项修复位置、前后区别及原因。下方各节是原阶段历史说明，当前总体运行与结果入口以本节及[README](../README.md)为准。环境仍依据原Python 3.9+与requirements.txt，不要求恢复原作者未声明环境。

<a id="snapshot"></a>
## 当前同次结果与复现入口

使用[ABCD_verified.zip](../results/ABCD_verified.zip)，解压后先阅读README_RESULTS.md。正式数字源为report/metrics.json；report/T5_数字核对表.md登记107处报告数字及实际页码，report/T5_all_numbers.csv覆盖完整数值叶子。报告为根目录report.docx，8页，原填写稿未重写；PPT页码待E实际稿。

workspace/保留原A、B、C、D01、D02产物与清单；早期阶段T5不覆盖，正式页码以report/为准。snapshot.json及run/artifact_catalog.json提供原运行路径到ZIP成员的映射，输入源码/CSV在仓库内，不重复打包。

从项目根目录执行`python scripts/reproduce_all.py`，从原CSV重新运行全部阶段，不读取ZIP作计算缓存。需要独立ABC时仍可运行`python scripts/reproduce_abc.py`，其阶段结果不包含D补充。

<!-- D04_03 原组合验收状态保留
D04-02拟提交18文件，另保留4个仓库原有输入，共22个运行文件；详见README末节。P01旧12文件方案及旧快照是归档历史，未覆盖。本次候选已整合统一包，但尚待原Git基线覆盖组合验收；未推送或提交学校。
D04_03 原状态段结束 -->

D04-03发布候选仍为18文件＋4原有必要输入；完整路径清单及原Git基线见README末节。验收使用原Git内容的独立副本覆盖这18文件，并按原requirements建立隔离环境，结果以实际验收记录为准。P01及D04-01/D04-02旧包继续归档；候选待用户重跑及最终阅读，PPT未登记，未推送或提交学校。

以下独立阶段节中的旧数量、尚未开展D、默认命令或历史数字属于当时范围，不代表当前报告没有D结果。46点源码位置和旧实现注释继续有效。

<a id="a01"></a>
## A01 数据质量与运行入口

### A01 修复说明与组员本地操作指南

本说明供小组成员定位Part A修复、比较前后实现，并在自己的电脑复现。适用于含A01-01至A01-21标记的修订源码；原始基线提交为 `bfdfedb3e6cf82ea59254279a5352af4f2a395e8`。

本文件须与A01源码同批发布。下载原始基线中的未修复脚本，再单独下载本说明，不能获得修复效果。源码行号对应本次A01版本；后续行号变化时，以A01编号搜索定位。

#### 环境与本次范围

环境以仓库[README](../README.md)与[requirements.txt](../requirements.txt)为准：Python 3.9或以上；pandas==2.2.3、scikit-learn==1.6.1、PyYAML==6.0.2、matplotlib==3.9.4。仓库没有声明精确Python补丁版本或完整间接依赖，不把某台电脑的安装记录补成小组标准。

本次修复A的运行入口、产物一致性、字段说明、输入校验和留痕。原数据值、清洗决定、features.yaml、60/20/20切分及B/C模型方案保持既定口径；B/C环境差异、C发布改进和D报告不在此次修复内。

#### Python文件内的21个修改点

所有改动位于[01_data_quality.py](../01_data_quality.py)。被替换代码已先注释保留，再加入带编号的新实现；新增段落也注明用途。

| 修改点 | 文件位置 | 修复前 | 修复后 | 原因 |
|---|---|---|---|---|
| A01-01 模块说明 | [A01-01 新实现](../01_data_quality.py#L23-L32)；[旧实现注释](../01_data_quality.py#L2) | 局部说明使用未固定版本的安装命令，未交代修订留痕。 | 说明环境按GitHub README及requirements；增加隔离输出与备份说明。 | 明确修复边界与运行依据。 |
| A01-02 标准库导入 | [A01-02 新实现](../01_data_quality.py#L38-L42) | 没有参数解析、依赖版本核对和备份所需的辅助导入。 | 新增argparse、importlib.metadata、shutil。 | 支撑入口、核对和备份；不是新增分析方法。 |
| A01-03 配置读取支持 | [A01-03 新实现](../01_data_quality.py#L49-L51) | A字段说明与B特征配置分开维护。 | 导入仓库已有依赖PyYAML，读取features.yaml。 | 让字段说明取自同一实际配置。 |
| A01-04 输出路径、环境检查与备份 | [A01-04 新实现](../01_data_quality.py#L66-L136)；[旧实现注释](../01_data_quality.py#L59) | 输出位置固定；已有产物通常直接被新产物覆盖。 | 支持项目内--output-root；核对GitHub已声明依赖；生成前备份；新增Markdown原文保留函数。 | 允许安全隔离重跑，记录修改前状态。 |
| A01-05 原始数据内容指纹 | [A01-05 新实现](../01_data_quality.py#L158-L165) | 只有原始字节SHA256，换行改变时难以辨别内容是否变化。 | 保留原字节SHA，另外计算CRLF/CR转LF后的内容SHA；核对冻结内容。 | 解释跨系统换行差异，源CSV保持原字节。 |
| A01-06 提前校验冻结切分 | [A01-06 新实现](../01_data_quality.py#L171-L191) | 已有split时未由A核对内容。 | 校验列名、连续row_id与原行序60/20/20分段。 | 错误切分在生成统计和图表前被拒绝。 |
| A01-07 unknown注释语义 | [A01-07 新实现](../01_data_quality.py#L219-L221)；[旧实现注释](../01_data_quality.py#L216) | 注释将unknown称为真实类别。 | 明确unknown是缺失标签，当前保留为独立类别。 | 描述真实处理，不改变编码选择。 |
| A01-08 清洗决定表述 | [A01-08 新实现](../01_data_quality.py#L229-L231)；[旧实现注释](../01_data_quality.py#L226) | CLEAN_ACTIONS将unknown写为真实类别。 | 改为缺失标签保留为独立类别，继续不删除、不插补。 | 表格说明与字段语义一致。 |
| A01-09 contact备注 | [A01-09 新实现](../01_data_quality.py#L260-L262)；[旧实现注释](../01_data_quality.py#L257) | 备注写“仅作误差切片”，实际进入B主模型。 | 改为进入主模型、不单独作为联系依据。 | 修正文案与实际使用的矛盾。 |
| A01-10 month备注 | [A01-10 新实现](../01_data_quality.py#L266-L268)；[旧实现注释](../01_data_quality.py#L263) | 备注写“仅作误差切片”，实际进入B主模型。 | 改为进入主模型，同时保留无精确日期的说明。 | 保持说明准确。 |
| A01-11 day_of_week备注 | [A01-11 新实现](../01_data_quality.py#L272-L274)；[旧实现注释](../01_data_quality.py#L269) | 备注写“仅作误差切片”，实际进入B主模型。 | 改为进入主模型，同时保留无精确日期的说明。 | 保持说明准确。 |
| A01-12 字典入模标记 | [A01-12 新实现](../01_data_quality.py#L292-L294) | 入模与否是手工写入字典的另一份清单。 | 根据features.yaml的main集合生成进主模型列。 | 降低两份清单再次失步的可能。 |
| A01-13 F1字段用途文字 | [A01-13 新实现](../01_data_quality.py#L318-L320)；[旧实现注释](../01_data_quality.py#L315) | contact/month/day_of_week标成仅作切片。 | 图内改为主模型使用。 | 图、字典与B配置一致。 |
| A01-14 F1字段数量文字 | [A01-14 新实现](../01_data_quality.py#L327-L329)；[旧实现注释](../01_data_quality.py#L324) | 未清楚区分可用字段与实际输入数量。 | 明确19列通话前可知、实际主模型使用14列。 | 避免把可知字段全部解释为主模型输入。 |
| A01-15 split生成及沿用 | [A01-15 新实现](../01_data_quality.py#L432-L442)；[旧实现注释](../01_data_quality.py#L422) | 有文件就跳过生成，随后直接读取。 | 正确切分验证后沿用且不重写；新切分验证后写出。 | 保留既定划分并防止错误输入被静默沿用。 |
| A01-16 A_summary来源字段 | [A01-16 新实现](../01_data_quality.py#L479-L486) | 汇总以原有数据统计为主。 | 增加规范化指纹、入模字段及数量、GitHub环境依据和声明依赖。 | 支持后续追溯；没有替换C冻结指标。 |
| A01-17 T1生成模板 | [A01-17 新实现](../01_data_quality.py#L556-L606)；[旧实现注释](../01_data_quality.py#L505) | 部分措辞混淆缺失语义、换行指纹，或超出已做实验。 | 补双指纹并修正unknown、漂移和外推表述。 | 结论与实际证据范围匹配。 |
| A01-18 T1写入 | [A01-18 新实现](../01_data_quality.py#L610-L612)；[旧实现注释](../01_data_quality.py#L607) | 重新生成直接写入当前Markdown。 | 改用保留原文HTML注释的写入函数。 | 组员可在编辑器核对旧文，GitHub渲染显示当前有效正文。 |
| A01-19 README生成步骤 | [A01-19 新实现](../01_data_quality.py#L617-L813) | Python脚本止于T1；生成README的代码只在Notebook中。 | 把完整README生成补入权威脚本。 | 脚本和Notebook产生同样的A交付物。 |
| A01-20 README安装入口 | [A01-20 新实现](../01_data_quality.py#L714-L811)；[旧实现注释](../01_data_quality.py#L618) | 生成的README还使用pip install pandas matplotlib。 | 改为python -m pip install -r requirements.txt，并说明GitHub为环境依据。 | 组员不会按旧说明安装一套未固定的依赖。 |
| A01-21 F1b图题 | [A01-21 新实现](../01_data_quality.py#L402-L404)；[旧实现注释](../01_data_quality.py#L399) | “越靠后的记录越高”可能被理解为逐段单调。 | 改为“后段总体正类率更高”。 | 图题符合实际非单调的分段变化，柱形数值不变。 |

#### 其他文件的修复位置与区别

| 文件 | 位置 | 修复前后区别及原因 |
|---|---|---|
| [01_data_quality.ipynb](../01_data_quality.ipynb) | 第一个代码格，即Notebook第3个单元、JSON索引2；以及其余原代码格 | 原先直接使用__file__，普通新内核报错。现在定位项目目录后通过runpy调用脚本。13格旧代码均注释保留；第一个代码格执行完整A，后续12格只供对照，不重复计算。 |
| [.gitattributes](../.gitattributes) | 原始CSV的text/eol规则、ZIP的-text规则 | 新增CSV按LF检出的约定；不强制改写电脑上已有CSV。脚本双指纹区分字节差异和数据内容差异。 |
| [data/README_data.md](#snapshot) | 数据字典、质量、隐私与复现章节 | 由统一脚本生成；修正入模用途、unknown、隐私保证和安装入口。旧正文在HTML注释中保留，当前正文是有效说明。 |
| [outputs/T1_数据质量表.md](#snapshot) | 文件指纹、unknown及结构性事实说明 | 保留旧稿注释，新增双指纹，删除超出实验范围的论断；统计值保持原口径。 |
| [outputs/data_dictionary.csv](#snapshot) | 进主模型列及contact/month/day_of_week的备注 | 入模标记来自配置；三个字段备注与实际入模一致。CSV保持可读取，不插入注释行。 |
| [outputs/A_summary.json](#snapshot) | data.raw_normalized_sha256、raw_normalization、main_features、main_feature_count、environment_authority、github_declared_dependencies | 新增来源和配置元数据；原统计字段保留。JSON保持有效格式。 |
| [F1](#snapshot) | 左侧本次安排及字段数量文字 | 修正实际用途，区分19列可知与14列入模。 |
| [F1b](#snapshot) | 图题 | 改为总体后段正类率更高，不表示逐段单调；数据值不变。 |
| [F2](#snapshot) | 脚本运行产物 | 随A重新生成，流程方案没有新增分析步骤。 |

生成的CSV、JSON和图片无法加入普通代码注释。运行覆盖前，脚本会在该次输出根目录的 `local_review/repairs/A01/generated_before/时间戳/` 保存旧文件及manifest.json；Markdown另外保留原正文HTML注释。新克隆的成员不需要本次作者电脑上的历史备份即可运行。

#### 组员如何在自己的电脑操作

以下终端命令以Windows PowerShell为例，均在仓库根目录执行。macOS/Linux应使用相应的虚拟环境Python路径，项目依赖版本不变。

##### 1 获取包含修复的源码

首次下载：

```powershell
git clone https://github.com/Yeeeeee01/INT_6163_8th_GroupWork.git
cd INT_6163_8th_GroupWork
git log -1 --oneline
Select-String -Path .\01_data_quality.py -Pattern 'A01-01','A01-21'
```

必须取得带A01修改标记的版本。如果尚未合入main，请切换到小组实际发布的修复分支或提交；没有标记时先核实发布版本，不继续把原始脚本当作修复版。已有克隆的成员先保留自己的改动，再更新到团队发布版本，不覆盖未保存工作。

##### 2 准备符合GitHub声明的解释器与依赖

```powershell
python --version
```

选择满足仓库声明、且能安装原requirements的Python解释器。首次为本项目创建虚拟环境时执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果已有本项目的可用虚拟环境，可以复用并按原requirements核对。虚拟环境只是隔离工具，不代表固定为作者电脑的Python版本。依赖安装失败时保留Python版本及报错，与组内核实，不通过自行升级四项固定依赖来消除报错。

##### 3 先运行隔离输出

```powershell
.\.venv\Scripts\python.exe .\01_data_quality.py --output-root local_review/A01_check
```

输入仍来自仓库的原始CSV和features.yaml；本次输出写到：

- `local_review/A01_check/data/README_data.md`
- `local_review/A01_check/outputs/A_summary.json`、T1、数据字典与split_v1.csv
- `local_review/A01_check/figures/` 下三张A图

预期终端出现 `[A01_PASS]`。可查看汇总：

```powershell
Get-Content .\local_review\A01_check\outputs\A_summary.json
```

##### 4 运行默认正式位置与Notebook

确认隔离结果符合下表后，运行默认入口：

```powershell
.\.venv\Scripts\python.exe .\01_data_quality.py
```

此命令在根目录的data、outputs、figures生成A产物；已有生成件先备份，正确冻结split不重写。不要手工改生成表格来迁就预期数字。

VS Code中打开整个仓库文件夹，打开 `01_data_quality.ipynb`，选择同一项目虚拟环境对应的Python内核，重启内核后从头运行所有单元格。第一个代码格调用统一脚本，因此Notebook也生成默认正式位置产物。Notebook运行需要可用的VS Code/Jupyter工具组件与内核，这些工具组件不替代或重写requirements中的项目依赖。

终端脚本应出现 `[A01_PASS]`，Notebook还应出现 `[A01_NOTEBOOK_PASS]`。本说明不要求组员取得作者本地专用的28项审计脚本。

#### 通过标准与问题处理

| 检查项 | 预期 |
|---|---|
| 数据规模 | 41188行、21列 |
| y=yes | 4640条 |
| NaN / 完全重复行 | 0 / 12 |
| pdays=999 | 39673条，保留其哨兵语义 |
| unknown | job 330、marital 80、education 1731、default 8597、housing 990、loan 990 |
| Train / Validation / Test | 24712 / 8238 / 8238，原行序连续留出 |
| 实际主特征 | 14列，与features.yaml一致；无duration、y、row_id |
| LF规范内容SHA256 | `233e260d5d1d506a2c10381da5b8c2f75f2c08d1b373ca7b825e39ebe1bd30df` |
| A产物 | README、A_summary、21列字典、T1、split及F1/F2/F1b完整生成 |
| 两入口 | 新内核无错误，Notebook与脚本统计和说明一致 |

- 依赖版本报错：检查当前解释器和原requirements，不把本机不同版本当小组标准。
- 原始字节哈希不同：先看规范内容哈希；LF/CRLF会改变字节哈希，不能据此直接判定观测值被改动。
- 内容哈希报错：停止使用该输入，核对仓库原始数据；不要改预期哈希绕过校验。
- 冻结split报错：保留出错文件，核对来源与行序；不要为了通过而随意重划或使用--force。
- Notebook找不到项目：从仓库根目录或其子目录启动，并确认脚本和原始CSV齐全。
- ZMQ等运行警告：根据后续是否成功和输出是否齐全判断；若有实际异常，保留完整日志，不仅截取最后一行。

该修复已完成原始数据运行、新内核和一致性检查，并收到一次用户28项技术重跑通过日志。这不代表其他组员的电脑已经通过，也不代表B/C待修问题已经解决。


<a id="b01"></a>
## B01 模型产出与追溯

### B01 环境核对与模型产出追溯修订指南

本文件供组员定位B01修复、比较前后实现，并在自己的电脑重跑。适用于含B01-01至B01-11标记的02_models.py，须与该源码同批使用；当前为本地待发布说明，尚未推送GitHub。

#### 本阶段完成与仍未证实的事项

已完成环境声明核对、冻结输入指纹、候选隔离、输出备份、来源清单与旧预测差异记录。模型、特征、候选网格、seed=42、Train内预处理、Validation选参和导出精度保持原方案。

<!-- B01 验收口径修订：原作者环境相同不是硬性验收条件
原作者B完整训练环境在现有GitHub资料中未提供，因此仍不能声称跨环境精确恢复了旧预测。新训练结果是候选，不替换根目录scores、T2或C冻结metrics，也不根据Test表现调整模型。
-->

验收以GitHub已声明的环境要求为基础：原始数据能完成分析流程，同次输入的重复结果一致，指标计算可核对，旧结果差异如实说明。不要求找回或完全匹配原作者未声明的环境；该信息缺失不是流程复刻的失败条件。候选暂与旧冻结结果分开保存，以便C阶段将同一次A/B/C结果配对，避免混用。

#### 环境依据

以仓库[README](../README.md)的Python3.9+和[requirements.txt](../requirements.txt)四项固定版本为准：pandas2.2.3、scikit-learn1.6.1、PyYAML6.0.2、matplotlib3.9.4。原始基线提交为bfdfedb3e6cf82ea59254279a5352af4f2a395e8。

精确Python版本、NumPy/SciPy等原训练版本未声明；B01只记录本次实际版本，不将其补成小组标准。原Notebook元数据和A/C图片元数据不能证明B完整训练环境。

#### 按文件与编号查看修改

全部代码修订位于[02_models.py](../02_models.py)。被替换代码先保留为注释，再加入新实现；新增段落也有B01标记。行号对应当前B01版本，后续行号变化时可搜索编号。

| 修改点 | 文件位置 | 修复前 | 修复后 | 原因 |
|---|---|---|---|---|
| B01-01 说明与边界 | [新实现](../02_models.py#L5-L12)；[原代码注释](../02_models.py#L2) | 原说明没有交代候选与冻结版本的关系。 | 明确GitHub环境依据、新结果隔离和原结果保护。 | 防止把本机候选当作新标准。 |
| B01-02 辅助标准库 | [新实现](../02_models.py#L18-L27) | 无运行记录、指纹和备份辅助导入。 | 增加argparse、hashlib、metadata、platform、shutil等标准库。 | 补足追溯，不新增模型依赖。 |
| B01-03 输出默认位置 | [新实现](../02_models.py#L49-L52)；[原代码注释](../02_models.py#L46) | 默认覆盖根outputs，可能使新scores与旧C指标不匹配。 | 原outputs作为只读参考；默认候选写到local_review/B01_candidate/outputs。 | 保持旧scores与C冻结结果配对。 |
| B01-04 环境与来源函数 | [新实现](../02_models.py#L97-L275) | 缺少完整环境、输入、输出和旧预测对比记录。 | 按GitHub声明检查；另记实际环境；核对输入内容；隔离、备份、校验输出并生成运行清单。 | 未声明项保持缺失，不反推原机版本。 |
| B01-05 配置与切分校验 | [新实现](../02_models.py#L288-L295) | 配置seed、标签或行号字段与代码不一致时可能未明确指出。 | 校验seed=42、yes、y、row_id，以及切分列名、缺失、重复和整数行号。 | 避免记录配置与实际执行协议失步。 |
| B01-06 特征清单结构 | [新实现](../02_models.py#L329-L332) | 未明确检查列表类型与重复项。 | 先检查结构与重复，再执行原特征限制。 | 保持既定特征，提前报告错误输入。 |
| B01-07 main入口 | [新实现](../02_models.py#L461-L469)；[原代码注释](../02_models.py#L457) | 没有按次运行的环境与输入来源快照。 | 训练前解析输出位置、核对GitHub声明和输入指纹。 | 将本次输出绑定实际输入与源码。 |
| B01-08 候选旧版备份 | [新实现](../02_models.py#L608-L611)；[原代码注释](../02_models.py#L605) | 候选重复运行可能覆盖已有产物。 | 写出前逐字节备份候选文件并生成清单。 | 保留运行历史。 |
| B01-09 预测输出校验 | [新实现](../02_models.py#L623-L626)；[原代码注释](../02_models.py#L620) | 直接导出分数。 | 检查键唯一、概率有效、七模型两分段及逐行覆盖后再导出；仍保留原10位有效数字格式。 | 确保交给C的候选文件完整且可核对。 |
| B01-10 T2 Markdown | [新实现](../02_models.py#L672-L674)；[原代码注释](../02_models.py#L669) | 重新生成直接覆盖当前文字。 | 保留旧正文HTML注释，科学表格正文不改。 | 满足旧文保留约定。 |
| B01-11 完成记录 | [新实现](../02_models.py#L701-L703) | 只打印文件位置，缺少整次运行清单。 | 输出B_run_manifest.json和B_legacy_comparison.json，明确候选状态与历史环境未恢复。 | 支持追溯与差异解释，避免虚报旧结果已精确重现。 |

#### 新输出与原冻结结果的关系

默认命令 `python 02_models.py` 现在把候选写到 `local_review/B01_candidate/outputs/`。显式指定--output-root时，该目录下仍有outputs子目录。

| 候选文件 | 内容 |
|---|---|
| scores.csv | 七模型在Validation/Test的风险分；字段与原格式一致 |
| T2_模型对比表.csv及.md | Validation指标与选定参数；不是新Test评价 |
| model_selection_pool.csv | 原候选网格的Validation选择证据 |
| logistic_coefficients.csv | 原Logistic系数输出，解释仍限于相关 |
| B_run_manifest.json | GitHub声明、本次实测环境、输入/源码/输出指纹、特征、种子及选参协议 |
| B_legacy_comparison.json | 原GitHub预测参考是否匹配、按模型和分段统计的风险值差异；不读取Test标签或计算新Test指标 |

运行清单的environment.authority是环境依据，observed_for_this_run_only只是本次观察。release_status为candidate_only_not_C_frozen；历史环境未恢复的状态会明确保留。CSV/JSON保持有效格式，旧版另存逐字节备份；Markdown还保留旧稿HTML注释。

<!-- C01更新前的B阶段说明
原C脚本仍读取根目录 `outputs/scores.csv`，B01不会自动把候选接入C。候选与C重新配对的工作留待C阶段，不手工覆盖原scores使其与旧metrics混用。
-->

C01已新增同次结果配对：修订后的03_eval.py默认读取B01_candidate，候选metrics与表图另存C01_candidate，原根目录结果保留。完整入口及状态见[C01指南](#c01)。B清单中关于历史环境的字段仅为差异诊断，不是恢复原作者环境的验收要求。

#### 在自己电脑上的操作

命令以Windows PowerShell为例，先取得含A01与B01标记的实际修复版本；只下载说明配原始脚本不会获得修复。

1. 在VS Code打开仓库文件夹，进入项目根目录，检查源码标记。

```powershell
Select-String -Path .\01_data_quality.py -Pattern 'A01-01'
Select-String -Path .\02_models.py -Pattern 'B01-01','B01-11'
python --version
```

2. 使用能够满足GitHub要求的Python解释器。首次需要虚拟环境时创建；已有本项目环境可复用。安装依据仍是原requirements，不自行换固定版本。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. A01已运行且根目录split正确时可继续B。首次从原始数据开始时先执行A；它会验证并沿用正确的既定切分。

```powershell
.\.venv\Scripts\python.exe .\01_data_quality.py
```

4. 记录原冻结文件哈希，再运行B01隔离候选。

```powershell
$b01OriginalScoreHash = (Get-FileHash .\outputs\scores.csv -Algorithm SHA256).Hash
$b01OriginalMetricHash = (Get-FileHash .\outputs\metrics.json -Algorithm SHA256).Hash
.\.venv\Scripts\python.exe .\02_models.py --output-root local_review/B01_check
```

5. 检查候选状态、来源和差异记录，确认原文件没有被替换。

```powershell
Get-Content .\local_review\B01_check\outputs\B_run_manifest.json
Get-Content .\local_review\B01_check\outputs\B_legacy_comparison.json
(Get-FileHash .\outputs\scores.csv -Algorithm SHA256).Hash -eq $b01OriginalScoreHash
(Get-FileHash .\outputs\metrics.json -Algorithm SHA256).Hash -eq $b01OriginalMetricHash
```

预期出现 `[B01_PASS]`，末两条哈希比较为True。B01_LEGACY可能显示原预测完全一致，也可能显示已记录差异；两种情况都必须按实际记录，不能把“必须得到本机同样差异”当通过条件。

#### 验收与异常处理

- 七模型×两分段×8238条，共115332行分数，键不重复、概率有限且处于[0,1]。
- Validation表能从同次分数复算；参数仍取Validation AP最优候选；28次Pipeline拟合只使用24712条Train记录。
- 同一环境、相同输入和代码重复运行，科学CSV应一致；运行清单的时间戳可以变化。
- 清单中的输入与输出SHA可对应实际文件。源CSV或split/config内容改变时应停止并核实，而不是改预期哈希绕过检查。
- GitHub声明版本不符时先核对解释器和原requirements；未声明版本只登记，不从本机记录反推原作者环境。
- 原预测差异不等于新模型更优；不能用它决定换模型，也不能据此宣称完成旧环境精确恢复。
- 根目录输出覆盖请求会拒绝。当前先保留配对的旧scores与C指标，待C阶段明确接入候选与指标版本。

<!-- B01 验收口径修订：记录用户实际通过并明确B与整条流程的边界
助手已通过同环境原脚本对照、修订版两次运行、动态标签与拟合行号检查，共33项程序核查。此记录不代表其他组员电脑或用户已通过B01，也不代表历史环境缺口已解决。组员可使用上述原入口自行核查，不必获取作者本机专用审计脚本。
-->

助手已完成33项检查，2026-11-16收到用户实际33 PASS / 0 FAIL日志，B01技术重跑通过。验证的是GitHub已声明要求下的B流程、计算一致性与记录正确性；其他组员仍需在各自电脑运行。整条A/B/C链路还要由C阶段完成同次结果配对与端到端核查。


<a id="c01"></a>
## C01 同次结果评价与数字核对

### C01 同次结果配对与完整复刻指南

本文件供组员查阅修复位置、前后区别、原因及自己电脑上的操作。适用于含C01-01至C01-14标记的03_eval.py及配套c01_support.py、scripts/reproduce_abc.py和03_eval.ipynb。当前仍为本地待发布版，尚未推送GitHub；取得源码时须连同已经修订的A01/B01一起获取。

#### 复刻标准与当前状态

以GitHub原README的Python3.9+和原requirements.txt四项依赖为准：pandas2.2.3、scikit-learn1.6.1、PyYAML6.0.2、matplotlib3.9.4。不要求恢复原作者未声明的完整环境；NumPy/SciPy及精确Python版本只记录本次观察，不设为新增小组标准。

A01已收到用户28项技术通过，B01已收到用户33项技术通过。C01助手36项检查全部通过，包括两次从原CSV无缓存完整运行、科学结果一致、独立复算及普通新内核Notebook。<!-- C01用户验收更新：旧状态保留
C01仍待用户亲自重跑确认，D报告尚未开始。
-->

2026-11-16已收到用户实际C01完整36 PASS / 0 FAIL日志，C01技术重跑通过；与A01的28项、B01的33项用户技术通过记录衔接。当前进入D任务准备，正式报告尚未撰写。完整运行成功不表示每个环境都必须与历史文件逐位相等；同次A/B/C对应、重复运行可核对及差异披露是本轮标准。

#### 每处修复的位置与原因

下列14处均先注释保留被替换原代码，再加入修订代码。行号对应本稿，后续可按C01编号搜索。原排名、AP、Top-K、混淆矩阵、业务三量、切片和失败案例的计算函数未改；模型和参数仍由B按Validation选择。

| 修改点 | 文件位置 | 修复前 | 修复后 | 为什么修复 |
|---|---|---|---|---|
| C01-01 说明 | [原文注释](../03_eval.py#L2) / [新代码](../03_eval.py#L26) | 默认根目录产物，未说明新旧运行关系。 | 说明GitHub环境标准、同次候选路径及完整入口。 | 明确复刻口径与候选位置 |
| C01-02 导入 | [原文注释](../03_eval.py#L48) / [新代码](../03_eval.py#L52) | 无统一登记/渲染模块。 | 增加c01_support模块，数值评价公式仍在03_eval.py。 | 共享数字登记和渲染辅助模块 |
| C01-03 输入输出路径 | [原文注释](../03_eval.py#L60) / [新代码](../03_eval.py#L69) | 固定读取根outputs/scores，写回旧metrics。 | 默认衔接B01_candidate，写C01_candidate；支持显式输入。 | 默认衔接同次B候选，避免覆盖原冻结分数和指标 |
| C01-04 切分检查 | [原文注释](../03_eval.py#L104) / [新代码](../03_eval.py#L117) | 仅核对Test行号。 | 核对全部41188个行号及Train/Validation/Test连续60/20/20。 | 核对全部连续切分，避免只检查Test遗漏Train或Validation错误 |
| C01-05 分数检查 | [原文注释](../03_eval.py#L152) / [新代码](../03_eval.py#L170) | 只校验Test模型和逐行对应。 | 检查7模型2分段115332行、唯一键、[0,1]有限概率和全部行号。 | 校验完整7模型两分段的唯一键与概率，拒绝损坏或错版分数 |
| C01-06 模型表 | [原文注释](../03_eval.py#L421) / [新代码](../03_eval.py#L451) | 直接从内存models写表。 | 先落盘metrics，再只从该JSON生成模型表。 | 模型表只读取已落盘的统一数字 |
| C01-07 切片和案例 | [原文注释](../03_eval.py#L456) / [新代码](../03_eval.py#L510) | JSON缺具体记录；解释写死百分比，直接建议联系上限。 | 登记全部切片/案例；说明随本次结果取数；联系上限尚未评价。 | 切片和案例纳入JSON；解释文字动态取数，不预先声称联系上限已评价 |
| C01-08 duration消融 | [原文注释](../03_eval.py#L515) / [新代码](../03_eval.py#L566) | 表从models和T2分别取数。 | Validation与Test先统一登记，再生成表；原计算口径不变。 | 消融表从统一登记的Validation和Test数值生成 |
| C01-09 T5核对 | [原文注释](../03_eval.py#L571) / [新代码](../03_eval.py#L622) | 仅12个常用数字。 | 扩展常用数字键，并新增所有数值叶节点CSV索引，页码待D/E填写。 | 扩展常用核对表和全部数值叶节点索引，供报告逐项引用 |
| C01-10 F3 PR曲线 | [原文注释](../03_eval.py#L627) / [新代码](../03_eval.py#L678) | PR点直线相连，图下面积易与AP混淆。 | 坐标入JSON，使用post阶梯；阶梯积分与average_precision_score一致。 | PR坐标纳入JSON；使用与AP一致的阶梯连接，避免离散基线梯形面积误读 |
| C01-11 F4预算曲线 | [原文注释](../03_eval.py#L683) / [新代码](../03_eval.py#L734) | 各点只在绘图用临时表中。 | 全部30点入JSON后再绘图，30%仍为主工作点。 | 全部预算点从JSON生成，保留10%至100%敏感性及30%主工作点 |
| C01-12 metrics写出 | [原文注释](../03_eval.py#L739) / [新代码](../03_eval.py#L750) | 写出并设只读，缺少本次配对来源。 | 保留只读，写出前拒绝NaN/Infinity，候选旧版先备份。 | 保持只读锁定，拒绝非有限数值，旧件先由configure逐字节备份 |
| C01-13 数字登记 | [原文注释](../03_eval.py#L755) / [新代码](../03_eval.py#L859) | 缺A质量统计、B完整验证/参数、C具体切片/案例/预算坐标。 | 补齐这些数字、系数、候选池、PR坐标及输入指纹；原模型指标不改。 | 补齐A统计、B验证与参数、C切片案例预算坐标和来源指纹 |
| C01-14 main流程 | [原文注释](../03_eval.py#L866) / [新代码](../03_eval.py#L914) | 先写表图，最后写metrics，不能证明都由冻结JSON生成。 | 核对B同次清单，评价一次，先冻结JSON，再读回生成所有表图并写C清单。 | 同次清单校验后先写统一JSON，再用其生成所有表图；不更改原评价公式 |

#### 新文件和Notebook

- [c01_support.py / configure](../c01_support.py#L49)：核对GitHub声明，检查B运行清单绑定的代码、输入和输出，保护原冻结文件，备份已有候选。
- [c01_support.py / build_registry](../c01_support.py#L109)：统一登记A数据统计、B验证与选参证据、系数及C全部结果；验证A汇总对应实际Test。
- [c01_support.py / number_audit](../c01_support.py#L245)及图表函数：只从已落盘JSON生成表图和数字索引。
- [c01_support.py / finish](../c01_support.py#L301)：确认评价期间输入未变，为每个输出登记指纹。
- [scripts/reproduce_abc.py](../scripts/reproduce_abc.py#L19)：创建全新隔离工作目录，只复制原始CSV、代码、Notebook、配置和依赖声明，顺序运行A→B→C；不复制已有outputs/figures，记录日志与输入清单。
- [03_eval.ipynb](../03_eval.ipynb)：原两代码格逐行注释保留，调用同一修订脚本，再读取它实际返回的候选metrics路径；普通新内核无需注入__file__。

这些是新增支持文件，原仓库没有对应旧文件。它们使用GitHub已声明的分析依赖和Python标准库，没有新增模型依赖。

#### 在自己电脑上的完整操作

先在VS Code打开实际修订版本的项目根目录。不要只将本指南与GitHub当前旧脚本配用。环境已有且符合requirements时可直接使用；首次可创建虚拟环境：

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Select-String -Path .\03_eval.py -Pattern 'C01-01','C01-14'
.\.venv\Scripts\python.exe .\scripts\reproduce_abc.py
```

预期依次出现PASS A、PASS B、PASS C及[ABC_REPRODUCED]。每次完整运行创建新目录，避免缓存产物参与分析：

```text
local_review/ABC_reproduction/<本次编号>/
  input_manifest.json
  run_manifest.json
  A.log / B.log / C.log
  workspace/outputs/                   A本次统计与切分
  workspace/local_review/B01_candidate/outputs/
  workspace/local_review/C01_candidate/outputs/
  workspace/local_review/C01_candidate/figures/
```

定位本次结果：

```powershell
$abcRun = Get-Content .\local_review\ABC_reproduction\latest_run.txt
Get-Content (Join-Path $abcRun 'run_manifest.json')
Get-Content (Join-Path $abcRun 'workspace\local_review\C01_candidate\outputs\metrics.json')
```

run_manifest状态应为ABC_REPRODUCED，三个退出码均为0，cached_outputs_copied为false。B_run_manifest记录Validation-only、seed42及分数来源；C_run_manifest将本次B输出与C产物配对。再次运行完整入口后，比较本次模型指标和科学结果，时间与运行目录允许变化。

若要逐步审阅或运行C Notebook，在这次workspace目录中打开VS Code并使用同一解释器；这里A/B已运行，直接运行03_eval.py或03_eval.ipynb即可。当前正式项目已验收A且有默认B01_candidate时，也可在项目根目录运行：

```powershell
.\.venv\Scripts\python.exe .\02_models.py
.\.venv\Scripts\python.exe .\03_eval.py
```

此处C默认读local_review/B01_candidate，写local_review/C01_candidate。若B指定了其他输出位置，C也必须指定相同输入根目录，不能手工搬分数而漏掉同批清单：

```powershell
.\.venv\Scripts\python.exe .\02_models.py --output-root local_review/member_B
.\.venv\Scripts\python.exe .\03_eval.py --input-root local_review/member_B --output-root local_review/member_C
```

#### 输出及报告引用

| C候选outputs内文件 | 作用 |
|---|---|
| metrics.json | 本次A/B/C统一数字源，生成后只读 |
| C_run_manifest.json | 绑定本次代码、输入、B清单、全部表图指纹 |
| C_测试集模型比较表.md | 同Test、同K的7模型比较 |
| T3_误差切片表.md | 全部21切片、随本次数字更新的说明及三例失败案例 |
| T4_duration消融表.md | Validation/Test消融对比 |
| T5_数字核对表.md | 常用数字及metrics键；D/E随后填写页码 |
| T5_all_numbers.csv | 全部数值叶节点索引，含系数、参数、曲线及案例 |

候选figures内F3为阶梯PR，AP仍按average_precision_score；F4保留10%—100%的30个数据点。两图只读取同次metrics。Markdown保留旧稿HTML注释，候选JSON/CSV/图片再次运行前逐字节归档到C01_generated_before；原提交件亦保留。

报告一旦选用本次完整运行，必须始终引用其同一份metrics及配套表图；不要混入根目录旧metrics的AP、阈值或随机森林命中数。本轮实际测试主模型AP约0.448274、命中1200；随机森林AP约0.403767、命中1051，历史文件分别约0.448276/1200、0.404940/1054。差异如实记录，不根据Test重新调参追平。

在同样K=2472下，主模型比规则基线多命中276，无效联系少276，漏报1340。两个276是固定名单规模下同一变化的不同表达，不相加。10%预算下规则命中536、主模型417，不能写所有预算均胜出。联系上限策略及其额外损失尚未定义或评价，现有切片FN不能冒充该策略代价。

#### 验收与故障定位

通过标准：依据原GitHub声明成功从原CSV运行，B仅Train拟合/Validation选参，C配对同次结果；所有表图数字可回到metrics与实际分数，重复运行科学结果一致，原冻结文件不被替换。<!-- C01验收标准状态更新：旧状态保留
当前助手检查通过，用户重跑尚未记录通过。
-->

当前助手检查及用户实际36项重跑均通过；正式报告与D行动规则代价评价尚未完成。未取得原作者完整环境不构成失败。

遇到缺文件先查看A/B/C.log；B输入/输出或源码指纹变化时应重跑对应分析，再评价，不能删除指纹检查。分数错位、重复、NaN/Infinity或清单不匹配会明确拒绝。C拒绝--output-root指向项目根目录。--legacy-reference仅用于读取原GitHub分数做数值回归，不能当成从原CSV重新训练的证据。

本机详细验收脚本和绝对路径仅在本地记录中，不作为组员运行的依赖。Notebook执行工具是本地核查工具，不加入分析requirements。尚未commit/push；共享指南是待发布材料，不表示GitHub当前已有源码修复。

