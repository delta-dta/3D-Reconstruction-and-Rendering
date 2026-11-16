"""Archive the committed course code, reports and compact results."""

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GIT = ['git', '-c', f'safe.directory={ROOT}', '-C', str(ROOT)]


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
    (dist / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
    report = {'git_commit': revision, 'archive': archive.name, 'sha256': digest,
              'bytes': archive.stat().st_size, 'archive_entries': entries,
              'experiments_complete': True, 'group_and_repository': summary['submission'],
              'formal_report': {'markdown': formal['source'], 'pdf': formal['pdf'], 'pages': formal['pages']}}
    (dist / 'submission.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
