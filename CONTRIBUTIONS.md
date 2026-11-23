# 成员贡献与文件—图表对应

依据`INT6163_第8组_小组分工.docx`及[report.docx](report.docx)第7页，按“文件→负责人→图表或章节”记录。姓名沿用报告，学号保留在报告中；下表登记分工，不替代成员对实际贡献的确认。

## 各部分职责与对应产出

| 部分 | 负责人 | 职责说明与对应产出 | 当前登记 |
|---|---|---|---|
| A | YE ZHAOLAN | 负责问题界定、数据来源与数据质量，并为 B/C 建立可复核的数据输入。<br>1. 明确分析对象为留出期的一条客户—营销活动联系记录，预测时点为电话拨出前；定义风险分、联系排序、预算和人工复核等问题边界，并说明数据没有客户 ID、精确日期或未拨打对照组。<br>2. 核对 UCI 完整版数据集、许可和引用；核验数据为 41,188 行 × 21 列、正类 4,640 条；检查分隔符、标签比例、缺失标签、重复记录和 `pdays = 999` 哨兵值，说明保留或排除的理由。<br>3. 建立 21 列字段字典，标注通话前可知性、入模情况和敏感属性；将 `duration` 标为通话后字段、将 `y` 标为标签，并与 `configs/features.yaml` 的 14 项主特征保持一致。<br>4. 按原始行序固定 60/20/20 切分（24,712/8,238/8,238），不打乱、不使用随机数；生成后供 B/C 只读使用，并记录时间漂移及切分限制。<br>5. 生成 F1 字段边界图、F1b 时间漂移图和 F2 数据血缘图；交付数据说明、T1、字典和 A 阶段结构化摘要。 | 按已通过报告登记；详细产出见下表 |
| B | YANG BO | 负责模型基线、候选模型训练与验证集选型。<br>1. 建立恒预测“不订阅”的无技能基线，以及按 `poutcome == success` 排序的规则基线。<br>2. 比较逻辑回归、限深决策树和随机森林，并保留宏观指标对照；把预处理放入 Pipeline，仅在训练集拟合，依据验证集 AP 选择参数，不用测试集标签选型。<br>3. 冻结 14 项通话前主特征；单独登记宏观对照与 `duration` 泄漏消融，确保 `duration` 不进入主模型。<br>4. 生成统一格式的验证集/测试集风险分数、验证集比较表、候选参数记录和逻辑回归系数；系数解释为条件关联，不作因果结论。<br>对应产出：`02_models.py`、`configs/features.yaml`、`scores.csv`、T2、`model_selection_pool.csv`、`logistic_coefficients.csv`、`B_run_manifest.json`。 | 按已通过报告登记；详细产出见下表 |
| C | ZHOU KEAO | 设计留出评价，复核AP/TopK、混淆矩阵和三项业务量，分析误差、消融及预算。对应产出：03_eval.ipynb、metrics.json、T3/T4/T5、F3/F4。 | 按已通过报告登记；对应文件见下表 |
| D | ZHANG YANG | 撰写六章报告、行动与限制，核对联系限制回放及图表数字，整合复现说明、引用、GenAI和贡献材料。对应产出：report.docx、F5、T6及README。 | 按已通过报告登记；对应文件见下表 |
| E | LIN QIAOSHUANG | 制作并讲述PPT，核对三项业务量及F4，呈现成员工作并准备问答。对应产出：slides.pptx及结果页数字核对。 |  |

## 文件与可核验图表对应

| 文件或结果位置 | 负责部分 | 支撑内容 |
|---|---|---|
| [01_data_quality.py](01_data_quality.py)、[Notebook](01_data_quality.ipynb) | A | 共同调用的数据质量入口：核实来源与字段边界，记录 `unknown`、重复行、`pdays=999`、标签漂移及隐私限制；生成字段字典、冻结切分和 F1/F1b/F2 |
| [数据说明](data/README_data.md)、[字典](outputs/data_dictionary.csv)、[切分](outputs/split_v1.csv)、[T1](outputs/T1_数据质量表.md)、[A统计](outputs/A_summary.json) | A | 21列用途、数据质量、24712/8238/8238分段 |
| [F1](figures/F1_通话前后字段分界图.png)、[F1b](figures/F1b_时间漂移证据.png)、[F2](figures/F2_数据血缘图.png) | A | 字段分界、原行序变化、数据血缘 |
| [02_models.py](02_models.py)、[特征配置](configs/features.yaml)、[分数](outputs/scores.csv)、[T2 Markdown](outputs/T2_模型对比表.md)、[T2 CSV](outputs/T2_模型对比表.csv)、[选参池](outputs/model_selection_pool.csv)、[系数](outputs/logistic_coefficients.csv)、[B运行清单](outputs/B_run_manifest.json) | B | 建立两类基线并比较三类模型；训练集拟合、验证集选参；冻结通话前特征并排除主模型中的泄漏字段；登记分数、参数、系数及运行来源 |
| [03_eval.py](03_eval.py)、[Notebook](03_eval.ipynb)、[c01_support.py](c01_support.py)、[Test模型表](outputs/C_测试集模型比较表.md)、[T3](outputs/T3_误差切片表.md)、[T4](outputs/T4_duration消融表.md) | C | Test AP/TopK、混淆矩阵、切片、duration消融 |
| [F3](figures/F3_PR曲线.png)、[F4](figures/F4_预算收益曲线.png) | C | PR与预算收益，含低预算时规则优于主模型的结果 |
| [D01脚本](scripts/d01_contact_policy.py)、[固定规则](outputs/D01_policy_spec.json)、[T6](outputs/T6_联系限制补充评价.md)、[逐记录审计](outputs/D01_逐记录审计.csv) | D | 联系限制事后回放、不递补与递补对照、额外漏报 |
| [D02脚本](scripts/d02_report_assets.py)、[F5 PNG](outputs/F5_行动闭环.png)、[F5 SVG](outputs/F5_行动闭环.svg)、[章节对应表](outputs/章节_图表_数字对应表.md) | D | 建议行动流程及报告证据对应 |
| [report.docx](report.docx) | D | 六章、六图、科学表、引用、GenAI及成员贡献 |
| [README.md](README.md)、本表 | D（材料整合） | 项目流程、整合变更概要、主要文件用途及来源 |
| [ABC入口](scripts/reproduce_abc.py)、[完整入口](scripts/reproduce_all.py)、[发布模块](scripts/result_bundle.py)、[证据登记](docs/REPORT_EVIDENCE.json)、[发布清单](outputs/publication_manifest.json) | D（复现与整合）；A/B/C保留各自科学职责 | 从原CSV完整执行、同次结果配对、107数字核对及直接目录展示 |
| [统一指标](outputs/metrics.json)、[T5](outputs/T5_数字核对表.md)、[数字索引](outputs/T5_all_numbers.csv) | C原指标；D补充回放与报告整合 | 原C键值保留，D01与文档登记追加；报告实际页码 |
| `slides.pptx`及结果页数字核对 | E | 原定PPT、转录核对及问答职责；是否完成以实际材料为准 |

## 使用说明

各文件均可直接查看，无需解压分析结果包。修复后源码在原路径替代main版本，项目范围及主要修改概要见[README](README.md)。科学模型分工与材料整合职责分别登记，不把代码修复等同于重新分配组员原有工作。AI使用范围以报告第7页为准：工具Codex，模型按用户确认记录为GPT-6.1 Sol。
