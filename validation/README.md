# Validation outputs

Each file here was produced from this release tree on 18 September 2026 (Linux, R 4.5.2,
Python 3.12 with NumPy 2.5.3 and SciPy 1.18.1, pandoc 3.10, XeTeX from TeX Live 2026,
Chrome 152).

| File | Command | Result |
|---|---|---|
| `companion.txt` | `bash pub/paper2/companion/run_all.sh` | Exit 0; 96 results; 96/96 pass at stated tolerances, 75/96 at a flat 0.5% |
| `free_tt_controls.txt` | `python3 calc/free_tt_controls.py` | Exit 0; rewrites `calc/free_tt_controls.json` byte for byte |
| `weak_yukawa_benchmark.txt` | `python3 calc/weak_yukawa_benchmark.py` | Exit 0; rewrites `calc/weak_yukawa_benchmark.json` byte for byte |
| `figure5_audit.txt` | `python3 calc/audit_fig5_redesign.py` | Exit 0 |
| `supp_figures_audit.txt` | `python3 calc/audit_supp_figures_v3.py` | Exit 0 |
| `svg_legibility.txt` | `Rscript ../../calc/audit_svg_legibility_v3.R 6.5 graphical_abstract_v3.svg fig1_dictionary.svg fig2_janus.svg fig3_curvature.svg fig4_tilt.svg` (run in `pub/paper2`) | No figure text below 8 pt at 6.5 in |
| `svg_legibility_fig5.txt` | `Rscript ../../calc/audit_svg_legibility_v3.R 5.6225 fig5_data.svg` (run in `pub/paper2`) | No figure text below 8 pt at the printed width |
| `portability_checks.json` | Run against the original sources before copying | Recorded result; not rerunnable from this release |

`python3 beyond/push/P2_NUR_DM/bft_reproduce.py` also exits 0 and gives
I = 0.0127596673634 and M₁ = 4.848 × 10⁸ GeV. `half_advanced.py` and
`echo_damping_from_barrier.py` exit 0. The full likelihood fits and the Kerr radial
sweep were not rerun for this release.

`python3 build_pdfs.py` builds all four PDFs: main 29 pages (browser) and 30 (XeLaTeX),
supplement 15 and 16. XeLaTeX reports no overfull boxes, undefined references or missing
glyphs. It reports one float 0.8 pt taller than the page (Figure 5); the rendered page
shows no clipping. The build logs are local output and are not included.
