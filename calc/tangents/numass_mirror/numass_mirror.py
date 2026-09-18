#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
numass_mirror.py
================
Does the "two-sheet toy" dark-energy model relax the GEOMETRIC Sum m_nu bound the
way w0waCDM does, enough to make Sum m_nu = 58.8 meV comfortable?

SCOPE: these are geometry-only likelihood profiles for LCDM, w0waCDM,
and the phenomenological density rho_x(a) = Lambda - Omega_f a^3.
The toy density is an exploratory parametrisation, not a fold-derived action.
See WORKING_CALCULATIONS.md and data/README.md in the release root.

DATA / PRIORS:
  * DESI DR2 BAO: the NumPy-only calc/desi_dr2_geometry.py loader;
  * Pantheon+: zHD > 0.01 and IS_CALIBRATOR == 0, full STAT+SYS covariance,
    script-M marginalised analytically. Set PAPER2_PANTHEON_DIR or install
    the two declared inputs under data/pantheon_plus/;
  * approximate compressed CMB priors, detailed below and in the public README.

WHAT IS NEW HERE
  1. massive neutrinos in the background, exact Fermi-Dirac rho_nu(a);
  2. the omega prior is re-read as a prior on omega_cb = omega_b + omega_c
     (see MODELLING NOTE below) so that Sum m_nu moves omega_m but not r_d;
  3. profile chi^2(Sum m_nu) in three models: LCDM, w0waCDM, two-sheet toy.

MODELLING NOTE -- what the Planck prior fixes.
  In a CMB analysis the acoustic peaks fix omega_b and omega_c; for
  Sum m_nu <~ 0.3 eV every neutrino is still (near-)relativistic at z* = 1090
  (y = m a / T_nu = 0.55 at m = 0.1 eV), so the CMB's *pre-recombination*
  inference is blind to the mass and omega_c does not move with Sum m_nu.  The
  Sum m_nu information in DESI+CMB geometry therefore enters entirely through
  the LATE-time expansion: omega_m = omega_cb + omega_nu raises H(z) at z < 100,
  shrinks D_M(z*), and must be paid for with a lower h to keep 100 theta_* fixed
  -- while DESI BAO and Pantheon+ pin the low-z shape.  That is exactly the
  geometric degeneracy Elbers et al. (2503.14744, Sec. II) describe: "there is a
  geometric degeneracy between CMB constraints on Sum m_nu and the basic
  parameters H0 and Omega_m ... This degeneracy can be broken with measurements
  of the BAO distance scale at late times."
  So: the 0.1430 +- 0.0011 prior is applied to omega_cb, and r_d is evaluated at
  omega_cb (NOT at omega_m).  The residual explicit neutrino dependence of r_d is
  restored with the Aubourg et al. 2015 (1411.1074, Eq. 16) factor
  exp[-72.3 (omega_nu + 0.0006)^2], normalised to 1 at omega_nu = 0; it is a
  -0.1% effect at Sum m_nu = 0.3 eV and 1e-4 at 0.06 eV.
  At Sum m_nu = 0 this reduces EXACTLY to mirror_repulsion_combined.py.

NEUTRINO BACKGROUND
  rho_i(a) = omega_rel1 a^-4 f(y_i),  y_i = m_i a / T_nu0,
  f(y) = (120/7 pi^4) Int_0^inf dx x^2 sqrt(x^2+y^2)/(e^x+1)   [f(0)=1,
  f(y) -> A y with A = 180 zeta(3)/(7 pi^4) = 0.317316 as y -> inf].
  The integral is tabulated exactly (not the Komatsu et al. 2011 fitting
  formula); the fitting formula is printed as a cross-check.
  T_nu0 is fixed by requiring the non-relativistic limit to be exactly
  Omega_nu h^2 = Sum m_nu / (93.14 eV); a tiny massless top-up makes the
  relativistic limit exactly N_eff = 3.044.  Both limits are therefore exact and
  the relativistic -> non-relativistic transition is the exact FD one.

