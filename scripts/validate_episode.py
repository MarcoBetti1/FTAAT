"""Independently regenerate cases and regrade the immutable response ledgers offline."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contextfrontier.tasks import make_case
from contextfrontier.scoring import grade,VERSION

p=argparse.ArgumentParser();p.add_argument('runs',nargs='+');p.add_argument('--output',required=True);args=p.parse_args()
checks=Counter();outcomes=Counter();tokens=[];hashes={};corrections=[]
for arg in args.runs:
 root=Path(arg);raw=(root/'events.jsonl').read_bytes();hashes[root.name]=hashlib.sha256(raw).hexdigest()
 cases={}
 for line in (root/'cases.jsonl').read_text().splitlines():
  c=json.loads(line);reconstructed=make_case(c['task'],**{k:c[k] for k in ['seed','n','k','depth','absent']}).to_dict()
  assert c==reconstructed,c['id'];cases[c['id']]=c;checks['case_reproductions']+=1
 rows=[json.loads(x) for x in raw.splitlines()];reserved=set();settled=set()
 for r in rows:
  if r['event']=='reserved':reserved.add(r['request_key'])
  if r['event']!='result':continue
  settled.add(r['request_key']);c=cases[r['case_id']];g=r['grade']
  if r['reply']['status']=='completed':
   fixed=grade(r['reply']['text'],c['expected'],symbols_per_answer=c['k'])
   assert {k:v for k,v in g.items() if k!='format_ok'}=={k:v for k,v in fixed.items() if k!='format_ok'}
   if g['format_ok']!=fixed['format_ok']:corrections.append(r['request_key'])
  else:assert g is None
  checks['primary_response_regrades_unchanged']+=1
  assert r['reply']['model']==r['model'];checks['returned_model_matches']+=1
  assert r['count_delta']==0;checks['preflight_actual_input_matches']+=1
  outcomes[r['reply']['status']]+=1;tokens.append(r['actual_input_tokens'])
 assert reserved==settled,(root.name,reserved-settled);checks['ledgers_with_no_unsettled_requests']+=1
checks['secondary_format_labels_corrected']=len(corrections)
result=dict(status='passed',checks=dict(checks),outcomes=dict(outcomes),actual_input_token_range=[min(tokens),max(tokens)],
 source_commit='417102b182371060b4760cdfd583bb3446ee6943',analysis_scoring_version=VERSION,raw_ledger_sha256=hashes,
 note='The experiment used the original scorer. Analysis corrects secondary UNKNOWN format labels only; original ledgers are unchanged.')
Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['checks']))
