"""Collect the completed course experiments into reports and a compact submission."""

import csv
import gzip
from html import escape
import json
import os
from pathlib import Path
import shutil
from export_matching import export_matching

os.environ['MPLCONFIGDIR'] = '/tmp/3dvision-matplotlib'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
DOCS = ROOT / 'docs'


def read(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def copy(source, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def write_csv(path, rows):
    with Path(path).open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|'] +
                     ['| ' + ' | '.join(str(value) for value in row) + ' |' for row in rows])


def collect(course):
    objects, controls = [], []
    for obj in course['objects']:
        source = ROOT / obj['output_dir']
        main = read(source / 'summary.json')
        early = read(source / 'evaluation_7000/summary.json')
        novel = read(ROOT / 'outputs/novel_views' / obj['slug'] / 'evaluation/summary.json')
        assert main['complete'] and early['complete'] and novel['complete']
        assert main['sfm']['registered_images'] == 96 and main['evaluation']['test_views'] == 24
        assert Image.open(source / 'reconstruction.gif').n_frames == 72
        groups = {elevation: [row for row in novel['per_view'] if row['name'].startswith(f'r{index:02d}_')]
                  for index, elevation in enumerate(course['novel_elevations'])}
        novel_by_height = {elevation: {key: float(np.mean([row[key] for row in group]))
                                      for key in ['psnr', 'ssim', 'foreground_psnr']}
                           for elevation, group in groups.items()}
        objects.append({**obj, 'main': main, 'early': early, 'novel': novel, 'novel_by_height': novel_by_height})
    for slug in course['representatives']:
        for kind in course['experiments']:
            root = ROOT / 'outputs/ablations' / f'{slug}_{kind}'
            evaluation = read(root / 'evaluation/summary.json')
            training = read(root / 'model/summary.json')
            assert evaluation['complete'] and training['complete']
            if kind == 'gt_poses':
                geometry = read(root / 'pose_control.json')
                assert geometry['same_sparse_initialization']
                registration = 96
                error = None
                rotation_error = 0.0
            else:
                geometry = read(root / 'sfm/summary.json')
                registration = geometry['registered_images']
                error = geometry['mean_reprojection_error_pixels']
                rotation_error = geometry['median_rotation_error_degrees']
            controls.append({'object': slug, 'condition': kind, 'input_train_views': geometry['train_images'], 'train_views': evaluation['train_views'],
                             'registered_images': registration, 'sparse_points': geometry['points3D'], 'reprojection_error_px': error,
                             'median_rotation_error_degrees': rotation_error,
                             'psnr': evaluation['mean_psnr'], 'ssim': evaluation['mean_ssim'],
                             'foreground_psnr': evaluation['mean_foreground_psnr'],
                             'gaussians': training['gaussians'], 'training_seconds': training['elapsed_seconds']})
    return objects, controls


def compact_results(objects, controls):
    from finalize_hw2 import write_viewer
    bank = RESULTS / 'assignment1'
    bank.mkdir(parents=True, exist_ok=True)
    for name in ['summary.json', 'cleaned_models.jsonl', 'cleaned_models.csv', 'cleaned_uids.txt', 'hw2_candidates.jsonl']:
        copy(ROOT / 'cleaned' / name, bank / name)
    selected = [json.loads(line) for line in (ROOT / 'cleaned/hw2_candidates.jsonl').read_text().splitlines()]
    selected_uids = {row['uid'] for row in selected}
    case = next(row for row in map(json.loads, (ROOT / 'cleaned/cleaned_models.jsonl').read_text().splitlines())
                if row['uid'] == '5bda8ef98bfb4a908bd671b248ee22ba')
    credits = []
    metadata = {}
    for row in [*selected, case]:
        if row['shard'] not in metadata:
            with gzip.open(Path('/mnt/aoss/datasets/Objaversev1.0/metadata') / (row['shard'] + '.json.gz'), 'rt') as source:
                metadata[row['shard']] = json.load(source)
        record = metadata[row['shard']][row['uid']]
        user = record.get('user', {})
        credits.append({'uid': row['uid'], 'name': row['name'], 'license_code': row['license'],
                        'creator': user.get('displayName', user.get('username', '元数据未提供')),
                        'source_url': record.get('viewerUrl', 'https://sketchfab.com/3d-models/' + row['uid']),
                        'sha256': row['sha256'], 'shard': row['shard']})
        if row['uid'] in selected_uids:
            copy(ROOT / 'cleaned' / row['preview'], bank / row['preview'])
    write_json(RESULTS / 'asset_credits.json', credits)
    write_csv(RESULTS / 'asset_credits.csv', credits)
    (DOCS / 'ASSET_CREDITS.md').write_text('# 资产来源与署名\n\n许可代码来自原始元数据，源链接指向对应资产。前 10 项是正式对象，末项是匹配歧义案例。模型名称与作者按元数据保留；本项目对模型进行了归一化、多视角渲染和高斯重建。\n\n' + markdown_table(
        ['名称', '作者', '许可代码', '源资产', 'UID'],
        [[row['name'].replace('|', '\\|'), row['creator'].replace('|', '\\|'), row['license_code'],
          f"[来源]({row['source_url']})", row['uid']] for row in credits]) + '\n')
    for obj in objects:
        source = ROOT / obj['output_dir']
        target = RESULTS / f"hw2_{obj['slug']}"
        for name in ['reconstruction.gif', 'reconstruction_overview.jpg', 'dataset_overview.jpg', 'summary.json', 'environment.json',
                     'data/metadata.json', 'data/splits.json', 'sfm/summary.json', 'sfm/cameras.json', 'sfm/viewer.html', 'sfm/points_aligned.ply',
                     'model/loss.csv', 'model/cameras.json', 'model/training_config.json', 'evaluation/summary.json', 'evaluation_7000/summary.json']:
            copy(source / name, target / name)
        for image in (source / 'sfm/matches').glob('*.jpg'):
            copy(image, target / 'sfm/matches' / image.name)
        for image in (source / 'evaluation/comparisons').glob('*.jpg'):
            copy(image, target / 'evaluation/comparisons' / image.name)
        copy(source / 'evaluation_7000/comparisons/r01_v00.jpg', target / 'evaluation_7000/comparisons/r01_v00.jpg')
        export_matching(source / 'sfm/database.db', target / 'sfm')
        novel = ROOT / 'outputs/novel_views' / obj['slug']
        copy(novel / 'evaluation/summary.json', target / 'novel/summary.json')
        copy(novel / 'data/metadata.json', target / 'novel/metadata.json')
        for name in ['r00_v00.jpg', 'r01_v00.jpg', 'r02_v00.jpg', 'r02_v03.jpg']:
            copy(novel / 'evaluation/comparisons' / name, target / 'novel' / name)
    for row in controls:
        source = ROOT / 'outputs/ablations' / f"{row['object']}_{row['condition']}"
        target = RESULTS / 'ablations' / source.name
        for name in ['data/splits.json', 'model/loss.csv', 'model/cameras.json', 'model/training_config.json', 'model/summary.json', 'evaluation/summary.json', 'evaluation/comparisons/r01_v00.jpg']:
            copy(source / name, target / name)
        if row['condition'] == 'gt_poses':
            copy(source / 'pose_control.json', target / 'pose_control.json')
        else:
            write_viewer(source)
            for name in ['sfm/summary.json', 'sfm/cameras.json', 'sfm/points_aligned.ply', 'sfm/viewer.html']:
                copy(source / name, target / name)
            for image in (source / 'sfm/matches').glob('*.jpg'):
                copy(image, target / 'sfm/matches' / image.name)


def metrics(objects, controls):
    rows, iterations, heights = [], [], []
    for obj in objects:
        main, early = obj['main'], obj['early']
        sfm, training, evaluation = main['sfm'], main['training'], main['evaluation']
        rows.append({'object': obj['slug'], 'name': obj['name'], 'uid': obj['uid'], 'registered_images': sfm['registered_images'],
                     'sparse_points': sfm['points3D'], 'reprojection_error_px': sfm['mean_reprojection_error_pixels'],
                     'rotation_error_median_deg': sfm['median_rotation_error_degrees'], 'center_rmse': sfm['center_rmse_object_units'],
                     'psnr': evaluation['mean_psnr'], 'ssim': evaluation['mean_ssim'], 'foreground_psnr': evaluation['mean_foreground_psnr'],
                     'gaussians': training['gaussians'], 'training_seconds': training['elapsed_seconds'],
                     'foreground_psnr_7000': early['mean_foreground_psnr']})
        for iteration, result in [(7000, early), (30000, evaluation)]:
            iterations.append({'object': obj['slug'], 'iteration': iteration, 'psnr': result['mean_psnr'],
                               'ssim': result['mean_ssim'], 'foreground_psnr': result['mean_foreground_psnr'], 'gaussians': result['gaussians']})
        for elevation, result in obj['novel_by_height'].items():
            heights.append({'object': obj['slug'], 'elevation_degrees': elevation, 'views': 12, **result})
    write_csv(RESULTS / 'metrics.csv', rows)
    write_csv(RESULTS / 'iterations.csv', iterations)
    write_csv(RESULTS / 'novel_views.csv', heights)
    write_csv(RESULTS / 'experiments.csv', controls)
    write_json(RESULTS / 'metrics.json', rows)
    write_json(RESULTS / 'experiments.json', controls)
    return rows, iterations, heights


def plots(objects, controls, rows):
    folder = RESULTS / 'figures'
    folder.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.dpi': 180, 'axes.grid': True, 'grid.alpha': .18})

    def save(figure, name):
        figure.tight_layout()
        for extension in ['png', 'pdf']:
            figure.savefig(folder / f'{name}.{extension}', bbox_inches='tight')
        plt.close(figure)

    names = [row['object'] for row in rows]
    x = np.arange(len(rows))
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    axes[0].bar(x - .18, [row['psnr'] for row in rows], .36, label='Full image', color='#6b8cba')
    axes[0].bar(x + .18, [row['foreground_psnr'] for row in rows], .36, label='Foreground', color='#28636b')
    axes[0].set(ylabel='PSNR (dB)', title='96-view SfM + 30,000-step 3DGS', xticks=x, xticklabels=names)
    axes[0].legend()
    axes[1].bar(x, [row['reprojection_error_px'] for row in rows], color='#c17a46')
    axes[1].set(ylabel='Mean reprojection error (pixels)', title='SfM: 96/96 cameras per object', xticks=x, xticklabels=names)
    for axis in axes:
        axis.tick_params(axis='x', rotation=55)
    save(fig, 'baseline_metrics')

    fig, axis = plt.subplots(figsize=(10, 4.6))
    for obj in objects:
        with (ROOT / obj['output_dir'] / 'model/loss.csv').open() as source:
            loss = list(csv.DictReader(source))
        steps = np.array([int(row['iteration']) for row in loss])
        values = np.array([float(row['loss']) for row in loss])
        average = np.convolve(values, np.ones(10) / 10, mode='valid')
        axis.plot(steps[9:], average, label=obj['slug'], linewidth=1.1)
    axis.set(xlabel='Iteration', ylabel='Training loss (10 logged samples averaged)', yscale='log',
             title='Independent object optimization; one seed per run')
    axis.axvline(15000, color='#888', linestyle='--', linewidth=.8)
    axis.legend(ncol=5, fontsize=8)
    save(fig, 'training_loss')

    by_object = {obj['slug']: obj for obj in objects}
    by_control = {(row['object'], row['condition']): row for row in controls}
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4))
    for slug in ['lamb', 'can', 'robot']:
        scores = [by_control[slug, 'views24']['foreground_psnr'], by_control[slug, 'views48']['foreground_psnr'],
                  by_object[slug]['main']['evaluation']['mean_foreground_psnr']]
        axes[0].plot([24, 48, 96], scores, 'o-', label=slug)
        axes[1].plot([0, 1], [scores[-1], by_control[slug, 'gt_poses']['foreground_psnr']], 'o-', label=slug)
    for obj in objects:
        axes[2].plot([7, 30], [obj['early']['mean_foreground_psnr'], obj['main']['evaluation']['mean_foreground_psnr']],
                     'o-', label=obj['slug'], linewidth=1)
    axes[0].set(xlabel='Input training views', ylabel='Foreground PSNR (dB)', xticks=[24,48,96], title='Fixed 30,000-step budget')
    axes[1].set(xticks=[0,1], xticklabels=['SfM poses', 'Ground-truth poses'], title='Same sparse-point initialization')
    axes[2].set(xlabel='Iteration (thousands)', xticks=[7,30], title='Saved checkpoints; same test views')
    axes[0].legend(fontsize=8)
    axes[1].legend(fontsize=8)
    axes[2].legend(fontsize=7, ncol=2)
    save(fig, 'ablation_results')

    fig, axis = plt.subplots(figsize=(9, 4.5))
    for obj in objects:
        axis.plot([0,30,60], [obj['novel_by_height'][e]['foreground_psnr'] for e in [0,30,60]], 'o-', label=obj['slug'], linewidth=1)
    axis.axvspan(45, 63, color='#d39a60', alpha=.13)
    axis.set(xlabel='Test elevation (degrees)', ylabel='Foreground PSNR (dB)', xticks=[0,30,45,60],
             title='New elevations: 12 azimuths each; training elevations = -20, 15, 45')
    axis.legend(ncol=5, fontsize=8)
    save(fig, 'novel_elevations')


