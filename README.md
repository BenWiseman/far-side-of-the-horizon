# The Far Side of the Horizon

**A geometric fold for CPT-related copies of spacetime**

B. H. Wiseman · Version 3.0.6 · 18 September 2026

Repository: <https://github.com/BenWiseman/far-side-of-the-horizon>
Release: <https://github.com/BenWiseman/far-side-of-the-horizon/releases/tag/v3.0.6>

This repository holds the manuscript, supplement, figures and checking code for the
paper. The paper proposes a geometric restriction of the Schwinger-Keldysh closed time
path for CPT-symmetric cosmology. The second leg of the contour is fixed as the image of
the first under a spacetime involution. The paper works out what that restriction does
and does not change, and tests several specified states and responses against it.

## Citation

> B. H. Wiseman, *The Far Side of the Horizon: a geometric fold for CPT-related copies of
> spacetime*, version 3.0.6 (2026), https://github.com/BenWiseman/far-side-of-the-horizon

Machine-readable metadata is in `CITATION.cff`. A dated preview of the paper and
supplement PDFs, without code, is at https://doi.org/10.5281/zenodo.22811618.

## Contents

| Path | What it is |
|---|---|
| `pub/paper2/PAPER2_v3.md` | Main manuscript (Markdown source) |
| `pub/paper2/SUPPLEMENT_v3.md` | Supplement, sections S1 to S13 |
| `pub/paper2/arxiv_src_v3/` | Generated LaTeX sources and figure PDFs, prepared for arXiv |
| `output/pdf/` | Built PDFs: browser route and XeLaTeX route, main and supplement |
| `pub/paper2/fig*.{svg,pdf,png}`, `graphical_abstract_v3.*` | Figure masters and renders |
| `pub/paper2/figure_authoring_r/` | R scripts that edit the SVG masters and render the figures |
| `pub/paper2/fig5_data.py` | Original generator for Figure 5, with every plotted value and its source |
| `pub/paper2/companion/` | Fifteen base-R scripts that make 96 arithmetic comparisons against the paper |
| `pub/paper2/refs_*.json`, `REFERENCES_V3_INDEX.md` | Reference metadata lookups and an index of what they cover |
| `pub/paper2/*.lua`, `paper_pdf.css`, `release_header.tex`, `render_html_mathjax.R` | Build filters and styles |
| `calc/`, `beyond/` | Selected Python working calculations (see `WORKING_CALCULATIONS.md`) |
| `data/` | Instructions, pinned URLs and hashes for the external Pantheon+ inputs |
| `validation/` | Outputs of the checks listed below, from this exact tree |
| `build_pdfs.py` | Builds all four PDFs from the Markdown sources |
| `ARXIV_METADATA_v3.txt` | Title, categories, comments and abstract for arXiv |
| `SHA256SUMS.txt` | SHA-256 of every other file in the release |

## Checking the numbers

The quick check needs only base R (tested with R 4.5.2). From the repository root:

```bash
bash pub/paper2/companion/run_all.sh
```

It runs the fifteen scripts, prints each comparison, and exits non-zero if any script
fails or if it does not see exactly 96 results. All 96 pass at the tolerance each script
states and justifies in its header. Against one flat 0.5% relative bar, 75 pass; the
companion README names the other 21 and says why each uses a looser tolerance. Passing
these checks shows the listed formulas and inputs give the quoted numbers. It does not
test the physical assumptions behind them.

The Python calculations need Python 3.12 or later and the packages in
`calc/requirements.txt` (NumPy, SciPy, SymPy, mpmath):

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r calc/requirements.txt
python3 beyond/push/P2_NUR_DM/bft_reproduce.py          # BFT occupation integral and mass
python3 calc/free_tt_controls.py                        # free-graviton construction controls
python3 calc/weak_yukawa_benchmark.py                   # Supplement S13 decay benchmark
python3 beyond/main/fold_dynamics/half_advanced.py      # time-symmetric response controls
python3 calc/tangents/greybody/echo_damping_from_barrier.py
```

`WORKING_CALCULATIONS.md` describes each calculation, its inputs and its limits,
including the slower Kerr barrier sweep and the geometry-only neutrino-mass fits.

## External data

The geometry-only fits use the Pantheon+ distance table and covariance, which are not
redistributed here. `data/README.md` gives the upstream commit, download commands and
SHA-256 of both files; `python3 data/check_inputs.py` verifies them. Set
`PAPER2_PANTHEON_DIR` to use an existing copy. The DESI DR2 BAO table is built into
`calc/desi_dr2_geometry.py`.

## Building the PDFs

```bash
python3 build_pdfs.py
```

This needs R with the `rmarkdown` package, pandoc 3, XeLaTeX with DejaVu fonts, and
Google Chrome or Chromium. It writes the browser and XeLaTeX PDFs to `output/pdf/`,
regenerates the LaTeX in `pub/paper2/arxiv_src_v3/`, and writes build logs to
`validation/`. Those logs and the TeX `.aux`/`.log` files are local build output and are
not part of the release. The figure scripts in `figure_authoring_r/` also need the R
package `xml2`.

## Verifying the files

```bash
sha256sum -c SHA256SUMS.txt
```

The release page lists the SHA-256 of the two attached archives: the full source and the
arXiv source.

## Scope and limits

- The closed-time-path average/difference algebra is standard. The paper's addition is
  the geometric rule that pairs the two legs, its compatibility with one stated nonzero
  free-graviton sector, the branch-overlap calculations, and tests of specified
  alternative states and responses. Those tests do not exclude every quotient theory.
- The cosmological application adopts Boyle, Finn and Turok's radiation history,
  particle content, state and stabilising rule. The fold does not derive them. The
  484.8 PeV heavy mass is calibrated to the observed dark-matter abundance in that
  branch; its extra digits are arithmetic, and the physical scale is about 480 PeV.
- The weak-Yukawa decay example has a free lifetime and flavour direction. It does not
  predict an observed neutrino spectrum or event rate, and it is not evidence from the
  KM3NeT event.
- The dark-energy and neutrino-mass fits are exploratory, geometry-only fits with
  compressed CMB priors. They are not full CMB or growth analyses. The retained fit log
  records an earlier run; rerun it to reproduce those numbers.
- This release is a selected set of files. It is not the author's complete development
  history. Comments in some scripts name working notes that are not included; every
  expected value is written out in the scripts themselves.
- `validation/portability_checks.json` records a check run against the original
  calculation sources before they were copied here. It cannot be rerun from this
  release alone.

## Licence

Code (`.py`, `.R`, `.sh`, `.lua`) is under the MIT License. The manuscript, supplement,
figures and documentation are under CC BY 4.0. See `LICENSE`.
