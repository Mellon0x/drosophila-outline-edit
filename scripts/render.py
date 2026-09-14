"""Run inside Blender; PNG names are zero-based, Blender frames are one-based."""
import argparse
import sys
from pathlib import Path
import bpy

p=argparse.ArgumentParser()
p.add_argument('--frames', default='0:600', help='start:end, end exclusive; or comma-separated indexes')
p.add_argument('--output', default=str(Path(__file__).resolve().parents[1]/'work'/'frames'))
p.add_argument('--device', choices=['CPU','OPTIX','CUDA','HIP','METAL'],default='CPU')
p.add_argument('--samples', type=int,default=16)
p.add_argument('--overwrite',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if ':' in a.frames:
    start,end=map(int,a.frames.split(':')); frames=list(range(start,end))
else: frames=list(map(int,a.frames.split(',')))
if not frames or min(frames)<0 or max(frames)>599 or a.samples<1:
    p.error('Use frame indexes 0..599 and positive samples.')
s=bpy.context.scene
s.render.engine='CYCLES'; s.cycles.device='CPU'
if a.device!='CPU':
    pref=bpy.context.preferences.addons['cycles'].preferences
    pref.compute_device_type=a.device; pref.get_devices()
    active=[d for d in pref.devices if d.type==a.device]
    if not active: raise RuntimeError(f'No {a.device} device. Retry with --device CPU.')
    for d in pref.devices: d.use=d.type==a.device
    s.cycles.device='GPU'
s.cycles.samples=a.samples
s.render.use_persistent_data=True
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
for n in frames:
    target=out/f'{n:04}.png'
    if target.exists() and not a.overwrite:
        with target.open('rb') as f:
            f.seek(max(0,target.stat().st_size-12))
            if f.read()==b'\x00\x00\x00\x00IEND\xaeB\x60\x82': continue
    s.frame_set(n+1)
    temp=out/f'{n:04}.pending.png';s.render.filepath=str(temp)
    bpy.ops.render.render(write_still=True)
    temp.replace(target)
    print(f'RENDERED {n+1}/600',flush=True)
