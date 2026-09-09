"""Original narration using a stock OpenAI voice, cached by exact text and settings.
A fixed planning allowance is reserved per clip; the audio endpoint returns no usage
in WAV mode. This allowance is not an invoice or a provider-enforced spending cap.
No automatic retry after an uncertain request.
"""
import hashlib
import json
import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

MODEL='gpt-4o-mini-tts-2025-12-15'
VOICE='cedar'
DIRECTION=('Narrate an original educational science video. Warm, curious, conversational, with dry humor. '
           'Clear American English, moderate pace around 165 words per minute. '
           'Use gentle emphasis for contrasts and a brief pause before a punchline. '
           'Do not imitate any real person. Read only the supplied script. Say model names clearly.')


def render(text, destination, cache_dir):
    load_dotenv(Path.cwd()/'.env')
    cache_dir=Path(cache_dir); cache_dir.mkdir(parents=True,exist_ok=True)
    payload=dict(model=MODEL,voice=VOICE,input=text,instructions=DIRECTION,response_format='wav')
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    cached=cache_dir/(identity+'.wav'); receipt=cache_dir/(identity+'.json')
    if cached.exists():
        Path(destination).write_bytes(cached.read_bytes()); return
    if receipt.exists():raise RuntimeError('Uncertain prior speech request; inspect before retrying')
    receipts=list(cache_dir.glob('*.json'))
    # At most 26 clips under a $0.65 planning allowance for this production pass.
    if len(receipts)>=26:raise RuntimeError('Speech planning allowance exhausted')
    if len(text)>2500:raise ValueError('Narration clip is too long')
    key=os.environ.get('OPENAI_API_KEY')
    if not key:raise RuntimeError('Missing OPENAI_API_KEY')
    receipt.write_text(json.dumps(dict(status='reserved',allowance_usd=.025,identity=identity,
                                      model=MODEL,voice=VOICE,text=text,instructions=DIRECTION),indent=2)+'\n')
    # No SDK retry. On a network error, keep reservation and do not resend.
    with httpx.Client(timeout=90) as client:
        r=client.post('https://api.openai.com/v1/audio/speech',headers={'Authorization':'Bearer '+key},json=payload)
        if r.status_code!=200:raise RuntimeError(f'Speech HTTP {r.status_code}; reservation kept')
        cached.write_bytes(r.content)
    Path(destination).write_bytes(cached.read_bytes())
    data=json.loads(receipt.read_text());data.update(status='received',request_id=r.headers.get('x-request-id'),
                                                  bytes=len(r.content),usage=None)
    receipt.write_text(json.dumps(data,indent=2)+'\n')
