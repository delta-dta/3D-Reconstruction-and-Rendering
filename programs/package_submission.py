"""Archive the committed course code, reports and compact results."""

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import subprocess
from urllib.parse import unquote, urlsplit
import zipfile

import markdown

ROOT = Path(__file__).resolve().parents[1]
GIT = ['git', '-c', f'safe.directory={ROOT}', '-C', str(ROOT)]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for key, value in attrs if key in {'href', 'src'} and value)


def main():
    summary = json.loads((ROOT / 'results/course_summary.json').read_text())
    verification = json.loads((ROOT / 'results/verification.json').read_text())
    assert summary['experiments_complete'] and verification['complete']
    formal = json.loads((ROOT / 'results/submission_verification.json').read_text())
    assert formal['complete']
    assert formal['source_sha256'] == hashlib.sha256((ROOT / formal['source']).read_bytes()).hexdigest()
    assert formal['pdf_sha256'] == hashlib.sha256((ROOT / formal['pdf']).read_bytes()).hexdigest()
    changes = subprocess.check_output([*GIT, 'status', '--porcelain'], text=True)
    if changes:
        raise RuntimeError('Commit the final source, reports and results before packaging.')
    files = subprocess.check_output([*GIT, 'ls-files', '-z']).decode().split('\0')[:-1]
    assert 'ds_api_key' not in files and '.env' not in files
    assert formal['source'] in files and formal['pdf'] in files
    assert not any(path.startswith(('outputs/', 'cleaned/', '.tools/')) for path in files)
    revision = subprocess.check_output([*GIT, 'rev-parse', 'HEAD'], text=True).strip()
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    archive = dist / 'coursework_submission.zip'
    subprocess.run([*GIT, 'archive', '--format=zip', '--output=' + str(archive), 'HEAD'], check=True)
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        entries = len(bundle.infolist())
        names = set(bundle.namelist())
        checked_links = 0
        for page in sorted(name for name in names if name.endswith(('.html', '.md'))):
            content = bundle.read(page).decode('utf-8')
            if page.endswith('.md'):
                content = markdown.markdown(content, extensions=['tables', 'fenced_code', 'md_in_html'])
            references = References()
            references.feed(content)
            for target in references.targets:
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                destination = posixpath.normpath(posixpath.join(posixpath.dirname(page), unquote(url.path)))
                assert destination in names, f'File absent from submission: {page} -> {target}'
                checked_links += 1
    (dist / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
    report = {'git_commit': revision, 'archive': archive.name, 'sha256': digest,
              'bytes': archive.stat().st_size, 'archive_entries': entries, 'local_links_checked': checked_links,
              'experiments_complete': True, 'group_and_repository': summary['submission'],
              'formal_report': {'markdown': formal['source'], 'pdf': formal['pdf'], 'pages': formal['pages']}}
    (dist / 'submission.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
