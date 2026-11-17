# 成员贡献与文件—图表对应

本表依据`INT6163_第8组_小组分工.docx`和`report.docx`第7页整理，按“文件→负责人→支撑图表/章节”记录分工。

`Z:`表示`results/ABCD_verified.zip`解压根目录，包内路径保留已验收阶段结构。E的PPT及T5后续修改按用户指示暂缓，E行只记录原分工，不登记已完成。

## 报告已确认的职责

| 部分 | 负责人 | 已确认报告中的职责与对应产出 | 当前登记 |
|---|---|---|---|
| A | YE ZHAOLAN | 界定对象与预测时点，核对来源、许可及质量，建立字段字典和只读切分。对应产出：01_data_quality.ipynb、T1、split_v1.csv、F1/F1b/F2。 | 按已通过报告登记；对应文件见下表 |
| B | YANG BO | 建立规则及无技能基线，训练并以Validation选参，冻结特征及消融配置。对应产出：02_models.py、features.yaml、scores.csv、T2及系数表。 | 按已通过报告登记；对应文件见下表 |
| C | ZHOU KEAO | 设计留出评价，复核AP/TopK、混淆矩阵和三项业务量，分析误差、消融及预算。对应产出：03_eval.ipynb、metrics.json、T3/T4/T5、F3/F4。 | 按已通过报告登记；对应文件见下表 |
| D | ZHANG YANG | 撰写六章报告、行动与限制，核对联系限制回放及图表数字，整合复现说明、引用、GenAI和贡献材料。对应产出：report.docx、F5、T6及README。 | 按已通过报告登记；对应文件见下表 |
| E | LIN QIAOSHUANG | 制作并讲述PPT，转录核对三项业务量及F4，回填PPT页码，呈现成员工作并准备问答。对应产出：slides.pptx及T5对应页码。 | 原分工保留；本轮暂缓PPT与页码工作 |

## 文件与可核验图表对应

| 文件或结果位置 | 负责部分 | 支撑内容 |
|---|---|---|
| `01_data_quality.py`、`01_data_quality.ipynb` | A | 数据质量、字段用途、来源、按行序切分；F1/F1b/F2与T1 |
| `Z:workspace/data/README_data.md`、`Z:workspace/outputs/data_dictionary.csv`、`split_v1.csv`、`T1_数据质量表.md`、`A_summary.json` | A | 数据说明、21列字典、固定切分与质量证据 |
| `Z:workspace/figures/`三张PNG | A | F1字段分界、F1b行序变化、F2数据血缘 |
| `02_models.py`、`configs/features.yaml` | B | Train拟合、Validation选参、主特征与duration消融方案 |
| `Z:workspace/local_review/B01_candidate/outputs/`的`scores.csv`、`T2_模型对比表.csv`/`.md`、`model_selection_pool.csv`、`logistic_coefficients.csv` | B | 统一模型分数、T2、参数选择与系数解释；为C的F3/F4提供输入 |
| `03_eval.py`、`03_eval.ipynb`、`c01_support.py` | C | 固定Test评价、AP/TopK/混淆矩阵、三项业务量及数字登记 |
| `Z:workspace/local_review/C01_candidate/outputs/`及`figures/` | C | 原C指标、Test比较、T3切片、T4消融、阶段T5、F3/F4 |
| `scripts/d01_contact_policy.py`及`Z:workspace/local_review/D01_candidate/outputs/` | D | 固定联系限制事后回放、T6、逐记录审计及额外漏报来源 |
| `scripts/d02_report_assets.py`及`Z:workspace/local_review/D02_candidate/outputs/` | D | F5两格式、报告章节—图表—数字对应表及素材索引 |
| `report.docx` | D | 六章报告，整合F1/F1b/F2/F3/F4/F5、科学表、参考资料、GenAI和成员贡献 |
| `README.md`、`README_D.md`、`CONTRIBUTIONS.md` | D（材料整合） | 执行顺序、依赖、文件分类、引用/素材来源及贡献对应 |
| `scripts/reproduce_abc.py`、`scripts/reproduce_all.py`、`scripts/result_bundle.py`、`.gitattributes`、`.gitignore` | D（复现与发布整合）；A/B/C保留各自科学职责 | 无缓存完整入口、Git输入保护、同次结果归档及报告证据检查 |
| `docs/ABC_FIX_GUIDE.md`、`docs/REPORT_EVIDENCE.json`、`results/ABCD_verified.zip` | D（整合），ABC与D原产物保持原分工 | 46点修订说明、107数字/图像来源、统一正式数字源和T5报告页码 |
| `slides.pptx`及实际PPT页码 | E | 原定汇报与转录核对职责；本轮暂缓，不包含在当前20文件上传目录 |

## 使用与核验说明

报告、科学结果及全部科学实现本轮保持原字节；旧18文件发布目录也完整保留。当前准备区只为README和共享指南增加导航，并补充两份文档。ABC与D补充分析的技术验收、原Git加发布文件的完整重建均已有用户成功重跑记录；报告也已获用户通过。当前新增文档只整理已确认职责及文件映射，不新增分析结果或成员身份信息。

代码修复、核验、写作与材料整理使用AI的范围，以报告第7页实际GenAI声明为准，工具为Codex，模型按用户确认记录为GPT-6.1 Sol。报告源文件与验收原始记录在本地保留。当前未推送GitHub，目标分支为`report`。
