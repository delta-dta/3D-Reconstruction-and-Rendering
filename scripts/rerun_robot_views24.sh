#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views24.json > /data/260010047/3d_homework/outputs/ablations/robot_views24/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views24.json > /data/260010047/3d_homework/outputs/ablations/robot_views24/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views24.json > /data/260010047/3d_homework/outputs/ablations/robot_views24/logs/evaluate.log 2>&1