Runtime: a few minutes.  No pip installs.  Writes nothing but stdout.
"""
import os
import sys
import time
from pathlib import Path
import numpy as np
from scipy.integrate import quad, cumulative_simpson
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize, brentq

T0 = time.time()
np.set_printoptions(linewidth=150)

# ---------------------------------------------------------------- constants
C_KMS = 299792.458
KB = 8.617333262e-5            # eV / K
T_CMB_K = 2.7255
T_GAM0 = T_CMB_K * KB          # eV
OM_GAM = 2.469e-5              # Omega_gamma h^2, value used in the record script
NU_COEF = 0.2271               # (7/8)(4/11)^(4/3) as spelled in the record script
NEFF = 3.044
OMB = 0.02236
ZSTAR = 1089.9
RS_OVER_RD = 0.9819
NU_NORM_EV = 93.14             # Omega_nu h^2 = Sum m_nu / 93.14 eV
ZETA3 = 1.2020569031595943
A_FD = 180.0 * ZETA3 / (7.0 * np.pi ** 4)          # 0.3173164...
DM21 = 7.49e-5                 # eV^2 (NuFIT-6.0-era, matches the record's 8.65 meV)
DM31 = 2.513e-3                # eV^2 (matches the record's 50.13 meV)
SUM_TARGET = 0.0588            # eV  -- PAPER2_v2.md 4.4 prediction
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pantheon_data import pantheon_files
SN_TABLE, SN_COVARIANCE = pantheon_files()

# T_nu0 from the exact non-relativistic normalisation
T_NU_RATIO = (T_GAM0 / (NU_NORM_EV * (7.0 / 8.0) * OM_GAM * A_FD)) ** (1.0 / 3.0)
T_NU0 = T_NU_RATIO * T_GAM0
OM_NU_REL1 = (7.0 / 8.0) * T_NU_RATIO ** 4 * OM_GAM        # per species, relativistic
OM_EXTRA = OM_GAM * (NU_COEF * NEFF - 3.0 * (7.0 / 8.0) * T_NU_RATIO ** 4)
OM_RAD = OM_GAM + OM_EXTRA     # photons + massless top-up (a^-4 always)


# ---------------------------------------------------------------- f(y) table
def _f_exact(y):
    v = quad(lambda x: x * x * np.sqrt(x * x + y * y) / (np.exp(x) + 1.0),
             0.0, 60.0, limit=300)[0]
    return v * 120.0 / (7.0 * np.pi ** 4)


_LY = np.linspace(-4.0, 5.0, 1801)
_LF = np.log10(np.array([_f_exact(10.0 ** t) for t in _LY]))
_FSP = CubicSpline(_LY, _LF)


def f_nu(y):
    """rho_nu(y) / rho_nu(massless), exact FD, per species."""
    y = np.asarray(y, dtype=float)
    out = np.ones_like(y)
    lo = y > 1e-4
    hi = y > 1e5
    if lo.any():
        out[lo] = 10.0 ** _FSP(np.log10(y[lo]))
    if hi.any():
        out[hi] = A_FD * y[hi]
    return out


def f_komatsu(y):
    """Komatsu et al. 2011 (WMAP7) fitting formula, cross-check only."""
    p = 1.83
    return (1.0 + (A_FD * np.asarray(y, float)) ** p) ** (1.0 / p)


# ---------------------------------------------------------------- data
import desi_dr2_geometry as bt                                       # noqa: E402

D_BAO, C_BAO, META = bt._desi_vectors()
CI_BAO = np.linalg.inv(C_BAO)

rows = np.genfromtxt(SN_TABLE, names=True, dtype=None,
                     encoding=None)
NSN = int(open(SN_COVARIANCE).readline())
COV = np.loadtxt(SN_COVARIANCE,
                 skiprows=1).reshape(NSN, NSN)
SEL = (rows['zHD'] > 0.01) & (rows['IS_CALIBRATOR'] == 0)
ZSN = rows['zHD'][SEL]
ZHEL = rows['zHEL'][SEL]
MB = rows['m_b_corr'][SEL]
CI_SN = np.linalg.inv(COV[np.ix_(SEL, SEL)])
ONE = np.ones(SEL.sum())
CI_ONE = CI_SN @ ONE
ONE_CI_ONE = float(ONE @ CI_ONE)
print("SN used: %d of %d" % (SEL.sum(), NSN))

# ---------------------------------------------------------------- grids
NG = 8001                                    # even number of intervals
U = np.linspace(0.0, np.log(1.0 + ZSTAR), NG)
DU = U[1] - U[0]
ZG = np.exp(U) - 1.0
AG = 1.0 / (1.0 + ZG)
AG_M3 = AG ** -3
AG_M4 = AG ** -4
AG_P3 = AG ** 3
ONEPZ = 1.0 + ZG

U_SN = np.log(1.0 + ZSN)
U_STAR = np.log(1.0 + ZSTAR)
Z_BAO = np.array([m[0] for m in META])
A_BAO = 1.0 / (1.0 + Z_BAO)
U_BAO = np.log(1.0 + Z_BAO)


# ---------------------------------------------------------------- neutrinos
def masses_for(summ, spectrum='deg'):
    """Return the 3 masses (eV) for a given Sum m_nu."""
    if summ <= 0.0:
        return np.zeros(3)
    if spectrum == 'deg':
        return np.full(3, summ / 3.0)
    if spectrum == 'NO':
        floor = np.sqrt(DM21) + np.sqrt(DM31)
        if summ < floor - 1e-12:
            raise ValueError("Sum m_nu = %g below the NO floor %g" % (summ, floor))
        if summ <= floor + 1e-12:
            return np.array([0.0, np.sqrt(DM21), np.sqrt(DM31)])
        g = lambda m1: m1 + np.sqrt(m1 ** 2 + DM21) + np.sqrt(m1 ** 2 + DM31) - summ
        m1 = brentq(g, 0.0, summ)
        return np.array([m1, np.sqrt(m1 ** 2 + DM21), np.sqrt(m1 ** 2 + DM31)])
    raise ValueError(spectrum)


class NuBg(object):
    """Precomputed omega_nu(a) on the U grid and at the BAO redshifts."""

    def __init__(self, masses):
        self.m = np.asarray(masses, float)
        self.summ = float(self.m.sum())
        self.omnu_g = np.zeros(NG)
        self.omnu_bao = np.zeros(len(Z_BAO))
        for mi in self.m:
            self.omnu_g += OM_NU_REL1 * AG_M4 * f_nu(mi * AG / T_NU0)
            self.omnu_bao += OM_NU_REL1 * A_BAO ** -4 * f_nu(mi * A_BAO / T_NU0)
        self.omnu_today = float(np.sum([OM_NU_REL1 * f_nu(np.array([mi / T_NU0]))[0]
                                        for mi in self.m]))
        # the value that enters the Aubourg r_d neutrino factor
        self.omnu_nr = self.summ / NU_NORM_EV


NU_MASSLESS = NuBg(np.zeros(3))


# ---------------------------------------------------------------- background
def _ode(ocb, h, Of, nu):
    return 1.0 - (ocb + nu.omnu_today + OM_RAD) / h ** 2 + Of


def E2_grid(ocb, h, Of, w0, wa, nu):
    fde = AG ** (-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - AG))
    return ((ocb * AG_M3 + nu.omnu_g + OM_RAD * AG_M4) / h ** 2
            + _ode(ocb, h, Of, nu) * fde - Of * AG_P3)


def E2_bao(ocb, h, Of, w0, wa, nu):
    fde = A_BAO ** (-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - A_BAO))
    return ((ocb * A_BAO ** -3 + nu.omnu_bao + OM_RAD * A_BAO ** -4) / h ** 2
            + _ode(ocb, h, Of, nu) * fde - Of * A_BAO ** 3)


def r_drag(ocb, nu):
    """Record's fitting formula evaluated at omega_cb, times the Aubourg nu factor."""
    base = 147.05 * (ocb / 0.1432) ** -0.23 * (OMB / 0.02236) ** -0.13
    onu = nu.omnu_nr
    return base * np.exp(-72.3 * ((onu + 0.0006) ** 2 - 0.0006 ** 2))


BIG = 1e9


def chi2(p, nu, parts=False):
    ocb, h, Of, w0, wa = p
    if not (0.10 < ocb < 0.20 and 0.40 < h < 1.00 and -0.60 < Of < 0.60
            and -2.5 < w0 < 0.0 and -4.0 < wa < 3.0):
        return BIG
    e2 = E2_grid(ocb, h, Of, w0, wa, nu)
    if np.any(e2 <= 1e-12):
        return BIG
    integ = ONEPZ / np.sqrt(e2)
    icum = cumulative_simpson(integ, dx=DU, initial=0.0)
    if not np.all(np.isfinite(icum)):
        return BIG
    isp = CubicSpline(U, icum)

    dh_over_c = C_KMS / (100.0 * h)
    rd = r_drag(ocb, nu)

    # ---- BAO
    e2b = E2_bao(ocb, h, Of, w0, wa, nu)
    if np.any(e2b <= 0):
        return BIG
    dm_b = dh_over_c * isp(U_BAO)
    dhz_b = dh_over_c / np.sqrt(e2b)
    th = []
    for i, (z, kind) in enumerate(META):
        if kind == 'DV':
            th.append((z * dm_b[i] ** 2 * dhz_b[i]) ** (1.0 / 3.0) / rd)
        else:
            th += [dm_b[i] / rd, dhz_b[i] / rd]
    r = D_BAO - np.array(th)
    x2_bao = float(r @ CI_BAO @ r)

    # ---- SN (script-M marginalised analytically; h drops out with M)
    isn = isp(U_SN)
    if np.any(isn <= 0):
        return BIG
    mu_shape = 5.0 * np.log10((1.0 + ZHEL) * isn)
    rs_ = MB - mu_shape
    A = float(rs_ @ CI_SN @ rs_)
    B = float(rs_ @ CI_ONE)
    x2_sn = A - B * B / ONE_CI_ONE

    # ---- priors
    x2_om = ((ocb - 0.1430) / 0.0011) ** 2
    th_star = 100.0 * RS_OVER_RD * rd / (dh_over_c * isp(U_STAR))
    x2_th = ((th_star - 1.04109) / 0.00030) ** 2

    tot = x2_bao + x2_sn + x2_om + x2_th
    if parts:
        return dict(total=tot, bao=x2_bao, sn=x2_sn, om=x2_om, theta=x2_th,
                    rd=rd, theta_star=th_star, DM_star=dh_over_c * isp(U_STAR))
    return float(tot)


