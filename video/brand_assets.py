"""Original procedural channel artwork, matching the episode's paper-clerk motif."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import render_preview as f
out=Path('artifacts/episode-01');out.mkdir(parents=True,exist_ok=True)
im=Image.new('RGB',(1280,720),f.PAPER);d=ImageDraw.Draw(im)
f.text(d,(65,48),'GPT LEARNING  /  EXPERIMENT 01',25,bold=True,fill=f.GRAY)
f.text(d,(65,118),'ONE HIDDEN FACT.',68,bold=True)
f.text(d,(65,205),'111,000 tokens. Eight fresh trials.',35)
for x,name,score,color in [(65,'GPT-4o Mini','0 / 8',f.GOLD),(525,'GPT-5.6 Luna','8 / 8',f.MINT)]:
 d.rounded_rectangle((x,300,x+420,607),radius=22,fill=color,outline=f.INK,width=3)
 f.text(d,(x+28,329),name,33,bold=True)
 f.text(d,(x+28,402),score,94,bold=True)
 f.text(d,(x+28,535),'exact answers',28)
f.pip(d,1080,372,0,1.1)
f.text(d,(65,649),'A selected-condition check, not an intelligence ranking.',25,fill=f.GRAY)
im.save(out/'thumbnail.png')
im=Image.new('RGB',(800,800),f.PAPER);d=ImageDraw.Draw(im)
f.pip(d,260,160,1,2.8)
f.text(d,(400,585),'GPT LEARNING',53,bold=True,anchor='mm')
im.save(out/'channel-avatar.png')
im=Image.new('RGB',(2560,1440),f.PAPER);d=ImageDraw.Draw(im)
# Keep all essential content within YouTube's centered safe area.
f.text(d,(635,630),'GPT LEARNING',100,bold=True)
f.text(d,(635,766),'Small experiments. Better questions.',43,fill=f.GRAY)
f.pip(d,1810,687,0,1.6)
d.line((635,845,1900,845),fill=f.GOLD,width=8)
im.save(out/'channel-banner.png')
print(out)