def matching_case(objects):
    from finalize_hw2 import write_viewer
    source = ROOT / 'outputs/hw2_basket'
    target = RESULTS / 'matching_case'
    write_viewer(source)
    for name in ['dataset_overview.jpg', 'sfm/summary.json', 'sfm/cameras.json', 'sfm/viewer.html']:
        copy(source / name, target / name)
    geometry = read(source / 'sfm/summary.json')
    for image in (source / 'sfm/matches').glob('*.jpg'):
        copy(image, target / 'sfm/matches' / image.name)
    shoe = next(obj for obj in objects if obj['slug']=='shoe')['main']['sfm']
    table = markdown_table(['候选','每图 SIFT 中位数','注册图','重投影误差 px','旋转误差中位数','中心 RMSE'],
        [['编织器物', geometry['median_keypoints'], '96/96', f"{geometry['mean_reprojection_error_pixels']:.3f}",
          f"{geometry['median_rotation_error_degrees']:.3f}°", f"{geometry['center_rmse_object_units']:.4f}"],
         ['彩色跑鞋', shoe['median_keypoints'], '96/96', f"{shoe['mean_reprojection_error_pixels']:.3f}",
          f"{shoe['median_rotation_error_degrees']:.3f}°", f"{shoe['center_rmse_object_units']:.4f}"]])
    text = f'''# 匹配案例：特征很多，为什么相机仍然恢复错误？

在正式对象验证中，编织器物 `5bda8ef98bfb4a908bd671b248ee22ba` 的 96 张图全部完成注册，平均重投影误差也不高。但与合成参考位姿对照后，发现全局相机结构明显错误。

{table}

中心 RMSE 的单位为物体最长边=2；旋转误差是在仅用训练相机中心做 Sim(3) 对齐后计算。

![编织器物的多视角输入](../results/matching_case/dataset_overview.jpg)

该物体的编织细节有很强的周期重复。结合多视角外观、{geometry['verified_pairs']:,} 个被验证图像对及位姿结果，我们判断局部相似纹理产生了大量歧义对应。SfM 能在这些对应上得到较低的重投影误差，却没有恢复正确的环绕相机结构。

这说明 SIFT 数量、注册率和重投影误差分别衡量不同事情：局部特征可以很多，错误的重复点对应也可能形成内部自洽的几何。相机与参考位姿对照、连续环绕的视觉结果提供了额外证据。

为满足 10 个正式对象均具有稳定重建条件的要求，本项目中止该候选的高斯训练，从已有清洗清单选择彩色跑鞋。跑鞋的文字、非周期色块、鞋带和磨损提供了更明确的对应，正式的 10 物体清单由 `configs/hw2_course.json` 与 `cleaned/hw2_candidates.jsonl` 统一记录。全量 7,819 个清洗结果不变。

该案例保存输入、真实匹配图与估计相机，单独作为流程分析，未混入正式 10 物体均值。可[交互查看相机和点云](../results/matching_case/sfm/viewer.html)，也可查看[原始 SfM 统计](../results/matching_case/sfm/summary.json)。

继续优化这一类对象时，可以研究使用拍摄顺序约束匹配图、提高对应的区分度，以及检查不同视图之间的几何一致性。这里的正式结果继续采用相同的 SIFT/COLMAP 基线完成。
'''
    (DOCS / 'MATCHING_CASE.md').write_text(text)


