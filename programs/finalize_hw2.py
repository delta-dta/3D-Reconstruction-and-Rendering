"""Build an object's pipeline report, reconstruction overview and offline viewer."""

import argparse
from html import escape
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw
import pycolmap
import torch


def write_viewer(root):
    reconstruction = pycolmap.Reconstruction(str(root / 'data/sparse/0'))
    points = [[*np.round(point.xyz, 5).tolist(), *point.color.tolist()] for point in reconstruction.points3D.values()]
    cameras = json.loads((root / 'sfm/cameras.json').read_text())
    payload = {'points': points, 'estimated': [row['center_aligned'] for row in cameras], 'truth': [row['center_gt'] for row in cameras]}
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>SfM 点云与相机</title>
<style>body{font:15px system-ui;margin:12px;color:#222}canvas{width:100%;max-width:900px;border:1px solid #ddd;touch-action:none}label{margin-right:20px}</style>
<p>拖动旋转，滚轮缩放。彩色为 SfM 稀疏点云；蓝色为估计相机，绿色为真实相机。位姿仅用训练相机进行相似变换对齐。</p>
<label><input id="cameras" type="checkbox" checked>显示相机</label><button id="reset">重置视角</button><br><canvas id="view" width="900" height="620"></canvas>
<script>const data=__DATA__;const canvas=document.getElementById('view'),ctx=canvas.getContext('2d'),toggle=document.getElementById('cameras');
let yaw=.6,pitch=.35,scale=55,last=null;
function project(p){let x=Math.cos(yaw)*p[0]-Math.sin(yaw)*p[1],y=Math.sin(yaw)*p[0]+Math.cos(yaw)*p[1];return [450+x*scale,310-(Math.cos(pitch)*p[2]-Math.sin(pitch)*y)*scale,Math.sin(pitch)*p[2]+Math.cos(pitch)*y];}
function draw(){ctx.fillStyle='#fff';ctx.fillRect(0,0,900,620);let dots=data.points.map(p=>[...project(p),p[3],p[4],p[5]]).sort((a,b)=>a[2]-b[2]);for(let p of dots){ctx.fillStyle=`rgb(${p[3]},${p[4]},${p[5]})`;ctx.fillRect(p[0],p[1],2,2);}if(toggle.checked){for(let p of data.truth){let q=project(p);ctx.strokeStyle='#209443';ctx.beginPath();ctx.arc(q[0],q[1],4,0,Math.PI*2);ctx.stroke();}for(let p of data.estimated){let q=project(p);ctx.fillStyle='#2859cb';ctx.fillRect(q[0]-1.5,q[1]-1.5,3,3);}}
let o=project([0,0,0]);for(let [p,color,label] of [[[1.3,0,0],'#c22','X'],[[0,1.3,0],'#292','Y'],[[0,0,1.3],'#22c','Z']]){let q=project(p);ctx.strokeStyle=color;ctx.beginPath();ctx.moveTo(o[0],o[1]);ctx.lineTo(q[0],q[1]);ctx.stroke();ctx.fillStyle=color;ctx.fillText(label,q[0]+5,q[1]);}}
canvas.onpointerdown=e=>{last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)};canvas.onpointerup=()=>last=null;canvas.onpointermove=e=>{if(last){yaw+=(e.clientX-last[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];draw();}};
canvas.onwheel=e=>{e.preventDefault();scale=Math.max(10,Math.min(1000,scale*Math.exp(-e.deltaY*.001)));draw()};toggle.onchange=()=>{scale=toggle.checked?55:190;draw()};document.getElementById('reset').onclick=()=>{yaw=.6;pitch=.35;scale=toggle.checked?55:190;draw()};draw();</script></html>'''
    (root / 'sfm/viewer.html').write_text(page.replace('__DATA__', json.dumps(payload, separators=(',', ':'))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    config = json.loads(Path(parser.parse_args().config).read_text())
    root = Path(config['output_dir'])
    dataset = json.loads((root / 'data/summary.json').read_text())
    sfm = json.loads((root / 'sfm/summary.json').read_text())
    training = json.loads((root / 'model/summary.json').read_text())
    evaluation = json.loads((root / 'evaluation/summary.json').read_text())
    assert all(row['complete'] for row in [dataset, sfm, training, evaluation])
    assert dataset['train'] == sfm['registered_images'] == 96 and dataset['test'] == evaluation['test_views'] == 24
    assert sfm['test_images_used'] == 0
    gif = Image.open(root / 'reconstruction.gif')
    assert gif.n_frames == config['evaluation']['orbit_frames']
    write_viewer(root)
    overview = Image.new('RGB', (1280, 680), 'white')
    draw = ImageDraw.Draw(overview)
    for index, frame in enumerate(range(0, config['evaluation']['orbit_frames'], 9)):
        image = Image.open(root / 'orbit' / f'frame_{frame:03d}.png').convert('RGB')
        left, top = index % 4 * 320, index // 4 * 340
        overview.paste(image.resize((320, 320), Image.Resampling.LANCZOS), (left, top + 20))
        draw.text((left + 6, top + 4), f'3DGS azimuth {frame * 5} degrees', fill='black')
    overview.save(root / 'reconstruction_overview.jpg', quality=95)
    repository = Path(config['gaussian_repo'])
    revisions = {}
    for name, path in [('3dgs', repository), ('rasterizer', repository / 'submodules/diff-gaussian-rasterization'), ('simple_knn', repository / 'submodules/simple-knn'), ('fused_ssim', repository / 'submodules/fused-ssim')]:
        revisions[name] = subprocess.check_output(['git', '-c', 'safe.directory=*', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    environment = {'python': platform.python_version(), 'python_executable': sys.executable, 'torch': torch.__version__,
        'cuda_runtime': torch.version.cuda, 'gpu': torch.cuda.get_device_name(), 'pycolmap': pycolmap.__version__,
        'sfm_device': 'CPU', 'training_device': 'CUDA sm_120', 'repositories': revisions,
        'local_patch': 'patches/gaussian_rasterizer_cuda129.patch'}
    (root / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n')
    name = config.get('name', '羊摆件')
    summary = {'complete': True, 'scope': 'Single-object complete image-to-3DGS pipeline', 'uid': config['uid'], 'name': name,
        'dataset': dataset, 'sfm': sfm, 'training': training, 'evaluation': evaluation, 'environment': environment}
    (root / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    page = [
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>作业 2：{escape(name)}重建流程</title>',
        '<style>body{font:16px/1.7 system-ui;max-width:1200px;margin:30px auto;padding:0 20px;color:#222}img{max-width:100%;height:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;text-align:left}.pair{margin:20px 0}a{color:#1558a6}iframe{width:100%;height:740px;border:1px solid #ddd}</style>',
        f'<h1>{escape(name)}：图像 → SfM → 3DGS → 新视角渲染</h1>',
        f'<p>对象 UID：{config["uid"]}。本页完成单物体的第 1～4 步，使用官方 3DGS 实现和真实训练结果。</p>',
        '<h2>重建动画</h2><img src="reconstruction.gif" alt="3DGS 重建环绕动画">',
        '<p><a href="reconstruction.gif">下载 GIF</a> · <a href="summary.json">完整统计与设置</a> · <a href="environment.json">运行环境与代码版本</a></p>',
        '<table><tr><th>项目</th><th>结果</th></tr>',
        '<tr><td>数据</td><td>512×512，三个高度，96 张训练 / 24 张留出测试</td></tr>',
        f'<tr><td>SfM 注册 / 点数</td><td>{sfm["registered_images"]}/96 张，{sfm["points3D"]:,} 个稀疏点</td></tr>',
        f'<tr><td>平均重投影误差</td><td>{sfm["mean_reprojection_error_pixels"]:.4f} 像素</td></tr>',
        f'<tr><td>位姿对照</td><td>旋转误差中位数 {sfm["median_rotation_error_degrees"]:.4f}°；中心 RMSE {sfm["center_rmse_object_units"]:.5f}（物体最长边=2）</td></tr>',
        f'<tr><td>训练</td><td>{training["iteration"]:,} 次迭代，{training["gaussians"]:,} 个高斯，{training["elapsed_seconds"]:.1f} 秒</td></tr>',
        f'<tr><td>24 视角平均 PSNR / SSIM</td><td>{evaluation["mean_psnr"]:.3f} dB / {evaluation["mean_ssim"]:.5f}</td></tr>',
        f'<tr><td>前景 PSNR</td><td>{evaluation["mean_foreground_psnr"]:.3f} dB</td></tr></table>',
        '<p>匹配与 SfM 只读取 96 张训练图。使用已知相机内参；真实外参和 GLB 表面点未用于 SfM 初始化。恢复结果仅用训练相机中心做全局相似变换对齐；测试采用留出图像及真实相机位姿。</p>',
        '<p>PSNR/SSIM 在含白色背景的完整图像上计算，同时报告仅在真实前景掩码内计算的 PSNR。GIF 由训练后的高斯模型生成。</p>',
        '<h2>多角度重建</h2><img src="reconstruction_overview.jpg" alt="八个重建视角">',
        '<h2>输入数据</h2><img src="dataset_overview.jpg" alt="三个高度的输入图像">',
        '<p><a href="data/metadata.json">真实相机参数与归一化</a> · <a href="data/splits.json">固定训练测试划分</a></p>',
        '<h2>实际匹配结果</h2>',
    ]
    for row in sfm['matches']:
        page.append(f'<div class="pair"><p>{escape(row["first"])} ↔ {escape(row["second"])}：{row["verified_matches"]} 个几何验证内点</p><img src="sfm/{escape(row["image"])}" alt="特征匹配"></div>')
    page.extend(['<h2>SfM 点云与相机</h2><iframe src="sfm/viewer.html" title="交互式稀疏点云与相机"></iframe>',
        '<p><a href="sfm/viewer.html">独立打开交互视图</a> · <a href="sfm/points_aligned.ply">SfM 点云 PLY</a> · <a href="sfm/cameras.json">估计位姿</a></p>',
        '<h2>测试视角逐项结果</h2><p>比较图依次为真实图像、3DGS 渲染、放大后的绝对误差。</p>',
        '<table><tr><th>视角</th><th>PSNR</th><th>SSIM</th><th>前景 PSNR</th></tr>'])
    for row in evaluation['per_view']:
        page.append(f'<tr><td><a href="evaluation/comparisons/{Path(row["name"]).stem}.jpg">{row["name"]}</a></td><td>{row["psnr"]:.3f}</td><td>{row["ssim"]:.5f}</td><td>{row["foreground_psnr"]:.3f}</td></tr>')
    ply = f'model/point_cloud/iteration_{config["evaluation"]["iteration"]}/point_cloud.ply'
    page.extend(['</table>', f'<p><a href="{ply}">训练后的高斯模型 PLY</a> · <a href="model/loss.csv">训练损失记录</a> · <a href="model/training_config.json">完整训练参数</a></p>',
        '<p>参考实现：<a href="https://github.com/graphdeco-inria/gaussian-splatting">官方 3DGS</a>；<a href="https://colmap.github.io/pycolmap/index.html">PyCOLMAP</a>。</p></html>'])
    (root / 'index.html').write_text('\n'.join(page) + '\n')
    print(json.dumps({'complete': True, 'registered_images': sfm['registered_images'], 'gaussians': training['gaussians'], 'psnr': evaluation['mean_psnr'], 'ssim': evaluation['mean_ssim'], 'gif_frames': gif.n_frames}), flush=True)


if __name__ == '__main__':
    main()
