# FreeCAD Part API Patterns

Use this reference when writing model geometry with FreeCAD's `Part` workbench API.

## Coordinate Convention

Default convention:

- Units are millimeters.
- XY is the primary sketch/profile plane.
- +Z is the main extrusion direction.
- The primary part is centered at the origin unless the user or project says otherwise.

## Primitive Solids

```python
box = Part.makeBox(width, depth, height, App.Vector(-width / 2, -depth / 2, -height / 2))
cyl = Part.makeCylinder(radius, height, App.Vector(0, 0, -height / 2), App.Vector(0, 0, 1))
```

For cylinders on other axes, pass an axis direction:

```python
x_cyl = Part.makeCylinder(radius, length, App.Vector(-length / 2, 0, 0), App.Vector(1, 0, 0))
```

## Booleans

```python
shape = base.fuse(addition)
shape = shape.cut(cutter)
shape = shape.common(other)
shape = shape.removeSplitter()
```

Make cutters pass fully through the target with a small extra depth.

## Holes and Bolt Patterns

For through-holes, subtract cylinders:

```python
cutter = Part.makeCylinder(
    hole_diameter / 2,
    thickness + 2 * extra,
    App.Vector(x, y, -thickness / 2 - extra),
    App.Vector(0, 0, 1),
)
shape = shape.cut(cutter)
```

For circular bolt patterns:

```python
for index in range(hole_count):
    angle = math.radians(angle_offset + index * 360.0 / hole_count)
    x = bolt_circle_radius * math.cos(angle)
    y = bolt_circle_radius * math.sin(angle)
```

## Faces, Wires, Extrudes, and Revolves

Use profile construction for non-primitive shapes:

```python
edges = [
    Part.LineSegment(p1, p2).toShape(),
    Part.LineSegment(p2, p3).toShape(),
    Part.LineSegment(p3, p1).toShape(),
]
wire = Part.Wire(edges)
face = Part.Face(wire)
solid = face.extrude(App.Vector(0, 0, height))
```

For axisymmetric parts, prefer revolve when the profile is clear and stable.

## Fillets and Chamfers

Apply fillets/chamfers late, after major booleans. Keep radii smaller than nearby
feature distances.

```python
edges = [edge for edge in shape.Edges if ...]
shape = shape.makeFillet(radius, edges)
```

If edge selection is fragile, use bounding boxes, centers, or normals rather than
list indexes alone.

## Document Objects

Use document objects for user-visible outputs:

```python
obj = doc.addObject("Part::Feature", "round_flange")
obj.Shape = shape
doc.recompute()
```

Use `Part.show(shape, "name")` only for quick scripts. Prefer explicit
`doc.addObject()` in generated source so object names are deterministic.

## When To Use Sketcher or PartDesign

Prefer `Part` for backend generation and export. Use Sketcher or PartDesign when:

- the user explicitly needs editable FreeCAD features,
- constraints are the main design intent,
- an existing project already uses Sketcher/PartDesign objects.

When using Sketcher/PartDesign, document why and keep a STEP export path.
