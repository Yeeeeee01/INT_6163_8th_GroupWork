# Part A｜数据说明（README_data.md）

**负责人：A（问题界定与数据质量）** ｜ 生成方式：`python 01_data_quality.py` ｜ 切分版本：v1

---

## 1. 问题陈述五字段（报告第一段照此写，L13 p9）

| 字段 | 内容 |
|---|---|
| **对象** | 留出期一条待联系记录（客户 × 某轮 campaign；**无客户 ID**，用 `row_id` 标识） |
| **预测点** | **这一通电话拨出之前**；只能用当时可知的客户属性、历史联系记录与宏观指标 |
| **输出** | 订阅倾向分 `risk` + 按分排序的联系顺序 + 预算–收益曲线（**不是「某一类客户」**） |
| **行动** | 按分数从高到低联系；对 `previous` 高且 `poutcome=failure` 的人设联系上限；人工复核后执行、结果留痕回流 |
| **约束** | 外呼工时有限；`duration` 不可得；观察性数据无「未拨打」对照组；敏感属性不得单独作为联系依据 |

配图：`figures/F1_通话前后字段分界图.png`。左侧 19 列通话前可知 → 这一通外呼 → 右侧 `duration` / `y` 不可用。
**不要画**「T-4 周预警」式时间窗——数据没有精确日期列。

## 2. 数据来源与许可

| 项 | 内容 |
|---|---|
| 数据集 | UCI #222 Bank Marketing（**bank-additional-full.csv**，不是 10% 抽样的 bank-additional.csv） |
| 规模 | 实测 **41188 行 × 21 列**（20 输入 + `y`） |
| 时间跨度 | 2008-05 → 2010-11，官方说明「ordered by date」；只有 `month` / `day_of_week`，无精确日期列 |
| 分隔符 | `;` |
| 正类 | `y == "yes"` 实测 **4640 行（11.2654%）**，约 89% 外呼无效 |
| 许可 | **CC BY 4.0**，DOI 10.24432/C5K306 |
| 引用 | Moro, S., Cortez, P. & Rita, P. (2014), *A Data-Driven Approach to Predict the Success of Bank Telemarketing*, Decision Support Systems 62:22–31 |
| 本地快照 | `data/raw/bank-additional-full.csv`，5,834,924 bytes，sha256 `74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8`，落盘日期 2026-11-11 |

> 数据集官方说明第 56 行原文："this input should only be included for benchmark purposes and should be discarded if the intention is to have a realistic predictive model." —— 这是 `duration` 必须剔除、只做含/不含消融的官方依据。

## 3. 21 列数据字典

