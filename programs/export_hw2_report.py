"""Convert the formal Markdown report to a Chinese PDF and inspect its output."""

import hashlib
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit

import markdown
from PIL import Image, ImageDraw
import pymupdf
from weasyprint import CSS, HTML

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'img':
            self.images.append(attributes['src'])
        if tag == 'a' and 'href' in attributes:
            self.links.append(attributes['href'])


def main():
    config = json.loads((ROOT / 'configs/report_export.json').read_text())
    submission = json.loads((ROOT / 'configs/submission.json').read_text())
    source, destination = ROOT / config['markdown'], ROOT / config['pdf']
    text = source.read_text()
    for value in [submission['group_number'], *[member['name'] for member in submission['members']]]:
        assert value in text
    assert sum(member['workload_percent'] for member in submission['members']) == 100
    metrics = json.loads((ROOT / 'results/metrics.json').read_text())
    for row in metrics:
        expected = ('| ' + ' | '.join([row['name'], '96/96', f"{row['sparse_points']:,}",
                    f"{row['reprojection_error_px']:.3f}", f"{row['foreground_psnr']:.3f}",
                    f"{row['psnr']:.3f}", f"{row['ssim']:.5f}"]) + ' |')
        assert expected in text, row['object']
        assert row['uid'] in text
    assert json.loads((ROOT / 'configs/preview_deepseek.json').read_text())['prompt'] in text
    body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc', 'attr_list', 'md_in_html'],
                             extension_configs={'toc': {'toc_depth': '2-2'}})
    references = References()
    references.feed(body)
    for target in references.images + references.links:
        url = urlsplit(target)
        if not url.scheme and not url.netloc and url.path:
            assert (source.parent / unquote(url.path)).resolve().is_file(), target
    repository = submission['github_url'].removesuffix('.git')

    def link(match):
        target = unescape(match.group(1))
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            return match.group(0)
        relative = (source.parent / unquote(url.path)).resolve().relative_to(ROOT).as_posix()
        public = f"{repository}/blob/{config['github_branch']}/{quote(relative)}"
        if url.fragment:
            public += '#' + url.fragment
        return 'href="' + escape(public, quote=True) + '"'

    body = re.sub(r'href="([^"]+)"', link, body)
    html = ('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
            f'<title>{escape(config["title"])}</title><meta name="author" content="{escape(config["author"])}">'
            f'<base href="{source.parent.as_uri()}/"><body>{body}</body></html>')
    preview = ROOT / config['preview_dir']
    preview.mkdir(parents=True, exist_ok=True)
    (preview / 'report.html').write_text(html)
    HTML(string=html, base_url=str(source.parent)).write_pdf(destination, stylesheets=[CSS(filename=str(ROOT / config['stylesheet']))])
    document = pymupdf.open(destination)
    extracted = ''.join(page.get_text() for page in document)
    normalized = re.sub(r'\s+', '', extracted)
    for value in [submission['group_number'], *[member['name'] for member in submission['members']], '31.896', '37.599']:
        assert value in normalized, value
    links = [item['uri'] for page in document for item in page.get_links() if 'uri' in item]
    assert repository in links
    assert all(not item.startswith('file:') for item in links)
    assert '\ufffd' not in extracted
    assert '.page-start' not in extracted
    for index, page in enumerate(document):
        page.get_pixmap(matrix=pymupdf.Matrix(0.9, 0.9), alpha=False).save(preview / f'page_{index + 1:02d}.png')
    for start in range(0, len(document), 6):
        sheet = Image.new('RGB', (900, 900), '#dbe3e7')
        draw = ImageDraw.Draw(sheet)
        for offset in range(min(6, len(document) - start)):
            page_image = Image.open(preview / f'page_{start + offset + 1:02d}.png')
            page_image.thumbnail((280, 410))
            left, top = (offset % 3) * 300 + 10, (offset // 3) * 450 + 24
            sheet.paste(page_image, (left, top))
            draw.text((left, top - 18), f'Page {start + offset + 1}', fill='black')
        sheet.save(preview / f'preview_{start // 6 + 1:02d}.jpg', quality=90)
    report = {'complete': True, 'source': config['markdown'], 'pdf': config['pdf'], 'pages': len(document),
              'pdf_bytes': destination.stat().st_size, 'baseline_rows_verified': len(metrics),
              'prompt_matches_actual_config': True, 'image_references': len(references.images),
              'local_references_checked': sum(not urlsplit(target).scheme and bool(urlsplit(target).path)
                                              for target in references.images + references.links),
              'clickable_pdf_links': len(links), 'github_url': repository, 'members': [row['name'] for row in submission['members']],
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'pdf_sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}
    (ROOT / 'results/submission_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