def experiment_report(objects, controls):
    by_object = {obj['slug']: obj for obj in objects}
    robot24 = next(row for row in controls if row['object']=='robot' and row['condition']=='views24')
    robot48 = next(row for row in controls if row['object']=='robot' and row['condition']=='views48')
    rows = []
    for slug in ['lamb','can','robot']:
        for label, views, result in [('24 views', 24, next(r for r in controls if r['object']==slug and r['condition']=='views24')),
                                     ('48 views', 48, next(r for r in controls if r['object']==slug and r['condition']=='views48'))]:
            rows.append([slug, label, views, result['registered_images'], result['train_views'], result['sparse_points'], f"{result['foreground_psnr']:.3f}",
                         f"{result['psnr']:.3f}", f"{result['ssim']:.5f}"])
        baseline = by_object[slug]['main']['evaluation']
        rows.append([slug, '96 views / SfM', 96, 96, 96, by_object[slug]['main']['sfm']['points3D'], f"{baseline['mean_foreground_psnr']:.3f}", f"{baseline['mean_psnr']:.3f}", f"{baseline['mean_ssim']:.5f}"])
        truth = next(r for r in controls if r['object']==slug and r['condition']=='gt_poses')
        rows.append([slug, '96 views / GT poses', 96, '标定位姿', 96, truth['sparse_points'], f"{truth['foreground_psnr']:.3f}", f"{truth['psnr']:.3f}", f"{truth['ssim']:.5f}"])
    views_table = markdown_table(['物体','条件','输入训练图','注册图','实际训练图','初始稀疏点','前景 PSNR','全图 PSNR','SSIM'], rows)
    checkpoint_table = markdown_table(['物体','7k 前景 PSNR','30k 前景 PSNR','变化 dB','7k 高斯数','30k 高斯数'],
        [[obj['slug'], f"{obj['early']['mean_foreground_psnr']:.3f}", f"{obj['main']['evaluation']['mean_foreground_psnr']:.3f}",
          f"{obj['main']['evaluation']['mean_foreground_psnr'] - obj['early']['mean_foreground_psnr']:+.3f}",
          obj['early']['gaussians'], obj['main']['training']['gaussians']] for obj in objects])
    novel_table = markdown_table(['物体','0° 前景 PSNR','30° 前景 PSNR','60° 前景 PSNR'],
        [[obj['slug']] + [f"{obj['novel_by_height'][e]['foreground_psnr']:.3f}" for e in [0,30,60]] for obj in objects])
    mean_delta = float(np.mean([obj['main']['evaluation']['mean_foreground_psnr'] - obj['early']['mean_foreground_psnr'] for obj in objects]))
    views_delta = float(np.mean([by_object[s]['main']['evaluation']['mean_foreground_psnr'] - next(r for r in controls if r['object']==s and r['condition']=='views24')['foreground_psnr'] for s in ['lamb','can','robot']]))
    pose_delta = float(np.mean([next(r for r in controls if r['object']==s and r['condition']=='gt_poses')['foreground_psnr'] - by_object[s]['main']['evaluation']['mean_foreground_psnr'] for s in ['lamb','can','robot']]))
    height_means = {e: float(np.mean([obj['novel_by_height'][e]['foreground_psnr'] for obj in objects])) for e in [0,30,60]}
    text = f'''# 作业 2：对照实验与实际结果

图像子集、分辨率与训练预算在运行前写入 `configs/experiments/`。每个条件记录一次固定种子的正式训练结果；机器人 24 图条件在修正最终模型导出后重算，过程见复现说明。表中数值来自实际保存的评估文件。各物体内部使用同一测试集；比较时先取每视角指标，再取物体均值。

## 1. 图像数量与相机位姿

羊摆件、罐头和机器人使用 24⊂48⊂96 的嵌套训练子集，三个高度均匀覆盖。96 张原训练图按顺序每 4 张选 1 张得到 24 张，每 2 张选 1 张得到 48 张。所有条件使用相同的 24 张测试图、512 分辨率、30,000 次迭代和随机种子。每个子集重新提取特征、匹配和执行 SfM。

位姿对照只将 96 张训练图的相机外参替换为渲染器标定值，仍使用相同 COLMAP 稀疏点初始化，没有添加 GLB 表面点。`pose_control.json` 记录点坐标一致性。

{views_table}

三个对象从 24 张扩展到 96 张，前景 PSNR 的配对均值变化为 **{views_delta:+.3f} dB**。从 SfM 位姿改为真实位姿，配对均值变化为 **{pose_delta:+.3f} dB**。逐物体结果用于判断这些变化是否一致。

图像数量同时影响视角覆盖、匹配约束、稀疏初始化和每张图被优化的次数；这里测量的是固定迭代预算下整条流程的效果。位姿对照保留 SfM 点云误差和有限优化过程，因此不将它表述为完整几何真值的重建上界。

机器人 24 图输入最终注册了 {robot24['registered_images']} 个相机，旋转误差中位数为 {robot24['median_rotation_error_degrees']:.3f}°，出现明显几何退化。该对照使用最终返回重建中的 {robot24['train_views']} 个相机训练，输入数量和有效训练数量分别记录；未使用真实位姿修补或改变匹配参数。48 图条件注册了 {robot48['registered_images']}/48，相机旋转误差中位数仍为 {robot48['median_rotation_error_degrees']:.3f}°，因此注册率本身不足以证明几何正确。指标描述低视图条件下包含 SfM 失败影响的端到端结果。正式机器人基线使用 96/96 相机，旋转误差中位数约 0.079°。

可[查看机器人 24 图条件](../results/ablations/robot_views24/sfm/viewer.html)、[48 图条件](../results/ablations/robot_views48/sfm/viewer.html)的相机与点云，与[96 图条件](../results/hw2_robot/sfm/viewer.html)对照。

## 2. 训练时长

直接加载每个主实验保存的 7,000 和 30,000 步高斯模型，在同一测试集重新评估。7,000 步仍处于增密阶段，30,000 步已完成增密与后续优化，所以该实验同时反映训练时间和表示容量的变化。

{checkpoint_table}

10 个物体从 7k 到 30k 的前景 PSNR 配对均值变化为 **{mean_delta:+.3f} dB**。损失曲线展示训练趋势，留出指标判断这些优化是否转化为新视角收益。

![三组对照实验](../results/figures/ablation_results.png)

## 3. 新高度测试

独立渲染 0°、30°、60° 三个高度，各 12 个方位角，方位角统一偏移 4.5°，共 36 张/物体。这些图像与相机不进入任何训练或训练相机对齐。0°、30°处于训练高度之间；60°超过最高训练高度 45°。相同图像分辨率、光照和相机内参用于评价视角变化的影响。

{novel_table}

10 物体前景 PSNR 的均值分别为：0° **{height_means[0]:.3f} dB**，30° **{height_means[30]:.3f} dB**，60° **{height_means[60]:.3f} dB**。将高处测试与原 24 张插值测试分开报告，避免混淆评价范围。

![新高度测试](../results/figures/novel_elevations.png)

## 数据与图像入口

- `results/experiments.csv`：9 次额外训练的逐条件指标。
- `results/iterations.csv`：10 物体两个检查点的指标。
- `results/novel_views.csv`：各物体、各新高度的均值。
- `results/ablations/`：配置对应结果、损失、固定测试视角对照图。
- `outputs/ablations/`：完整输入、SfM、模型、检查点和全部对照图。
- `outputs/novel_views/`：全部独立测试图、相机参数和逐视角结果。

实验结论覆盖当前合成数据、固定采样和所选物体。进一步优化可以优先围绕误差集中区域增加观测，再比较特征匹配、图像分辨率与训练设置。
'''
    (DOCS / 'EXPERIMENTS.md').write_text(text)
    return {'view_count_mean_delta_fg_db': views_delta, 'gt_pose_mean_delta_fg_db': pose_delta,
            'iteration_mean_delta_fg_db': mean_delta, 'novel_height_mean_fg_db': height_means}


