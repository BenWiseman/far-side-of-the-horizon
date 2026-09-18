#!/usr/bin/env python3
"""Read-only invariant audit for the publication Figure 5 redesign."""

from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "pub/paper2/fig5_data.py"
REDESIGN = ROOT / "calc/generate_fig5_v3.py"
SVG = ROOT / "pub/paper2/fig5_data.svg"


def literal(node: ast.AST):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [literal(item) for item in node.elts]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -literal(node.operand)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "np" and node.func.attr == "array":
            return literal(node.args[0])
    raise ValueError(f"unsupported assignment: {ast.dump(node, include_attributes=False)}")


def assignments(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = literal(node.value)
        except ValueError:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                out[target.id] = value
            elif isinstance(target, ast.Tuple) and isinstance(value, list):
                for item, item_value in zip(target.elts, value):
                    if isinstance(item, ast.Name):
                        out[item.id] = item_value
    return out


old = assignments(ORIGINAL)
new = assignments(REDESIGN)

name_map = {
    "NH_SUM": "NH",
    "IH_SUM": "IH",
    "LCDM_UL": "LCDM",
    "FC_UL": "FC",
    "W0WA_UL": "W0WA",
    "SUM_GRID": "X",
    "D_LCDM": "DL",
    "D_W0WA": "DW",
    "D_TOY": "DT",
}
for old_name, new_name in name_map.items():
    assert old[old_name] == new[new_name], f"value drift: {old_name} -> {new_name}"

old_points = [row[2:] for row in old["DESI_POINTS"]]
new_points = [row[1:] for row in new["FITS"]]
assert old_points == new_points, "DESI centres or error bars drifted"

svg = SVG.read_text(encoding="utf-8")
required = (
    "58.8 meV",
    "98.9 meV",
    "&lt; 64.2 meV",
    "&lt; 53 meV",
    "&lt; 163 meV",
    "No CMB lensing or primary-CMB amplitude",
    "not a substitute for panel (a)",
    "exact Λ: (−1, 0)",
    "bars: quoted 1σ",
)
for text in required:
    assert text in svg, f"missing required disclosure or value: {text}"

# Figure 5 is included at 0.865 of the 6.5-inch text block. Its SVG viewBox
# is 504 units wide, so 10 source points render at just over 8 final points.
fonts = [float(value) for value in re.findall(r'font-size="([0-9.]+)pt"', svg)]
final_pt = min(fonts) * (0.865 * 6.5 * 72.0) / 504.0
assert final_pt >= 8.0, f"Figure 5 minimum final type is {final_pt:.2f} pt"

print(f"PASS: Figure 5 preserves all values/caveats; minimum final type {final_pt:.2f} pt")
