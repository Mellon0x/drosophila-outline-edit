# Setup and troubleshooting

## Requirements

Install Blender (tested: 5.2.1 LTS), Python 3.11+ and FFmpeg. Install the single Python dependency using `python -m pip install -r requirements.txt`. Blender uses its bundled Python for `build_scene.py` and `render.py`; your normal Python runs `export.py`.

Official downloads: [Blender](https://www.blender.org/download/), [Python](https://www.python.org/downloads/), [FFmpeg](https://ffmpeg.org/download.html).

You can open `assets/Drosophila.blend` directly in Blender and scrub the timeline. The finished video also needs the export step: typography, retiming and optical transitions are added outside Blender.

## Paths

Run the documented commands from the repository root. Quote paths with spaces. Use `--ffmpeg 'C:\Tools\ffmpeg\bin\ffmpeg.exe'` on the exporter if FFmpeg is not on PATH. All output defaults are relative to the repository, not the creator's computer.

## GPU

`render.py -- --device OPTIX` is incorrect: the separator belongs to the **Blender command**. Example:

```powershell
& $blender -b assets/Drosophila.blend --python-exit-code 1 --python scripts/render.py -- --device OPTIX
```

Supported choices are CPU, OPTIX, CUDA, HIP and METAL; availability depends on Blender and your hardware/drivers. Only CPU and NVIDIA OptiX were used during development. A missing GPU raises an error; retry with CPU. Do not change samples midway through a source render unless you overwrite all frames.

## Fonts

No fonts are distributed. The compositor searches for Consolas on Windows, then DejaVu Sans Mono, then Menlo on macOS. To choose an installed font:

```powershell
$env:EDIT_FONT = 'C:\Fonts\YourMono-Regular.ttf'
$env:EDIT_FONT_BOLD = 'C:\Fonts\YourMono-Bold.ttf'
```

Different fonts change the appearance and text width. Long handles may need a smaller font in `typography.py`.

## Missing frames / interrupted rendering

Rerun the render command; complete PNGs are skipped. Incomplete PNGs are rerendered. The exporter fails immediately with the first missing frame indexes instead of waiting forever. To inspect selected source frames, pass `--frames '90,265,451,530'`. Ranges use `start:end` with the end excluded.

Rebuild or change the scene → render with `--overwrite`. Render caching does not detect scene edits automatically.

## Resolution and reproducibility

The current compositor is designed for 1280×720 at 30 fps and 600 output frames. This is intentional; changing only Blender's resolution does not scale text or timing. Increase render samples for cleaner geometry, but keep resolution at 100%. The provided model is procedural and needs no textures or external model assets. Different Blender versions, devices or fonts may produce small visual differences.

## Disk space

Keep space for 600 PNGs and the MP4 (typically hundreds of MB, depending on your changes). `work/` is excluded from Git. The supplied `.blend` is small enough for ordinary Git; no LFS setup is required.
