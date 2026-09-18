"""
How much does the Teukolsky barrier attenuate anything generated at the seam?

Section 7 says the seam reflectivity is "observable in principle and unmeasured in practice until the
Teukolsky barrier, the excitation residue, mode mixing and the detector response are composed in. That
calculation is not done here." The first of those four is now doable, because the flux conversion is
calibrated -- against Regge-Wheeler at a = 0 across five frequencies and against |R|^2 = 1 at the
superradiant threshold at a = 0.9 to 3.6e-5.

An echo born near the horizon has to climb out through the barrier, and by reciprocity that transmission
equals the transmission inward from infinity, Gamma = 1 - |R|^2. So Gamma is the factor by which the
barrier suppresses echo ENERGY relative to whatever the seam reflects.

The thing to notice before computing: for a = 0.9 the l = m = 2 superradiant threshold is
m Omega_H = 0.62679, and the fundamental ringdown frequency is Re(M omega_220) ~ 0.67. The ringdown sits
just ABOVE the threshold, i.e. in the region where Gamma has only just turned positive -- so the barrier is
close to opaque exactly where the ringdown lives.
"""
import os, subprocess, sys, numpy as np
from pathlib import Path
from sympy.physics.wigner import wigner_3j
from sympy import Integer

AA, MM, SS, LL = 0.9, 2, -2, 2
rp = 1.0 + np.sqrt(1.0 - AA**2)
OmH = AA / (2.0 * rp)
TH = MM * OmH

_c = {}
def cel(lp, l):
    if abs(lp - l) > 1 or lp < max(abs(MM), abs(SS)) or l < max(abs(MM), abs(SS)): return 0.0
    k = (lp, l)
    if k not in _c:
        pref = (-1)**(MM + SS) * np.sqrt(float((2*l+1)*(2*lp+1)))
        _c[k] = pref * float(wigner_3j(Integer(l), Integer(1), Integer(lp), Integer(MM), Integer(0), Integer(-MM))) \
                     * float(wigner_3j(Integer(l), Integer(1), Integer(lp), Integer(-SS), Integer(0), Integer(SS)))
    return _c[k]

def lam_of(omega, lmax=40):
    c = AA * omega
    ls = list(range(max(abs(MM), abs(SS)), lmax + 1))
    X = np.array([[cel(lp, l) for l in ls] for lp in ls])
    D = np.diag([l*(l+1) - SS*(SS+1) for l in ls]).astype(float)
    ev = np.linalg.eigvals(D - c**2 * (X @ X) + 2*c*SS * X)
    A0 = LL*(LL+1) - SS*(SS+1)
    A = ev[np.argmin(np.abs(ev - A0))].real
    return A + c**2 - 2*MM*c

def Csq(lam, omega):
    amw, a2w2 = AA*MM*omega, AA**2*omega**2
    return (((lam+2)**2 + 4*amw - 4*a2w2) * (lam**2 + 36*amw - 36*a2w2)
            + (2*lam+3)*(96*a2w2 - 48*amw) + 144*omega**2*(1-AA**2))

def rho(omega, lam):
    env = dict(os.environ, OM=repr(float(omega)), AA=repr(AA), LAMBDA=repr(float(lam)))
    o = subprocess.run([sys.executable, '-u', str(Path(__file__).resolve().with_name('_kerr_runner.py'))],
                       capture_output=True, text=True, env=env, cwd=Path(__file__).resolve().parent)
    if o.returncode != 0: raise RuntimeError(o.stderr[-600:])
    return float(o.stdout.strip().splitlines()[-1])

print(f"a = {AA}   superradiant threshold m*Omega_H = {TH:.6f}")
print(f"\n{'omega':>8} {'lambda':>12} {'|R|^2':>14} {'Gamma = 1-|R|^2':>18} {'note':>22}")
for om in (0.58, 0.62, 0.6268, 0.65, 0.67, 0.70, 0.75, 0.85):
    lam = lam_of(om)
    r = rho(om, lam) * Csq(lam, om) / (256.0 * om**8)
    g = 1.0 - r
    note = "threshold" if abs(om - TH) < 2e-3 else ("superradiant" if om < TH else
           ("ringdown band" if 0.65 <= om <= 0.70 else ""))
    print(f"{om:8.4f} {lam:12.7f} {r:14.8f} {g:18.8f} {note:>22}")
print("""
   Gamma is the energy transmission of the barrier, and by reciprocity the factor by which anything
   generated at the seam is attenuated on its way out. Where Gamma is small the barrier is close to opaque
   and an echo is suppressed by that factor in energy -- which is a quantitative statement section 7
   currently does not make.""")