STYLE = '''body{font:16px/1.7 system-ui,sans-serif;max-width:1240px;margin:32px auto;padding:0 20px;color:#24313b;background:#f8fafb}
a{color:#175d87}h1{font-size:32px;line-height:1.25}h2{margin-top:36px}img{max-width:100%;height:auto;background:white}
table{width:100%;border-collapse:collapse;background:white;font-size:14px}th,td{padding:8px;border-bottom:1px solid #dbe3e7;text-align:left}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}.card{background:#fff;padding:18px;border:1px solid #dce4e8;border-radius:9px}
.card img{width:100%}.card h3{margin:0}.sub{color:#576974;font-size:14px}.stats{display:flex;gap:16px;flex-wrap:wrap}.stats div{padding:15px 24px;background:#e9f1f1;border-radius:7px}
nav a{display:inline-block;margin:5px 18px 5px 0}.tablewrap{overflow-x:auto}iframe{width:100%;height:730px;border:1px solid #dce4e8}
button{padding:8px 14px;margin:8px 8px 15px 0;border:1px solid #afc5cc;background:white;border-radius:5px;cursor:pointer}.active{background:#28636b;color:white}
code{font-size:13px;overflow-wrap:anywhere}@media print{body{max-width:none;background:white}nav,button{display:none}.card{break-inside:avoid}}'''


