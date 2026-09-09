"""Package an explicit allowlist of public experiment artifacts; fail on key bytes."""
from pathlib import Path
import hashlib
import json
import os
import re
import zipfile
from dotenv import load_dotenv

root=Path.cwd();load_dotenv(root/'.env');files=[]
for name in ['smoke','pilot','current','long','confirm']:
 run=root/'results'/f'{name}-20260909'
 files.extend(run/n for n in ['manifest.json','cases.jsonl','events.jsonl','report.md','report.json'])
files.extend(p for p in (root/'docs/episodes/01').iterdir() if p.suffix in ['.md','.json','.png'])
files.extend(root/'artifacts/episode-evidence'/n for n in ['evidence.json','audit.md','strict-results.png'])
files.extend(root/'artifacts'/n for n in ['token-accounting.json','campaign-budget.json'])
files.extend(sorted((root/'experiments').glob('*.json')))
files.extend(root/p for p in ['experiments/PROTOCOL.md','docs/methodology.md','docs/audits/2026-09-09.md'])
keys=[os.environ[k].encode() for k in ['OPENAI_API_KEY','ANTHROPIC_API_KEY'] if os.environ.get(k)]
checksums={}
for p in files:
 data=p.read_bytes()
 if any(key in data for key in keys):raise RuntimeError('Credential bytes found; publication blocked')
 if re.search(rb'sk-(?:proj-|ant-api)[A-Za-z0-9_-]{20,}',data):raise RuntimeError('Credential-like string found; publication blocked')
 checksums[str(p.relative_to(root))]=hashlib.sha256(data).hexdigest()
release=root/'artifacts/release';release.mkdir(exist_ok=True)
archive=release/'ContextFrontier-episode-01-evidence.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,p.relative_to(root))
 z.writestr('SHA256SUMS.json',json.dumps(checksums,indent=2)+'\n')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(dict(archive=str(archive),files=len(files),bytes=archive.stat().st_size,secret_scan='passed')))
