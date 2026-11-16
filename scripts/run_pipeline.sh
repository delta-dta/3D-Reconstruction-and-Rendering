#!/usr/bin/env bash
set -e

# 从仓库根目录运行；新结果位置由 configs/pipeline.json 指定。
python -B programs/run_pipeline.py --config configs/hw2_shell.json
python -B programs/run_pipeline.py --config configs/hw2_can.json
python -B programs/run_pipeline.py --config configs/hw2_shoe.json
python -B programs/run_pipeline.py --config configs/hw2_brain.json
python -B programs/run_pipeline.py --config configs/hw2_stone.json
python -B programs/run_pipeline.py --config configs/hw2_candle.json
python -B programs/run_pipeline.py --config configs/hw2_jug.json
python -B programs/run_pipeline.py --config configs/hw2_owl.json
python -B programs/run_pipeline.py --config configs/hw2_robot.json
# 已完成统一入口的六阶段验证。
# python -B programs/run_pipeline.py --config configs/hw2_lamb.json
