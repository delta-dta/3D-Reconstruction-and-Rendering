#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export CUDA_HOME="$(dirname "$(dirname "$(command -v nvcc)")")"
export PATH="$CUDA_HOME/bin:$PATH"
export TORCH_CUDA_ARCH_LIST=12.0
export MAX_JOBS=4

# 官方源代码已获取；只初始化计算所需的三个子模块。
# git clone https://github.com/graphdeco-inria/gaussian-splatting.git .tools/gaussian-splatting
# git -C .tools/gaussian-splatting checkout 54c035f7834b564019656c3e3fcc3646292f727d
# git -C .tools/gaussian-splatting submodule update --init --recursive -- submodules/diff-gaussian-rasterization submodules/simple-knn submodules/fused-ssim
# 已完成：固定版本的 SfM 与数据读写依赖。
# python -m pip install numpy==1.26.4 pycolmap==3.13.0 plyfile==1.1.3 tqdm==4.67.1 ninja==1.11.1.4
# 已应用：补充 CUDA 12.9 编译所需的标准整数类型头文件。
# git -C .tools/gaussian-splatting/submodules/diff-gaussian-rasterization apply ../../../../patches/gaussian_rasterizer_cuda129.patch
# 已完成：三个扩展均针对 RTX 5090 的 sm_120 编译并安装。
# python -m pip install --no-build-isolation --no-deps .tools/gaussian-splatting/submodules/diff-gaussian-rasterization .tools/gaussian-splatting/submodules/simple-knn .tools/gaussian-splatting/submodules/fused-ssim
