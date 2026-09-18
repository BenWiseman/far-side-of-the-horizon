"""
Turning section 7's denominator argument into a number.

Section 7 argues that composing a seam with the barrier outside it replaces the seam's own denominator, so
a fitted ringdown damping is not the seam's damping. Eliminating the internal port of a two-port barrier,

    S_eff = R_B + T'_B S_s (1 - R'_B S_s)^{-1} T_B,

and the poles of S_eff sit where 1 = R'_B S_s, not where S_s has its own pole. The physical content is a
cavity: a wave bouncing between the seam and the inside of the barrier is multiplied by R'_B S_s each round
trip, so the echo train's damping is set by |R'_B|, the barrier's reflectivity seen FROM INSIDE, together
with whatever the seam does -- and |R'_B| is now measurable.

WHY |R'_B| = |R_B|. Above the superradiant threshold the barrier is passive and flux-conserving, so
|R|^2 + |T|^2 = 1 from either side, and reciprocity gives |T| = |T'| and hence |R'| = |R|. The ringdown
band sits above the threshold (m Omega_H = 0.6268 for a = 0.9, fundamental near M omega = 0.67), so the
barrier reflectivities computed in barrier_at_ringdown.py apply directly. Below the threshold the relation
fails, which is why only the band above it is used here.

INPUT, not recomputed: the |R|^2 values from barrier_at_ringdown.py, themselves resting on a conversion
calibrated against Regge-Wheeler at a = 0 and against |R|^2 = 1 at the threshold to 4.5e-5.
"""
import numpy as np

# a = 0.9, l = m = 2, from barrier_at_ringdown.py
BAND = [(0.6500, 0.84280419), (0.6700, 0.60488363), (0.7000, 0.24471443), (0.7500, 0.02912158)]
TH, rp = 0.626789, 1.0 + np.sqrt(1.0 - 0.9**2)

print("=" * 96)
print("ECHO DAMPING SET BY THE BARRIER, for a perfectly reflecting seam |S_s| = 1")
print(f"   (threshold m*Omega_H = {TH}; every row below is above it, so |R'| = |R| holds)\n")
print(f"   {'M omega':>9} {'|R_B|^2':>10} {'|R_B|':>9} {'per round trip':>15} {'trips per e-fold':>18}")
for om, r2 in BAND:
    r = np.sqrt(r2)
    n = 1.0 / abs(np.log(r)) if r < 1 else float('inf')
    print(f"   {om:9.4f} {r2:10.6f} {r:9.6f} {r:15.6f} {n:18.2f}")

r67 = np.sqrt(0.60488363)
print(f"""
   At the fundamental, M omega = 0.67, the cavity multiplies the amplitude by {r67:.4f} per round trip even
   when the seam reflects perfectly. That is {1.0/abs(np.log(r67)):.2f} round trips per e-fold: the echo train dies on the
   BARRIER's reflectivity, not on anything the seam does, which is section 7's claim made numerical.""")

print("\n" + "=" * 96)
print("WHAT A SEAM REFLECTIVITY BUYS, since the two multiply")
print(f"   {'|S_s|':>8} {'|R_B S_s| at 0.67':>19} {'trips per e-fold':>18} {'note':>26}")
for Ss in (1.0, 0.5, 0.2, 0.1, 0.01):
    q = r67 * Ss
    n = 1.0 / abs(np.log(q))
    note = "no real-axis pole: |R_B S_s| < 1" if Ss == 1.0 else ""
    print(f"   {Ss:8.2f} {q:19.6f} {n:18.2f} {note:>26}")
print("""
   |R_B S_s| < 1 for every seam reflectivity, so the composed response has NO pole on the real axis: the
   cavity is always leaky, and a seam cannot produce an undamped ringing however well it reflects. The
   damping is bounded below by the barrier alone.""")

print("\n" + "=" * 96)
print("THE ROUND-TRIP TIME, which sets where the echoes land")
print("""   The delay is 2|r_*(seam) - r_*(peak)| and depends on where the seam sits, which the framework does
   not fix, so no number is quoted for it here. What IS fixed is the per-trip amplitude factor above, so
   the echo train's ENVELOPE is predicted even though its spacing is not.""")
