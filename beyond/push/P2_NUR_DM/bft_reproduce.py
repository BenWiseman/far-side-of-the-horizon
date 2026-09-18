#!/usr/bin/env python
"""
Adopted Boyle-Finn-Turok abundance calculation and occupation-family controls.
The half-angle occupation and radiation-era inputs reproduce the integral and
abundance calibration in arXiv:1803.08930, equations (125)-(135).

This calculation adopts the BFT state prescription. Antipodal or CPT invariance
alone does not determine this prescription or its abundance. The comparison with
the in-state and the parameterised occupation family tests the dependence on the
chosen state. The code does not derive a fold-to-BFT state equivalence.

Conventions: c = hbar = k_B = 1, GeV units, flat FRW conformal frame,
comoving momentum p and present scale factor a_0 = 1. Extra printed digits reflect
quadrature precision for fixed inputs, not physical precision of the mass.
"""
import numpy as np
import mpmath as mp

mp.mp.dps = 40

# ---------------------------------------------------------------- BFT inputs
# 1803.08930 eq. (110)
MU_HAT   = mp.mpf('5.966e18')      # GeV, = (4 pi G / 3)^{-1/2}
G_STAR   = mp.mpf('106.75')        # BFT eq. (131) text: SM without the nu_R
RHO_DM_0 = mp.mpf('9.7e-48')       # GeV^4, BFT eq. (134)
S_0      = mp.mpf('2.3e-38')       # GeV^3, BFT text below eq. (133)

# ------------------------------------------------------------ the I integral
# BFT eq. (128):  I = (1/2 pi^2) int_0^inf dx x^2 [1 - sqrt(1 - e^{-x^2})]
# Derivation check: n_dm = sum_{h=1,2} int d^3p/(2pi)^3 |beta_+|^2, with
#   |beta_+|^2 = sin^2(lam/2) = (1 - cos lam)/2 = (1 - sqrt(1-|beta|^2))/2,
#   |beta|^2 = exp(-pi p^2 / gamma),  x^2 = pi p^2 / gamma.
# sum_h int d^3p/(2pi)^3 f = (1/pi^2) int dp p^2 f   ->   n = (gamma/pi)^{3/2} I. OK.

def occ_a(x2):
    """(a) BFT half-angle CPT vacuum: sin^2(lam/2)."""
    return (1 - mp.sqrt(1 - mp.e**(-x2))) / 2

def occ_b(x2):
    """(b) the 'in' vacuum |0_->: |beta|^2 = sin^2(lam) = e^{-x^2}."""
    return mp.e**(-x2)

def occ_eta(x2, eta):
    """the CPT-invariant eta-family: cos^2(eta) sin^2(lam/2) + sin^2(eta) cos^2(lam/2).
       This is the supplied occupation family; eta=0 reproduces (a)."""
    s2 = (1 - mp.sqrt(1 - mp.e**(-x2))) / 2          # sin^2(lam/2)
    c2 = (1 + mp.sqrt(1 - mp.e**(-x2))) / 2          # cos^2(lam/2)
    return mp.cos(eta)**2 * s2 + mp.sin(eta)**2 * c2

def I_of(occ):
    """I = (1/2 pi^2) * 2 * int_0^inf dx x^2 * occ(x^2)  ... careful with the 2.

    n = (1/pi^2) int dp p^2 occ  = (gamma/pi)^{3/2} (1/pi^2) int dx x^2 occ.
    BFT define I so that n = (gamma/pi)^{3/2} I, and their occ_a = (1-sqrt(..))/2,
    so I = (1/pi^2) int dx x^2 occ = (1/2 pi^2) int dx x^2 [1-sqrt(1-e^{-x^2})]. OK.
    """
    f = lambda x: x**2 * occ(x**2)
    return mp.quad(f, [0, mp.inf]) / mp.pi**2

I_bft = I_of(occ_a)
I_in  = I_of(occ_b)

# --------------------------------------------------------- M_1 from I (eq.132-135)
# Y_dm = (3 I / 2 pi^2) (15/g*)^{1/4} (M_1/mu_hat)^{3/2}          [BFT eq. 132]
# rho_dm^(0) = M_1 Y_dm s^(0)                                     [BFT eq. 133]
#  => M_1^{5/2} = rho_dm^(0) mu_hat^{3/2} / [ s^(0) (3I/2pi^2) (15/g*)^{1/4} ]
def M1_from_I(I):
    K = (3*I/(2*mp.pi**2)) * (15/G_STAR)**mp.mpf('0.25')
    return (RHO_DM_0 * MU_HAT**mp.mpf('1.5') / (S_0 * K))**mp.mpf('0.4')

# also re-derive eq. (132) from eqs. (112,122,127,131) to check the prefactor
def check_eq132():
    #  n = (gamma/pi)^{3/2} I ; gamma = (M/muhat)(2 rho_1)^{1/2}
    #  Y = n/s = I pi^{-3/2} (M/muhat)^{3/2} (2 rho_1)^{3/4}/s
    #  (2 rho)^{3/4}/s = (3/2)(15/(g* pi^2))^{1/4}                [eq. 131]
    #  => Y = (3I/2) pi^{-3/2} pi^{-1/2} (15/g*)^{1/4} (M/muhat)^{3/2}
    #       = (3I/(2 pi^2)) (15/g*)^{1/4} (M/muhat)^{3/2}         [eq. 132]  OK
    lhs = mp.mpf(1)/mp.pi**mp.mpf('1.5') * (mp.mpf(3)/2) * (1/mp.pi**2)**mp.mpf('0.25')
    rhs = (mp.mpf(3)/2) / mp.pi**2
    return lhs, rhs, abs(lhs-rhs)

