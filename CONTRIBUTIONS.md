# 成员贡献与文件—图表对应

依据`INT6163_第8组_小组分工.docx`及[report.docx](report.docx)第7页，按“文件→负责人→图表或章节”记录。姓名沿用报告，学号保留在报告中；下表登记分工，不替代成员对实际贡献的确认。

## 报告已确认的职责

| 部分 | 负责人 | 已确认报告中的职责与对应产出 | 当前登记 |
|---|---|---|---|
| A | YE ZHAOLAN | 界定对象与预测时点，核对来源、许可及质量，建立字段字典和只读切分。对应产出：01_data_quality.ipynb、T1、split_v1.csv、F1/F1b/F2。 | 按已通过报告登记；对应文件见下表 |
| B | YANG BO | 建立规则及无技能基线，训练并以Validation选参，冻结特征及消融配置。对应产出：02_models.py、features.yaml、scores.csv、T2及系数表。 | 按已通过报告登记；对应文件见下表 |
| C | ZHOU KEAO | 设计留出评价，复核AP/TopK、混淆矩阵和三项业务量，分析误差、消融及预算。对应产出：03_eval.ipynb、metrics.json、T3/T4/T5、F3/F4。 | 按已通过报告登记；对应文件见下表 |
| D | ZHANG YANG | 撰写六章报告、行动与限制，核对联系限制回放及图表数字，整合复现说明、引用、GenAI和贡献材料。对应产出：report.docx、F5、T6及README。 | 按已通过报告登记；对应文件见下表 |
| E | LIN QIAOSHUANG | 制作并讲述PPT，转录核对三项业务量及F4，回填PPT页码，呈现成员工作并准备问答。对应产出：slides.pptx及T5对应页码。 |  |

## 文件与可核验图表对应

| 文件或结果位置 | 负责部分 | 支撑内容 |
|---|---|---|
| [01_data_quality.py](01_data_quality.py)、[Notebook](01_data_quality.ipynb) | A | 来源、字段、质量与原行序切分；T1、F1/F1b/F2 |
| [数据说明](data/README_data.md)、[字典](outputs/data_dictionary.csv)、[切分](outputs/split_v1.csv)、[T1](outputs/T1_数据质量表.md)、[A统计](outputs/A_summary.json) | A | 21列用途、数据质量、24712/8238/8238分段 |
| [F1](figures/F1_通话前后字段分界图.png)、[F1b](figures/F1b_时间漂移证据.png)、[F2](figures/F2_数据血缘图.png) | A | 字段分界、原行序变化、数据血缘 |
| [02_models.py](02_models.py)、[特征配置](configs/features.yaml)、[分数](outputs/scores.csv)、[T2](outputs/T2_模型对比表.md)、[选参池](outputs/model_selection_pool.csv)、[系数](outputs/logistic_coefficients.csv) | B | Train拟合、Validation选参、主模型与消融输入 |
| [03_eval.py](03_eval.py)、[Notebook](03_eval.ipynb)、[c01_support.py](c01_support.py)、[Test模型表](outputs/C_测试集模型比较表.md)、[T3](outputs/T3_误差切片表.md)、[T4](outputs/T4_duration消融表.md) | C | Test AP/TopK、混淆矩阵、切片、duration消融 |
| [F3](figures/F3_PR曲线.png)、[F4](figures/F4_预算收益曲线.png) | C | PR与预算收益，含低预算时规则优于主模型的结果 |
| [D01脚本](scripts/d01_contact_policy.py)、[固定规则](outputs/D01_policy_spec.json)、[T6](outputs/T6_联系限制补充评价.md)、[逐记录审计](outputs/D01_逐记录审计.csv) | D | 联系限制事后回放、不递补与递补对照、额外漏报 |
| [D02脚本](scripts/d02_report_assets.py)、[F5 PNG](outputs/F5_行动闭环.png)、[F5 SVG](outputs/F5_行动闭环.svg)、[章节对应表](outputs/章节_图表_数字对应表.md) | D | 建议行动流程及报告证据对应 |
| [report.docx](report.docx) | D | 六章、六图、科学表、引用、GenAI及成员贡献 |
| [README.md](README.md)、[README_D.md](README_D.md)、本表 | D（材料整合） | 全项目执行顺序、46项修复、文件用途及来源 |
| [ABC入口](scripts/reproduce_abc.py)、[完整入口](scripts/reproduce_all.py)、[发布模块](scripts/result_bundle.py)、[证据登记](docs/REPORT_EVIDENCE.json)、[发布清单](outputs/publication_manifest.json) | D（复现与整合）；A/B/C保留各自科学职责 | 从原CSV完整执行、同次结果配对、107数字核对及直接目录展示 |
| [统一指标](outputs/metrics.json)、[T5](outputs/T5_数字核对表.md)、[数字索引](outputs/T5_all_numbers.csv) | C原指标；D补充回放与报告整合 | 原C键值保留，D01与文档登记追加；报告实际页码 |
| `slides.pptx`及实际PPT页码 | E | 原定PPT、转录核对及问答职责；是否完成以实际材料为准 |

## 使用说明

各文件均可直接查看，无需解压分析结果包。修复后源码在原路径替代main版本，具体前后区别见[README_D](README_D.md#abc-repairs)。科学模型分工与材料整合职责分别登记，不把代码修复等同于重新分配组员原有工作。AI使用范围以报告第7页为准：工具Codex，模型按用户确认记录为GPT-6.1 Sol。
