# FreeCAD Source Contract

Use this reference when creating or refactoring FreeCAD Python source.

## Required Shape

Generated source should be runnable both from FreeCAD GUI and FreeCADCmd.

```python
from pathlib import Path

import FreeCAD as App
import Import
import Part


PARAMS = {
    "outer_diameter": 80.0,
    "thickness": 10.0,
}


def build_model(doc):
    ...
    doc.recompute()
    return obj


def validate_model(obj):
    shape = obj.Shape if hasattr(obj, "Shape") else obj
    if shape.isNull():
        raise ValueError("Generated shape is null.")
    if not shape.isValid():
        raise ValueError("Generated shape is invalid.")
    return {
        "bbox": [
            shape.BoundBox.XLength,
            shape.BoundBox.YLength,
            shape.BoundBox.ZLength,
        ],
        "volume": shape.Volume,
    }


def export_model(doc, objects, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fcstd_path = output_dir / f"{doc.Name}.FCStd"
    step_path = output_dir / f"{doc.Name}.step"
    doc.saveAs(str(fcstd_path))
    Import.export(objects, str(step_path))
    return {"fcstd": str(fcstd_path), "step": str(step_path)}


def main():
    doc = App.newDocument("model_name")
    obj = build_model(doc)
    report = validate_model(obj)
    paths = export_model(doc, [obj], Path(__file__).with_suffix("").name)
    print({"validation": report, "exports": paths})


if __name__ == "__main__":
    main()
```

## Rules

- Put all important dimensions in named constants, a `PARAMS` dictionary, or a
  dataclass near the top of the file.
- Do not hardcode output paths inside geometry functions. Use `main()` or CLI
  arguments to decide output directories.
- Return the created object or shape from `build_model()`.
- Validate before export when possible.
- Keep document object names stable and descriptive.
- Use `doc.recompute()` after creating or changing document objects.
- Prefer one source file per generated model unless the user is working in an
  existing project package.

## GUI Compatibility

Scripts should remain usable from the FreeCAD Python console:

```python
import runpy
runpy.run_path(r"C:\path\to\model.py")
```

Avoid GUI-only modules unless the user explicitly asks for UI, task panels, or
workbench commands.
