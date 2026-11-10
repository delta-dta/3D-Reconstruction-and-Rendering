#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_shoe/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_shoe.json > /data/260010047/3d_homework/outputs/hw2_shoe/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_shoe.json > /data/260010047/3d_homework/outputs/hw2_shoe/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_shoe.json > /data/260010047/3d_homework/outputs/hw2_shoe/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_shoe.json > /data/260010047/3d_homework/outputs/hw2_shoe/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_shoe.json > /data/260010047/3d_homework/outputs/hw2_shoe/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_shoe.json > /data/260010047/3d_homework/outputs/hw2_shoe/logs/finalize.log 2>&1

