"""Refresh the ten explicit course objects and their four-view feature statistics."""

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    course = json.loads((ROOT / 'configs/hw2_course.json').read_text())
    visual = json.loads((ROOT / 'configs/preview_deepseek.json').read_text())
    prior = json.loads((ROOT / 'configs/hw2_selection.json').read_text())['selected']
    notes = {row['uid']: row['suitability'] for row in prior}
    notes['40a95876e4164dfc885b6e8f0136dfe3'] = '单只跑鞋完整独立，鞋带、文字、色块与磨损纹理提供非周期特征，表面不透明低反光。'
    bank = {row['uid']: row for row in map(json.loads, (ROOT / 'cleaned/cleaned_models.jsonl').read_text().splitlines())}
    sift = cv2.SIFT_create()
    kernel = np.ones((2 * visual['foreground_erosion_pixels'] + 1,) * 2, np.uint8)
    selected = []
    for obj in course['objects']:
        uid = obj['uid']
        assert uid in bank
        counts, fractions = [], []
        for index in range(4):
            rgba = Image.open(ROOT / 'outputs/full_frames' / uid / f'view_{index}.png').convert('RGBA')
            mask = (np.array(rgba)[:, :, 3] > 127).astype(np.uint8) * 255
            rgb = Image.alpha_composite(Image.new('RGBA', rgba.size, 'white'), rgba).convert('RGB')
            gray = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)
            gray = cv2.GaussianBlur(gray, (0, 0), visual['gaussian_sigma'])
            counts.append(len(sift.detect(gray, cv2.erode(mask, kernel))))
            fractions.append(float((mask > 0).mean()))
        selected.append({'uid': uid, 'category': obj['name'], 'suitability': notes[uid],
                         'sift_per_view': counts, 'foreground_fraction_per_view': fractions})
    (ROOT / 'configs/hw2_selection.json').write_text(json.dumps({'selected': selected}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'selected': len(selected), 'uids': [row['uid'] for row in selected]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
