"""
Numerical controls for a prescribed time-symmetric response kernel.
This selected record retains the numerical calculations from September 10, 2026.
It compares retarded, advanced, symmetric and commutator kernels; computes net
work for compact pulses; samples de Sitter image separation; and contrasts the
response coefficient with an image-covariance fraction.

Scope: a commuting field covariance does not fix its interacting response.
Zero net work is a property of the time-symmetric kernel imposed here.
These controls do not derive a dynamical gravity theory or exclude all possible
fold implementations. Historical interpretations extending beyond that scope
have been removed; the numerical expressions and input values are retained.
See WORKING_CALCULATIONS.md for the limited role of this source in V3.
Run: python3 beyond/main/fold_dynamics/half_advanced.py
"""

import numpy as np

rng = np.random.default_rng(20260910)
LINE = "=" * 78


def head(t):
    print("\n" + LINE + "\n" + t + "\n" + LINE)


# ------------------------------------------------------- 1. G_ret = G_sym + (1/2) Delta
head("1.  G_ret = G_sym + (1/2) Delta.  All the dissipation is in Delta.")
r = 1.0                       # light-travel delay, c = 1
w = np.linspace(0.01, 8.0, 9)
Gret = np.exp(1j * w * r)     # FT of delta(tau - r)
Gadv = np.exp(-1j * w * r)    # FT of delta(tau + r)
Gsym = 0.5 * (Gret + Gadv)
Del = Gret - Gadv
print(f"  {'omega':>8s} {'Im Gtilde_ret':>16s} {'Im Gtilde_sym':>16s} {'Im[(1/2)Deltatilde]':>22s}")
for wi, a, s, d in zip(w, Gret, Gsym, Del):
    print(f"  {wi:8.3f} {a.imag:16.8f} {s.imag:16.2e} {(0.5*d).imag:22.8f}")
print(f"  max |Im Gtilde_sym| = {np.abs(Gsym.imag).max():.2e}    "
      f"max |Im Gtilde_ret - Im (1/2)Deltatilde| = {np.abs(Gret.imag - 0.5*Del.imag).max():.2e}")
# Historical interpretation omitted; numerical control retained.

# --------------------------------------------- 2. net work on a pair: zero for symmetric K
head("2.  Net work done on a source pair by the mutual field")
dt = 2.0e-4
t = np.arange(-40.0, 40.0, dt)


def pulse(t0, s, a=1.0):
    return a * np.exp(-0.5 * ((t - t0) / s) ** 2)


q1 = pulse(-1.3, 0.9, 1.0) + 0.4 * pulse(1.1, 0.5, 1.0)
q2 = pulse(0.6, 0.7, 0.8)
q1d = np.gradient(q1, dt)
q2d = np.gradient(q2, dt)
R = 2.3                                   # separation / light delay


def shift(f, tau):
    """f(t - tau) by spectral interpolation (periodic window, sources compactly supported)."""
    n = len(f)
    k = 2 * np.pi * np.fft.fftfreq(n, d=dt)
    return np.real(np.fft.ifft(np.fft.fft(f) * np.exp(-1j * k * tau)))


def work(kernel):
    """W = int dt [ q2dot(t) Phi1(t) + q1dot(t) Phi2(t) ],  Phi_i = (K * q_i)/(4 pi R)."""
    P1 = kernel(q1) / (4 * np.pi * R)
    P2 = kernel(q2) / (4 * np.pi * R)
    return np.sum(q2d * P1 + q1d * P2) * dt


K_ret = lambda f: shift(f, +R)                    # q(t - R)
K_adv = lambda f: shift(f, -R)                    # q(t + R)
K_sym = lambda f: 0.5 * (shift(f, +R) + shift(f, -R))
K_del = lambda f: (shift(f, +R) - shift(f, -R))
Wret, Wadv, Wsym, Wdel = work(K_ret), work(K_adv), work(K_sym), work(K_del)
print(f"  W(G_ret)       = {Wret:+.10e}")
print(f"  W(G_adv)       = {Wadv:+.10e}      (= -W(G_ret): dev {abs(Wret+Wadv):.2e})")
print(f"  W(G_sym)       = {Wsym:+.10e}      <-- ZERO to machine precision")
print(f"  W((1/2)Delta)  = {0.5*Wdel:+.10e}  (= W(G_ret): dev {abs(0.5*Wdel-Wret):.2e})")
scale = np.abs(np.sum(q2d * K_ret(q1)) * dt / (4 * np.pi * R))
print(f"  |W(G_sym)| / |W(G_ret)| = {abs(Wsym)/abs(Wret):.2e}")
# Historical interpretation omitted; numerical control retained.

