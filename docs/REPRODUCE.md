# 环境、执行顺序与复现

## 当前机器

项目根目录：`/data/260010047/3d_homework`。源数据：`/mnt/aoss/datasets/Objaversev1.0/`。GPU：RTX 5090，32 GB。Conda 环境：`/data/260010047/miniconda3/envs/3dvision`。

```bash
source /data/260010047/miniconda3/etc/profile.d/conda.sh
conda activate 3dvision
cd /data/260010047/3d_homework
```

Python 程序使用该环境；Blender 使用自带 Python。环境定义在 `environment.yml`，不继承系统 Python 的 site-packages。

## 已完成命令的约定

启动脚本均不接收参数。具体对象、实验参数与结果目录在对应 JSON 配置中。执行完成的完整命令已用 `#` 注释保留；复现时取消需要执行的命令注释。清洗的续跑依据已有进度，其他实验按指定目录执行，不自动尝试其他配置。

重新做实验时建议复制对应配置，明确改成一个新的输出目录，再把该配置的完整命令加入启动脚本。这样可以同时保留原有结果与修改后的实验。

## 作业 1

| 顺序 | 启动脚本 | 主要输出 |
|---|---|---|
| 1 | `scripts/run_coarse_filter.sh` | `outputs/coarse_candidates.jsonl` |
| 2 | `scripts/run_glb_filter.sh` | `outputs/material_candidates.jsonl` |
| 3 | `scripts/run_render_full.sh` | `outputs/full_frames/`、`outputs/full_render/` |
| 4 | `scripts/run_preview_deepseek.sh` | `cleaned/cleaned_models.jsonl` 与 UID 清单 |
| 5 | `scripts/run_finalize_cleaning.sh` | CSV、页面、10 物体清单 |

当前正式清洗结果完整，作业 2 可直接使用。要在全新目录重新调用 DeepSeek，需在 `ds_api_key` 配置密钥，并理解这一步会上传四视角图片和产生 API 费用；限额与端点在配置中。本次后续重建没有再次调用 API。

## 作业 2 单物体与 10 物体主实验

羊摆件的阶段脚本为 `run_hw2_render_lamb.sh`、`run_hw2_prepare_lamb.sh`、`run_hw2_sfm_lamb.sh`、`run_hw2_train_lamb.sh`、`run_hw2_evaluate_lamb.sh`、`run_hw2_finalize_lamb.sh`。它们现在调用共用的 `programs/*_hw2.py`。

其余对象的固定完整命令集中在：

| 脚本 | 对象 |
|---|---|
| `scripts/run_hw2_first_two.sh` | shell、can |
| `scripts/run_hw2_remaining.sh` | brain、stone、candle、jug、owl、robot；另保留 basket 的 SfM 案例命令 |
| `scripts/run_hw2_shoe.sh` | shoe，替换重复纹理导致位姿歧义的 basket 候选 |

每个对象严格按 render → prepare → reconstruct → train → evaluate → finalize 执行。输出位于 `outputs/hw2_对象/`，各阶段日志在 `logs/`。

进度查看：

```bash
/data/260010047/miniconda3/envs/3dvision/bin/python -B programs/course_status.py
```

训练日志包含 tqdm 的回车更新。查看进度优先读取 `training_progress.json`，避免用按行 tail 打印很长的进度条内容。

## 对照实验

| 脚本 | 条件 | 是否重新训练 |
|---|---|---|
| `scripts/run_hw2_checkpoints.sh` | 全部 10 物体，7k 模型同测试集评估 | 否 |
| `scripts/run_hw2_ablations_lamb_can.sh` | lamb/can，各 views24、views48、gt_poses | 是，共 6 次 |
| `scripts/run_hw2_ablations_robot.sh` | robot 的 views24、views48、gt_poses | 是，共 3 次 |
| `scripts/run_hw2_novel_views.sh` | 全部 10 物体，0°/30°/60°各 12 个新视角 | 否，生成参考图并评价 |
| `scripts/run_finalize_course.sh` | 聚合报告、图表、精简结果和网页 | 否 |

视图数量子集由 `prepare_hw2_experiment.py` 准备，RGB 与掩码使用硬链接，不重复复制。该准备步骤应在新的输出目录执行；已经建立的数据保留在原处。

位姿对照保持相同稀疏点，只设置真实训练外参。新高度评估通过 `model_dir` 明确读取主实验模型，并在独立目录保存图像与指标。

机器人 24 图条件观察到 19 个相机注册及几何退化。该条件明确设置 `require_all_registered=false`，训练只读取稀疏模型中实际注册的相机；输入图仍保留 24 张，测试集不变。规范的 `robot_views24.json` 可从图像重新执行 SfM。`robot_views24_export.json` 记录本次从已有 `sfm/raw/0` 恢复导出的设置，仅用于复用这次保存的原始结果；首次全新执行应使用规范配置。首次触发全部注册检查的日志保留为 `sfm_initial.log`。

## 新环境搭建

1. 根据 `environment.yml` 创建 `3dvision`，或使用本机已有环境。
2. 使用 CUDA 12.9、兼容 GCC（本机 13.3）。RTX 5090 构建设置为 `TORCH_CUDA_ARCH_LIST=12.0`。
3. 按 `scripts/setup_hw2_tools.sh` 获取固定提交的官方 3DGS，只初始化三个计算子模块，应用标准头文件补丁，再安装扩展。
4. 准备 Blender 4.5.3 Linux 版本至 `.tools/blender-4.5.3-linux-x64/`。本机额外的 libICE/libSM 位于 `.tools/system-libs/usr/lib/x86_64-linux-gnu/`，渲染启动命令为 Blender 单独设置 `LD_LIBRARY_PATH`。
5. 使源 Objaverse 文件位于配置指定路径。可先依照 `results/assignment1/cleaned_uids.txt` 准备所需对象，再复现单物体。

该项目的启动命令针对本机写明了绝对路径。更换根目录、Conda 位置或数据挂载位置时，修改相应 JSON 和 Bash 路径。预编译工具、源 GLB、完整中间图像和模型检查点保存在本机，提交包包含代码、配置与可查看结果。

## 结果保存在哪里

| 目录 | 用途 |
|---|---|
| `cleaned/` | 本机完整清洗结果与预览 |
| `outputs/full_frames/` | 清洗中间渲染，可复用做外观判别 |
| `outputs/hw2_*/` | 10 物体完整输入、SfM、3DGS、检查点和评价 |
| `outputs/ablations/` | 9 个对照条件的完整过程 |
| `outputs/novel_views/` | 360 张新高度参考图及对照 |
| `results/` | 可提交的匹配、GIF、指标、必要相机数据和图表 |
| `docs/` | 课程报告、学习指南、实验与复现说明 |

必要条件都已写入配置。优先复制一个已有配置开展下一次实验，保持测试划分固定，再对照新的指标与误差图。
