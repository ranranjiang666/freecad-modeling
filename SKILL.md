---
name: freecad-modeling
description: Create, modify, run, validate, and export FreeCAD Python parametric models from natural-language CAD requirements. Use for FreeCAD macros, FreeCADCmd automation, Part/Sketcher/PartDesign modeling, FCStd/STEP/STL export, geometry checks, and CAD Explorer visual review.
---

# FreeCAD Modeling

## Purpose

Create and maintain FreeCAD Python source as the model source of truth, run it through
FreeCADCmd when available, export reviewable CAD artifacts, and return checked results.
Use STEP as the primary interchange artifact for downstream inspection and CAD Explorer
review. Use `.FCStd` when the user needs a native FreeCAD document.

## Use This Skill When

Use this skill when the user asks for FreeCAD Python code, FreeCAD macros, FreeCADCmd
automation, `.FCStd` documents, Part/Sketcher/PartDesign scripts, FreeCAD-based STEP
or STL export, or wants natural-language CAD requirements turned into FreeCAD source.

Use `$cad` instead when the user explicitly wants build123d/CadQuery/OCP source or
the existing build123d STEP-first workflow. This skill can still hand generated STEP
files to `$cad` inspection tools or `$cad-explorer` for visual review when those skills
are available.

## Defaults

- Units: millimeters.
- Origin: center of the main part unless a mating datum or existing project convention
  says otherwise.
- Base plane: XY.
- Up/extrusion axis: positive Z.
- Primary source: FreeCAD Python.
- Primary exchange output: STEP.
- Native output: FCStd when useful or requested.
- Output geometry: valid closed solids unless the user requests surfaces, wires, or
  construction geometry.
- Prefer `Part` BRep operations for robust command-line generation. Use Sketcher or
  PartDesign only when the user needs editable FreeCAD feature-tree behavior.

Ask one focused clarification question only when missing information makes the model
impossible, fit-critical, safety-critical, or compliance-bound. Otherwise proceed with
explicit assumptions.

## Root Model

Keep these roots separate:

- **Skill directory**: this folder. The runner lives at `scripts/run_freecad.py`.
- **Project/workspace directory**: where model source and generated artifacts belong.
- **FreeCAD installation**: discovered through `FREECADCMD`, an explicit path, PATH,
  or common Windows install locations.
- **CAD Explorer**: visual review target for generated `.step`, `.stp`, `.stl`, or
  `.3mf` files.

Do not write generated model artifacts into the skill directory. Keep FreeCAD source,
FCStd, STEP, STL, and preview outputs near the user's project or requested output folder.

## Required Workflow

1. **Classify the task.** Identify whether this is a new FreeCAD model, source edit,
   export request, validation request, conversion from another CAD source, or visual
   review request.
2. **Load only needed references.** Use the progressive references below instead of
   reading every file.
3. **Create a natural-language CAD brief.** Capture dimensions, units, coordinate
   convention, key features, output paths, assumptions, and validation checks.
4. **Plan before coding.** Define parameters, object names, expected bounding boxes,
   feature counts, and export targets.
5. **Edit source, not generated artifacts.** Keep important dimensions in named
   parameters. Use the source contract in `references/source-contract.md`.
6. **Run with FreeCADCmd.** Prefer `scripts/run_freecad.py` so path discovery and
   output capture are consistent.
7. **Validate geometrically.** At minimum check script exit status, `Shape.isValid()`
   in source, exported file existence, and expected bounding box. Use `$cad` inspection
   tools on STEP outputs when available.
8. **Hand off to CAD Explorer.** Pass generated STEP/STL artifacts to `$cad-explorer`
   when available and return the review link.
9. **Repair and rerun.** If FreeCADCmd, export, validation, or visual review fails,
   make the smallest source change, rerun, and report the final checks actually run.

## Commands

Run a FreeCAD script from a project root:

```bash
python path/to/freecad-modeling/scripts/run_freecad.py path/to/model.py --json
```

Forward arguments to the model script after `--`:

```bash
python path/to/freecad-modeling/scripts/run_freecad.py path/to/model.py -- --output-dir out
```

Pass a custom FreeCADCmd path:

```bash
python path/to/freecad-modeling/scripts/run_freecad.py path/to/model.py --freecadcmd "E:/FreeCAD/bin/freecadcmd.exe"
```

When invoking FreeCAD directly, prefer:

```bash
"E:/FreeCAD/bin/freecadcmd.exe" path/to/model.py
```

## Non-Negotiables

- Do not treat visual inspection as a substitute for geometry checks.
- Do not claim manufacturing, strength, tolerance, or safety compliance unless those
  checks were explicitly performed.
- Do not hardcode one user's absolute FreeCAD path into generated model source.
  Use the runner, `FREECADCMD`, or documented setup instead.
- Do not silently fall back from FreeCAD source to build123d source. Ask or state the
  change if FreeCAD cannot run.
- Do not edit generated STEP/STL/FCStd files directly. Regenerate from Python source.
- Report only checks that actually ran.

## Progressive References

- `references/source-contract.md` - required shape of generated FreeCAD Python source.
- `references/part-api-patterns.md` - Part API modeling patterns, booleans, holes,
  fillets, chamfers, sketches, and feature-tree guidance.
- `references/export-and-validation.md` - FreeCADCmd execution, export targets,
  STEP inspection, CAD Explorer handoff, and final report shape.
- `references/repair-loop.md` - common FreeCAD failures and repair procedures.

Final responses should include generated source, exported artifacts, CAD Explorer links
when available, validation actually run, assumptions, and caveats.
