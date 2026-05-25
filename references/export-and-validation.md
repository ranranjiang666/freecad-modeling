# Export and Validation

Use this reference when running FreeCADCmd, exporting files, validating geometry,
or handing output to CAD Explorer.

## FreeCADCmd Execution

Prefer the bundled runner:

```bash
python path/to/freecad-modeling/scripts/run_freecad.py path/to/model.py --json
```

The runner executes the target script through FreeCADCmd console mode with a
small `runpy` bootstrap. This is more reliable than passing the `.py` file as a
plain positional argument on FreeCAD builds that open a console instead of
executing the file.

Discovery order:

1. `--freecadcmd <path>`
2. `FREECADCMD`, `FREECAD_CMD`, or `FREECADCMD_PATH`
3. `FreeCADCmd` / `freecadcmd` on PATH
4. common Windows locations, including `E:\FreeCAD\bin\freecadcmd.exe`

If discovery fails, ask the user for the FreeCADCmd path or tell them how to set
`FREECADCMD`.

## Export Targets

Recommended outputs:

- `.py`: source of truth
- `.FCStd`: native FreeCAD document when useful
- `.step`: primary interchange and review file
- `.stl`: optional mesh output when requested

Use `Import.export(objects, step_path)` for STEP exports. Use `Mesh.export()` or
FreeCAD's mesh workbench only when the user asks for STL or mesh output.

## Minimum Validation

Generated source should perform:

- `shape.isNull()` check
- `shape.isValid()` check
- bounding box report
- volume report for solids
- export path report

Agent-side checks after FreeCADCmd:

- command exit code is zero
- stdout/stderr reviewed for FreeCAD errors
- expected files exist and are non-empty
- STEP opens in CAD Explorer or is inspected with `$cad` tools when available

## STEP Inspection

When `$cad` is available, inspect generated STEP:

```bash
python path/to/cad/scripts/inspect refs path/to/model.step --facts --planes --positioning
```

Use targeted checks when needed:

- bounding box size
- hole counts or cylindrical face radii
- face/plane references
- mating datums and offsets

## CAD Explorer Handoff

For supported generated artifacts, start or reuse CAD Explorer with the explicit file path.
Return the URL in the final response. If CAD Explorer fails, report the failure and rely
on the command-line validation that actually ran.

## Final Report

Report:

- source file path
- exported file paths
- FreeCADCmd result
- geometry validation facts
- CAD Explorer URL or failure
- assumptions
- skipped checks or limitations

Do not claim manufacturability, tolerance compliance, or structural safety without
specific analysis.
