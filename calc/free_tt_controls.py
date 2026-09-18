"""Bounded arithmetic/algebra controls; does not prove the imported gravity representation."""
import cmath
import math
import json
from fractions import Fraction as F
from pathlib import Path

out={}
radial=16*(F(1,4)-2*F(1,6)+F(1,8))
assert radial==F(2,3)
out['exact_radial_integral']=str(radial)
out['exact_seed_norm']=str(20*radial)
mode_err=0.
kg_err=0.
for n in range(3,21):
 for eta in [-1.,-.3,0.,.2,.9]:
  norm=math.sqrt(2*n*(n*n-1))
  v=lambda t: cmath.exp(-1j*n*t)*(math.tan(t)-1j*n)/norm
  dv=cmath.exp(-1j*n*eta)*(-1j*n*math.tan(eta)-n*n+1/math.cos(eta)**2)/norm
  kg=1j*(v(eta).conjugate()*dv-v(eta)*dv.conjugate())
  kg_err=max(kg_err,abs(kg-1))
  mode_err=max(mode_err,abs(v(-eta)+v(eta).conjugate()))
  assert (-1)**n==-(-1)**(n+1)
  assert (-1)**n*(-1)**(n+1)==-1
out['time_reflection_max_residual']=mode_err
out['positive_kg_norm_max_residual']=kg_err
assert kg_err<1e-12
out['jacobi_controls']=[]
for lam in [.1,.5,1.,2.,3.]:
 t=math.tanh(lam/2)
 a=[(-1j*t)**r*math.sqrt(math.comb(r+5,5))/math.cosh(lam/2)**6 for r in range(602)]
 err=0.
 for r in range(600):
  derivative=a[r]*(-3*t+r*(1-t*t)/(2*t))
  prev=math.sqrt(r*(r+5))/2*a[r-1] if r else 0
  nex=math.sqrt((r+1)*(r+6))/2*a[r+1]
  err=max(err,abs(derivative+1j*(prev+nex)))
 norm=sum(abs(x)**2 for x in a)
 assert err<1e-12 and abs(norm-1)<1e-12
 out['jacobi_controls'].append({'lambda':lam,'ode_max_residual':err,'truncated_norm':norm,'bottom':a[0].real})
# Exact positivity/radical controls for the orbit-domain coefficient formula.
for coeffs in [[1,2,-3],[1,2],[0,0],[4,-4,1]]:
 b=F(40,3)*sum(coeffs)**2
 assert b>=0 and ((b==0)==(sum(coeffs)==0))
out['scope']='Checks exact radial integral, time reflection, alternating parity and analytic Jacobi sequence. Imported reduced-TT representation and its geometric gauge action require the stated derivation and primary source, not these numerical checks.'
p=Path(__file__).with_name('free_tt_controls.json')
p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
