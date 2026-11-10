#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_lamb.json
