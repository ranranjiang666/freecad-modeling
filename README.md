[README.md](https://github.com/user-attachments/files/28207349/README.md)
# FreeCAD Modeling Skill

`freecad-modeling` is a Codex skill for creating, editing, running, validating,
and exporting FreeCAD Python parametric CAD models from natural-language
requirements.

It is designed for workflows where the source of truth should be FreeCAD Python
code, while generated CAD artifacts such as `.FCStd`, `.step`, and optional
`.stl` files are derived outputs.

## What It Does

- Generates FreeCAD Python model source from natural-language CAD descriptions.
- Runs generated scripts through `FreeCADCmd` when available.
- Exports native FreeCAD documents (`.FCStd`) and STEP files (`.step`).
- Encourages parameterized, editable source instead of one-off geometry.
- Performs basic geometry validation such as null shape, invalid shape, bounding
  box, volume, and export checks.
- Can hand generated STEP/STL artifacts to CAD Explorer or other CAD inspection
  workflows for visual review.

## Typical Workflow

```text
Natural-language model request
-> FreeCAD Python source
-> FreeCADCmd execution
-> FCStd / STEP export
-> geometry validation
-> CAD Explorer visual review
-> source edits and regeneration
```

Example prompt:

```text
Use $freecad-modeling to create an 80 mm round flange with a 30 mm center bore
and six 6 mm bolt holes. Save the FreeCAD Python source, export FCStd and STEP,
and open the STEP in CAD Explorer.
```

## Requirements

- Codex with user skills enabled.
- FreeCAD installed locally.
- `FreeCADCmd` available through one of:
  - `FREECADCMD` environment variable,
  - `FREECAD_CMD` or `FREECADCMD_PATH`,
  - system `PATH`,
  - a common Windows install path.

The bundled runner also checks this Windows path:

```text
E:\FreeCAD\bin\freecadcmd.exe
```

For portability, generated model scripts should not hardcode a user-specific
FreeCAD path. Use the runner or environment variables instead.

## Installation

Clone or download this repository into your Codex skills directory:

```bash
git clone https://github.com/ranranjiang666/freecad-modeling.git ~/.codex/skills/freecad-modeling
```

On Windows, the target directory is usually:

```text
C:\Users\<your-user-name>\.codex\skills\freecad-modeling
```

Restart Codex after installation so the skill can be loaded.

## Repository Layout

```text
freecad-modeling/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    run_freecad.py
  references/
    source-contract.md
    part-api-patterns.md
    export-and-validation.md
    repair-loop.md
```

## Runner

The runner executes a FreeCAD Python script through `FreeCADCmd` using a small
`runpy` bootstrap. This avoids version-specific behavior where some FreeCADCmd
builds open a console instead of executing a `.py` file passed as a positional
argument.

Basic usage:

```bash
python scripts/run_freecad.py path/to/model.py --json
```

With an explicit FreeCADCmd path:

```bash
python scripts/run_freecad.py path/to/model.py --freecadcmd "E:/FreeCAD/bin/freecadcmd.exe" --json
```

Forward arguments to the model script after `--`:

```bash
python scripts/run_freecad.py path/to/model.py -- --output-dir out
```

## Modeling Guidance

The skill defaults to FreeCAD's `Part` API for robust command-line generation:

- `Part.makeBox`
- `Part.makeCylinder`
- `fuse`
- `cut`
- `common`
- `removeSplitter`
- `makeFillet`
- `makeChamfer`
- wires, faces, extrudes, and revolves

Use Sketcher or PartDesign only when editable FreeCAD feature-tree behavior is a
specific requirement.

## Notes

- STEP is treated as the main interchange and review format.
- `.FCStd` is useful when the user wants a native FreeCAD document.
- Visual review does not replace geometry checks.
- This skill does not certify manufacturability, strength, tolerance compliance,
  or safety.