# also verify eq. (131) itself
def check_eq131():
    # rho = (pi^2/30) g* T^4 ; s = (2 pi^2/45) g* T^3
    # (2 rho)^{3/4}/s = (2 pi^2 g*/30)^{3/4} T^3 / ((2 pi^2/45) g* T^3)
    g = G_STAR
    lhs = (2*mp.pi**2*g/30)**mp.mpf('0.75') / ((2*mp.pi**2/45)*g)
    rhs = mp.mpf(3)/2 * (15/(g*mp.pi**2))**mp.mpf('0.25')
    return lhs, rhs, abs(lhs-rhs)/rhs

if __name__ == "__main__":
    print("="*74)
    print("PART 1 -- reproduction of BFT 1803.08930 eqs. (128), (131), (132), (135)")
    print("="*74)
    l131 = check_eq131(); print(f"eq.(131) LHS={float(l131[0]):.10f} RHS={float(l131[1]):.10f} relerr={float(l131[2]):.2e}")
    l132 = check_eq132(); print(f"eq.(132) prefactor LHS={float(l132[0]):.10f} RHS={float(l132[1]):.10f} |diff|={float(l132[2]):.2e}")
    print()
    print(f"I  (eq.128, 40-digit quad)           = {mp.nstr(I_bft, 12)}")
    print(f"   BFT quoted                        = 0.01276")
    print(f"   relative difference               = {float(abs(I_bft-mp.mpf('0.01276'))/mp.mpf('0.01276')):.3e}")
    print()
    M1 = M1_from_I(I_bft)
    print(f"M_1 (eq.135) from I, g*={float(G_STAR)}, mu_hat={mp.nstr(MU_HAT,4)} GeV,")
    print(f"     rho_dm^0={mp.nstr(RHO_DM_0,3)} GeV^4, s^0={mp.nstr(S_0,3)} GeV^3")
    print(f"  => M_1 = {mp.nstr(M1, 6)} GeV       (BFT quote 4.8e8 GeV)")
    print(f"     ratio to BFT quote               = {float(M1/mp.mpf('4.8e8')):.4f}")
    print()
    print("="*74)
    print("STATE DEPENDENCE -- I and M_1 for the supplied occupation functions")
    print("="*74)
    rows = [
        ("(a) BFT half-angle CPT vacuum |0_0>", I_bft),
        ("(b) 'in' vacuum |0_->  (|beta|^2)   ", I_in),
    ]
    for name, I in rows:
        print(f"{name}: I = {mp.nstr(I,8):>14}   I/I_a = {float(I/I_bft):8.5f}"
              f"   M_1 = {mp.nstr(M1_from_I(I),5):>12} GeV   M1/M1_a = {float(M1_from_I(I)/M1):.5f}")
    print("Geometric antipodal/CPT invariance alone does not select I_a.")
    print("The quoted abundance mass adopts the BFT half-angle state and its production inputs.")
    print()
    print("closed form for (b):  I_in = (1/pi^2) int x^2 e^{-x^2} dx = 1/(4 pi^{3/2})")
    print(f"   numeric {mp.nstr(I_in,10)}   closed form {mp.nstr(1/(4*mp.pi**mp.mpf('1.5')),10)}")
    print()
    print("-"*74)
    print("the eta-family (CPT-invariant; eta(k) odd in k, |eta| = h(|k|)).")
    print("A CONSTANT h is non-Hadamard: n(p) -> sin^2(h) as p->inf, so")
    print("  int dx x^2 n  diverges like (1/3) sin^2(h) X^3.  n_dm is UV-divergent.")
    print("  => the Hadamard/adiabatic condition is exactly what bounds the family.")
    print("Take instead the Hadamard-admissible one-parameter family")
    print("  h(p) = h_0 exp(-x^2/2),   x^2 = pi p^2/gamma   (Gaussian, so Hadamard):")
    print("-"*74)
    print(f"{'h_0/pi':>8} {'I(h_0)':>16} {'I/I_a':>10} {'M_1 [GeV]':>14} {'M1/M1_a':>10}")
    for frac in [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]:
        h0 = frac*mp.pi
        occ = lambda x2, H=h0: occ_eta(x2, H*mp.e**(-x2/2))
        Ie = I_of(occ)
        print(f"{frac:8.2f} {mp.nstr(Ie,8):>16} {float(Ie/I_bft):10.4f}"
              f" {mp.nstr(M1_from_I(Ie),5):>14} {float(M1_from_I(Ie)/M1):10.4f}")
    print()
    print("Within the family, n_eta(p) - n_0(p) = sin^2(eta) cos(lam) >= 0 pointwise")
    print("(cos lam = sqrt(1-e^{-x^2}) > 0), so eta=0 minimises the particle number")
    print("AND the energy in BOTH asymptotic regions simultaneously.  BFT's stated")
    print("selection criterion (1803.08928, after eq. 8) is therefore consistent and")
    print("eta=0 minimises this supplied occupation family. A nonzero occupation change gives a")
    print("LARGER I, hence a SMALLER M_1: 4.8e8 GeV is an UPPER bound on M_1 within")
    print("the CPT family (at fixed radiation-era production).")
