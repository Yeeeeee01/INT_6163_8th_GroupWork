<!-- C01_ORIGINAL_MARKDOWN_BEGIN
本次新生成，无被替换旧稿。
C01_ORIGINAL_MARKDOWN_END -->

# T4 duration消融

主模型与消融只差duration；不可用于通话前决策的字段不作为主模型输入。

| 数据段 | 主模型AP | 主模型命中 | 含duration AP | 含duration命中 | AP绝对差 | 命中差 | AP相对差 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validation | 0.208115 | 488 | 0.388499 | 678 | +0.180384 | +190 | +86.68% |
| Test | 0.448274 | 1200 | 0.536352 | 1434 | +0.088078 | +234 | +19.65% |

UCI说明："should be discarded if the intention is to have a realistic predictive model"。