def head(title):
    return f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>{STYLE}</style><body>'


def object_pages(objects):
    for obj in objects:
        folder = RESULTS / f"hw2_{obj['slug']}"
        main = obj['main']
        sfm, train, evaluation = main['sfm'], main['training'], main['evaluation']
        parts = [head(obj['name'] + '：完整重建结果'), '<nav><a href="../../index.html">结果总览</a><a href="../../docs/PIPELINE.md">流程与复现</a></nav>',
                 f'<h1>{escape(obj["name"])}</h1><p class="sub">UID：<code>{obj["uid"]}</code> · SfM 初始化 → 官方 3DGS</p>',
                 '<img src="reconstruction.gif" width="512" alt="训练后的高斯模型环绕动画">',
                 f'<p>96 张训练 / 24 张测试；相机注册 {sfm["registered_images"]}/96；稀疏点 {sfm["points3D"]:,}；重投影误差 {sfm["mean_reprojection_error_pixels"]:.3f} px。</p>',
                 f'<p>30,000 步，{train["gaussians"]:,} 个高斯；全图 PSNR {evaluation["mean_psnr"]:.3f} dB，SSIM {evaluation["mean_ssim"]:.5f}，前景 PSNR {evaluation["mean_foreground_psnr"]:.3f} dB。</p>',
                 '<nav><a href="summary.json">完整统计</a><a href="model/training_config.json">训练参数</a><a href="model/loss.csv">损失</a><a href="data/splits.json">划分</a><a href="data/metadata.json">标定与真实相机</a><a href="environment.json">环境</a></nav>',
                 '<h2>输入图像与多角度重建</h2><img loading="lazy" src="dataset_overview.jpg" alt="输入图像"><img loading="lazy" src="reconstruction_overview.jpg" alt="八视角重建">',
                 '<h2>几何验证后的特征匹配</h2><p>每张图最多画 80 条线，标题和下表记录全部几何验证内点数量。</p>']
        for match in sfm['matches']:
            parts.append(f'<p>{escape(match["first"])} ↔ {escape(match["second"])}：{match["verified_matches"]} 个内点。</p><img loading="lazy" src="sfm/{escape(match["image"])}" alt="实际特征匹配">')
        parts.extend(['<nav><a href="sfm/verified_pairs.csv">全部验证图像对</a><a href="sfm/geometric_matches.npz">关键点与全部内点数组</a><a href="sfm/image_ids.json">图像 ID</a><a href="../../docs/MATCHING_FORMAT.md">读取方法</a></nav>',
                      '<h2>交互式 SfM 点云与相机</h2><iframe loading="lazy" src="sfm/viewer.html" title="点云与相机"></iframe>',
                      '<h2>24 张固定留出图像</h2><p>点击视角可查看真实图像、预测图像及放大的误差。</p><table><tr><th>视角</th><th>前景 PSNR</th><th>全图 PSNR</th><th>SSIM</th></tr>'])
        for row in evaluation['per_view']:
            parts.append(f'<tr><td><a href="evaluation/comparisons/{Path(row["name"]).stem}.jpg">{row["name"]}</a></td><td>{row["foreground_psnr"]:.3f}</td><td>{row["psnr"]:.3f}</td><td>{row["ssim"]:.5f}</td></tr>')
        parts.extend(['</table><h2>训练时长与新高度测试</h2>',
                      f'<p>7,000 步前景 PSNR：{obj["early"]["mean_foreground_psnr"]:.3f} dB。<a href="evaluation_7000/comparisons/r01_v00.jpg">7k 对照图</a> · <a href="evaluation/comparisons/r01_v00.jpg">30k 同视角对照图</a>。</p>',
                      '<table><tr><th>独立测试高度</th><th>视角数</th><th>前景 PSNR</th><th>全图 PSNR</th><th>示例</th></tr>'])
        for index, elevation in enumerate([0,30,60]):
            row = obj['novel_by_height'][elevation]
            parts.append(f'<tr><td>{elevation}°</td><td>12</td><td>{row["foreground_psnr"]:.3f}</td><td>{row["psnr"]:.3f}</td><td><a href="novel/r{index:02d}_v00.jpg">对照图</a></td></tr>')
        parts.extend(['</table><p>0°/30°位于训练高度之间，60°超过训练最高高度。所有测试图像未参与训练。<a href="novel/summary.json">逐视角指标</a></p>',
                      '<p>本页为可提交的紧凑结果。原始数据、SQLite 数据库、高斯 PLY、训练检查点和全部 PNG 保存在本地 outputs/ 对应目录。</p></body></html>'])
        (folder / 'index.html').write_text('\n'.join(parts) + '\n')


