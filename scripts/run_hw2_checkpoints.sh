#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/shell_iter7000.json > /data/260010047/3d_homework/outputs/hw2_shell/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_iter7000.json > /data/260010047/3d_homework/outputs/hw2_can/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/shoe_iter7000.json > /data/260010047/3d_homework/outputs/hw2_shoe/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/brain_iter7000.json > /data/260010047/3d_homework/outputs/hw2_brain/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/stone_iter7000.json > /data/260010047/3d_homework/outputs/hw2_stone/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/candle_iter7000.json > /data/260010047/3d_homework/outputs/hw2_candle/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/jug_iter7000.json > /data/260010047/3d_homework/outputs/hw2_jug/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/owl_iter7000.json > /data/260010047/3d_homework/outputs/hw2_owl/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_iter7000.json > /data/260010047/3d_homework/outputs/hw2_robot/logs/evaluate7000.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_iter7000.json > /data/260010047/3d_homework/outputs/hw2_lamb/logs/evaluate7000.log 2>&1