# ---------------------------------------------------------------- fitting
FREE = {'lcdm': [0, 1], 'w0wa': [0, 1, 3, 4], 'mirror': [0, 1, 2],
        'toy2side': [0, 1, 2]}
P_DEF = {'lcdm': [0.1430, 0.68, 0.0, -1.0, 0.0],
         'w0wa': [0.1430, 0.68, 0.0, -0.85, -0.60],
         'mirror': [0.1430, 0.68, 0.10, -1.0, 0.0],
         'toy2side': [0.1430, 0.68, 0.00, -1.0, 0.0]}
BND = [(0.128, 0.160), (0.50, 0.90), (0.0, 0.55), (-2.0, -0.2), (-3.5, 2.0)]
# 'toy2side' = the same one-parameter toy but with the sign of the inter-face
# term FREE (Omega_f < 0 = attractive coupling, rho_x = Lambda + |Of| a^3).
BND_OF = {'mirror': (0.0, 0.55), 'toy2side': (-0.35, 0.55)}


def fit(model, nu, seed=None, ntries=3):
    free = FREE[model]
    base = list(P_DEF[model])
    if seed is not None:
        base = list(seed)
        if model == 'lcdm':
            base[2], base[3], base[4] = 0.0, -1.0, 0.0
        if model in ('mirror', 'toy2side'):
            base[3], base[4] = -1.0, 0.0
        if model == 'w0wa':
            base[2] = 0.0

    def obj(x):
        p = list(base)
        for i, j in enumerate(free):
            p[j] = x[i]
        return chi2(p, nu)

    bnds = [BND[j] if j != 2 else BND_OF.get(model, BND[2]) for j in free]
    base[2] = float(np.clip(base[2], bnds[free.index(2)][0] + 1e-6,
                            bnds[free.index(2)][1] - 1e-6)) if 2 in free else base[2]
    best = None
    for t in range(ntries):
        rng = np.random.default_rng(1000 * t + len(free))
        x0 = np.array([base[j] for j in free], float)
        if t > 0:
            span = np.array([b[1] - b[0] for b in bnds])
            x0 = np.clip(x0 + 0.06 * span * rng.standard_normal(len(free)),
                         [b[0] for b in bnds], [b[1] for b in bnds])
        r1 = minimize(obj, x0, method='Nelder-Mead', bounds=bnds,
                      options=dict(xatol=1e-7, fatol=1e-6, maxiter=6000,
                                   maxfev=6000))
        r2 = minimize(obj, r1.x, method='Powell', bounds=bnds,
                      options=dict(xtol=1e-8, ftol=1e-9, maxiter=6000))
        r = r2 if r2.fun < r1.fun else r1
        if best is None or r.fun < best.fun:
            best = r
    p = list(base)
    for i, j in enumerate(free):
        p[j] = best.x[i]
    return float(best.fun), p


def fit_best(model, nu, seed=None, ntries=3):
    """fit() plus, for the two-sided toy, an explicit start on the negative-Of
    branch so the continuation cannot get trapped on the Omega_f > 0 side."""
    x2, p = fit(model, nu, seed=seed, ntries=ntries)
    if model == 'toy2side':
        for of0 in (-0.10, -0.25):
            s2 = list(p)
            s2[2] = of0
            y2, q = fit(model, nu, seed=s2, ntries=2)
            if y2 < x2:
                x2, p = y2, q
    return x2, p


# ================================================================ RUN
def hr(t):
    print('\n' + '=' * 78)
    print(t)
    print('=' * 78)


hr("0.  SETUP / SELF-TESTS")
print("T_nu0/T_gamma0        = %.6f      [(4/11)^(1/3) = %.6f]"
      % (T_NU_RATIO, (4.0 / 11.0) ** (1.0 / 3.0)))
print("implied N_eff from the 3 nu species (relativistic) = %.4f"
      % (3.0 * (7.0 / 8.0) * T_NU_RATIO ** 4 / NU_COEF))
print("massless top-up omega_extra = %.3e  -> total N_eff = %.4f"
      % (OM_EXTRA, (3.0 * (7.0 / 8.0) * T_NU_RATIO ** 4 * OM_GAM + OM_EXTRA)
         / (NU_COEF * OM_GAM)))
print("total radiation at Sum m_nu = 0 : omega_r = %.6e ; record value = %.6e  (diff %.2e)"
      % (OM_RAD + 3 * OM_NU_REL1, OM_GAM * (1 + NU_COEF * NEFF),
         OM_RAD + 3 * OM_NU_REL1 - OM_GAM * (1 + NU_COEF * NEFF)))
_nrchk = NuBg(np.full(3, 0.1))
print("NR normalisation check: Omega_nu h^2 at Sum m_nu = 0.3 eV -> %.6f ; Sum/93.14 = %.6f"
      % (_nrchk.omnu_today, 0.3 / NU_NORM_EV))
for yy in (0.03, 0.3, 1.0, 3.0, 30.0):
    print("   f(y=%6.2f): exact %.6f   Komatsu-2011 fit %.6f   (diff %+.3e)"
          % (yy, f_nu(np.array([yy]))[0], f_komatsu(yy),
             f_nu(np.array([yy]))[0] - f_komatsu(yy)))
# transition check
for lab, mm in (("50.13 meV (NO heaviest)", 0.05013), ("19.6 meV (deg, Sum=58.8)", 0.0196),
                ("8.65 meV (NO middle)", 0.008654), ("100 meV (deg, Sum=300)", 0.1)):
    ynow = mm / T_NU0
    zstar_y = mm / (T_NU0 * (1.0 + ZSTAR))
    print("   m = %-26s  y(a=1) = %8.1f (NR since z ~ %6.1f) ; y(z*) = %.3f, f = %.4f"
          % (lab, ynow, ynow - 1.0, zstar_y, f_nu(np.array([zstar_y]))[0]))

