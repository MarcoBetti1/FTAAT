"""Offline final export checks: streams, full decode, timing, loudness, review frames."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
root=Path('artifacts/episode-01').resolve();video=root/'GPT-Learning-01.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'])==(1920,1080,'24/1','h264')
assert a['codec_name']=='aac' and a['sample_rate']=='48000'
timeline=json.loads((root/'timeline.json').read_text());duration=sum(s['duration'] for s in timeline)
assert abs(float(probe['format']['duration'])-duration)<.15
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
loudness=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True).stderr
summary=loudness.rsplit('Summary:',1)[-1];(root/'loudness.txt').write_text(summary)
integrated=float(re.search(r'I:\s*([-\d.]+) LUFS',summary).group(1));peak=float(re.search(r'Peak:\s*([-\d.]+) dBFS',summary).group(1))
assert -17.5<integrated<-14.5 and peak<0,(integrated,peak)
srt=(root/'GPT-Learning-01.en.srt').read_text()
last=0;count=0
for block in srt.strip().split('\n\n'):
 lines=block.splitlines();times=lines[1].split(' --> ')
 def sec(t):
  h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
 start,end=map(sec,times);assert 0<=start<end<=duration+.1 and start>=last-.02
 assert len(lines)<=4 and all(len(line)<=68 for line in lines[2:]),lines
 last=end;count+=1
review=root/'export-review';review.mkdir(exist_ok=True);elapsed=0
for i,s in enumerate(timeline):
 time=elapsed+min(s['duration']-.3,max(1,s['duration']*.7))
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(time),'-i',str(video),'-frames:v','1',str(review/f'scene-{i:02}.png')],check=True)
 elapsed+=s['duration']
result=dict(status='passed',duration_seconds=float(probe['format']['duration']),width=v['width'],height=v['height'],fps=v['r_frame_rate'],
 video_codec=v['codec_name'],audio_codec=a['codec_name'],audio_sample_rate=a['sample_rate'],full_decode='passed',caption_cues=count,
 integrated_lufs=integrated,true_peak_dbfs=peak,bytes=video.stat().st_size,sha256=hashlib.sha256(video.read_bytes()).hexdigest(),
 scope='Automated full decode, stream/timing/loudness checks, plus exported frames for visual review. Spoken-number QA uses the separately reviewed ASR transcript.')
(root/'export-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
