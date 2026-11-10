#!/usr/bin/env bash
set -e

export LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_lamb.json
