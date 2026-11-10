"""Print the persisted progress of the ten concrete course experiments."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
course = json.loads((ROOT / 'configs/hw2_course.json').read_text())
statuses = []
for row in course['objects']:
    root = ROOT / row['output_dir']
    status = {'object': row['slug'], 'name': row['name']}
    for label, path in [('render', 'render_progress.json'), ('data', 'data/summary.json'),
                        ('sfm', 'sfm/summary.json'), ('train', 'training_progress.json'),
                        ('eval', 'evaluation/summary.json'), ('final', 'summary.json')]:
        if (root / path).exists():
            item = json.loads((root / path).read_text())
            if label == 'render':
                status[label] = f"{item['processed']}/{item['total']}"
            elif label == 'sfm':
                status[label] = f"{item['registered_images']}/{item['train_images']}"
            elif label == 'train':
                status[label] = f"{item['iteration']}/{item['total']}"
            elif label == 'eval':
                status[label] = {'foreground_psnr': round(item['mean_foreground_psnr'], 3), 'psnr': round(item['mean_psnr'], 3)}
            else:
                status[label] = item['complete']
    print(json.dumps(status, ensure_ascii=False))
    statuses.append(status)

controls = []
for slug in course['representatives']:
    for condition in course['experiments']:
        root = ROOT / 'outputs/ablations' / f'{slug}_{condition}'
        item = {'object': slug, 'condition': condition}
        if (root / 'training_progress.json').exists():
            progress = json.loads((root / 'training_progress.json').read_text())
            item['train'] = f"{progress['iteration']}/{progress['total']}"
        if (root / 'evaluation/summary.json').exists():
            result = json.loads((root / 'evaluation/summary.json').read_text())
            item['complete'] = result['complete']
            item['foreground_psnr'] = round(result['mean_foreground_psnr'], 3)
        if len(item) > 2:
            print(json.dumps(item))
        controls.append(item)
early = sum((ROOT / row['output_dir'] / 'evaluation_7000/summary.json').exists() for row in course['objects'])
novel = sum((ROOT / 'outputs/novel_views' / row['slug'] / 'evaluation/summary.json').exists() for row in course['objects'])
completed = sum(bool(row.get('final')) for row in statuses)
control_count = sum(bool(row.get('complete')) for row in controls)
print(json.dumps({'baseline_complete': completed, 'baseline_total': 10, 'control_complete': control_count,
                  'control_total': 9, 'early_checkpoint_evaluations': early, 'novel_object_evaluations': novel}))
lines = ['# 课程作业当前进度', '', '| 步骤 | 进度 |', '|---|---|',
         '| 作业 1 清洗 | 完成：55,000 → 7,819 |', '| 共用程序 | 完成 |',
         f'| 作业 2 主实验 | {completed}/10 |', f'| 对照训练 | {control_count}/9 |',
         f'| 7k 检查点评估 | {early}/10 |', f'| 新高度评估 | {novel}/10 |',
         '| 报告与学习说明 | 初稿已准备；最终数据在实验完成后汇总 |',
         '| 提交信息 | 组号、成员分工、仓库地址待填写 |', '',
         '| 物体 | 渲染 | SfM | 训练 | 结果 |', '|---|---|---|---|---|']
for row in statuses:
    lines.append(f"| {row['name']} | {row.get('render', '已完成' if row.get('data') else '待执行')} | {row.get('sfm', '待执行')} | {row.get('train', '待执行')} | {'完成' if row.get('final') else '进行中' if len(row)>2 else '待执行'} |")
if not (ROOT / 'results/course_summary.json').exists():
    (ROOT / 'PROGRESS.md').write_text('\n'.join(lines) + '\n')
