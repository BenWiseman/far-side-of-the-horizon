"""
Tortoise-coordinate Teukolsky integration and asymptotic matching.
The equation uses u = r_* so its coefficients remain regular at the horizon.
The retained convergence and basis-matching checks use outward integration,
without Abel weighting, a Jost recurrence, or inward propagation.
The fixed comparison amplitudes below are historical comparison inputs only;
the barrier driver extracts run() and basis() and does not use those inputs.
"""
import mpmath as mp
mp.mp.dps = 40

M,a,om,m,s = mp.mpf(1), mp.mpf('0.9'), mp.mpf('0.5'), 2, -2
lam = mp.mpf('1.048373382264869')
rp = M+mp.sqrt(M**2-a**2); rm = M-mp.sqrt(M**2-a**2)
OmH = a/(2*M*rp); kH = om-m*OmH
kap = (rp-rm)/(2*(rp**2+a**2))

Delta = lambda r: (r-rp)*(r-rm)
dDelta= lambda r: 2*r-2*M
Kf    = lambda r: (r**2+a**2)*om - a*m
def rstar(r):
    return r + (2*M*rp/(rp-rm))*mp.log((r-rp)/(2*M)) - (2*M*rm/(rp-rm))*mp.log((r-rm)/(2*M))
def r_launch(u0):
    """Invert r_*(r) near the horizon analytically: r_* -> C + (1/2kappa) ln(r-r_+).
    Used ONCE for the launch; thereafter r is integrated alongside the system via dr/du."""
    A = 2*M*rp/(rp-rm); B = 2*M*rm/(rp-rm)
    C = rp - A*mp.log(2*M) - B*mp.log((rp-rm)/(2*M))
    x = mp.e**((mp.mpf(u0) - C)/A)
    # one Newton polish on the exact relation
    for _ in range(60):
        r = rp + x
        F = rstar(r) - u0
        dF = (r**2+a**2)/Delta(r)
        x = x - F/dF
        if x <= 0: x = mp.mpf('1e-30')
    return rp + x

def coeffs(r):
    D=Delta(r); Dp=dDelta(r); A2=r**2+a**2; K=Kf(r)
    f  = D/A2
    fp = Dp/A2 - D*2*r/A2**2
    c1 = fp - (s+1)*Dp/A2
    c0 = -((K**2 - 2j*s*(r-M)*K)/A2**2 + (4j*s*om*r - lam)*D/A2**2)
    return c1, c0

print("="*96)
print("TORTOISE-COORDINATE INTEGRATION (regular at the horizon by construction)")
print(f"  r_+ = {mp.nstr(rp,12)}  kappa = {mp.nstr(kap,12)}  k = {mp.nstr(kH,12)}")

def run(u0, umax, nsteps):
    """State is (R, dR/du, r); r is integrated via dr/du = Delta/(r^2+a^2), so no root-finding."""
    r = r_launch(u0)
    D = Delta(r); A2 = r**2+a**2
    R  = D**(-s) * mp.e**(-1j*kH*mp.mpf(u0))
    dR = (-s*dDelta(r)/A2 - 1j*kH) * R
    h  = (mp.mpf(umax)-mp.mpf(u0))/nsteps
    u  = mp.mpf(u0); y = mp.matrix([R, dR, r])
    def f(y):
        rr = y[2]; c1, c0 = coeffs(rr)
        return mp.matrix([y[1], c1*y[1] + c0*y[0], Delta(rr)/(rr**2+a**2)])
    for _ in range(nsteps):
        k1=f(y); k2=f(y+h/2*k1); k3=f(y+h/2*k2); k4=f(y+h*k3)
        y = y + h/6*(k1+2*k2+2*k3+k4); u = u+h
    return y[0], y[1], y[2]