| # | 字段 | 语义 | 类型 | 通话前可知 | 进主模型 | 备注 |
|---|---|---|---|---|---|---|
| 1 | `age` | 客户年龄 | 数值 | 是 | 是 |  |
| 2 | `job` | 职业类别 | 类别 | 是 | 是 | 含 unknown；敏感属性，不单独作为联系依据 |
| 3 | `marital` | 婚姻状况 | 类别 | 是 | 是 | 含 unknown；敏感属性 |
| 4 | `education` | 教育程度 | 类别 | 是 | 是 | 含 unknown；敏感属性 |
| 5 | `default` | 是否有信用违约记录 | 类别 | 是 | 是 | unknown 8,597 行，保留为类别 |
| 6 | `housing` | 是否有住房贷款 | 类别 | 是 | 是 | 含 unknown |
| 7 | `loan` | 是否有个人贷款 | 类别 | 是 | 是 | 含 unknown |
| 8 | `contact` | 本次联系的通讯方式（手机/固话） | 类别 | 是 | 是 | 仅作误差切片，不作主结论 |
| 9 | `month` | 本次联系所在月份 | 类别 | 是 | 是 | 仅作误差切片；无精确日期列 |
| 10 | `day_of_week` | 本次联系所在星期 | 类别 | 是 | 是 | 仅作误差切片；无精确日期列 |
| 11 | `duration` | 本次通话时长（秒） | 数值 | 否 | 否 | 泄漏特征！通话结束才知道；UCI 官方要求剔除，仅用于含/不含消融 |
| 12 | `campaign` | 本轮 campaign 中该客户被联系次数（含本次） | 数值 | 是 | 是 | 历史联系记录 |
| 13 | `pdays` | 距上次 campaign 联系的天数 | 数值 | 是 | 是 | 999 = 从未联系，哨兵值 |
| 14 | `previous` | 本轮之前该客户被联系次数 | 数值 | 是 | 是 | 历史联系记录 |
| 15 | `poutcome` | 上次营销活动结果 | 类别 | 是 | 是 | 简单规则基线按它排序 |
| 16 | `emp.var.rate` | 就业变动率（季度宏观指标） | 数值 | 是 | 是 | 2008 金融危机期间可能漂移，时间留出能暴露 |
| 17 | `cons.price.idx` | 消费者价格指数（月度） | 数值 | 是 | 是 | 宏观指标，同上 |
| 18 | `cons.conf.idx` | 消费者信心指数（月度） | 数值 | 是 | 是 | 宏观指标，同上 |
| 19 | `euribor3m` | 欧元同业拆借 3 月利率（日度） | 数值 | 是 | 是 | 宏观指标，同上 |
| 20 | `nr.employed` | 就业人数（季度） | 数值 | 是 | 是 | 宏观指标，同上 |
| 21 | `y` | 客户是否订阅定期存款 | 类别 | 否 | 否 | 真值 / 标签，只用来对答案，绝不进模型 |

`row_id` 是我们自建的行标识（0-based，**不是原始字段**），只用于切分与核对，明确丢弃、不进模型。
机器可读版：`outputs/data_dictionary.csv`。

## 4. 数据质量摘要

完整表格见 `outputs/T1_数据质量表.md`。要点：

- `unknown` 按列计数后**保留为真实类别**，不删除不插补（`job` 330, `marital` 80, `education` 1731, `default` 8597, `housing` 990, `loan` 990）；
- `pdays = 999` 是「从未联系」哨兵，共 39673 行，保留原值但不解释为 999 天；
- 完全重复行 12 行，无客户 ID 无法判定，保留不删；
- 无 NaN 单元格；清洗前后行数不变，所有处理决定与影响行数都在 T1 可查；
- 类别不平衡 89:11 → 全猜 `no` 就有约 88.73% accuracy，**accuracy 不能当主指标**。
- **实测发现：标签随时间漂移**。按原始行序十等分，订阅率从 2.77% 升到 45.93%；三段正类率 Train 4.81% / Validation 11.07% / Test 30.83%（见 `F1b_时间漂移证据.png`）。这既解释了「为什么必须按行序留出、不能随机切分」，也提醒 C：Test 命中数偏高源于数据本身，必须与两个基线同一切分比较；报告限制章要写「结论不外推到其他时期」。

## 5. 切分协议（交给 B / C）

按**原始行序**时间留出，不 shuffle：Train 24712 行 / Validation 8238 行 / Test 8238 行。
数据按日期排序，随机切分等于「用未来预测过去」。`outputs/split_v1.csv`（`row_id`, `fold`）由本脚本**只生成一次**，之后只读；Test 只在最终评价时用一次。SEED=42 只用于 B 的模型随机性；A 的切分不用任何随机性。
各段正类人数：{'train': 1188, 'validation': 912, 'test': 2540}。

## 6. 隐私与伦理（报告要写）

- 数据无客户 ID，无法重识别到具体个人；`row_id` 仅为技术主键，不携带身份信息。
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

复现：`pip install pandas matplotlib` → 保持 `data/raw/bank-additional-full.csv` 在原位 → 运行 `python 01_data_quality.py` →
比对 `A_summary.json` 的 41188 行 / 正类占比 / unknown 各列计数 / 21 列字典 / 三段行数，换台电脑应完全一致。