def dashboard(objects, rows, findings):
    submission = read(ROOT / 'configs/submission.json')
    parts = [head('三维视觉课程作业：清洗、重建与实验'), '<h1>从 Objaverse 清洗到三维高斯重建</h1>',
             '<p>从55,000个资产筛选到10个物体的重建、匹配、环绕动画与流程对照实验。</p>',
             '<nav><a href="docs/HOMEWORK2_REPORT.pdf">正式报告 PDF</a><a href="docs/HOMEWORK2_REPORT.md">正式报告 Markdown</a></nav>',
             '<nav><a href="docs/PIPELINE.md">流程与运行</a><a href="docs/EXPERIMENTS.md">对照实验</a><a href="docs/MATCHING_CASE.md">匹配歧义案例</a><a href="docs/REPRODUCE.md">复现</a><a href="docs/PROMPTS.md">提示词</a><a href="docs/ASSET_CREDITS.md">资产署名</a></nav>',
             '<div class="stats"><div><b>7,819</b><br>清洗后资产</div><div><b>10 / 10</b><br>完整重建与 GIF</div><div><b>960 / 960</b><br>训练相机注册</div><div><b>9</b><br>额外对照训练</div><div><b>360</b><br>新高度测试图</div></div>',
             '<h2>10 个物体的重建结果</h2><p>每个物体使用独立模型。点击进入，可查看全部匹配、测试图像对照及交互式 SfM 点云。</p><div class="grid">']
    for obj in objects:
        evaluation = obj['main']['evaluation']
        folder = f'results/hw2_{obj["slug"]}'
        parts.append(f'<article class="card"><h3><a href="{folder}/index.html">{escape(obj["name"])}</a></h3><img loading="lazy" src="{folder}/reconstruction.gif" alt="{escape(obj["name"])}重建动画"><p class="sub">前景 PSNR {evaluation["mean_foreground_psnr"]:.2f} dB · SSIM {evaluation["mean_ssim"]:.4f}</p><a href="{folder}/index.html">匹配、点云与指标 →</a></article>')
    parts.extend(['</div><h2>逐物体指标</h2><button class="active" data-mode="fg">前景 PSNR</button><button data-mode="full">全图 PSNR</button>',
                  '<div class="tablewrap"><table id="metrics"><thead><tr><th>物体</th><th>注册</th><th>稀疏点</th><th>重投影 px</th><th id="metric-title">前景 PSNR</th><th>SSIM</th><th>高斯数</th></tr></thead><tbody>'])
    for row in rows:
        parts.append(f'<tr><td>{escape(row["name"])}</td><td>96/96</td><td>{row["sparse_points"]:,}</td><td>{row["reprojection_error_px"]:.3f}</td><td class="psnr" data-fg="{row["foreground_psnr"]:.3f}" data-full="{row["psnr"]:.3f}">{row["foreground_psnr"]:.3f}</td><td>{row["ssim"]:.5f}</td><td>{row["gaussians"]:,}</td></tr>')
    parts.extend(['</tbody></table></div><p><a href="results/metrics.csv">下载全部指标 CSV</a> · <a href="results/course_summary.json">全课程统计</a></p>',
                  '<h2>流程影响分析</h2>', f'<p>训练 7k→30k 的前景 PSNR 平均变化：{findings["iteration_mean_delta_fg_db"]:+.3f} dB；三个代表物体 24→96 视图的变化：{findings["view_count_mean_delta_fg_db"]:+.3f} dB；SfM→真实位姿对照变化：{findings["gt_pose_mean_delta_fg_db"]:+.3f} dB。</p>',
                  '<img loading="lazy" src="results/figures/ablation_results.png" alt="视图数、位姿、训练时长对照"><p><a href="docs/EXPERIMENTS.md">实验设置、逐项数据与分析</a></p>',
                  '<img loading="lazy" src="results/figures/novel_elevations.png" alt="新高度评估"><img loading="lazy" src="results/figures/training_loss.png" alt="训练损失曲线">',
                  '<h2>作业 1 结果</h2><p>55,000 → 44,597 → 31,614 → 31,607 → 17,150 → 7,819。原始 GLB 保持原路径，输出清单与 SHA。</p>',
                  '<nav><a href="results/assignment1/cleaned_models.csv">清洗 CSV</a><a href="results/assignment1/cleaned_uids.txt">UID 清单</a><a href="results/assignment1/summary.json">清洗统计</a></nav>',
                  f'<p>{escape(submission["group_number"])} · {"、".join(escape(row["name"]) for row in submission["members"])} · <a href="{escape(submission["github_url"].removesuffix(".git"))}">GitHub 仓库</a>。成员分工与网站提交方法见 <a href="docs/SUBMISSION.md">提交说明</a>。</p>',
                  '''<script>document.querySelectorAll('button[data-mode]').forEach(button=>button.onclick=()=>{document.querySelectorAll('button[data-mode]').forEach(b=>b.classList.toggle('active',b===button));document.getElementById('metric-title').textContent=button.dataset.mode==='fg'?'前景 PSNR':'全图 PSNR';document.querySelectorAll('td.psnr').forEach(cell=>cell.textContent=cell.dataset[button.dataset.mode]);});</script></body></html>'''])
    (ROOT / 'index.html').write_text('\n'.join(parts) + '\n')