# distance accuracy vs quad
_p = [0.1430, 0.68, 0.0, -1.0, 0.0]
_e2f = lambda a: ((0.1430 * a ** -3 + OM_RAD * a ** -4 + 3 * OM_NU_REL1 * a ** -4) / 0.68 ** 2
                  + _ode(0.1430, 0.68, 0.0, NU_MASSLESS))
_e2g = E2_grid(*_p, NU_MASSLESS)
_ic = cumulative_simpson(ONEPZ / np.sqrt(_e2g), dx=DU, initial=0.0)
_isp = CubicSpline(U, _ic)
for zt in (0.01, 0.3, 1.0, 2.33, ZSTAR):
    qq = quad(lambda zz: 1.0 / np.sqrt(_e2f(1.0 / (1.0 + zz))), 0, zt, limit=400)[0]
    gg = float(_isp(np.log(1.0 + zt)))
    print("   I(z=%8.3f): grid %.8f  quad %.8f  rel diff %+.2e" % (zt, gg, qq, gg / qq - 1))

hr("1.  REPRODUCTION OF THE RECORD AT Sum m_nu = 0")
rec = {}
for m in ('lcdm', 'w0wa', 'mirror'):
    x2, p = fit(m, NU_MASSLESS, ntries=4)
    rec[m] = (x2, p)
    print("%-8s chi2 = %9.3f   omega_cb=%.5f h=%.5f Of=%.4f w0=%+.3f wa=%+.3f  (Om=%.4f)"
          % (m, x2, p[0], p[1], p[2], p[3], p[4], p[0] / p[1] ** 2))
print("\n  record (TANGENTS_20260908.md sec.11 / mirror_repulsion_combined.py):")
print("     LCDM 1406.86 ; w0wa 1397.74 (D=-9.1) ; mirror 1404.12 (D=-2.7), Of=0.054, h=0.673")
print("  here:  LCDM %.2f ; w0wa %.2f (D=%+.2f) ; mirror %.2f (D=%+.2f)"
      % (rec['lcdm'][0], rec['w0wa'][0], rec['w0wa'][0] - rec['lcdm'][0],
         rec['mirror'][0], rec['mirror'][0] - rec['lcdm'][0]))
_pm = rec['mirror'][1]
_OL = 1.0 - (_pm[0] + NU_MASSLESS.omnu_today + OM_RAD) / _pm[1] ** 2 + _pm[2]
print("  NOTE on the record's toy diagnostics: mirror_repulsion_combined.py:71 sets")
print("  OL = 1-Om-Of for the diagnostic block, but the OL that appears in its own E2")
print("  (line 25) is 1-Om-Or+Of.  With the correct OL = %.4f the same best fit gives"
      % _OL)
print("  (w0, wa) = (%+.3f, %+.3f) and rho_x = 0 at a = %.3f, not (-0.91,-0.30) and 2.28."
      % (-1 + _pm[2] / (_OL - _pm[2]), -3 * _pm[2] * _OL / (_OL - _pm[2]) ** 2,
         (_OL / _pm[2]) ** (1 / 3.0)))
print("  The FIT itself (chi2, Om, h, Of) is unaffected -- only the printed projection.")

hr("2.  PROFILE chi^2(Sum m_nu)  --  3 degenerate species")
SUMS = np.array([0.0, 0.010, 0.020, 0.030, 0.040, 0.050, SUM_TARGET, 0.070,
                 0.085, 0.100, 0.120, 0.150, 0.180, 0.220, 0.260, 0.300])
MODELS = ('lcdm', 'w0wa', 'mirror', 'toy2side')
prof = {m: np.zeros(len(SUMS)) for m in MODELS}
pars = {m: [None] * len(SUMS) for m in MODELS}
seed = {m: None for m in MODELS}
print("%9s | %10s %10s %10s %10s | %s"
      % ("Sum(meV)", "LCDM", "w0waCDM", "toy Of>=0", "toy Of any",
         "toy(Of>=0): Of    h      w0     wa"))
for i, s in enumerate(SUMS):
    nu = NuBg(masses_for(s, 'deg'))
    line = "%9.1f |" % (1000 * s)
    for m in MODELS:
        x2, p = fit_best(m, nu, seed=seed[m], ntries=3)
        prof[m][i] = x2
        pars[m][i] = p
        seed[m] = p
        line += " %10.3f" % x2
    pm = pars['mirror'][i]
    OL = 1.0 - (pm[0] + nu.omnu_today + OM_RAD) / pm[1] ** 2 + pm[2]
    rx = OL - pm[2]
    w0p = -1.0 + pm[2] / rx
    wap = -3.0 * pm[2] * OL / rx ** 2          # -dw/da at a=1
    line += " | %7.4f %.4f %+.3f %+.3f" % (pm[2], pm[1], w0p, wap)
    print(line, flush=True)
print("\n  best-fit Omega_f in the two-sided toy (sign free):")
print("   " + "  ".join("%.1f:%+.4f" % (1000 * SUMS[i], pars['toy2side'][i][2])
                        for i in range(len(SUMS))))
print("\n  LCDM along the profile (omega_cb, h, Om_total, and the omega_cb prior pull):")
for i in (0, 6, 9, 15):
    p = pars['lcdm'][i]
    nu = NuBg(masses_for(SUMS[i], 'deg'))
    print("    Sum=%6.1f meV : omega_cb=%.5f (%.2f sigma from 0.1430)  h=%.5f"
          "  Om_tot=%.4f  omega_m=%.5f"
          % (1000 * SUMS[i], p[0], (p[0] - 0.1430) / 0.0011, p[1],
             (p[0] + nu.omnu_today) / p[1] ** 2, p[0] + nu.omnu_nr))
print("  bound-saturation check (fit box vs best fits over the whole grid):")
for j, nm in ((0, 'omega_cb'), (1, 'h'), (2, 'Omega_f')):
    vals = [pars[m][i][j] for m in MODELS for i in range(len(SUMS))]
    lo, hi = BND[j] if j != 2 else BND_OF['toy2side']
    print("    %-9s range [%+.5f, %+.5f]   box [%+.4f, %+.4f]  %s"
          % (nm, min(vals), max(vals), lo, hi,
             "OK (interior)" if min(vals) > lo + 1e-4 and max(vals) < hi - 1e-4
             else "*** AT A BOX EDGE ***"))

hr("3.  BOUNDS AND Delta chi^2")


def bound(sums, x2, target=2.71):
    d = x2 - x2.min()
    ib = int(np.argmin(x2))
    sp = CubicSpline(sums, d - target)
    for k in range(ib, len(sums) - 1):
        if (d[k] - target) * (d[k + 1] - target) < 0:
            return brentq(lambda s: float(sp(s)), sums[k], sums[k + 1]), sums[ib], d
    return np.nan, sums[ib], d


