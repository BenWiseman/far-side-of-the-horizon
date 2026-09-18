"""Mirror-repulsion DE vs LCDM vs w0waCDM on DESI DR2 BAO + Pantheon+ SN + Planck-anchored priors.
Priors (Planck 2018 base-LCDM, Table 2 values; approximate compressed-CMB use):
  omega_m = Omega_m h^2 = 0.1430 +- 0.0011 ;  100 theta_* = 1.04109 +- 0.00030
  r_d from the standard fitting formula r_d = 147.05 (om/0.1432)^-0.23 (ob/0.02236)^-0.13 Mpc (ob fixed 0.02236);
  r_s(z*) = 0.9819 r_d (fixed ratio, same for all models -> cancels in comparisons).
Model: E^2 = Om a^-3 + Or a^-4 + OL f_DE(a) - Of a^3, flat, OL = 1-Om-Or+Of.
Parameters: LCDM (Om,h) ; w0wa (Om,h,w0,wa) ; mirror (Om,h,Of).
"""
import sys, numpy as np
from pathlib import Path
from scipy.optimize import minimize
from scipy.integrate import quad, solve_ivp
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import desi_dr2_geometry as bt
from pantheon_data import pantheon_files
SN_TABLE, SN_COVARIANCE = pantheon_files()
c=299792.458
# --- BAO
d_bao,C_bao,meta=bt._desi_vectors(); Ci_bao=np.linalg.inv(C_bao)
# --- SN (Pantheon+, Hubble-flow z>0.01, no SH0ES calibrators)
rows=np.genfromtxt(SN_TABLE,names=True,dtype=None,encoding=None)
N=int(open(SN_COVARIANCE).readline()); cov=np.loadtxt(SN_COVARIANCE,skiprows=1).reshape(N,N)
sel=(rows['zHD']>0.01)&(rows['IS_CALIBRATOR']==0)
zsn=rows['zHD'][sel]; zhel=rows['zHEL'][sel]; mb=rows['m_b_corr'][sel]; Csn=cov[np.ix_(sel,sel)]; Ci_sn=np.linalg.inv(Csn); one=np.ones(len(zsn))
print(f"SN used: {sel.sum()} of {N}")
ob=0.02236; zstar=1089.9
def E2(a,Om,h,Of,w0,wa):
    Or=2.469e-5/h**2*(1+0.2271*3.044); OL=1-Om-Or+Of
    f=a**(-3*(1+w0+wa))*np.exp(-3*wa*(1-a))
    return Om*a**-3+Or*a**-4+OL*f-Of*a**3
def DM(z,p):  # Mpc
    Om,h,Of,w0,wa=p
    return c/(100*h)*quad(lambda zz: 1/np.sqrt(max(E2(1/(1+zz),Om,h,Of,w0,wa),1e-14)),0,z,limit=400)[0]
def chi2(p):
    Om,h,Of,w0,wa=p
    if not(0.1<Om<0.6 and 0.5<h<0.9 and 0<=Of<0.6 and -2.5<w0<0 and -4<wa<3): return 1e9
    if E2(1.0,Om,h,Of,w0,wa)<=0: return 1e9
    om=Om*h*h; rd=147.05*(om/0.1432)**-0.23*(ob/0.02236)**-0.13
    # BAO
    th=[]
    for (z,kind) in meta:
        dm=DM(z,p); dh=c/(100*h)/np.sqrt(E2(1/(1+z),Om,h,Of,w0,wa))
        th+=[(z*dm*dm*dh)**(1/3)/rd] if kind=='DV' else [dm/rd,dh/rd]
    r=d_bao-np.array(th); x2=r@Ci_bao@r
    # SN (marginalize M analytically)
    dl=np.array([ (1+zh)*DM(z,p) for z,zh in zip(zsn,zhel)])
    mu=5*np.log10(dl)+25; r=mb-mu
    A=r@Ci_sn@r; B=r@Ci_sn@one; Cc=one@Ci_sn@one; x2+=A-B*B/Cc
    # priors
    x2+=((om-0.1430)/0.0011)**2
    th_star=100*0.9819*rd/DM(zstar,p); x2+=((th_star-1.04109)/0.00030)**2
    return float(x2)
