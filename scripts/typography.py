"""Typography for the 1280 x 720 source timeline. No top labels or watermark."""
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1280,720,30
def get_font(size,bold=False):
    env=os.environ.get('EDIT_FONT_BOLD' if bold else 'EDIT_FONT')
    candidates=[env] if env else []
    candidates += [str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/('consolab.ttf' if bold else 'consola.ttf')),
                   'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf',
                   '/System/Library/Fonts/Menlo.ttc']
    for candidate in candidates:
        try: return ImageFont.truetype(candidate,size)
        except OSError: pass
    raise RuntimeError('Set EDIT_FONT and EDIT_FONT_BOLD to installed monospace TTF files.')
fonts={s:get_font(s) for s in [12,14,16,18,21,24]}
title=get_font(62,True);medium=get_font(26,True)
blocks=[(0,'01 / COMPOUND VISION',['// drosophila.optics','// facet array: online']),
        (4,'02 / WING STRUCTURE',['// wings.deploy()','// venation / membrane / hinge']),
        (8,'03 / NEURAL SIGNAL',['// neural input','// processing motion','// author: @Mellon0x']),
        (12,'04 / MOTOR CONTROL',['// beat.sync()','// front suspension: active']),
        (16,'05 / FLIGHT',['// flight.initiate()','// authored by @Mellon0x'])]

def overlay(frame):
 t=frame/FPS;chapter=min(4,int(t/4));at,label,lines=blocks[chapter]
 out=Image.new('RGBA',(W,H));d=ImageDraw.Draw(out)
 # Quiet corner registration marks; no decorative dashboards.
 for x,y,sx,sy in [(25,22,1,1),(1255,22,-1,1),(25,695,1,-1),(1255,695,-1,-1)]:
  d.line((x,y,x+13*sx,y),fill=(76,86,80,170),width=1)
  d.line((x,y,x,y+13*sy),fill=(76,86,80,170),width=1)
 elapsed=max(0,t-at-.38);count=int(elapsed*36)
 y0=565 if chapter!=4 else 492
 for j,line in enumerate(lines):
  length=min(len(line),count);count-=length
  if length:
   d.text((41,y0+j*27),f'{j+1:02}',font=fonts[14],fill=(111,128,116,230))
   d.text((76,y0+j*27),line[:length],font=fonts[21],fill=(223,230,223,255),stroke_width=2,stroke_fill=(0,0,0,230))
   if length<len(line) and int(t*9)%2==0:
    x=76+d.textlength(line[:length],font=fonts[21]);d.rectangle((x+3,y0+j*27+3,x+10,y0+j*27+22),fill=(218,226,218,255))
  if count<=0:break
 if chapter==0 and t>2.7:
  label='DROSOPHILA';d.text((39,644),label[:int((t-2.7)*30)],font=medium,fill='white')
 if chapter==4 and t>17.6:
  label='DROSOPHILA';d.text((37,585),label[:int((t-17.6)*22)],font=title,fill='white')
  if t>18.5:d.text((41,660),'SMALL BODY. COMPLEX SYSTEM.',font=fonts[18],fill=(148,167,152,255))
 return out