def course_averages(rows):
    return {key: float(np.mean([row[key] for row in rows]))
            for key in ['psnr', 'ssim', 'foreground_psnr', 'reprojection_error_px', 'training_seconds']}


def prompt_document():
    config = read(ROOT / 'configs/preview_deepseek.json')
    parameters = {key: config[key] for key in ['endpoint','model','model_version_at_setup','temperature','max_tokens','thinking','response_format','image_detail']}
    (DOCS / 'PROMPTS.md').write_text('# 正式流程使用的提示词\n\n作业 1 的实际提示词从 `configs/preview_deepseek.json` 原样导出。每个资产发送同一段文字与四视角 JPEG 拼图（按 0、90、180、270°顺序排列）。代码未添加独立 system 消息。\n\n## 用户消息文字\n\n```text\n' + config['prompt'] + '\n```\n\n## 请求设置\n\n```json\n' + json.dumps(parameters, ensure_ascii=False, indent=2) + '\n```\n\nJSON 的 `keep=true` 表示保留。`caption` 参与返回结构，不持久保存为淘汰原因。SfM、3DGS 与评价不使用语言模型提示词。AI 编程辅助的任务指令摘录见 `AI_USAGE.md`。\n')


def readme(rows, averages):
    submission = read(ROOT / 'configs/submission.json')
    members = markdown_table(['成员', '分工'],
        [[row['name'], row['contribution']] for row in submission['members']])
    table = markdown_table(['物体','前景 PSNR','全图 PSNR','SSIM','结果'],
        [[row['name'], f"{row['foreground_psnr']:.3f}", f"{row['psnr']:.3f}", f"{row['ssim']:.5f}",
          f"[GIF](results/hw2_{row['object']}/reconstruction.gif) · [详细结果](results/hw2_{row['object']}/index.html)"] for row in rows])
    text = f'''# 三维视觉课程项目：Objaverse 清洗、SfM 与 3DGS

已完成 **55,000 → 7,819** 资产筛选，以及 **10个物体的完整重建、10个GIF、全部匹配结果和流程对照实验**。

**{submission['group_number']}** · GitHub：[{submission['github_url'].removesuffix('.git')}]({submission['github_url'].removesuffix('.git')})

**正式提交报告：[PDF](docs/HOMEWORK2_REPORT.pdf) · [Markdown 源文件](docs/HOMEWORK2_REPORT.md)**

[结果总览](index.html) · [Pipeline](docs/PIPELINE.md) · [对照实验](docs/EXPERIMENTS.md) · [复现](docs/REPRODUCE.md) · [提示词](docs/PROMPTS.md) · [提交说明](docs/SUBMISSION.md)

另有一个[重复纹理造成位姿歧义的实际案例](docs/MATCHING_CASE.md)，用于理解“特征多”和“对应可靠”的区别。

完整下载仓库（Code → Download ZIP）或本机生成的 `dist/coursework_submission.zip` 后解压，用浏览器打开根目录 `index.html`，保持 `results/` 与 `docs/` 的相对位置。单独下载 HTML 不包含图片资源。GitHub 可直接阅读 Markdown、PDF 并打开各 GIF。

## 运行pipeline

激活 `3dvision` 并在 `configs/pipeline.json` 中设置数据与工具位置后，从仓库根目录运行：

```bash
python -B programs/run_pipeline.py --config configs/hw2_lamb.json
```

统一入口依次完成成像、图像准备、SIFT/SfM、3DGS训练、评价/GIF和结果页面，新运行保存在 `outputs/pipeline/`。环境安装、十物体批处理和各阶段输出见 [PIPELINE](docs/PIPELINE.md)。六个阶段共用原实验的代码与参数。

只检查已提交材料可运行 `python -B programs/verify_repository.py`，不需要原始数据或GPU。

## 成员与分工

{members}

{submission['contribution_note']} AI 辅助范围见 [AI_USAGE](docs/AI_USAGE.md)。

## 主要结果

主实验：每物体 120 张 512² 参考图，96 张训练、24 张留出测试；SIFT / COLMAP 相机恢复与三角化，官方 3DGS 训练 30,000 次。全部 **960/960** 张训练相机注册成功。

10 物体等权平均：前景 PSNR **{averages['foreground_psnr']:.3f} dB**，全图 PSNR **{averages['psnr']:.3f} dB**，SSIM **{averages['ssim']:.5f}**。

{table}

每个结果页提供实际匹配图、全部几何验证内点、相机与稀疏点、24 个测试视角的对照及误差图。GIF 均由训练后的高斯模型生成。

## 流程与实验

```mermaid
flowchart LR
    A[Objaverse GLB] --> B[规则与视觉清洗]
    B --> C[多视角图像]
    C --> D[SIFT / 几何验证]
    D --> E[SfM 相机与稀疏点]
    E --> F[3DGS 优化]
    F --> G[新视角 / GIF / 评估]
```

- 图像数量：羊、罐头、机器人分别使用 24/48/96 个训练视角，固定测试集与迭代预算。
- 位姿：同三个对象比较 SfM 与真实训练外参，保持同一稀疏点初始化。
- 时长：全部 10 个对象比较 7k/30k 检查点。
- 视角覆盖：另渲染 0°/30°/60°各 12 个新视角，共 360 张独立测试图。

主流程使用标定内参，从训练图恢复外参；稀疏初始化来自图像三角化。训练相机中心只用于全局 Sim(3) 对齐，测试图像与外参不进入 SfM 或训练。全图指标包含白背景，因此同时报告前景 PSNR。

## 环境

```bash
source /data/260010047/miniconda3/etc/profile.d/conda.sh
conda activate 3dvision
```

RTX 5090；Python 3.12.3；PyTorch 2.8.0+cu129、torchvision 0.23.0+cu129；PyCOLMAP 3.13.0；Blender 4.5.3；CUDA 12.9、GCC 13.3、原生 sm_120 扩展。固定依赖在 `environment.yml`。

官方 3DGS 提交 `54c035f7834b564019656c3e3fcc3646292f727d`。环境重建后，按 `scripts/setup_hw2_tools.sh` 获取代码、应用 `<cstdint>` 补丁、安装三个扩展。各子模块提交记录在 `results/hw2_*/environment.json`。

## 代码与结果

```text
programs/          清洗、渲染、SfM、训练、评价与报告程序
configs/           筛选规则、完整提示词、对象、实验参数
scripts/           无参数启动脚本；已完成命令以注释保留
patches/           CUDA 12.9 标准头文件补丁
docs/              报告、实验、学习、复现、资产署名
results/           可提交的 GIF、匹配数组、对照图、指标与图表
outputs/           本机完整图像、数据库、模型与检查点（不入 Git）
cleaned/           本机全量清洗清单与预览（不入 Git）
.tools/            本机 Blender、官方 3DGS 和系统库（不入 Git）
```

清洗输入为 `/mnt/aoss/datasets/Objaversev1.0/` 的 000-000～000-010，共 11 个分片。最终完整清单同时收集至 `results/assignment1/`，原始 GLB 保持不变。

作业 1 按 `run_coarse_filter` → `run_glb_filter` → `run_render_full` → `run_preview_deepseek` → `run_finalize_cleaning` 执行。作业 2 从 `configs/hw2_lamb.json` 和 `programs/render_hw2.py` 开始阅读，再依次看 prepare、reconstruct、train、evaluate。详细命令见[复现说明](docs/REPRODUCE.md)。

API Key 位于本地 `ds_api_key`，由 `.gitignore` 排除。清洗正式请求使用 `deepseek-flash`，配置时版本记录为 `DeepSeek-V4.1-Flash-1017`；已记录用量按当时离峰/峰值参数估算 $1.0621/$2.1242，属于同一用量的两种估算。后续重建与实验不调用 API。

资产来源和许可见 [ASSET_CREDITS](docs/ASSET_CREDITS.md)，第三方依赖见 [THIRD_PARTY](docs/THIRD_PARTY.md)，AI 辅助范围见 [AI_USAGE](docs/AI_USAGE.md)。
'''
    (ROOT / 'README.md').write_text(text)


