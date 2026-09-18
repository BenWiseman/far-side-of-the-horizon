"""Fixed-input arithmetic for Supplement S13; no spectrum or lifetime fit."""
from pathlib import Path
import math,json

M = 4.848e8  # GeV, adopted abundance benchmark
v = 246.22  # GeV; H0=(v+h+iG0)/sqrt(2)
tau = 1e28  # seconds; freely chosen leading-order lifetime
hbar = 6.582119569e-25  # GeV seconds
Mplanck = 1.2209e19  # non-reduced, GeV
gstar = 106.75
rho_dm = 9.7e-48  # GeV^4, adopted present density
s0 = 2.3e-38  # GeV^3, adopted present entropy density
q = 8*math.pi*hbar/(M*tau)
Gamma0 = q*M/(8*math.pi)
H_M = 1.66*math.sqrt(gstar)*M*M/Mplanck
Y_inverse = 135*2/(8*math.pi**3*gstar)*Gamma0/H_M
out = {
 'inputs': {'M_GeV': M, 'v_GeV':v, 'tau_s_free':tau, 'gstar':gstar},
 'q':q, 'y_norm':math.sqrt(q), 'Gamma0_GeV':Gamma0,
 'tree_mass_bound_eV':v*v*q/(2*M)*1e9,
 'Born_branching_hnu_Znu_Wl':[0.25,0.25,0.5],
 'H_at_T_M_GeV':H_M, 'Gamma0_over_H_at_M':Gamma0/H_M,
 'scattering_over_H_per_coefficient':q*M/H_M,
 'Y_inverse_decay_MB':Y_inverse, 'Y_adopted_DM':rho_dm/(s0*M),
 'inverse_decay_fraction':Y_inverse/(rho_dm/(s0*M)),
 'depletion_13_8_Gyr':-math.expm1(-13.8e9*3.15576e7/tau),
 'scope':'Added tree-level mass term and Born decay width in the stated minimal bath. Lifetime is free. No all-orders mass bound, spectrum, flux or observational viability claim.'
}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