def bayes_bound(sums, x2, frac=0.95):
    """95% quantile of exp(-Dchi2/2) with a flat Sum m_nu >= 0 prior -- the
    construction DESI/Elbers quote (their 0.0642 eV), NOT the Dchi2=2.71 one."""
    sp = CubicSpline(sums, x2 - x2.min())
    g = np.linspace(sums[0], sums[-1], 40001)
    L = np.exp(-0.5 * sp(g))
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (L[1:] + L[:-1]) * np.diff(g))])
    cdf /= cdf[-1]
    return float(np.interp(frac, cdf, g))


res = {}
for m in MODELS:
    b, sbest, d = bound(SUMS, prof[m])
    bb = bayes_bound(SUMS, prof[m])
    dtar = float(CubicSpline(SUMS, d)(SUM_TARGET))
    res[m] = dict(bound=b, bayes=bb, sbest=sbest, dprof=d, dtarget=dtar,
                  chi2min=prof[m].min())
    print("%-8s : chi2_min = %9.3f at Sum m_nu = %6.1f meV" % (m, prof[m].min(),
                                                               1000 * sbest))
    print("           95%% profile-likelihood bound (Dchi2 = 2.71, = 1.645 sigma) = %6.1f meV"
          % (1000 * b))
    print("           95%% Bayesian-equivalent bound (flat Sum>=0 prior)          = %6.1f meV"
          % (1000 * bb))
    print("           Delta chi^2 at Sum m_nu = 58.8 meV vs this model's own best = %+.3f"
          " (= %.2f sigma)" % (dtar, np.sqrt(max(dtar, 0.0))))
print("\n  bound SHIFT vs LCDM (Dchi2=2.71):  w0wa %+.1f meV ; toy(Of>=0) %+.1f meV ;"
      " toy(Of any sign) %+.1f meV"
      % (1000 * (res['w0wa']['bound'] - res['lcdm']['bound']),
         1000 * (res['mirror']['bound'] - res['lcdm']['bound']),
         1000 * (res['toy2side']['bound'] - res['lcdm']['bound'])))
print("  bound SHIFT vs LCDM (Bayesian-equivalent): w0wa %+.1f ; toy(Of>=0) %+.1f ;"
      " toy(Of any) %+.1f meV"
      % (1000 * (res['w0wa']['bayes'] - res['lcdm']['bayes']),
         1000 * (res['mirror']['bayes'] - res['lcdm']['bayes']),
         1000 * (res['toy2side']['bayes'] - res['lcdm']['bayes'])))
print("\n  CROSS-CHECK vs DESI DR2 (Elbers et al. 2503.14744):")
print("    published, DESI DR2 BAO + CMB (Planck+ACT incl. lensing), LCDM, flat Sum>=0")
print("    prior, Bayesian 95%: Sum m_nu < 64.2 meV with sigma(Sum m_nu) = 20 meV.")
print("    here, geometry only (BAO + Pantheon+ + omega_cb + theta_* priors, NO CMB")
print("    lensing, NO primary-CMB amplitude/ISW): Bayesian-equivalent %.1f meV." % (
      1000 * res['lcdm']['bayes']))
_s = SUM_TARGET / np.sqrt(max(res['lcdm']['dtarget'], 1e-9))
print("    Gaussian width implied by this profile: s = %.1f meV (DESI's 20 meV is the"
      % (1000 * _s))
print("    std of the TRUNCATED posterior; for a half-Gaussian s = 20/0.6028 = 33.2 meV).")
print("  absolute chi2 at Sum m_nu = 58.8 meV (interpolated):")
c58 = {}
for m in MODELS:
    c58[m] = float(CubicSpline(SUMS, prof[m])(SUM_TARGET))
    print("     %-8s %10.3f" % (m, c58[m]))
print("  --> at Sum m_nu = 58.8 meV FIXED:  w0wa - LCDM = %+.2f (2 params) ;"
      " toy(Of>=0) - LCDM = %+.2f (1 param) ; toy(Of any) - LCDM = %+.2f (1 param)"
      % (c58['w0wa'] - c58['lcdm'], c58['mirror'] - c58['lcdm'],
         c58['toy2side'] - c58['lcdm']))
print("  --> compare at Sum m_nu = 0:      w0wa - LCDM = %+.2f ; toy(Of>=0) - LCDM = %+.2f"
      % (prof['w0wa'][0] - prof['lcdm'][0], prof['mirror'][0] - prof['lcdm'][0]))

hr("4.  TOY DIAGNOSTICS AT Sum m_nu = 58.8 meV (degenerate) AND (0, 8.65, 50.13) meV")
for spec in ('deg', 'NO'):
    nu = NuBg(masses_for(SUM_TARGET, spec))
    row = {}
    for m in MODELS:
        x2, p = fit_best(m, nu, seed=pars[m][6], ntries=4)
        row[m] = (x2, p)
    print("\n  spectrum = %s  masses = %s eV" % (spec, np.round(nu.m, 5)))
    for m in MODELS:
        x2, p = row[m]
        print("    %-8s chi2 = %9.3f  omega_cb=%.5f h=%.5f Of=%+.4f w0=%+.3f wa=%+.3f"
              " Om_tot=%.4f" % (m, x2, p[0], p[1], p[2], p[3], p[4],
                                (p[0] + nu.omnu_today) / p[1] ** 2))
    print("    Delta chi2 vs LCDM at fixed Sum m_nu = 58.8 meV : w0wa %+.3f ;"
          " toy(Of>=0) %+.3f ; toy(Of any) %+.3f"
          % (row['w0wa'][0] - row['lcdm'][0], row['mirror'][0] - row['lcdm'][0],
             row['toy2side'][0] - row['lcdm'][0]))
    pm = row['mirror'][1]
    ocb, h, Of = pm[0], pm[1], pm[2]
    OL = 1.0 - (ocb + nu.omnu_today + OM_RAD) / h ** 2 + Of
    rx0 = OL - Of
    w0p = -1.0 + Of / rx0
    wap = -3.0 * Of * OL / rx0 ** 2
    a_rx0 = (OL / Of) ** (1.0 / 3.0) if Of > 0 else np.inf
    # true turnaround: E^2 = 0
    ff = lambda a: ((ocb * a ** -3 + OM_RAD * a ** -4) / h ** 2
                    + (nu.summ / NU_NORM_EV) * a ** -3 / h ** 2 + OL - Of * a ** 3)
    try:
        a_h0 = brentq(ff, 1.0, 50.0)
    except ValueError:
        a_h0 = np.nan
    print("    TOY: Omega_f = %.4f  Omega_Lambda(code) = %.4f  rho_x(1) = %.4f" % (Of, OL, rx0))
    print("         CPL projection (w0, wa) = (%+.3f, %+.3f)" % (w0p, wap))
    print("         rho_x = 0 at a = %.3f (z = %+.3f) ; H = 0 (true turnaround) at a = %.3f"
          % (a_rx0, 1.0 / a_rx0 - 1.0, a_h0))
    if spec == 'deg':
        TOY58 = (row, nu, pm)

