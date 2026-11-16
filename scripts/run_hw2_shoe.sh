#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# mkdir -p outputs/hw2_shoe/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_shoe.json > outputs/hw2_shoe/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_shoe.json > outputs/hw2_shoe/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_shoe.json > outputs/hw2_shoe/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_shoe.json > outputs/hw2_shoe/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_shoe.json > outputs/hw2_shoe/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_shoe.json > outputs/hw2_shoe/logs/finalize.log 2>&1

