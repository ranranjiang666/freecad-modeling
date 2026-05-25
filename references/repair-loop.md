# Repair Loop

Use this reference when FreeCAD generation, export, validation, or visual review fails.

## Triage Order

1. Read FreeCADCmd return code, stdout, and stderr.
2. Identify whether the failure is import/path, syntax, API usage, invalid geometry,
   boolean failure, export failure, or CAD Explorer preview failure.
3. Change the smallest responsible source section.
4. Rerun FreeCADCmd.
5. Rerun geometry and visual validation.

## Common Failures

### FreeCADCmd Not Found

Use `--freecadcmd` or set `FREECADCMD`. Do not hardcode a user-specific path in the
model source.

### FreeCAD Module Import Fails

The script is being run with normal Python instead of FreeCADCmd. Run through
`scripts/run_freecad.py` or the FreeCADCmd executable.

### Boolean Produces Invalid Shape

Typical causes:

- cutter does not fully pass through the target,
- tangent or coincident faces create unstable topology,
- zero-thickness geometry,
- fillet/chamfer radius is too large,
- profile wire is open or self-intersecting.

Repair by adding cutter extra depth, avoiding exact tangency, reducing radii, or
building a simpler intermediate shape and validating it before later features.

### Export Fails

Ensure exports receive document objects, not only raw shapes, unless the FreeCAD API
being used accepts raw shapes. Create deterministic `Part::Feature` objects, assign
`Shape`, call `doc.recompute()`, then export.

### Shape Appears In CAD Explorer But Looks Wrong

Do not fix from the screenshot alone. Compare against expected dimensions and feature
counts. Use bounding boxes, cylindrical radii, hole positions, and STEP inspection when
available.

### Sketcher or PartDesign Fails In Headless Mode

Prefer Part API for headless generation. If feature-tree editability is required, keep
the feature-tree code minimal and add a Part API fallback only if the user agrees.

## Repair Report

When a repair was needed, report:

- the failing symptom,
- the source section changed,
- the validation rerun,
- any remaining limitation.
