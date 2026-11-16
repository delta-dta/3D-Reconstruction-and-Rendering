#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_lamb.json
