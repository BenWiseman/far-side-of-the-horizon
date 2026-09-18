"""DESI DR2 BAO block likelihood inputs used by the geometry-only fits.
Table source: https://arxiv.org/abs/2503.14738 .
The table and builder were extracted without numerical edits from the original
calculation module; this removes unrelated CAMB and Planck imports.
"""
import numpy as np

DESI_DR2 = [
    ("BGS",        0.295, "DV",   7.942, 0.075),
    ("LRG1",       0.510, "DMDH", 13.588, 0.167, 21.863, 0.425, -0.459),
    ("LRG2",       0.706, "DMDH", 17.351, 0.177, 19.455, 0.330, -0.404),
    ("LRG3+ELG1",  0.934, "DMDH", 21.576, 0.152, 17.641, 0.193, -0.416),
    ("ELG2",       1.321, "DMDH", 27.601, 0.318, 14.176, 0.221, -0.434),
    ("QSO",        1.484, "DMDH", 30.512, 0.760, 12.817, 0.516, -0.500),
    ("Lya",        2.330, "DMDH", 38.988, 0.531, 8.632, 0.101, -0.431),
]

def _desi_vectors():
    """Build data vector d, block covariance C, and per-row (z, kind)."""
    d = []
    blocks = []
    meta = []
    for row in DESI_DR2:
        if row[2] == "DV":
            _, z, _, v, s = row
            d.append(v)
            blocks.append(np.array([[s * s]]))
            meta.append((z, "DV"))
        else:
            _, z, _, vM, sM, vH, sH, r = row
            d += [vM, vH]
            cov = np.array([[sM * sM, r * sM * sH],
                            [r * sM * sH, sH * sH]])
            blocks.append(cov)
            meta.append((z, "DMDH"))
    n = len(d)
    C = np.zeros((n, n))
    i = 0
    for b in blocks:
        k = b.shape[0]
        C[i:i + k, i:i + k] = b
        i += k
    return np.array(d), C, meta
