# 作业2 pipeline 使用说明

入口是 `programs/run_pipeline.py`。它直接依次运行六个阶段，每一步都对应一个独立程序；物体与实验参数使用现有JSON配置，运行路径集中在 `configs/pipeline.json`。

| 阶段 | 程序 | 输出 |
|---|---|---|
| 多视角成像 | `render_hw2.py` | 120张RGBA、相机内外参及资产SHA |
| 图像准备 | `prepare_hw2.py` | 96张训练图、24张测试图、掩码和固定划分 |
| 匹配与SfM | `reconstruct_hw2.py` | 估计相机、稀疏点、4组匹配图、全部验证对应 |
| 3DGS训练 | `train_hw2.py` | 7k/30k高斯PLY、训练损失、参数和恢复状态 |
| 评价与动画 | `evaluate_hw2.py` | 24视角指标、对照图和72帧GIF |
| 结果页面 | `finalize_hw2.py` | 单物体HTML、相机交互图与重建总览 |

`export_matching.py`由SfM阶段调用，将数据库中的全部关键点和几何验证内点导出为NPZ、CSV及图像ID映射。训练不读取测试图像；高斯初始点来自SfM，未从GLB表面直接取点。

## 1. 环境和依赖

原实验环境为Linux、RTX5090、CUDA12.9、GCC13.3。Python依赖固定在 `environment.yml`：

```bash
conda env create -f environment.yml
conda activate 3dvision
mkdir -p .tools
```

准备Blender4.5.3：

```bash
curl -L https://download.blender.org/release/Blender4.5/blender-4.5.3-linux-x64.tar.xz -o .tools/blender-4.5.3-linux-x64.tar.xz
tar -xf .tools/blender-4.5.3-linux-x64.tar.xz -C .tools
```

Blender需要系统图形库；Ubuntu可安装 `libice6`、`libsm6`、`libxrender1`、`libxi6`、`libxfixes3`、`libxkbcommon0`、`libgl1`。本机额外库的位置已写在路径配置中。报告PDF导出另需Pango与Noto CJK字体，见 `REPRODUCE.md`。

获取固定版本的官方3DGS和三个计算子模块。CUDA12.9的 `nvcc` 需已加入 `PATH`，下列命令据此确定工具链位置：

```bash
git clone https://github.com/graphdeco-inria/gaussian-splatting.git .tools/gaussian-splatting
git -C .tools/gaussian-splatting checkout 54c035f7834b564019656c3e3fcc3646292f727d
git -C .tools/gaussian-splatting submodule update --init --recursive -- submodules/diff-gaussian-rasterization submodules/simple-knn submodules/fused-ssim
git -C .tools/gaussian-splatting/submodules/diff-gaussian-rasterization apply ../../../../patches/gaussian_rasterizer_cuda129.patch
export CUDA_HOME="$(dirname "$(dirname "$(command -v nvcc)")")"
export PATH="$CUDA_HOME/bin:$PATH"
export TORCH_CUDA_ARCH_LIST=12.0
export MAX_JOBS=4
python -m pip install --no-build-isolation --no-deps .tools/gaussian-splatting/submodules/diff-gaussian-rasterization .tools/gaussian-splatting/submodules/simple-knn .tools/gaussian-splatting/submodules/fused-ssim
```

`TORCH_CUDA_ARCH_LIST=12.0`针对本次RTX5090；使用其他GPU时按其架构修改。这里没有自动下载数据、切换实现或重试不同配置。

## 2. 准备作业1的数据

仓库中已提供 `results/assignment1/cleaned_models.jsonl` 和正式10物体清单 `hw2_candidates.jsonl`。无需重新调用DeepSeek即可运行作业2。源GLB没有随代码重复上传，需要准备这10个UID对应的文件。

在 `configs/pipeline.json` 中填写数据根目录，结构为：

```text
dataset_root/
  glbs/
    000-000/97989d443ac048acb6bb42a2f82c6324.glb
    ...其余正式物体，分片与UID见hw2_candidates.jsonl
```

统一入口根据清单中的分片、UID和新数据根目录定位GLB，核对SHA-256，并保存该次运行使用的资产清单。因此不依赖清单里原机器的绝对源路径。

## 3. 单物体和10物体运行

在仓库根目录、激活 `3dvision` 后运行：

```bash
python -B programs/run_pipeline.py --config configs/hw2_lamb.json
```

该命令从GLB开始实际运行全部六步，30,000步训练后生成GIF与结果页。其他9个对象分别使用 `configs/hw2_shell.json`、`hw2_can.json`、`hw2_shoe.json`、`hw2_brain.json`、`hw2_stone.json`、`hw2_candle.json`、`hw2_jug.json`、`hw2_owl.json`、`hw2_robot.json`。

十条完整命令也集中在零参数脚本中：

```bash
bash scripts/run_pipeline.sh
```

羊形摆件已用该统一入口从GLB重新完成120张成像、96/96张相机恢复、30,000步训练、24视角评价和72帧GIF，验证摘要见 `results/pipeline_validation.json`。这条命令按本项目运行记录约定保留为注释；要在新机器上完整重跑10个物体，取消羊摆件命令的注释。

默认输出 `outputs/pipeline/物体/`，与正式结果的原始实验目录分开。每次保存解析后的 `config.json`、`asset.jsonl`、`pipeline_progress.json` 和六个日志。已有输出目录会直接报错，重新实验时明确修改 `configs/pipeline.json` 的 `output_root`。

实验输出中的 `index.html` 可直接在浏览器打开。GPU、分辨率、视角、内参与迭代设置与现有正式实验一致；由于增量SfM的数值执行，重新运行的位姿和指标可能有小幅变化，正式报告引用的是 `results/metrics.csv` 中已保存的10物体主实验。

## 4. 已提交结果与对照实验

无需数据和GPU即可查看 `results/hw2_*/` 中的10个GIF、匹配图、全部验证对应、相机与测试误差；完整下载仓库后用浏览器打开根目录 `index.html`。

```bash
python -B programs/verify_repository.py
```

该检查只读取仓库材料，不要求本机原来的 `outputs/` 或 `cleaned/`。`verify_course.py`另外检查本机完整训练输入、原生相机与数据分离。

24/48/96视角、真实位姿、7k/30k和新高度实验的配置保存在 `configs/experiments/`；原始完整命令在 `scripts/run_hw2_ablations_*`、`run_hw2_checkpoints.sh`、`run_hw2_novel_views.sh` 中保留，条件与结果对应关系见 `EXPERIMENTS.md`。

历史脚本保留了本机的执行路径；新的统一入口使用仓库位置和单独的路径配置。六个计算阶段共用同一份实现。
