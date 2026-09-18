"""Runs the audited tortoise pipeline once at (AA, OM, LAMBDA) and prints |Z_out/Z_in|^2."""
import os, mpmath as mp
from pathlib import Path
src = (Path(__file__).resolve().parents[1] / 'kerr_teukolsky/teukolsky_zin_tortoise.py').read_text(encoding='utf-8')
cut = src.find('print("\\nCONVERGENCE FIRST')
assert cut > 0, 'tortoise convergence marker missing'
head = src[:cut]
b0 = src.find('def basis(sign, nterms, rfit):'); b1 = src.find('TZIN  =')
assert 0 < b0 < b1, 'tortoise basis markers missing'
head = head.replace("M,a,om,m,s = mp.mpf(1), mp.mpf('0.9'), mp.mpf('0.5'), 2, -2",
                    "M,a,om,m,s = mp.mpf(1), mp.mpf(os.environ['AA']), mp.mpf(os.environ['OM']), 2, -2")
head = head.replace("lam = mp.mpf('1.048373382264869')", "lam = mp.mpf(os.environ['LAMBDA'])")
for bad in ('print("TORTOISE-COORDINATE INTEGRATION (regular at the horizon by construction)")',
            'print(f"  r_+ = {mp.nstr(rp,12)}  kappa = {mp.nstr(kap,12)}  k = {mp.nstr(kH,12)}")'):
    head = head.replace(bad, '')
g = {'__name__': 'k', 'os': os, 'mp': mp}
exec(head + src[b0:b1], g)
run, basis = g['run'], g['basis']
vals = []
for umax in (60, 70):
    R, dR, rend = run(-25, umax, 8000)
    Fo, Fi = basis(+1, 5, rend), basis(-1, 5, rend)
    A = mp.matrix([[Fo(rend, 0), Fi(rend, 0)], [Fo(rend, 1), Fi(rend, 1)]])
    Z = mp.lu_solve(A, mp.matrix([R, dR]))
    vals.append(abs(Z[0] / Z[1])**2)
import sys
print(f"# umax 60 vs 70 relative change: {float(abs(vals[1]-vals[0])/abs(vals[1])):.3e}", file=sys.stderr)
print(mp.nstr(vals[-1], 14))
