"""Compose the edit. Default output has NO audio stream."""
import argparse
import io
import json
import os
from pathlib import Path
import subprocess
from PIL import Image,ImageChops,ImageFilter
import typography

ROOT=Path(__file__).resolve().parents[1]

def load_timing(path):
    timing=json.loads(Path(path).read_text(encoding='utf-8'))
    cuts=timing['cuts']; hits=timing['lowrider']
    if len(cuts)!=4 or not all(0<x<20 for x in cuts) or sorted(set(cuts))!=cuts:
        raise ValueError('cuts must contain four strictly increasing times inside 0..20 seconds')
    if not all(cuts[2]<=x<cuts[3] for x in hits):
        raise ValueError('lowrider impulses must fall inside the fourth shot')
    return timing

def source_frame(n,timing):
    bounds=[0]+timing['cuts']+[20];t=n/30
    k=next((j for j in range(5) if t<bounds[j+1]),4)
    u=(t-bounds[k])/(bounds[k+1]-bounds[k])
    return min(599,round((k*4+u*4)*30))

def compose(n,folder,timing):
    src=source_frame(n,timing)
    with Image.open(folder/f'{src:04}.png') as raw: im=raw.convert('RGB')
    if im.size!=(1280,720): raise ValueError(f'Frame {src} must be 1280x720. Rerender at 100%.')
    im=ImageChops.add(im,im.filter(ImageFilter.GaussianBlur(2)).point(lambda x:int(x*.19)))
    im=Image.alpha_composite(im.convert('RGBA'),typography.overlay(src)).convert('RGB')
    t=n/30;hit=max((h for h in timing['cuts']+timing['lowrider'] if h<=t),default=-10);u=t-hit
    if 0<=u<.25:
        amp=(1-u/.25)**3;zoom=1+.03*amp;dx=5*amp;dy=-4*amp
        im=im.transform(im.size,Image.Transform.AFFINE,(1/zoom,0,640-(640+dx)/zoom,0,1/zoom,360-(360+dy)/zoom),Image.Resampling.BICUBIC)
    if n>590: im=im.point(lambda x:int(x*max(0,(599-n)/9)))
    return im

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frames',type=Path,default=ROOT/'work'/'frames')
    p.add_argument('--timing',type=Path,default=ROOT/'config'/'timing.json')
    p.add_argument('--output',type=Path,default=ROOT/'work'/'drosophila.mp4')
    p.add_argument('--ffmpeg',default=os.environ.get('FFMPEG','ffmpeg'))
    p.add_argument('--audio',type=Path,help='Optional LOCAL soundtrack; never required or downloaded')
    p.add_argument('--author',default='@Mellon0x')
    p.add_argument('--still',type=int,help='Export one output-frame index 0..599 as PNG; no FFmpeg needed')
    a=p.parse_args();timing=load_timing(a.timing)
    if a.still is not None and not 0<=a.still<600: p.error('--still must be 0..599')
    if a.audio is not None and not a.audio.is_file(): p.error('Audio file not found')
    for i,(at,label,lines) in enumerate(typography.blocks):
        typography.blocks[i]=(at,label,[x.replace('@Mellon0x',a.author) for x in lines])
    numbers=[a.still] if a.still is not None else range(600)
    missing=sorted({source_frame(n,timing) for n in numbers if not(a.frames/f'{source_frame(n,timing):04}.png').exists()})
    if missing: p.error(f'Missing {len(missing)} source frames; first: {missing[:10]}. Run render.py first.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.still is not None:
        compose(a.still,a.frames,timing).save(a.output.with_suffix('.png'));return
    command=[a.ffmpeg,'-v','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','pipe:0']
    if a.audio: command+=['-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-af','apad','-c:a','aac','-b:a','192k','-ar','48000']
    else: command+=['-map','0:v:0','-an']
    temporary=a.output.with_name(a.output.stem+'.pending.mp4')
    command+=['-c:v','libx264','-preset','medium','-threads','4','-crf','16','-pix_fmt','yuv420p','-t','20','-movflags','+faststart',str(temporary)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for n in numbers:
            b=io.BytesIO();compose(n,a.frames,timing).save(b,format='JPEG',quality=96,subsampling=0)
            proc.stdin.write(b.getvalue())
            if n%60==0: print(f'COMPOSED {n}/600',flush=True)
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError('FFmpeg export failed')
    except BaseException:
        proc.kill();proc.wait();raise
    temporary.replace(a.output)
    print(f'Exported {a.output}'+(' with local audio' if a.audio else ' (silent)'))

if __name__=='__main__': main()
