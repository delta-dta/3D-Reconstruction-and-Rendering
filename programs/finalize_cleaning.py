"""Write the final retained-asset summary, CSV and bounded preview gallery."""

from collections import Counter
import csv
from html import escape
import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CLEANED = ROOT / "cleaned"
SHARDS = [f"000-{index:03d}" for index in range(11)]
GALLERY_LIMIT = 200


def read_json(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"无法生成最终报告：尚缺少 {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise RuntimeError(f"无法生成最终报告：{message}")


def main():
    coarse = read_json("outputs/coarse_summary.json")
    material = read_json("outputs/material_summary.json")
    visual = read_json("outputs/preview_progress.json")
    render_config = read_json("configs/render_full.json")
    visual_config = read_json("configs/preview_deepseek.json")
    require(visual["engine"] == "deepseek", "最终视觉筛选必须使用已确认的 DeepSeek 方案。")
    workers = [
        read_json(f"outputs/full_render/progress_{index}.json")
        for index in range(render_config["workers"])
    ]

    require(
        coarse["input_count"] == 55000
        and sorted(row["shard"] for row in coarse["shards"]) == SHARDS
        and all(row["input_count"] == 5000 for row in coarse["shards"]),
        "粗筛范围必须覆盖 000-000～000-010 的全部 55,000 个模型。",
    )
    require(material["input_count"] == coarse["kept_count"], "材质筛选输入数量与粗筛结果不一致。")
    for index, worker in enumerate(workers):
        require(
            worker["complete"] and worker["processed"] == worker["total"],
            f"渲染进程 {index} 尚未完成。",
        )
        require(
            visual["consumed_per_worker"][str(index)] == worker["rendered"],
            f"视觉筛选尚未处理完渲染进程 {index} 的结果。",
        )
    rendered_count = sum(worker["rendered"] for worker in workers)
    require(sum(worker["total"] for worker in workers) == material["kept_count"], "渲染任务未覆盖全部材质候选。")
    require(visual["complete"] and visual["processed"] == rendered_count, "视觉筛选尚未完成全部渲染对象。")

    manifest_path = CLEANED / "cleaned_models.jsonl"
    uids_path = CLEANED / "cleaned_uids.txt"
    require(manifest_path.is_file() and uids_path.is_file(), "保留模型清单尚未生成。")
    with manifest_path.open(encoding="utf-8") as source:
        rows = [json.loads(line) for line in source]
    listed_uids = uids_path.read_text(encoding="utf-8").splitlines()
    manifest_uids = [row["uid"] for row in rows]
    hashes = [row["sha256"] for row in rows]
    require(len(rows) == visual["kept"], "保留清单数量与视觉筛选完成数量不一致。")
    require(len(manifest_uids) == len(set(manifest_uids)), "保留清单包含重复 UID。")
    require(len(hashes) == len(set(hashes)), "保留清单包含重复 SHA-256 内容。")
    require(len(listed_uids) == len(rows) and set(listed_uids) == set(manifest_uids), "UID 文本清单与模型清单不一致。")
    for row in rows:
        require(row["shard"] in SHARDS, f"模型 {row['uid']} 不在约定分片范围内。")
        require((CLEANED / row["preview"]).is_file(), f"模型 {row['uid']} 的预览图不存在。")
    rows.sort(key=lambda row: (row["shard"], row["uid"]))

    selected = read_json("configs/hw2_selection.json")["selected"]
    selected_uids = [row["uid"] for row in selected]
    require(len(selected) == 10 and len(set(selected_uids)) == 10, "作业 2 必须选择 10 个不同物体。")
    accepted_by_uid = {row["uid"]: row for row in rows}
    require(all(uid in accepted_by_uid for uid in selected_uids), "所选 10 个物体必须全部进入最终保留清单。")
    confirmed = []
    for row in selected:
        uid = row["uid"]
        confirmed.append({
            **row, **accepted_by_uid[uid],
            "final_cleaning_acceptance_confirmed": True,
        })
    with (CLEANED / "hw2_candidates.jsonl").open("w", encoding="utf-8") as output:
        for row in confirmed:
            output.write(json.dumps(row, ensure_ascii=False) + "\n")

    kept_by_shard = Counter(row["shard"] for row in rows)
    coarse_by_shard = {row["shard"]: row["kept_count"] for row in coarse["shards"]}
    material_by_shard = {row["shard"]: row["kept_count"] for row in material["shards"]}
    shard_counts = [
        {
            "shard": shard, "input_count": 5000,
            "coarse_kept": coarse_by_shard[shard],
            "material_kept": material_by_shard[shard],
            "cleaned_count": kept_by_shard[shard],
        }
        for shard in SHARDS
    ]
    counts = {
        "input_count": coarse["input_count"],
        "coarse_kept": coarse["kept_count"],
        "material_kept": material["kept_count"],
        "rendered_count": rendered_count,
        "texture_passed": visual["texture_passed"],
        "duplicates": visual["duplicates"],
        "cleaned_count": len(rows),
        "hw2_selected_count": len(confirmed),
    }
    summary = {
        "complete": True,
        "scope": {"first_shard": SHARDS[0], "last_shard": SHARDS[-1], "shard_count": 11},
        "counts": counts,
        "by_shard": shard_counts,
        "criteria": {
            **coarse["criteria"],
            "asset": "完整、独立、静态的表面网格",
            "appearance": "可辨识表面纹理或颜色变化，以不透明、低反光材质为主",
            "deduplication": "完全相同的 SHA-256 内容仅保留一个",
            "selection": "GLB 材质信息、多视角渲染、前景 SIFT 和 DeepSeek 综合单问自动筛选",
        },
        "render_config": render_config,
        "visual_filter_config": visual_config,
        "visual_api": {
            key: visual[key]
            for key in (
                "engine", "model_requested", "model_version_at_setup", "models_returned",
                "requests", "usage", "cost", "usage_scope", "max_cost_usd",
            )
        },
        "validation_scope": "全量资产完成自动清洗，未逐个进行人工复核；下游重建仅针对作业 2 选定对象，结果另行汇总。",
        "gallery_items": min(GALLERY_LIMIT, len(rows)),
        "hw2_candidates": {
            "count": len(confirmed), "manifest": "hw2_candidates.jsonl",
            "uids": selected_uids, "final_cleaning_acceptance_confirmed": True,
            "selection": "10 个物体均按完整独立主体、清晰表面特征、不透明低反光条件选择",
            "validation_scope": "本清单记录四视角预览和前景特征；选定对象的相机恢复与 3DGS 结果见课程总览。",
        },
    }
    (CLEANED / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    fields = ["uid", "name", "shard", "path", "preview", "faces", "filebytes"]
    with (CLEANED / "cleaned_models.csv").open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                **{key: row[key] for key in fields[:5]},
                "faces": row["rendered_faces"], "filebytes": row["file_bytes"],
            })

    model_name = visual_config["model_version_at_setup"]
    page = [
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>Objaverse 作业 1 清洗结果</title>',
        '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:1200px;margin:32px auto;padding:0 20px;color:#222}',
        'table{border-collapse:collapse;width:100%;margin:20px 0}th,td{border:1px solid #ddd;padding:8px;text-align:left}',
        '.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}',
        'figure{margin:0;border:1px solid #ddd;border-radius:8px;padding:12px}img{width:100%;height:auto}',
        'figcaption{overflow-wrap:anywhere}.meta{color:#555;font-size:13px}a{color:#1558a6}</style>',
        '<h1>Objaverse 作业 1 清洗结果</h1>',
        f'<p>范围：000-000～000-010，共 11 个分片、55,000 个模型。最终保留 <strong>{len(rows):,}</strong> 个模型。</p>',
        f'<p>通过 GLB 材质与几何信息、Blender 多视角预览、前景 SIFT 和 <strong>{escape(model_name)}</strong> 自动筛选，',
        '并按 SHA-256 去除完全重复的内容。源模型保持原样。</p>',
        f'<p>固定条件：无动画，{coarse["criteria"]["min_faces"]:,}～{coarse["criteria"]["max_faces"]:,} 个三角面，',
        f'文件不超过 {coarse["criteria"]["max_file_bytes"] // (1024 * 1024)} MiB；',
        f'预览为 {len(render_config["view_angles_degrees"])} 个 {render_config["resolution"]}×{render_config["resolution"]} 视图，',
        f'前景 SIFT 数量中位数至少 {visual_config["sift_count_min"]}。',
        'DeepSeek 按完整独立主体、可辨识表面信息及不透明低反光材质进行保留判断。</p>',
        '<p>本报告展示作业 1 自动清洗结果；未逐个进行人工复核。选定对象的下游重建见<a href="../index.html">课程总览</a>。</p>',
        '<p><a href="cleaned_models.csv">完整 CSV 清单</a> · <a href="cleaned_models.jsonl">完整 JSONL 清单</a> · ',
        '<a href="cleaned_uids.txt">UID 清单</a> · <a href="summary.json">统计与实际筛选配置</a></p>',
        '<table><thead><tr><th>分片</th><th>原始模型</th><th>粗筛保留</th><th>材质候选</th><th>最终保留</th></tr></thead><tbody>',
    ]
    for shard in shard_counts:
        page.append(
            f"<tr><td>{shard['shard']}</td><td>{shard['input_count']}</td>"
            f"<td>{shard['coarse_kept']}</td><td>{shard['material_kept']}</td><td>{shard['cleaned_count']}</td></tr>"
        )
    page.extend([
        '</tbody></table>',
        '<h2>作业 2 的 10 个对象</h2>',
        '<p>以下 10 个不同物体均已确认进入最终清洗清单，并按完整独立主体、清晰表面特征、不透明低反光条件选择。',
        '四视角预览和前景特征用于对象选择；训练图像、相机恢复及重建结果在课程总览单独展示。</p>',
        '<p><a href="hw2_candidates.jsonl">10 个对象的完整清单</a></p><div class="gallery">',
    ])
    for row in confirmed:
        name = escape(row["name"])
        uid = escape(row["uid"])
        preview = escape(quote(row["preview"]))
        page.append(
            f'<figure><a href="{preview}"><img loading="lazy" src="{preview}" alt="{name}"></a>'
            f'<figcaption><strong>{name}</strong> · {escape(row["category"])}'
            f'<div class="meta">{uid}<br>{row["rendered_faces"]:,} 面 · '
            f'四视角 SIFT 最少 {min(row["sift_per_view"])} 个</div>'
            f'<p>{escape(row["suitability"])}</p></figcaption></figure>'
        )
    page.extend([
        '</div>',
        f'<h2>保留对象预览</h2><p>按分片和 UID 排序，展示前 {min(GALLERY_LIMIT, len(rows))} 个对象；完整结果见上方 CSV 清单。</p>',
        '<div class="gallery">',
    ])
    for row in rows[:GALLERY_LIMIT]:
        name = escape(row["name"])
        uid = escape(row["uid"])
        preview = escape(quote(row["preview"]))
        page.append(
            f'<figure><a href="{preview}"><img loading="lazy" src="{preview}" alt="{name}"></a>'
            f'<figcaption><strong>{name}</strong><div class="meta">{uid}<br>{escape(row["shard"])} · '
            f'{row["rendered_faces"]:,} 面 · SIFT 中位数 {row["sift_count"]:.1f}</div></figcaption></figure>'
        )
    page.append('</div></html>')
    (CLEANED / "index.html").write_text("\n".join(page) + "\n", encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
