#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
mkdir -p outputs/full_render

# 已完成：31,614 个候选全部处理，31,607 个成功渲染。
# taskset -c 0,1 .tools/blender-4.5.3-linux-x64/blender --background -t 1 --factory-startup --python-exit-code 1 --python programs/render_candidates.py -- --config configs/render_full.json --worker 0 > outputs/full_render/worker_0.log 2>&1 &
# render_pid_0=$!
# taskset -c 2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 1 --factory-startup --python-exit-code 1 --python programs/render_candidates.py -- --config configs/render_full.json --worker 1 > outputs/full_render/worker_1.log 2>&1 &
# render_pid_1=$!
# taskset -c 4,5 .tools/blender-4.5.3-linux-x64/blender --background -t 1 --factory-startup --python-exit-code 1 --python programs/render_candidates.py -- --config configs/render_full.json --worker 2 > outputs/full_render/worker_2.log 2>&1 &
# render_pid_2=$!
# taskset -c 6,7 .tools/blender-4.5.3-linux-x64/blender --background -t 1 --factory-startup --python-exit-code 1 --python programs/render_candidates.py -- --config configs/render_full.json --worker 3 > outputs/full_render/worker_3.log 2>&1 &
# render_pid_3=$!
# taskset -c 8,9 .tools/blender-4.5.3-linux-x64/blender --background -t 1 --factory-startup --python-exit-code 1 --python programs/render_candidates.py -- --config configs/render_full.json --worker 4 > outputs/full_render/worker_4.log 2>&1 &
# render_pid_4=$!
# taskset -c 10,11 .tools/blender-4.5.3-linux-x64/blender --background -t 1 --factory-startup --python-exit-code 1 --python programs/render_candidates.py -- --config configs/render_full.json --worker 5 > outputs/full_render/worker_5.log 2>&1 &
# render_pid_5=$!
#
# wait "$render_pid_0"
# wait "$render_pid_1"
# wait "$render_pid_2"
# wait "$render_pid_3"
# wait "$render_pid_4"
# wait "$render_pid_5"