hr("5.  ROBUSTNESS: r_d convention")
print("  primary: r_d = 147.05 (omega_cb/0.1432)^-0.23 (ob/0.02236)^-0.13 x Aubourg nu factor")
for s in (0.0, SUM_TARGET, 0.150, 0.300):
    nu = NuBg(masses_for(s, 'deg'))
    rd1 = r_drag(0.1430, nu)
    rd_omega_m = (147.05 * ((0.1430 + nu.omnu_nr) / 0.1432) ** -0.23
                  * (OMB / 0.02236) ** -0.13)
    rd_aub = (55.154 * np.exp(-72.3 * (nu.omnu_nr + 0.0006) ** 2)
              / (0.1430 ** 0.25351 * OMB ** 0.12807))
    print("   Sum=%6.1f meV : r_d(this work) = %7.3f  |  r_d if omega_m fed in = %7.3f"
          "  |  r_d Aubourg-16 = %7.3f Mpc" % (1000 * s, rd1, rd_omega_m, rd_aub))
print("  (feeding omega_m instead of omega_cb into the -0.23 exponent would fake a"
      " %.2f%% r_d drop at 0.3 eV; the true nu dependence is %.3f%%.)"
      % (100 * (1 - rd_omega_m / rd1), 100 * (np.exp(-72.3 * ((0.300 / NU_NORM_EV
                                                               + 0.0006) ** 2
                                                              - 0.0006 ** 2)) - 1)))

hr("6.  SENSITIVITY OF THE LCDM BOUND TO THE PRIOR CONVENTION")


def chi2_var(p, nu, prior_on='ocb', rd_on='ocb', sig_om=0.0011):
    """p[0] is omega_cb.  prior_on/rd_on select which combination the 0.1430 prior
    and the r_d formula see."""
    ocb, h, Of, w0, wa = p
    om = ocb + nu.omnu_nr
    if not (0.10 < ocb < 0.20 and 0.40 < h < 1.00):
        return BIG
    e2 = E2_grid(ocb, h, Of, w0, wa, nu)
    if np.any(e2 <= 1e-12):
        return BIG
    isp = CubicSpline(U, cumulative_simpson(ONEPZ / np.sqrt(e2), dx=DU, initial=0.0))
    dh_over_c = C_KMS / (100.0 * h)
    arg = ocb if rd_on == 'ocb' else om
    rd = 147.05 * (arg / 0.1432) ** -0.23 * (OMB / 0.02236) ** -0.13
    if rd_on == 'ocb':
        rd *= np.exp(-72.3 * ((nu.omnu_nr + 0.0006) ** 2 - 0.0006 ** 2))
    e2b = E2_bao(ocb, h, Of, w0, wa, nu)
    if np.any(e2b <= 0):
        return BIG
    dm_b = dh_over_c * isp(U_BAO)
    dhz_b = dh_over_c / np.sqrt(e2b)
    th = []
    for i, (z, kind) in enumerate(META):
        if kind == 'DV':
            th.append((z * dm_b[i] ** 2 * dhz_b[i]) ** (1.0 / 3.0) / rd)
        else:
            th += [dm_b[i] / rd, dhz_b[i] / rd]
    r = D_BAO - np.array(th)
    x2 = float(r @ CI_BAO @ r)
    isn = isp(U_SN)
    rr = MB - 5.0 * np.log10((1.0 + ZHEL) * isn)
    x2 += (float(rr @ CI_SN @ rr) - float(rr @ CI_ONE) ** 2 / ONE_CI_ONE)
    x2 += (((ocb if prior_on == 'ocb' else om) - 0.1430) / sig_om) ** 2
    th_star = 100.0 * RS_OVER_RD * rd / (dh_over_c * isp(U_STAR))
    x2 += ((th_star - 1.04109) / 0.00030) ** 2
    return float(x2)


VARIANTS = [('omega_cb prior, r_d(omega_cb)   [PRIMARY]', 'ocb', 'ocb', 0.0011),
            ('omega_cb prior widened to +-0.0015', 'ocb', 'ocb', 0.0015),
            ('omega_m  prior, r_d(omega_cb)', 'om', 'ocb', 0.0011),
            ('omega_m  prior, r_d(omega_m)  [naive]', 'om', 'om', 0.0011)]
for lab, po, ro, so in VARIANTS:
    pv = []
    x0 = [0.1430, 0.68]
    for s in SUMS:
        nu = NuBg(masses_for(s, 'deg'))
        f = lambda x: chi2_var([x[0], x[1], 0.0, -1.0, 0.0], nu, po, ro, so)
        r1 = minimize(f, x0, method='Nelder-Mead', bounds=[BND[0], BND[1]],
                      options=dict(xatol=1e-8, fatol=1e-7, maxiter=5000))
        r1 = minimize(f, r1.x, method='Powell', bounds=[BND[0], BND[1]],
                      options=dict(xtol=1e-9, ftol=1e-10))
        pv.append(float(r1.fun))
        x0 = list(r1.x)
    pv = np.array(pv)
    b_, s_, d_ = bound(SUMS, pv)
    bb_ = bayes_bound(SUMS, pv)
    print("  %-38s : min at %5.1f meV ; Dchi2=2.71 bound %6.1f meV ; Bayes-equiv %6.1f meV"
          % (lab, 1000 * s_, 1000 * b_, 1000 * bb_))
print("\n  6b. Do the model-to-model SHIFTS survive a wider omega_cb prior? (all 3 models,")
print("      sigma(omega_cb) = 0.0015 instead of 0.0011)")
_bw = {}
for m in MODELS[:3]:
    free = FREE[m]
    pv = []
    base0 = list(P_DEF[m])
    for s in SUMS:
        nu = NuBg(masses_for(s, 'deg'))

        def fo(x, _b=base0, _f=free, _nu=nu):
            p = list(_b)
            for i, j in enumerate(_f):
                p[j] = x[i]
            return chi2_var(p, _nu, 'ocb', 'ocb', 0.0015)
        bn = [BND[j] if j != 2 else BND_OF.get(m, BND[2]) for j in free]
        x0 = np.array([base0[j] for j in free], float)
        r1 = minimize(fo, x0, method='Nelder-Mead', bounds=bn,
                      options=dict(xatol=1e-8, fatol=1e-7, maxiter=6000, maxfev=6000))
        r1 = minimize(fo, r1.x, method='Powell', bounds=bn,
                      options=dict(xtol=1e-9, ftol=1e-10))
        pv.append(float(r1.fun))
        base0 = list(base0)
        for i, j in enumerate(free):
            base0[j] = r1.x[i]
    pv = np.array(pv)
    b_, s_, d_ = bound(SUMS, pv)
    _bw[m] = (b_, bayes_bound(SUMS, pv), float(CubicSpline(SUMS, pv - pv.min())(SUM_TARGET)),
              pv)
    print("      %-8s Dchi2=2.71 bound %6.1f meV ; Bayes-equiv %6.1f meV ;"
          " Dchi2(58.8) = %+.3f" % (m, 1000 * b_, 1000 * _bw[m][1], _bw[m][2]))
