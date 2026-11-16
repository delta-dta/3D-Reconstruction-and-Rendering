#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
source configs/cuda.env
export CUDA_HOME
export PATH="$CUDA_HOME/bin:$PATH"
export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
# python -B programs/train_hw2.py --config configs/hw2_lamb.json