# ------------------------------------------------------ 3. the near zone: only even powers
head("3.  The near zone: the half-advanced response has only EVEN powers of r/c")
# Historical interpretation omitted; numerical control retained.
print(f"  source q(t) = cos(Omega t + 0.6), sampled at t = 0 (a generic phase, so that the odd\n"
      f"  part of the response does not accidentally vanish):")
print(f"  {'r/lambda-bar = Omega r/c':>26s} {'|sym - static|/|static|':>26s} {'|ret - sym|/|static|':>24s}"
      f" {'odd/even':>10s}")
Om, ph = 1.0, 0.6
for rr in [1e-3, 1e-2, 1e-1, 0.5, 1.0]:
    q0 = np.cos(ph)
    sym = 0.5 * (np.cos(ph - Om * rr) + np.cos(ph + Om * rr))
    ret = np.cos(ph - Om * rr)
    ev, od = abs(sym - q0) / abs(q0), abs(ret - sym) / abs(q0)
    print(f"  {rr:26.4g} {ev:26.4e} {od:24.4e} {od/ev:10.1f}")
print("  (even part ~ (Omega r)^2/2, odd part ~ tan(0.6) Omega r: the odd/even ratio grows as 1/r)")
# Historical interpretation omitted; numerical control retained.

# ------------------------------------------------- 4. the image cannot be the absorber
head("4.  The image cannot serve as the Wheeler-Feynman absorber")


def X_static(t0, rad, n):
    s = np.sqrt(1.0 - rad * rad)
    return np.array([s * np.sinh(t0), s * np.cosh(t0), rad * n[0], rad * n[1], rad * n[2]])


def Zinv(P, Q):
    return -P[0] * Q[0] + P[1] * Q[1] + float(np.dot(P[2:], Q[2:]))


zmax = -1e9
for _ in range(200000):
    n1 = rng.normal(size=3); n1 /= np.linalg.norm(n1)
    n2 = rng.normal(size=3); n2 /= np.linalg.norm(n2)
    P = X_static(rng.uniform(-2.0, 2.0), rng.uniform(0, 0.995), n1)
    Q = X_static(rng.uniform(-2.0, 2.0), rng.uniform(0, 0.995), n2)
    zmax = max(zmax, Zinv(P, -Q))
print(f"  max Z(x,Ay) over 2x10^5 pairs in ONE static patch = {zmax:.10f}  (causal iff Z >= 1)")
# Historical interpretation omitted; numerical control retained.

# ------------------------------------------------------------- 5. the two numbers
head("5.  The two numbers that must not be conflated")
lH = 1.3725e26
sig = 1.0
img = np.sin(sig / (2 * lH)) ** 2
print(f"  advanced WEIGHT in the response  G_sym = 1/2(G_ret + G_adv):   exactly 0.5")
print(f"     -- a property of the GREEN FUNCTION, scale-free, the same at 1 m and at 1 Gpc")
print(f"  image FRACTION of the covariance 2[G_sym + G_img]:  sin^2(sigma/2l) = {img:.4e} at 1 m")
print(f"     -- a property of the STATE/COVARIANCE, running from 1.3e-53 to 1")
# Historical interpretation omitted; numerical control retained.

# ------------------------------------------------------------------ 6. Hulse-Taylor
head("6.  Comparison with the quoted binary-pulsar orbital-decay ratio")
obs, err = 0.9983, 0.0016
print(f"  Weisberg & Huang, arXiv:1606.02744 (fetched), verbatim: 'the ratio of observed orbital")
print(f"  period decrease due to gravitational wave damping (corrected by a kinematic term) to the")
print(f"  general relativistic prediction, is 0.9983 pm 0.0016'.")
print(f"  Assumed time-symmetric response with no dissipative completion:")
print(f"  comparison ratio = 0 for the prescribed zero-work response.")
print(f"  Deviation: ({obs:.4f} - 0)/{err} = {obs/err:.0f} sigma.")
# Historical interpretation omitted; numerical control retained.

head("Scope")
# Historical interpretation omitted; numerical control retained.

print("These controls concern the imposed symmetric kernel; they do not derive the response from a commuting covariance.")
