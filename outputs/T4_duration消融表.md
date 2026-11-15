# T4 duration 泄漏消融表

> 主模型与消融模型只差 `duration`。消融模型仅用于量化泄漏，不得作为最终模型。

| 数据段 | 不含 duration PR-AUC | 不含 duration 命中数 | 含 duration PR-AUC | 含 duration 命中数 | PR-AUC 绝对差 | 命中数绝对差 | PR-AUC 相对膨胀 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validation | 0.208120 | 488 | 0.388501 | 678 | +0.180381 | +190 | +86.67% |
| Test | 0.448276 | 1200 | 0.536352 | 1434 | +0.088076 | +234 | +19.65% |

结论：加入 `duration` 后指标明显变好，但这不表示模型更有业务价值，而是因为该字段在电话结束后才可得。UCI 官方说明原文："should be discarded if the intention is to have a realistic predictive model"。

因此，最终模型必须使用不含 `duration` 的 `logistic`；含 `duration` 版本只保留为泄漏证据。
