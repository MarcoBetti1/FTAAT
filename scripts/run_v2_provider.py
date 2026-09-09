"""Run fixed stages for one provider; ceilings include previous smoke allowance."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from contextfrontier.runner import run
from contextfrontier.report import report
p=argparse.ArgumentParser();p.add_argument('provider',choices=['openai','claude']);a=p.parse_args()
load_dotenv(Path.cwd()/'.env')
budgets={'openai':{'main':15.5,'format':1.0},'claude':{'main':3.7,'format':.9}}[a.provider]
for stage,budget in budgets.items():
 name=f'v2-{a.provider}-{stage}';directory=Path('results')/name
 print(f'Starting {name}; fixed stage cap ${budget:.2f}',flush=True)
 cfg=json.loads(Path(f'experiments/v2/{a.provider}-{stage}.json').read_text())
 result=run(cfg,directory,budget,live=True)
 print(json.dumps(result),flush=True);report(directory)
 if result['status']!='completed':raise SystemExit('Stage stopped; inspect recorded outcome before any further dispatch')
