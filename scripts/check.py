"""Fast checks for timing boundaries, source numbering and required repository files."""
import json
from pathlib import Path
import tempfile
from export import ROOT,load_timing,source_frame

t=load_timing(ROOT/'config'/'timing.json')
mapped=[source_frame(n,t) for n in range(600)]
assert mapped[0]==0 and mapped[-1] in [598,599]
assert all(0<=n<=599 for n in mapped)
assert mapped==sorted(mapped), 'Time mapping must never run backward'
for i,cut in enumerate(t['cuts'],1):
    n=int(cut*30)+1
    assert abs(source_frame(n,t)-i*120)<=2, (cut,n,source_frame(n,t))
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'timing.json'
    for bad in [{'cuts':[4,4,12,16],'lowrider':[]},
                {'cuts':[4,8,12,16],'lowrider':[19]},
                {'cuts':[4,8,12],'lowrider':[]}]:
        path.write_text(json.dumps(bad),encoding='utf-8')
        try: load_timing(path)
        except ValueError: pass
        else: raise AssertionError(f'Accepted invalid timing: {bad}')
for path in ['assets/Drosophila.blend','previews/banner.svg']:
    assert (ROOT/path).is_file(),path
print('Timing boundaries, invalid inputs and required files: OK')