def main():
    RESULTS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    course = read(ROOT / 'configs/hw2_course.json')
    objects, controls = collect(course)
    compact_results(objects, controls)
    matching_case(objects)
    rows, iterations, heights = metrics(objects, controls)
    plots(objects, controls, rows)
    findings = experiment_report(objects, controls)
    averages = course_averages(rows)
    readme(rows, averages)
    prompt_document()
    object_pages(objects)
    dashboard(objects, rows, findings)
    summary = {'experiments_complete': True, 'assignment1': read(ROOT / 'cleaned/summary.json')['counts'],
               'baseline_objects': len(objects), 'registered_cameras': sum(row['registered_images'] for row in rows),
               'gifs': len(objects), 'gif_frames_each': 72, 'baseline_train_views_each': 96, 'baseline_test_views_each': 24,
               'control_trainings': len(controls), 'checkpoint_evaluations': len(iterations),
               'novel_test_views': sum(row['views'] for row in heights), 'evaluation_reports': 39,
               'averages': averages, 'findings': findings, 'submission': read(ROOT / 'configs/submission.json')}
    write_json(RESULTS / 'course_summary.json', summary)
    write_progress()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def write_progress():
    (ROOT / 'PROGRESS.md').write_text('''# 课程作业执行进度

| 步骤 | 状态 | 结果 |
|---|---|---|
| 作业 1 清洗 | 完成 | 55,000 → 7,819 |
| 共用程序 | 完成 | 固定配置、独立程序和命令 |
| 作业 2 主实验 | 完成 | 10/10，960/960 相机，10 GIF |
| 图像数与位姿对照 | 完成 | 9 次额外训练 |
| 训练时长 | 完成 | 10 个物体，7k/30k |
| 新高度 | 完成 | 10 个物体、360 张测试图 |
| 报告与学习资料 | 完成 | docs/ 和总览页面 |
| 提交信息 | 已配置 | 第一组、成员1至4、等量分工、GitHub 地址 |
| 正式提交报告 | 已完成 | Markdown、PDF；校验见 results/submission_verification.json |
| 统一pipeline | 已验证 | 羊摆件六阶段重跑；results/pipeline_validation.json |
| GitHub仓库 | main分支 | https://github.com/delta-dta/3D-Reconstruction-and-Rendering |
''')


if __name__ == '__main__':
    main()
