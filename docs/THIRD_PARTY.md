# 方法来源与第三方依赖

| 方法或工具 | 用途 | 来源 |
|---|---|---|
| Objaverse 1.0 | 原始三维资产及元数据 | https://arxiv.org/abs/2212.08051 |
| Blender 4.5.3 LTS | 受控多视角渲染 | https://www.blender.org/ |
| OpenCV SIFT | 清洗时的前景特征统计 | https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html |
| COLMAP / PyCOLMAP 3.13.0 | SIFT、匹配、几何验证与增量 SfM | https://colmap.github.io/pycolmap/index.html |
| 3D Gaussian Splatting | 高斯优化和可微渲染 | https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/ |
| Matplotlib 3.10.3 | 指标与损失图，输出 PNG/PDF | https://matplotlib.org/ |

官方 3DGS 代码固定为 `54c035f7834b564019656c3e3fcc3646292f727d`。三个计算子模块版本记录在结果的 `environment.json`。光栅化补丁仅添加 `<cstdint>` 标准头文件，见 `patches/gaussian_rasterizer_cuda129.patch`。

3DGS 代码通过 `scripts/setup_hw2_tools.sh` 从官方仓库获取，其许可证保存在 `third_party/gaussian-splatting-LICENSE.txt`。Blender、Conda 和编译扩展作为本地依赖，不放入课程提交压缩包。

10 个对象的模型名称、来源、作者、许可代码和 SHA-256 单独列在 `ASSET_CREDITS.md` 与 `results/asset_credits.csv`。模型许可沿用各资产原始元数据。
