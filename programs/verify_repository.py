"""Verify the coursework files using only the contents of a fresh repository clone."""

import ast
import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    for source in (ROOT / 'programs').glob('*.py'):
        ast.parse(source.read_text(), filename=str(source))
    course = json.loads((ROOT / 'configs/hw2_course.json').read_text())
    metadata = json.loads((ROOT / 'configs/submission.json').read_text())
    assert len(course['objects']) == 10 and len(metadata['members']) == 4
    assert sum(row['workload_percent'] for row in metadata['members']) == 100
    selected = {row['uid'] for row in map(json.loads, (ROOT / 'results/assignment1/hw2_candidates.jsonl').read_text().splitlines())}
    assert selected == {row['uid'] for row in course['objects']}
    pairs, inliers = 0, 0
    for obj in course['objects']:
        config = json.loads((ROOT / obj['config']).read_text())
        assert config['uid'] == obj['uid']
        folder = ROOT / 'results' / f"hw2_{obj['slug']}"
        with Image.open(folder / 'reconstruction.gif') as gif:
            assert gif.n_frames == 72 and gif.size == (512, 512)
        assert len(list((folder / 'sfm/matches').glob('*.jpg'))) == 4
        with (folder / 'sfm/verified_pairs.csv').open() as stream:
            records = list(csv.DictReader(stream))
        with np.load(folder / 'sfm/geometric_matches.npz') as arrays:
            for record in records:
                pair_id = int(record['pair_id'])
                first, second = divmod(pair_id, 2147483647)
                indices = arrays[f'inliers_{pair_id}']
                assert len(indices) == int(record['inliers'])
                assert indices[:, 0].max() < len(arrays[f'keypoints_{first}'])
                assert indices[:, 1].max() < len(arrays[f'keypoints_{second}'])
                inliers += len(indices)
        pairs += len(records)
    prompt = json.loads((ROOT / 'configs/preview_deepseek.json').read_text())['prompt']
    assert prompt in (ROOT / 'docs/PROMPTS.md').read_text()
    assert (ROOT / 'docs/HOMEWORK2_REPORT.pdf').read_bytes().startswith(b'%PDF-')
    result = {'complete': True, 'objects': 10, 'gifs': 10, 'matching_visualizations': 40,
              'verified_pairs': pairs, 'geometric_inliers': inliers,
              'scope': 'Committed code, configs, prompts, report and all ten result directories; no local training data required'}
    (ROOT / 'results/repository_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