print("\nCONVERGENCE FIRST — this is what the last attempt failed.")
print(f"  {'nsteps':>8}{'|R(umax)|':>26}{'arg R':>18}")
prev=None
for n in (2000,4000,8000):
    R,dR,rend = run(-25, 60, n)
    print(f"  {n:>8}{mp.nstr(abs(R),16):>26}{mp.nstr(mp.arg(R),14):>18}")
    if prev is not None:
        print(f"           change vs previous: |dR| = {mp.nstr(abs(R-prev),6)}  rel = {mp.nstr(abs(R-prev)/abs(R),6)}")
    prev=R
print(f"\n  r at umax: {mp.nstr(rend,12)}")

# ---------------------------------------------------------------- asymptotic extraction
print("\n" + "="*96)
print("ASYMPTOTIC MATCH.  R -> Zout r^3 e^{i om u} (1+...) + Zin r^-1 e^{-i om u} (1+...)")
print("Series coefficients fixed from the ODE by collocation, not taken from anyone.")

def basis(sign, nterms, rfit):
    pw = 3 if sign>0 else -1
    def F(r, cs, d=0):
        S  = 1 + sum(cs[n]*r**(-(n+1)) for n in range(len(cs)))
        Sp = sum(-(n+1)*cs[n]*r**(-(n+2)) for n in range(len(cs)))
        u  = rstar(r); ph = mp.e**(sign*1j*om*u)
        g  = r**pw*S
        gp = pw*r**(pw-1)*S + r**pw*Sp          # d/dr of r^pw S
        val = ph*g
        if d==0: return val
        drdu = Delta(r)/(r**2+a**2)
        dval_dr = ph*(sign*1j*om*(r**2+a**2)/Delta(r)*g + gp)   # du/dr = (r^2+a^2)/Delta
        if d==1: return dval_dr*drdu                             # dF/du
        raise ValueError
    def resid(r, cs):
        # residual of the tortoise-form ODE
        h=mp.mpf('1e-12')*r
        F0=F(r,cs,0); Fp=F(r,cs,1)
        # d2F/du2 = (dr/du) * d/dr (dF/du);  the earlier version multiplied by a factor and its
        # inverse, which cancelled, leaving dF'/dr and making the collocation coefficients meaningless.
        Fpp=(Delta(r)/(r**2+a**2)) * (F(r+h,cs,1)-F(r-h,cs,1))/(2*h)
        c1,c0=coeffs(r)
        return Fpp - c1*Fp - c0*F0
    pts=[mp.mpf(rfit)*(1+mp.mpf(j)/10) for j in range(1,nterms+1)]
    zero=[mp.mpc(0)]*nterms; r0=[resid(x,zero) for x in pts]
    A=mp.matrix(nterms,nterms); b=mp.matrix(nterms,1)
    for j in range(nterms):
        for n in range(nterms):
            e=[mp.mpc(0)]*nterms; e[n]=mp.mpf(1)
            A[j,n]=resid(pts[j],e)-r0[j]
        b[j]=-r0[j]
    cs=mp.lu_solve(A,b); cs=[cs[i] for i in range(nterms)]
    return (lambda r,d=0: F(r,cs,d))

TZIN  = mp.mpc('0.909686513278','15.899645119647')
TZOUT = mp.mpc('-5.98277965893','-53.9412826073')
print(f"  Reference amplitudes: |Zin| = {mp.nstr(abs(TZIN),12)}  |Zout| = {mp.nstr(abs(TZOUT),12)}  "
      f"|Zin/Zout| = {mp.nstr(abs(TZIN/TZOUT),12)}")
print(f"\n  {'umax':>6}{'|Zin/Zout|  (mine)':>26}{'vs reference ratio':>20}")
for umax in (50, 60, 70):
    R,dR,rend = run(-25, umax, 8000)
    Fo=basis(+1,5,rend); Fi=basis(-1,5,rend)
    A=mp.matrix([[Fo(rend,0), Fi(rend,0)],[Fo(rend,1), Fi(rend,1)]])
    Z=mp.lu_solve(A, mp.matrix([R,dR]))
    zo,zi=Z[0],Z[1]
    rat=abs(zi/zo)
    print(f"  {umax:>6}{mp.nstr(rat,14):>26}{mp.nstr(rat/abs(TZIN/TZOUT),10):>20}")
