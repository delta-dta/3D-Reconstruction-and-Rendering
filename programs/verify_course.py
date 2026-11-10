"""Verify completed course artifacts, data separation, matches and local links."""

import csv
from html.parser import HTMLParser
import io
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text())


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {'href', 'src'} and value:
                self.targets.append(value)


def main():
    course = read(ROOT / 'configs/hw2_course.json')
    bank = {row['uid']: row for row in map(json.loads, (ROOT / 'cleaned/cleaned_models.jsonl').read_text().splitlines())}
    assert len(bank) == 7819
    selected = {row['uid'] for row in map(json.loads, (ROOT / 'cleaned/hw2_candidates.jsonl').read_text().splitlines())}
    assert selected == {row['uid'] for row in course['objects']} and len(selected) == 10
    total_pairs, total_inliers = 0, 0
    by_slug = {}
    for obj in course['objects']:
        source = ROOT / obj['output_dir']
        target = ROOT / 'results' / f"hw2_{obj['slug']}"
        data = source / 'data'
        metadata, splits = read(data / 'metadata.json'), read(data / 'splits.json')
        assert metadata['uid'] == obj['uid']
        assert metadata['source_sha256'] == bank[obj['uid']]['sha256']
        assert len(splits['train']) == 96 and len(splits['test']) == 24
        assert not set(splits['train']) & set(splits['test'])
        assert {path.name for path in (data / 'images').glob('*.png')} == set(splits['train'])
        assert {path.name for path in (data / 'test_images').glob('*.png')} == set(splits['test'])
        assert read(source / 'sfm/alignment.json')['fit_images'] == 96
        assert read(source / 'sfm/alignment.json')['test_images_used'] == 0
        assert read(source / 'model/training_config.json')['train_images'] == 96
        trained_cameras = read(source / 'model/cameras.json')
        assert len(trained_cameras) == 96
        assert {row['img_name'] for row in trained_cameras} == {Path(name).stem for name in splits['train']}
        assert read(source / 'model/summary.json')['iteration'] == 30000
        for directory, iteration in [('evaluation',30000), ('evaluation_7000',7000)]:
            evaluation = read(source / directory / 'summary.json')
            assert evaluation['complete'] and evaluation['iteration'] == iteration
            assert {row['name'] for row in evaluation['per_view']} == set(splits['test'])
            assert np.isfinite([evaluation['mean_psnr'], evaluation['mean_ssim'], evaluation['mean_foreground_psnr']]).all()
        gif = Image.open(target / 'reconstruction.gif')
        assert gif.n_frames == 72 and gif.size == (512,512)
        assert len(list((target / 'sfm/matches').glob('*.jpg'))) == 4
        with (target / 'sfm/verified_pairs.csv').open() as stream:
            pairs = list(csv.DictReader(stream))
        with np.load(io.BytesIO((target / 'sfm/geometric_matches.npz').read_bytes())) as arrays:
            keypoint_counts = {int(key.removeprefix('keypoints_')): len(arrays[key])
                               for key in arrays.files if key.startswith('keypoints_')}
            for pair in pairs:
                pair_id = int(pair['pair_id'])
                low, high = divmod(pair_id, 2147483647)
                matches = arrays[f'inliers_{pair_id}']
                assert len(matches) == int(pair['inliers'])
                assert matches[:,0].max() < keypoint_counts[low]
                assert matches[:,1].max() < keypoint_counts[high]
                total_inliers += len(matches)
        total_pairs += len(pairs)
        novel = ROOT / 'outputs/novel_views' / obj['slug']
        novel_frames = read(novel / 'data/metadata.json')['frames']
        assert len(novel_frames) == 36 and all(frame['split']=='test' for frame in novel_frames)
        assert {frame['elevation_degrees'] for frame in novel_frames} == {0,30,60}
        assert read(novel / 'evaluation/summary.json')['test_views'] == 36
        by_slug[obj['slug']] = splits
    for slug in course['representatives']:
        variants = {}
        for label, count in [('views24',24), ('views48',48), ('gt_poses',96)]:
            source = ROOT / 'outputs/ablations' / f'{slug}_{label}'
            splits = read(source / 'data/splits.json')
            assert len(splits['train']) == count and splits['test'] == by_slug[slug]['test']
            assert not set(splits['train']) & set(splits['test'])
            assert set(splits['train']) <= set(by_slug[slug]['train'])
            assert read(source / 'evaluation/summary.json')['complete']
            assert read(source / 'model/summary.json')['iteration'] == 30000
            actual = read(source / 'model/training_config.json')['train_images']
            assert actual == read(source / 'evaluation/summary.json')['train_views']
            assert 0 < actual <= count
            trained_cameras = read(source / 'model/cameras.json')
            assert len(trained_cameras) == actual
            assert {row['img_name'] for row in trained_cameras} <= {Path(name).stem for name in splits['train']}
            variants[label] = set(splits['train'])
        assert variants['views24'] < variants['views48'] < variants['gt_poses']
        assert read(ROOT / 'outputs/ablations' / f'{slug}_gt_poses/pose_control.json')['same_sparse_initialization']
    checked_links = 0
    for page in [ROOT / 'index.html', *sorted((ROOT / 'results').rglob('*.html'))]:
        parser = Links()
        parser.feed(page.read_text())
        for target in parser.targets:
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            destination = (page.parent / unquote(url.path)).resolve()
            assert destination.is_file(), f'Broken link: {page.relative_to(ROOT)} -> {target}'
            checked_links += 1
    report = {'complete': True, 'objects': 10, 'registered_cameras': 960, 'gifs_72_frames': 10,
              'control_trainings': 9, 'novel_test_views': 360, 'verified_pairs_exported': total_pairs,
              'geometric_inliers_exported': total_inliers, 'local_html_links_checked': checked_links,
              'data_separation': '96/24 disjoint; subset tests identical; new elevations excluded from training'}
    (ROOT / 'results/verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
