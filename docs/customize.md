# Customize the edit

| Change | Where | What to run afterward |
|---|---|---|
| Author handle | Export `--author @yourname` | Export only |
| Bottom code, title, fonts | `scripts/typography.py` | Export only |
| Bloom, optical zoom, fade | `scripts/export.py` | Export only |
| Local soundtrack | Export `--audio /path/to/file` | Export only |
| Cut times or lowrider times | `config/timing.json` | Rebuild, rerender with `--overwrite`, export |
| Model, wings, camera, leg motion | `scripts/build_scene.py` | Rebuild, rerender with `--overwrite`, export |
| Manual Blender scene changes | `assets/Drosophila.blend` | Rerender with `--overwrite`, export; do not rebuild |

## Timing

The edit is fixed at 20 seconds. `cuts` contains exactly four increasing times between 0 and 20. `lowrider` contains the output times of the body-lift impulses, all inside the fourth shot (`cuts[2]` through `cuts[3]`). The scene builder converts those impulse times into the 12–16 second source timeline.

For a different song, pick four musical transitions, keep room in the fourth shot for the body motion, then choose the impulse times. Rebuild and render again. There is no automatic beat detector in this repository.

The original lowrider motion starts after source time **14.05 s**. Keep your impulses in the latter half of that shot, or also adjust the `if t<14.05` gate and camera transition in `build_scene.py`. The pulse duration is 0.4 source seconds; changing shot length stretches it in the final video.

## Model and animation

The model is generated from simple meshes and curves: black opaque shells, bright outlines, compound-eye facets, wing venation, bristles and six segmented legs. Edit dimensions near the model-building sections of `build_scene.py`.

Animations are baked at every frame. Source shot boundaries are 0, 4, 8, 12, 16 and 20 seconds. Camera positions and targets are near the end of the base animation loop. The following lowrider section adjusts body pitch, feet and framing.

Replacing the fly with a different subject requires new geometry and animation logic. This is a complete fly project, not a universal one-click model swapper.

## Check a still

After rendering, create one composed output frame without FFmpeg:

```powershell
python scripts/export.py --still 300 --output work/neural.png
```

`--still` uses the **output** timeline. Its required source PNG is determined by the cut map. If it is missing, the error lists its index; render that index or all 600 source frames.

## Sharing

Commit source and intentional previews. Keep `work/`, local music, personal configuration and caches out of Git. The default export never includes audio; the optional audio path is read only when explicitly supplied.
