# 匹配结果的读取方法

每个 `results/hw2_物体/sfm/` 都包含四张匹配图，以及完整几何验证结果：

| 文件 | 含义 |
|---|---|
| `verified_pairs.csv` | 图像对、COLMAP pair ID、验证内点数量 |
| `image_ids.json` | 图像 ID 到文件名的映射 |
| `geometric_matches.npz` | 全部关键点与验证后的内点下标 |

NPZ 中 `keypoints_<image_id>` 是该图像的关键点矩阵，前两列为像素位置。`inliers_<pair_id>` 是 N×2 的 uint32 数组，每行是两个关键点的下标。第一列对应较小的图像 ID，第二列对应较大的 ID。

COLMAP 使用 `pair_id = smaller_id * 2147483647 + larger_id`。可通过 `divmod(pair_id, 2147483647)` 还原两个图像 ID；也可以直接从 CSV 的文件名定位。

下面的 Python 片段展示如何读取一对实际匹配；作为学习示例放到 `.py` 文件执行：

```python
import csv
import numpy as np

folder = 'results/hw2_lamb/sfm/'
with open(folder + 'verified_pairs.csv') as source:
    pair = next(csv.DictReader(source))
pair_id = int(pair['pair_id'])
first_id, second_id = divmod(pair_id, 2147483647)
with np.load(folder + 'geometric_matches.npz') as data:
    indices = data[f'inliers_{pair_id}']
    first_pixels = data[f'keypoints_{first_id}'][indices[:, 0], :2]
    second_pixels = data[f'keypoints_{second_id}'][indices[:, 1], :2]
print(pair['first'], pair['second'], len(indices))
```

匹配图最多显示 80 条线，标题记录实际内点总数；NPZ 保留所有内点，没有绘图抽样。完整的描述子、初始候选匹配和几何验证模型仍在本地 `outputs/hw2_物体/sfm/database.db`。紧凑提交保留几何验证后的对应，便于查看和继续分析。