print("      SHIFT vs LCDM at sigma=0.0015 :  w0wa %+.1f meV ; toy %+.1f meV"
      % (1000 * (_bw['w0wa'][0] - _bw['lcdm'][0]),
         1000 * (_bw['mirror'][0] - _bw['lcdm'][0])))
print("      (at sigma=0.0011 the same shifts were %+.1f and %+.1f meV)"
      % (1000 * (res['w0wa']['bound'] - res['lcdm']['bound']),
         1000 * (res['mirror']['bound'] - res['lcdm']['bound'])))
print("      chi2 gaps at Sum m_nu = 58.8 meV, sigma=0.0015: w0wa - LCDM = %+.2f ;"
      " toy - LCDM = %+.2f"
      % (float(CubicSpline(SUMS, _bw['w0wa'][3])(SUM_TARGET))
         - float(CubicSpline(SUMS, _bw['lcdm'][3])(SUM_TARGET)),
         float(CubicSpline(SUMS, _bw['mirror'][3])(SUM_TARGET))
         - float(CubicSpline(SUMS, _bw['lcdm'][3])(SUM_TARGET))))
print("\n  READING: the geometric Sum m_nu signal IS the gap between omega_cb and omega_m.")
print("  If the 0.1430 prior is (wrongly) imposed on the TOTAL omega_m, adding neutrino")
print("  mass merely swaps CDM for neutrinos -- both non-relativistic at z < 100 -- the")
print("  late-time background barely moves and the bound evaporates.  That is why the")
print("  prior must be read as omega_cb: the CMB peaks fix omega_b and omega_c, and")
print("  Sum m_nu adds on top of them.")

hr("7.  WHAT WOULD KILL THE TOY: BAO observables, toy vs LCDM at Sum m_nu = 58.8 meV")
row, nu58, pm = TOY58
pl = row['lcdm'][1]
zz = np.array([0.295, 0.51, 0.706, 0.934, 1.321, 1.484, 2.33, 0.15, 0.05])
aa = 1.0 / (1.0 + zz)


def obs(p, nu):
    ocb, h, Of, w0, wa = p
    e2 = E2_grid(ocb, h, Of, w0, wa, nu)
    isp = CubicSpline(U, cumulative_simpson(ONEPZ / np.sqrt(e2), dx=DU, initial=0.0))
    dh_over_c = C_KMS / (100.0 * h)
    rd = r_drag(ocb, nu)
    fde = aa ** (-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - aa))
    omnu_a = np.zeros_like(aa)
    for mi in nu.m:
        omnu_a += OM_NU_REL1 * aa ** -4 * f_nu(mi * aa / T_NU0)
    e2a = ((ocb * aa ** -3 + omnu_a + OM_RAD * aa ** -4) / h ** 2
           + _ode(ocb, h, Of, nu) * fde - Of * aa ** 3)
    dm = dh_over_c * isp(np.log(1 + zz))
    dhz = dh_over_c / np.sqrt(e2a)
    return dm / rd, dhz / rd


dmT, dhT = obs(pm, nu58)
dmL, dhL = obs(pl, nu58)
dmW, dhW = obs(row['w0wa'][1], nu58)
sig_dm = {0.51: 0.167 / 13.588, 0.706: 0.177 / 17.351, 0.934: 0.152 / 21.576,
          1.321: 0.318 / 27.601, 1.484: 0.760 / 30.512, 2.33: 0.531 / 38.988}
sig_dh = {0.51: 0.425 / 21.863, 0.706: 0.330 / 19.455, 0.934: 0.193 / 17.641,
          1.321: 0.221 / 14.176, 1.484: 0.516 / 12.817, 2.33: 0.101 / 8.632}
sig_dv = {0.295: 0.075 / 7.942}
print("  (a) toy MINUS LCDM  (both at Sum m_nu = 58.8 meV)")
print("   z      dDM/DM (%)   in DR2 sig    dDH/DH (%)   in DR2 sig")
for i, z in enumerate(zz):
    a1 = 100 * (dmT[i] / dmL[i] - 1)
    b1 = 100 * (dhT[i] / dhL[i] - 1)
    s1 = a1 / (100 * sig_dm[z]) if z in sig_dm else np.nan
    s2 = b1 / (100 * sig_dh[z]) if z in sig_dh else np.nan
    print("  %5.3f   %+9.3f    %+9.2f     %+9.3f    %+9.2f" % (z, a1, s1, b1, s2))
print("  (b) toy MINUS w0waCDM -- THE discriminant, both at Sum m_nu = 58.8 meV")
print("   z      dDM/DM (%)   in DR2 sig   need sig<   dDH/DH (%)   in DR2 sig   need sig<")
worst = 0.0
for i, z in enumerate(zz):
    a1 = 100 * (dmT[i] / dmW[i] - 1)
    b1 = 100 * (dhT[i] / dhW[i] - 1)
    s1 = a1 / (100 * sig_dm[z]) if z in sig_dm else np.nan
    s2 = b1 / (100 * sig_dh[z]) if z in sig_dh else np.nan
    n1 = abs(a1) / 2.0
    n2 = abs(b1) / 2.0
    worst = max(worst, abs(s1) if np.isfinite(s1) else 0, abs(s2) if np.isfinite(s2) else 0)
    print("  %5.3f   %+9.3f    %+9.2f     %6.3f%%    %+9.3f    %+9.2f     %6.3f%%"
          % (z, a1, s1, n1, b1, s2, n2))
print("   'need sig<' = the per-point fractional error at which that single point alone")
print("   separates the toy from free CPL at 2 sigma.  DR2's own errors are, in the same")
print("   order, DM: " + " ".join("%.2f%%" % (100 * sig_dm[z]) for z in zz if z in sig_dm))
print("   and DH: " + " ".join("%.2f%%" % (100 * sig_dh[z]) for z in zz if z in sig_dh))
print("   D_V(0.295) DR2 error = %.2f%%." % (100 * sig_dv[0.295]))
print("   Largest single-point separation now: %.2f sigma. The FULL-vector separation is"
      % worst)
