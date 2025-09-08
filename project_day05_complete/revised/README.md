V1 — JWST Deployment Accuracy + L2 Explainer (Manim 2D)

Contents
- `main.py`: Manim scene `MasterScene` intended to render V1 film.
- `PROMPTS.md`: AI reference prompts used for moodboard/references (not for frames).
- `github_link.txt`: placeholder; include commit URLs from both team members.

How to render (one-command requirement)

Run this from the `revised` folder:

```bash
manim -pqh main.py MasterScene
```

What this V1 includes
- Intro title card
- Sunshield pallets release + DTA extension
- Mid-boom extension
- Sunshield layer tensioning (1→5) with HUD counter
- Secondary mirror tripod deployment
- One primary mirror wing deployment
- L2 explainer: Sun, Earth, L2, halo orbit + thermal rationale

Known gaps (to address for V2)
- Refined proportions and precise hinge points for each mirror segment
- More cinematic lighting, textures, and wavefront phasing animation
- Additional deployment details (both primary wings, full pallets motion)
