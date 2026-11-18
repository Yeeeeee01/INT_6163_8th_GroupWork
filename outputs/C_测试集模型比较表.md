<!-- C01_ORIGINAL_MARKDOWN_BEGIN
本次新生成，无被替换旧稿。
C01_ORIGINAL_MARKDOWN_END -->

# C 测试集模型比较表

同次输入：Test 8238条，K=2472；同分按row_id升序。

| 模型 | Test AP | Precision@K | Recall@K | 命中@K | 无效联系 | 漏报订阅 |
|---|---:|---:|---:|---:|---:|---:|
| no_skill | 0.308327 | 0.084951 | 0.082677 | 210 | 2262 | 2330 |
| poutcome_success | 0.433075 | 0.373786 | 0.363780 | 924 | 1548 | 1616 |
| logistic | 0.448274 | 0.485437 | 0.472441 | 1200 | 1272 | 1340 |
| logistic_macro_control | 0.338823 | 0.372573 | 0.362598 | 921 | 1551 | 1619 |
| decision_tree | 0.439575 | 0.469660 | 0.457087 | 1161 | 1311 | 1379 |
| random_forest | 0.403767 | 0.425162 | 0.413780 | 1051 | 1421 | 1489 |
| logistic_duration_ablation | 0.536352 | 0.580097 | 0.564567 | 1434 | 1038 | 1106 |

AP为average_precision_score。恒0基线的Top-K由原行号决定，不是随机联系的期望表现。duration版本只作泄漏消融。