print("   the chi2 difference: chi2(toy) - chi2(w0wa) = %.3f at Sum m_nu = 58.8 meV,"
      % (row['mirror'][0] - row['w0wa'][0]))
print("   i.e. free CPL beats the toy by %.1f for one extra parameter (%.1f sigma) ALREADY."
      % (row['mirror'][0] - row['w0wa'][0], np.sqrt(row['mirror'][0] - row['w0wa'][0])))
print("\n  (c) the toy's exact locus in the CPL plane (a one-parameter curve, not a plane):")
print("      w_a = -3 (2 + w_0)(1 + w_0)   [derived: w(a) = -1 + Of a^3/(OL - Of a^3)]")
for w0t in (-0.98, -0.95, -0.932, -0.90, -0.87, -0.835, -0.80):
    print("        w0 = %+.3f -> toy demands wa = %+.4f" % (w0t, -3 * (2 + w0t) * (1 + w0t)))
print("      free-CPL best fit here (Sum m_nu = 58.8 meV): (w0, wa) = (%+.3f, %+.3f);"
      % (row['w0wa'][1][3], row['w0wa'][1][4]))
print("      the toy's curve at that w0 demands wa = %+.4f, i.e. off by %.3f."
      % (-3 * (2 + row['w0wa'][1][3]) * (1 + row['w0wa'][1][3]),
         row['w0wa'][1][4] + 3 * (2 + row['w0wa'][1][3]) * (1 + row['w0wa'][1][3])))
print("   toy w(z) projection, no phantom crossing by construction:")
ocb, h, Of = pm[0], pm[1], pm[2]
OL = 1.0 - (ocb + nu58.omnu_today + OM_RAD) / h ** 2 + Of
for z in (0.0, 0.3, 0.7, 1.0, 1.5, 2.3):
    a = 1.0 / (1 + z)
    rx = OL - Of * a ** 3
    print("      z=%4.1f  w_x = %+.4f   rho_x/rho_x0 = %.4f" % (z, -1 + Of * a ** 3 / rx,
                                                                rx / (OL - Of)))

hr("7b.  MECHANISM: dark-energy density history, best fits at Sum m_nu = 58.8 meV")
print("  rho_DE(z)/rho_DE(0).  Relaxing the Sum m_nu bound needs LESS dark energy in the")
print("  past than LCDM (so the extra nu density at z ~ 1-100 can be paid for);")
print("  w0waCDM does that with a phantom past, the toy does the opposite.")
print("     z      LCDM     w0waCDM   toy(Of>=0)  toy(Of any)")
for z in (0.0, 0.3, 0.7, 1.0, 1.5, 2.33, 5.0, 30.0):
    a = 1.0 / (1.0 + z)
    vals = []
    for m in MODELS:
        p = row[m]
        ocb, h, Of, w0, wa = p[1]
        OL = 1.0 - (ocb + nu58.omnu_today + OM_RAD) / h ** 2 + Of
        fde = a ** (-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - a))
        vals.append((OL * fde - Of * a ** 3) / (OL - Of))
    print("  %6.2f  %8.4f  %8.4f  %10.4f  %10.4f" % (z, vals[0], vals[1], vals[2],
                                                     vals[3]))
print("  effective w(z):")
print("     z      LCDM     w0waCDM   toy(Of>=0)  toy(Of any)")
for z in (0.0, 0.5, 1.0, 2.33):
    a = 1.0 / (1.0 + z)
    vals = []
    for m in MODELS:
        ocb, h, Of, w0, wa = row[m][1]
        OL = 1.0 - (ocb + nu58.omnu_today + OM_RAD) / h ** 2 + Of
        if m == 'w0wa':
            vals.append(w0 + wa * (1 - a))
        else:
            vals.append(-1.0 + Of * a ** 3 / (OL - Of * a ** 3))
    print("  %6.2f  %8.4f  %8.4f  %10.4f  %10.4f" % (z, vals[0], vals[1], vals[2],
                                                     vals[3]))

hr("7c.  THE ONE-PARAMETER OBSTRUCTION, MADE NUMERICAL (Sum m_nu = 58.8 meV)")
print("  The toy's past DE deficit saturates at |Of|/rho_x(1); the SAME Of fixes")
print("  1 + w0 = Of/rho_x(1).  To match w0waCDM's deficit at z = 2.33 the toy needs")
print("  Of < 0 with |Of| = deficit x rho_x(1) -- which forces w0 = -1 - deficit.")
_ocb, _h, _Of = row['mirror'][1][0], row['mirror'][1][1], row['mirror'][1][2]
_rx1 = 1.0 - (_ocb + nu58.omnu_today + OM_RAD) / _h ** 2
print("  rho_x(1) at the toy best fit = %.4f" % _rx1)
print("   target deficit   Of needed    implied w0    chi2 at that Of (Ocb,h refit)   Dchi2 vs toy best")
for deficit in (0.00, -0.05, 0.10, 0.20, 0.31):
    Of_t = -deficit * _rx1
    base_t = [_ocb, _h, Of_t, -1.0, 0.0]

    def f_t(x, _b=base_t):
        return chi2([x[0], x[1], _b[2], -1.0, 0.0], nu58)
    r_t = minimize(f_t, [_ocb, _h], method='Nelder-Mead', bounds=[BND[0], BND[1]],
                   options=dict(xatol=1e-8, fatol=1e-7, maxiter=5000))
    r_t = minimize(f_t, r_t.x, method='Powell', bounds=[BND[0], BND[1]],
                   options=dict(xtol=1e-9, ftol=1e-10))
    print("      %+.2f          %+.4f      %+.4f        %10.3f                    %+8.3f"
          % (deficit, Of_t, -1.0 - deficit, r_t.fun, r_t.fun - row['mirror'][0]))
print("  (row deficit = -0.05 is the toy's OWN best fit direction, Of > 0: a SURPLUS.)")
print("  w0waCDM's actual deficit at z = 2.33 is %.3f, and its chi2 is %.3f -- the toy"
      % (1.0 - 0.6920, row['w0wa'][0]))
print("  cannot reach it at any Of without paying the w0 penalty shown above.")

hr("8.  MACHINE-READABLE PROFILE")
print("Sum_meV  chi2_LCDM   chi2_w0wa   chi2_toyOf+   chi2_toyOf±"
      "    D_LCDM   D_w0wa   D_toy+   D_toy±")
for i, s in enumerate(SUMS):
    print("%7.1f %11.3f %11.3f %13.3f %12.3f %9.3f %8.3f %8.3f %8.3f"
          % (1000 * s, prof['lcdm'][i], prof['w0wa'][i], prof['mirror'][i],
             prof['toy2side'][i], res['lcdm']['dprof'][i], res['w0wa']['dprof'][i],
             res['mirror']['dprof'][i], res['toy2side']['dprof'][i]))
print("\nelapsed %.1f s" % (time.time() - T0))
