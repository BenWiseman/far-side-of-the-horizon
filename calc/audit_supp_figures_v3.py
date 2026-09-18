#!/usr/bin/env python3
"""Release checks for the V3 supplement figure redraws."""

from __future__ import annotations

import importlib.util
import math
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "pub/paper2"
GENERATOR = ROOT / "calc/generate_supp_figures_v3.py"


def check(name: str, condition: bool, detail: str = "") -> None:
    state = "PASS" if condition else "FAIL"
    print(f"[{state}] {name}" + (f": {detail}" if detail else ""))
    if not condition:
        raise SystemExit(1)


spec = importlib.util.spec_from_file_location("supp_figures_v3", GENERATOR)
assert spec and spec.loader
figs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(figs)

# The right panel of Figure 2 must retain the original exact regular-mode
# formulae, not a generic schematic U-curve.
scalar_residuals: list[float] = []
tensor_residuals: list[float] = []
for eta in (1e-4, 7e-4, 0.003, 0.02, 0.11, 0.30):
    k = 20.0
    x = k * eta / math.sqrt(3.0)
    j1x = math.sin(x) / x**2 - math.cos(x) / x
    expected_scalar = math.sqrt(2.0) / 3.0 * k * k * abs(3.0 * j1x / x) * eta * eta
    z = k * eta
    h = math.sin(z) / z
    hp = -k * (math.sin(z) / z**2 - math.cos(z) / z)
    a = -(2.0 / eta) * hp - 2.0 * k * k * h
    expected_tensor = eta * eta * math.sqrt((a * a + 4.0 * k * k * hp * hp) / 6.0)
    scalar_residuals.append(abs(figs.p_scalar(k, eta) - expected_scalar) / expected_scalar)
    tensor_residuals.append(abs(figs.p_tensor(k, eta) - expected_tensor) / expected_tensor)
check("Figure 2 exact regular scalar curve", max(scalar_residuals) < 2e-13, f"max rel {max(scalar_residuals):.3e}")
check("Figure 2 exact regular tensor curve", max(tensor_residuals) < 2e-13, f"max rel {max(tensor_residuals):.3e}")

required = {
    "fig1_dictionary.svg": ["2Tᵁ", "1/(32π²d⁴)", "Karch–Randall", "Hartle–Hawking"],
    "fig2_janus.svg": ["k = 20", "P ∝ η²", "P ∝ |η|⁻¹", "scalar", "tensor", "Linear order only", "10⁻⁸", "10²", "(b) regular modes"],
    "fig3_curvature.svg": ["−0.076", "−0.039", "−0.024", "−0.016", "−0.012", "13.0σ", "37.5σ", "2.09σ"],
    "fig4_tilt.svg": ["0.957888", "0.9498", "0.9510 ± 0.0110", "0.9752 ± 0.0030", "−0.35 to −0.82"],
}
for filename, strings in required.items():
    data = (PUB / filename).read_text(encoding="utf-8")
    missing = [value for value in strings if value not in data]
    check(f"{filename} invariant labels", not missing, ", ".join(missing))
    fonts = [float(value) for value in re.findall(r'font-size="([0-9.]+)', data)]
    final_pt = min(fonts) * 6.5 * 72.0 / 700.0
    check(f"{filename} minimum type", bool(fonts) and final_pt >= 8.0, f"{min(fonts):.1f} source units = {final_pt:.2f} pt at 6.5 inches")
    colours = set(re.findall(r"#[0-9a-fA-F]{6}", data))
    check(f"{filename} grayscale-safe", all(c[1:3] == c[3:5] == c[5:7] for c in colours))

fig2 = (PUB / "fig2_janus.svg").read_text(encoding="utf-8")
check("Figure 2 has no horizon icon claim", "black holes" not in fig2 and "white holes" not in fig2)
source = GENERATOR.read_text(encoding="utf-8")
check("Figure 4 full SPT range", "mn,mx=.938,.9825" in source and '"SPT-3G D1 alone",.9510,.0110' in source)

expected_pages = {
    # Chrome quantises this 5.80-inch canvas to 418.08 pt in its vector PDF.
    "fig1_dictionary.pdf": (504.0, 418.08),
    "fig2_janus.pdf": (504.0, 360.0),
    "fig3_curvature.pdf": (504.0, 346.08),
    "fig4_tilt.pdf": (504.0, 382.08),
}
for filename, expected in expected_pages.items():
    info = subprocess.run(["pdfinfo", str(PUB / filename)], check=True, capture_output=True, text=True).stdout
    match = re.search(r"Page size:\s+([0-9.]+) x ([0-9.]+) pts", info)
    check(f"{filename} tight vector page", bool(match))
    assert match
    actual = (float(match.group(1)), float(match.group(2)))
    check(f"{filename} physical size", all(abs(a - b) < 0.02 for a, b in zip(actual, expected)), str(actual))

print("ALL SUPPLEMENT FIGURE CHECKS PASS")
