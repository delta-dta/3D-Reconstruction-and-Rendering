"""Export every SIFT keypoint and geometrically verified image correspondence."""

import csv
import io
import json
from pathlib import Path
import sqlite3

import numpy as np


def export_matching(database_path, output):
    output = Path(output)
    arrays, pairs = {}, []
    with sqlite3.connect(database_path) as database:
        names = dict(database.execute('SELECT image_id,name FROM images'))
        for image_id, rows, cols, payload in database.execute('SELECT image_id,rows,cols,data FROM keypoints'):
            arrays[f'keypoints_{image_id}'] = np.frombuffer(payload, np.float32).reshape(rows, cols).copy()
        for pair_id, rows, payload in database.execute('SELECT pair_id,rows,data FROM two_view_geometries WHERE rows>0'):
            low, high = divmod(pair_id, 2147483647)
            arrays[f'inliers_{pair_id}'] = np.frombuffer(payload, np.uint32).reshape(rows, 2).copy()
            pairs.append({'pair_id': pair_id, 'first': names[low], 'second': names[high], 'inliers': rows})
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    (output / 'geometric_matches.npz').write_bytes(buffer.getvalue())
    with (output / 'verified_pairs.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(pairs[0]))
        writer.writeheader()
        writer.writerows(pairs)
    (output / 'image_ids.json').write_text(json.dumps(names, ensure_ascii=False, indent=2) + '\n')
