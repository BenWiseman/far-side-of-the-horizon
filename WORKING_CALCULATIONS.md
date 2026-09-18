# Selected working calculations

This release includes the bounded calculation sources listed below. They support
specific manuscript figures and controls. The retained fit log records an earlier
run; it is not presented as a fresh release-validation result. The release does
not include the complete development history or private working correspondence.

Install the calculation dependencies listed in `calc/requirements.txt` in a Python
environment. They cover NumPy, SciPy, SymPy and mpmath. The package list and commands
here concern the calculations; manuscript rendering has separate requirements.
Commands below are shown from the release root. Script and input paths are
resolved from each script's location, so the scripts can also be called by an
absolute path from another directory.

## Adopted BFT abundance calibration

```bash
python3 beyond/push/P2_NUR_DM/bft_reproduce.py
```

This reproduces the occupation integral and abundance calibration adopted from
Boyle, Finn and Turok, [arXiv:1803.08930](https://arxiv.org/abs/1803.08930), and
compares the mass inferred from other supplied occupation functions. The inputs
are `mu_hat = 5.966e18 GeV`, `g_* = 106.75`, `rho_DM,0 = 9.7e-48 GeV^4` and
`s_0 = 2.3e-38 GeV^3`. The heavy mass is calibrated to that dark-matter abundance
within the adopted production model and state. The printed quadrature digits
describe fixed-input arithmetic precision; the two-significant-digit density and
entropy inputs do not support comparable physical precision in the calibrated
mass. The geometric fold alone does not select the BFT state or these inputs.

## Geometry-only neutrino-mass profiles

```bash
python3 data/check_inputs.py
python3 calc/tangents/numass_mirror/numass_mirror.py
```

Acquire the two Pantheon+ inputs as described in `data/README.md`, or set
`PAPER2_PANTHEON_DIR` to an existing directory containing them. The fit also uses
the DESI DR2 BAO table in `calc/desi_dr2_geometry.py`. This loader is an exact
extraction of the table and vector builder from the original calculation, with
unrelated CAMB and Planck imports removed.

The calculation profiles LCDM, w0waCDM and the phenomenological density
`rho_x(a) = Lambda - Omega_f a^3`. The latter is an exploratory parametrisation,
without a fold-derived action. The models share approximate compressed CMB priors:
`omega_cb = 0.1430 +/- 0.0011`, `100 theta_* = 1.04109 +/- 0.00030`, fixed
`omega_b = 0.02236`, `z_* = 1089.9`, and `r_s(z_*)/r_d = 0.9819`. The source states
the sound-horizon approximation and its neutrino correction. These are
geometry-only conditional fits, not full CMB or growth analyses.

`calc/tangents/numass_mirror/numass_mirror_output.txt` is the retained output,
including the profile table used by Figure 5. Its one-sided profile bounds
at Delta chi-square = 2.71 are 54.5, 92.8 and 47.0 meV for LCDM, w0waCDM and the
nonnegative-Omega_f toy respectively. The corresponding Delta chi-square costs at
58.8 meV are 3.012, 1.420 and 3.645. Those values are copied from that log here;
they must be rerun to establish a new numerical reproduction. The calculation
contains optimisation and is excluded from the quick arithmetic companion.

References in the retained output to earlier working notes are historical
provenance labels. Those broader notes are not included or required to execute
this source. This document provides the public description in their place.

## Exploratory dark-energy fit

```bash
python3 calc/tangents/mirror_repulsion_combined.py
```

This compares the same phenomenological dark-energy forms with DESI DR2 and
Pantheon+, using the compressed matter-density prior on `omega_m` and a fixed
sound-horizon formula. It predates the mass-profile script. The release repairs
one diagnostic-only sign error: the printed `Omega_Lambda` now equals
`1 - Omega_m - Omega_r + Omega_f`, exactly as in the script's own `E2` function.
The original print block used `1 - Omega_m - Omega_f`. The optimiser, likelihood,
and fitted density evolution are unchanged. The later retained neutrino log
already reports and corrects that old diagnostic error.

## Kerr barrier and conditional echo damping

```bash
python3 calc/tangents/greybody/barrier_at_ringdown.py
python3 calc/tangents/greybody/echo_damping_from_barrier.py
```

The first command solves the angular problem and invokes `_kerr_runner.py` with
the same interpreter. That runner extracts the radial integration and matching
functions from `calc/tangents/kerr_teukolsky/teukolsky_zin_tortoise.py`. These files form
the source closure; no private environment or external data file is required.
The full barrier computation is slower than the quick checks.

`echo_damping_from_barrier.py` uses fixed barrier values recorded in its `BAND`
table. It computes the per-trip factors and e-fold counts for its stated passive,
above-threshold cavity assumptions. It does not recompute the barrier, determine
the seam reflectivity, predict the round-trip delay, or model detector response.
The standalone tortoise source also retains fixed historical comparison
amplitudes; the barrier driver does not use those amplitudes.

## Time-symmetric response controls

```bash
python3 beyond/main/fold_dynamics/half_advanced.py
```

This computes finite-difference and Fourier controls for prescribed retarded,
advanced and symmetric kernels, checks the net work for compact pulses, and
samples de Sitter image separations. A commuting covariance alone does not imply
a time-symmetric interacting response. The zero-work result concerns the
particular symmetric kernel supplied to this calculation. The source's older
interpretive paragraphs asserting a conclusion about every fold implementation
have been removed; numerical expressions and input values are retained. Its
binary-pulsar comparison is conditional on imposing that zero-work response.

## Release portability changes

The released files replace private absolute paths with file-relative resolution,
support `PAPER2_PANTHEON_DIR`, and use `sys.executable` for the Kerr subprocess.
The DESI extraction preserves its table and array builder. The BFT source's old
statement that antipodal/CPT invariance alone fixes its occupation has been
replaced by the explicit adopted-state dependency. The changes to printed
interpretation and the diagnostic sign are described above. The retained output
is unchanged. External Pantheon+ files are omitted; hashes and pinned upstream
URLs are supplied in `data/pantheon_inputs.json` and `data/README.md`.

`calc/SOURCE_PROVENANCE.json` records original and released source hashes. These are
curated calculation sources, not byte-identical historical copies, except where
the manifest states that no change was made. The echo print label now says
"no real-axis pole" in place of "no resonance": a leaky cavity can still have
damped resonances. This caption correction changes no arithmetic.

## New bounded controls

`python3 calc/free_tt_controls.py` checks the exact radial integral, normalized
mode reflection, positive Klein-Gordon norm, analytic Jacobi sequence and the
explicit cyclic-domain coefficient formula. These arithmetic controls do not
prove the imported TT representation or complete interacting gravity.

`python3 calc/weak_yukawa_benchmark.py` reproduces the stated S13 fixed-input
width, induced mass bound, inverse-decay estimate and depletion. Its lifetime is
a freely chosen input; it supplies no observed spectrum, flux or likelihood.
Both scripts use only Python's standard library and write adjacent JSON outputs.