def fit(model):
    if model=='lcdm':   p0=[0.31,0.68,0,-1,0]; free=[0,1]
    if model=='w0wa':   p0=[0.31,0.68,0,-0.8,-0.7]; free=[0,1,3,4]
    if model=='mirror': p0=[0.31,0.68,0.15,-1,0]; free=[0,1,2]
    def f(x):
        p=list(p0); 
        for i,j in enumerate(free): p[j]=x[i]
        return chi2(p)
    best=None
    for t in range(4):
        x0=np.array([p0[j] for j in free])*(1+0.05*np.random.default_rng(t).standard_normal(len(free)))
        r=minimize(f,x0,method='Nelder-Mead',options={'xatol':1e-5,'fatol':1e-4,'maxiter':3000})
        if best is None or r.fun<best.fun: best=r
    p=list(p0)
    for i,j in enumerate(free): p[j]=best.x[i]
    return best.fun,p
out={}
for m in ('lcdm','w0wa','mirror'):
    x2,p=fit(m); out[m]=(x2,p); print(f"{m:7s} chi2={x2:9.3f}  Om={p[0]:.4f} h={p[1]:.4f} Of={p[2]:.4f} w0={p[3]:.3f} wa={p[4]:.3f}")
print("\nDelta chi2 vs LCDM:  w0wa %+.2f (2 extra params)   mirror %+.2f (1 extra param)" % (out['w0wa'][0]-out['lcdm'][0], out['mirror'][0]-out['lcdm'][0]))
# mirror diagnostics
Om,h,Of,_,_=out['mirror'][1]
Or = 2.469e-5/h**2*(1+0.2271*3.044)
OL = 1-Om-Or+Of  # match E2; correct the historical diagnostic-only sign error
w=lambda a:-1+Of*a**3/(OL-Of*a**3)
print(f"mirror: OL={OL:.3f} Of={Of:.3f}  w0={w(1):.3f}  wa=-dw/da={-(w(1.0001)-w(0.9999))/2e-4:.3f}  turnaround a={(OL/Of)**(1/3) if Of>0 else np.inf:.3f}")
# age & growth for LCDM vs mirror
def age(p):
    Om,h,Of,w0,wa=p; return 977.8/(100*h)*quad(lambda a: 1/(a*np.sqrt(E2(a,Om,h,Of,w0,wa))),1e-8,1)[0]
def growth(p):  # linear growth delta'' + (3/a + E'/E) delta' - 1.5 Om/(a^5 E^2) delta = 0 in ln a; standard Poisson
    Om,h,Of,w0,wa=p
    def rhs(lna,y):
        a=np.exp(lna); e2=E2(a,Om,h,Of,w0,wa); de2=(E2(a*1.0001,Om,h,Of,w0,wa)-E2(a*0.9999,Om,h,Of,w0,wa))/(2e-4*a)
        D,Dp=y; return [Dp, -(2+0.5*a*de2/e2)*Dp+1.5*Om/(a**3*e2)*D]
    s=solve_ivp(rhs,[np.log(1e-3),0],[1e-3,1e-3],rtol=1e-8,atol=1e-10); return s.y[0,-1]
print(f"age: LCDM {age(out['lcdm'][1]):.2f} Gyr, mirror {age(out['mirror'][1]):.2f} Gyr")
gL=growth(out['lcdm'][1]); gM=growth(out['mirror'][1]); print(f"linear growth D(z=0) ratio mirror/LCDM = {gM/gL:.4f}  (sigma8 scales with this; S8 also by sqrt(Om) ratio {np.sqrt(Om/out['lcdm'][1][0]):.4f})")
