"""Run the six image-to-3DGS stages for one of the ten course objects."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, help='Object settings, for example configs/hw2_lamb.json')
    args = parser.parse_args()
    config_path = (ROOT / args.config).resolve()
    config = json.loads(config_path.read_text())
    paths = json.loads((ROOT / 'configs/pipeline.json').read_text())
    course = json.loads((ROOT / 'configs/hw2_course.json').read_text())
    obj = next(row for row in course['objects'] if row['uid'] == config['uid'])
    rows = map(json.loads, (ROOT / paths['cleaned_manifest']).read_text().splitlines())
    asset = next(row for row in rows if row['uid'] == config['uid'])
    source = Path(paths['dataset_root']) / 'glbs' / asset['shard'] / (asset['uid'] + '.glb')
    with source.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == asset['sha256']
    output = ROOT / paths['output_root'] / obj['slug']
    output.mkdir(parents=True, exist_ok=False)
    (output / 'logs').mkdir()
    asset['path'] = str(source)
    manifest = output / 'asset.jsonl'
    manifest.write_text(json.dumps(asset, ensure_ascii=False) + '\n')
    config.update({'name': obj['name'], 'slug': obj['slug'], 'cleaned_manifest': str(manifest),
                   'output_dir': str(output), 'gaussian_repo': str(ROOT / paths['gaussian_repo'])})
    resolved = output / 'config.json'
    resolved.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n')
    environment = {**os.environ, 'CUDA_VISIBLE_DEVICES': '0', 'CUDA_CACHE_PATH': '/tmp/3dvision-cuda-cache',
                   'OMP_NUM_THREADS': '4', 'OPENBLAS_NUM_THREADS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    started = time.monotonic()
    completed = []

    def run(stage, command, env):
        print(f'[{len(completed) + 1}/6] {stage}: {output}', flush=True)
        with (output / 'logs' / (stage + '.log')).open('w') as log:
            subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        completed.append(stage)
        (output / 'pipeline_progress.json').write_text(json.dumps({
            'uid': obj['uid'], 'completed_stages': completed, 'complete': len(completed) == 6,
            'elapsed_seconds': round(time.monotonic() - started, 2),
        }, indent=2) + '\n')

    run('render', [str(ROOT / paths['blender']), '--background', '-t', '4', '--factory-startup',
        '--python-exit-code', '1', '--python', str(ROOT / 'programs/render_hw2.py'), '--', '--config', str(resolved)],
        {**environment, 'LD_LIBRARY_PATH': str(ROOT / paths['blender_library_path'])})
    run('prepare', [sys.executable, '-B', str(ROOT / 'programs/prepare_hw2.py'), '--config', str(resolved)], environment)
    run('sfm', [sys.executable, '-B', str(ROOT / 'programs/reconstruct_hw2.py'), '--config', str(resolved)],
        {**environment, 'OMP_NUM_THREADS': str(config['sfm']['threads'])})
    run('train', [sys.executable, '-B', str(ROOT / 'programs/train_hw2.py'), '--config', str(resolved)], environment)
    run('evaluate', [sys.executable, '-B', str(ROOT / 'programs/evaluate_hw2.py'), '--config', str(resolved)], environment)
    run('finalize', [sys.executable, '-B', str(ROOT / 'programs/finalize_hw2.py'), '--config', str(resolved)], environment)
    print(f'Complete. Open {output / "index.html"}', flush=True)


if __name__ == '__main__':
    main()
