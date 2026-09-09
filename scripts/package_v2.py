"""Prepare local upload assets and a separate public, evidence-only archive."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from video.v2.art import *

ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/'artifacts/episode-01-v2'
DOCS=ROOT/'docs/episodes/01-v2'
DELIVERY=ROOT.parent/'Deliverables/GPT-Learning-01-v2'

def chapter(sec):return f'{int(sec)//60:02}:{int(sec)%60:02}'

def main():
    DELIVERY.mkdir(parents=True,exist_ok=True)
    timeline=json.loads((MEDIA/'timeline.json').read_text());audit=json.loads((MEDIA/'production-audit.json').read_text())
    assert hashlib.sha256((MEDIA/'GPT-Learning-01-v2.mp4').read_bytes()).hexdigest()==audit['sha256']
    im=backdrop('dark').copy();d=ImageDraw.Draw(im)
    for i in range(60):folder(d,35+(i%15)*125,605+(i//15)*105,112,84,[GOLD,MINT,BLUE][i%3])
    rr(d,(70,80,1275,593),INK,25)
    text(d,(104,105),'8,192 FILES.',126,WHITE,'bold');text(d,(101,267),'ONE ANSWER.',112,GOLD,'bold')
    label(d,(118,457),'GPT vs CLAUDE',MINT,INK,43)
    pip(im,1250,148,1,660,'panic','panic')
    im=im.resize((1280,720),Image.Resampling.LANCZOS);im.save(DELIVERY/'thumbnail.jpg',quality=94,subsampling=0)
    for name in ['GPT-Learning-01-v2.mp4','GPT-Learning-01-v2.en.srt','production-audit.json','spoken-review.json']:
        shutil.copy2(MEDIA/name,DELIVERY/name)
    shutil.copytree(DOCS,DELIVERY/'report',dirs_exist_ok=True)
    # Draft/partial observations are never part of the final package.
    (DELIVERY/'report/partial-summary.json').unlink(missing_ok=True)
    release='https://github.com/MarcoBetti1/FTAAT/releases/tag/episode-01-v2'
    desc=["AI vs the World’s Worst Filing Cabinet",'',
          'We gave older and newer GPT models and Claude Haiku a deliberately terrible office job: find one made-up fact among 8,192 records. Then we tested whether one extra formatting reminder could fix a different kind of failure.',
          '', 'Pip, our paper clerk, would like to appeal his performance review.', '',
          'Code and method: https://github.com/MarcoBetti1/FTAAT',
          'Full report: https://github.com/MarcoBetti1/FTAAT/blob/main/docs/episodes/01-v2/report.md',
          'Raw evidence and reproducibility archive: '+release,'',
          'CHAPTERS']
    chapters={'01_open':'One small job','05_rules':'The filing challenge','08_tokens':'Fix the token ruler','10_warmup':'The easy round','12_prediction':'Where would you hide it?','13_primary':'32 fresh seeds','17_claude':'The smaller Claude panel','19_job':'Two arrows, more paperwork','21_printer':'The performance review','24_reminder':'The sticky-note experiment','27_revision':'The stale memo','29_rules':'What actually failed?','32_end':'Check the filing'}
    for s in timeline:
        if s['id'] in chapters:desc.append(chapter(s['start'])+' '+chapters[s['id']])
    desc+=['','METHOD NOTES','API model results, not tests of the ChatGPT or Claude consumer apps. Versions, sampling settings, exact prompts, all planned/observed requests, model-specific actual token usage, uncertainty, and budgets are in the report. Claude’s smaller retrieval panel is labeled explicitly. The primary 32-seed comparison was specified before the new run. Other cells are descriptive; no universal intelligence or memory ranking is claimed.','',
           'PRODUCTION','Original script, procedural animation, Pip character, and synthesized sound cues. Narration is AI-generated using OpenAI stock voice Cedar; Pip uses stock voice Onyx. No real person is impersonated. This is a revised edition with fresh experiments, not a re-edit that pools the old results.','',
           '#ArtificialIntelligence #LLM #GPTLearning']
    (DELIVERY/'youtube-description.txt').write_text('\n'.join(desc)+'\n')
    script=['# AI vs the World’s Worst Filing Cabinet','', 'Original script; AI-generated stock voices Cedar and Onyx.','']
    for s in timeline:script.extend([f"## {chapter(s['start'])} — {s['title']}",'',('Pip: ' if s['voice']=='onyx' else '')+s['narration'],''])
    (DELIVERY/'script.md').write_text('\n'.join(script));(DOCS/'script.md').write_text('\n'.join(script))
    (DELIVERY/'README.txt').write_text('Ready for your YouTube upload.\n\nUpload GPT-Learning-01-v2.mp4. Use thumbnail.jpg and the supplied description.\nThe MP4 has burned-in English captions. An SRT is also included for accessibility;\nenabling it on YouTube will duplicate visible captions, so consider that choice.\nThe report folder contains full methods and result tables. No channel or YouTube\nvideo was created or uploaded by Codex.\n\nThe separate public GitHub archive contains experiment evidence only.\n')
    # Include only explicit experiment evidence paths, never .env or media caches.
    evidence=ROOT/'artifacts/ContextFrontier-episode-01-v2-evidence.zip'
    with zipfile.ZipFile(evidence,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted((ROOT/'results').glob('v2-*/*')):
            if path.name in ('manifest.json','cases.jsonl','events.jsonl','report.md','report.json'):z.write(path,path.relative_to(ROOT))
        for base in [DOCS,ROOT/'experiments/v2']:
            for path in sorted(base.rglob('*')):
                if path.is_file() and path.name!='partial-summary.json':z.write(path,path.relative_to(ROOT))
        z.write(MEDIA/'token-accounting.json','local-token-accounting.json')
        z.writestr('README.txt','Original immutable second-edition experiment ledgers, full prompts/responses, model-specific counts, protocol, and analysis. Source: https://github.com/MarcoBetti1/FTAAT. All paths are relative to the repository root except local-token-accounting.json. Smoke checks are separate from the substantive analysis. This archive contains no video or API key.\n')
    (DELIVERY/'evidence-link.txt').write_text(release+'\nSHA256 '+hashlib.sha256(evidence.read_bytes()).hexdigest()+'\n')
    package=DELIVERY.parent/'GPT-Learning-01-v2-upload-package.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(DELIVERY.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(DELIVERY))
    print(json.dumps(dict(video=str(DELIVERY/'GPT-Learning-01-v2.mp4'),package=str(package),evidence=str(evidence),evidence_sha256=hashlib.sha256(evidence.read_bytes()).hexdigest()),indent=2))

if __name__=='__main__':main()
