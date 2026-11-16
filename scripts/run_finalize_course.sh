#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
# python -B programs/finalize_course.py
