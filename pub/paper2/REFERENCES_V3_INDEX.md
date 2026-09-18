# Paper 2 v3 reference index

This index maps all 82 current bibliography entries to the five supplied historical metadata logs. It is a release documentation record, not a science gate. A matched lookup record is **not evidence that the source was read or that a manuscript claim was validated**. The logs are historical; their original `VERIFIED` labels refer to metadata lookup and are not renewed here.

The indexed [manuscript](PAPER2_v3.md) has SHA-256 `c043a77dcaaad17798bf46f669cdb47420466f408690a70ab1fee3c9ded4f590`; references occupy lines 969–1131. The machine-readable companion is [refs_v3_index.json](refs_v3_index.json), which preserves every citation, source line, matching record, exact JSON pointer and input hash.

Coverage: 2 current arxiv metadata, 53 historical arxiv match, 1 review/catalogue only, 18 historical title match, 8 no historical match. The eight unmatched entries are **49, 58–60 and 77–80**. References 81–82 were absent from the historical logs and use the current primary arXiv metadata-check receipts recorded for this release. Three additional current INSPIRE API checks resolve the metadata for references 2 and 12. All five current receipts were supplied by the parent session on 2026-09-18; this indexer performed no bulk browsing.

The bibliography’s line-967 statement now directs readers to this index and explicitly separates metadata matching from support for manuscript claims. Missing historical coverage is a documentation gap, not a finding that a reference is invalid. Journal-only references can have valid metadata matches. Source reading and claim validation remain unassessed by this index; the explicit source-access limits for references 64 and 73 remain visible.

## Inputs and matching rules

Matches use the actual arXiv identifier or the title after case, punctuation, diacritic and markup normalization. The related reviews for reference 1 and the second part of reference 22 are explicitly identified exceptions. Candidate position, search-query wording and old reference numbering were not used as identity evidence. A log may contain many unrelated search results; only the specified rows are mapped.

Pointers below follow RFC 6901: `~1` represents a slash inside a key, as in `hep-th~10209120`. Each pointer is relative to its indicated log. Complete historical rows and metadata are retained in the JSON.

| Key | Historical log | SHA-256 |
| --- | --- | --- |
| L1 | [refs_verified.json](refs_verified.json) | `0cc2e2e62f43dd44993030fcd3c9d29cab733a7560f9a4ff83265eaf30f0d00a` |
| L2 | [refs_verified2.json](refs_verified2.json) | `06ec2031df7b6ea9f4531d53025734bcce5c5cacc4e00c9646ac2f6f1ba9e916` |
| L3 | [refs_verified3.json](refs_verified3.json) | `fe1545d173cc6edab5158b94e366328d54b1e421a66219914aacdf77b0be1e91` |
| L4 | [refs_verified4.json](refs_verified4.json) | `f01682580c952bfe84f2204706c2c8664c1000146233c2a9e335c37556c13a4f` |
| L5 | [refs_verified5.json](refs_verified5.json) | `5dace714883839df273d7baaff56b40b0c2dc9be4817ff7d1a723ebc4c6b1669` |

## Limits and discrepancies

- **1:** The supplied Crossref records describe reviews or journal catalogue-style entries related to *Expanding Universes*. They do not supply a direct Cambridge University Press book record. The historical INSPIRE lookup was empty.
- **2:** The historical log wrongly used artid `86800220` as a page. The current primary [INSPIRE record 18221](https://inspirehep.net/api/literature/18221) check returns volume 271 (1986), pages 497–508, confirming the manuscript first page. This is a historical logging difference, not a current citation error.
- **12:** The current manuscript cites [INSPIRE 444838](https://inspirehep.net/api/literature/444838), agreeing with both the historical log and the current primary check for Moretti, `hep-th/9706191`, with no journal listed. A separate primary check identifies [INSPIRE 445039](https://inspirehep.net/api/literature/445039) as a different Euclidean SYM work, `hep-th/9706225`. The parent corrected that former staged identifier before this index was finalized.
- **18:** Two Penrose title records have different years (1980 and 1979) and no book/chapter venue. The 1979 record matches the manuscript year; full chapter metadata remains incomplete.
- **22:** The composite entry maps part I (page 473) and part II (page 493) separately. The logged part-II titles are truncated; journal, author, year, page and DOI identify the second part.
- **64, 73:** The manuscript respectively reports an unfetchable article and an article not read at source. Matching metadata does not remove these limits.
- **72:** The historical DOI `10.1142/9789811279461_0007` has book-chapter form. It is not established here as a DOI for the original 1964/1965 journal article.
- **79:** Neither the Nature article nor its erratum has a matching historical row. The quoted event energies are not checked by this index.
- **81–82:** Current primary abstract-page checks identify Atre et al., [arXiv:0901.3589](https://arxiv.org/abs/0901.3589), JHEP 05 (2009) 030, and Ciafaloni et al., [arXiv:1009.0224](https://arxiv.org/abs/1009.0224), JCAP 03 (2011) 019. These checks were supplied by the parent session on 2026-09-18 and are recorded as metadata receipts, not source-read or claim-validation certificates.

## All current entries

Every status in this table concerns metadata provenance only. The JSON supplies the full citation and explicit source-read/claim-validation fields for every entry.

| Ref. | Current title and identifier | Metadata coverage | Historical location or current receipt |
| --- | --- | --- | --- |
| 1 | Expanding Universes — book | Review/catalogue only | L3 `/schrodinger_cr/0`<br>L3 `/schrodinger_cr/1`<br>L3 `/schrodinger_cr/2`<br>L3 `/schrodinger_cr/3` |
| 2 | The elliptic interpretation of black holes and quantum mechanics — journal only in manuscript | Historical title match | L2 `/gibbons1986/candidates/0`<br>[Current INSPIRE metadata](https://inspirehep.net/api/literature/18221) |
| 3 | Elliptic de Sitter space: dS/Z₂ — `hep-th/0209120` | Historical arXiv match | L1 `/hep-th~10209120` |
| 4 | Black hole unitarity and antipodal entanglement — `1601.03447` | Historical arXiv match | L1 `/1601.03447` |
| 5 | What happens in a black hole when a particle meets its antipode — `1804.05744` | Historical arXiv match | L1 `/1804.05744` |
| 6 | Quantum field theory and the 'elliptic interpretation' of de Sitter space-time — journal only in manuscript | Historical title match | L2 `/folacci_sanchez/candidates/0` |
| 7 | Quantum fields on manifolds: PCT and gravitationally induced thermal states — journal only in manuscript | Historical title match | L2 `/sewell1982/candidates/1` |
| 8 | Global properties of vacuum states in de Sitter space — `gr-qc/9803036` | Historical arXiv match | L1 `/gr-qc~19803036` |
| 9 | Horizon complementarity in elliptic de Sitter space — `1409.6753` | Historical arXiv match | L1 `/1409.6753` |
| 10 | Quantum field theory in Lorentzian universes from nothing — `gr-qc/9505035` | Historical arXiv match | L1 `/gr-qc~19505035` |
| 11 | No boundary density matrix in elliptic de Sitter dS/Z₂ — `2512.00704` | Historical arXiv match | L2 `/dulac_wei/candidates/0`<br>L5 `/arxiv/2512.00704/0` |
| 12 | Zeta function renormalization of one-loop stress tensors in curved spacetimes — `hep-th/9706191` | Historical arXiv match | L1 `/hep-th~19706191`<br>[Current INSPIRE metadata](https://inspirehep.net/api/literature/444838) |
| 13 | Locally localized gravity — `hep-th/0011156` | Historical arXiv match | L1 `/hep-th~10011156` |
| 14 | A three three-brane universe: new phenomenology for the new millennium? — `hep-ph/9912552` | Historical arXiv match | L1 `/hep-ph~19912552` |
| 15 | Thermo field dynamics of black holes — journal only in manuscript | Historical title match | L2 `/israel1976/candidates/0` |
| 16 | Eternal black holes in anti-de Sitter — `hep-th/0106112` | Historical arXiv match | L2 `/maldacena_eternal/candidates/0` |
| 17 | Forbidden mass range for spin-2 field theory in de Sitter space-time — journal only in manuscript | Historical title match | L2 `/higuchi1987/candidates/0` |
| 18 | Singularities and time-asymmetry — book chapter | Historical title match | L2 `/penrose1979/candidates/0`<br>L2 `/penrose1979/candidates/1` |
| 19 | Isotropic singularities in cosmological models — journal only in manuscript | Historical title match | L2 `/goode_wainwright1985/candidates/0` |
| 20 | Isotropic cosmological singularities: I. Polytropic perfect fluid spacetimes — `gr-qc/9903008` | Historical arXiv match | L1 `/gr-qc~19903008`<br>L3 `/tod_isotropic/1`<br>L3 `/tod_isotropic_cr/0`<br>L3 `/anguige_tod_ii/0` |
| 21 | Isotropic cosmological singularities II: the Einstein–Vlasov system — `gr-qc/9903009` | Historical arXiv match | L3 `/tod_isotropic/2`<br>L3 `/tod_isotropic_cr/2`<br>L3 `/anguige_tod_ii/1` |
| 22 | On the structure of conformal singularities in classical general relativity — journal only in manuscript | Historical title match | L3 `/newman_conformal/0`<br>L3 `/newman_conformal/1`<br>L3 `/newman_conformal_cr/0`<br>L3 `/newman_conformal_cr/1` |
| 23 | Isotropic cosmological singularities: other matter models — `gr-qc/0209071` | Historical arXiv match | L3 `/tod_isotropic/0` |
| 24 | Gravitational entropy and the flatness, homogeneity and isotropy puzzles — `2201.07279` | Historical arXiv match | L1 `/2201.07279` |
| 25 | Two-sheeted universe, analyticity and the arrow of time — `2109.06204` | Historical arXiv match | L1 `/2109.06204` |
| 26 | CPT-symmetric universe — `1803.08928` | Historical arXiv match | L1 `/1803.08928` |
| 27 | Perturbations of spacetimes in general relativity — journal only in manuscript | Historical title match | L2 `/stewart_walker1974/candidates/1` |
| 28 | Super-energy tensors — `gr-qc/9906087` | Historical arXiv match | L4 `/senovilla_superenergy/0` |
| 29 | A gravitational entropy proposal — `1303.5612` | Historical arXiv match | L4 `/clifton_ellis_tavakol/0` |
| 30 | Identification of a gravitational arrow of time — `1409.0917` | Historical arXiv match | L1 `/1409.0917` |
| 31 | Janus points and arrows of time — `1604.03956` | Historical arXiv match | L1 `/1604.03956` |
| 32 | A gravitational origin of the arrows of time — `1310.5167` | Historical arXiv match | L1 `/1310.5167` |
| 33 | Structural morphology and the gravitational arrow of time — `2607.27526` | Historical arXiv match | L1 `/2607.27526` |
| 34 | The Big Bang, CPT, and neutrino dark matter — `1803.08930` | Historical arXiv match | L1 `/1803.08930` |
| 35 | Constraints on neutrino physics from DESI DR2 BAO and DR1 full shape — `2503.14744` | Historical arXiv match | L1 `/2503.14744` |
| 36 | Predicting spatial curvature Ω_K in globally CPT-symmetric universes — `2407.18225` | Historical arXiv match | L1 `/2407.18225`<br>L4 `/deng_handley_2025/2` |
| 37 | CMB constraints on quantized spatial curvature Ω_K in globally CPT-symmetric universes — `2509.10379` | Historical arXiv match | L1 `/2509.10379`<br>L4 `/deng_handley_2025/0` |
| 38 | DESI DR2 results. II. Measurements of baryon acoustic oscillations and cosmological constraints — `2503.14738` | Historical arXiv match | L1 `/2503.14738`<br>L4 `/desi_dr2_i/1` |
| 39 | Planck 2018 results VI: cosmological parameters — `1807.06209` | Historical arXiv match | L1 `/1807.06209` |
| 40 | A minimal explanation of the primordial cosmological perturbations — `2302.00344` | Historical arXiv match | L1 `/2302.00344` |
| 41 | Investigating the near-criticality of the Higgs boson — `1307.3536` | Historical arXiv match | L1 `/1307.3536` |
| 42 | The Atacama Cosmology Telescope: DR6 power spectra, likelihoods and ΛCDM parameters — `2503.14452` | Historical arXiv match | L1 `/2503.14452` |
| 43 | The Atacama Cosmology Telescope: DR6 constraints on extended cosmological models — `2503.14454` | Historical arXiv match | L1 `/2503.14454` |
| 44 | Pathologies of dimension-zero scalar fields — `2603.05683` | Historical arXiv match | L1 `/2603.05683` |
| 45 | Stress testing ΛCDM with high-redshift galaxy candidates — `2208.01611` | Historical arXiv match | L1 `/2208.01611` |
| 46 | Bursty star formation naturally explains the abundance of bright galaxies at cosmic dawn — `2307.15305` | Historical arXiv match | L1 `/2307.15305` |
| 47 | The rise of faint, red active galactic nuclei at z > 4: A Sample of Little Red Dots in the JWST Extragalactic Legacy Fields — `2404.03576` | Historical arXiv match | L1 `/2404.03576` |
| 48 | The CosmoVerse white paper: Addressing observational tensions in cosmology with systematics and fundamental physics — `2504.01669` | Historical arXiv match | L1 `/2504.01669` |
| 49 | Interpolating between a and F — `1409.1937` | No historical match | None in the five supplied logs |
| 50 | SPT-3G D1: CMB temperature and polarization power spectra and cosmology from 2019 and 2020 observations of the SPT-3G main field — `2506.20707` | Historical arXiv match | L1 `/2506.20707` |
| 51 | Cancelling the vacuum energy and Weyl anomaly in the Standard Model with dimension-zero scalar fields — `2110.06258` | Historical arXiv match | L1 `/2110.06258` |
| 52 | Higher codimension de Sitter branes — `2506.19515` | Historical arXiv match | L3 `/padilla_cr/0`<br>L4 `/padilla_2025/4`<br>L4 `/padilla_codim/0` |
| 53 | Improved cosmological fits with quantized primordial power spectra — `2104.01938` | Historical arXiv match | L2 `/bartlett_handley/candidates/0` |
| 54 | Rescuing palindromic universes with improved recombination modeling — `2111.14588` | Historical arXiv match | L2 `/prathaban_handley/candidates/0` |
| 55 | Perturbations and the future conformal boundary — `2104.02521` | Historical arXiv match | L1 `/2104.02521` |
| 56 | Casimir effect around a cone — journal only in manuscript | Historical title match | L2 `/dowker_cone/candidates/0` |
| 57 | Dai-Freed anomalies in particle physics — `1808.00009` | Historical arXiv match | L5 `/arxiv/1808.00009/0` |
| 58 | The Big Bang as a mirror: a solution of the strong CP problem — `2208.10396` | No historical match | None in the five supplied logs |
| 59 | Reflections on parity breaking — `2212.00039` | No historical match | None in the five supplied logs |
| 60 | The absence of global anomalies of CP symmetry — `2602.11475` | No historical match | None in the five supplied logs |
| 61 | Group averaging for de Sitter free fields — `0810.5163` | Historical arXiv match | L5 `/arxiv/0810.5163/0` |
| 62 | IR-fixed Euclidean vacuum for linearized gravity on de Sitter space — `2405.00866` | Historical arXiv match | L5 `/arxiv/2405.00866/0` |
| 63 | Quantum cosmology and the emergence of a classical world — `gr-qc/9308025` | Historical arXiv match | L5 `/arxiv/gr-qc~19308025/0` |
| 64 | Decoherence in quantum electrodynamics and quantum gravity — journal only in manuscript | Historical title match | L5 `/by_title/kiefer_decoherence_prd46/0` |
| 65 | The origin of structure in the universe — journal only in manuscript | Historical title match | L5 `/by_title/halliwell_hawking/0` |
| 66 | Wave function of the universe — journal only in manuscript | Historical title match | L5 `/by_title/hartle_hawking/0` |
| 67 | Relativistic measurements from timing the binary pulsar PSR B1913+16 — `1606.02744` | Historical arXiv match | L5 `/arxiv/1606.02744/0` |
| 68 | Gravitationally induced entanglement between two massive particles is sufficient evidence of quantum effects in gravity — `1707.06036` | Historical arXiv match | L5 `/arxiv/1707.06036/0` |
| 69 | Cosmological consequences of the spontaneous breakdown of discrete symmetry — journal only in manuscript | Historical title match | L5 `/by_title/kobzarev_okun_zeldovich/0` |
| 70 | Vacuum states in de Sitter space — journal only in manuscript | Historical title match | L5 `/by_title/allen_dS_vacuum/0` |
| 71 | Brownian motion of a quantum oscillator — journal only in manuscript | Historical title match | L5 `/by_title/schwinger_1961/0` |
| 72 | Diagram technique for nonequilibrium processes — journal only in manuscript | Historical title match | L5 `/by_title/keldysh_1964/0` |
| 73 | Finite temperature quantum field theory in Minkowski space — journal only in manuscript | Historical title match | L5 `/by_title/niemi_semenoff_1984/0` |
| 74 | Schwinger–Keldysh propagators from AdS/CFT correspondence — `hep-th/0212072` | Historical arXiv match | L5 `/arxiv/hep-th~10212072/0` |
| 75 | Is CP a gauge symmetry? — `hep-ph/9205202` | Historical arXiv match | L5 `/arxiv/hep-ph~19205202/0` |
| 76 | The CKM phase and θ̄ in Nelson–Barr models — `2105.09122` | Historical arXiv match | L5 `/arxiv/2105.09122/0` |
| 77 | Black hole S-matrix for a scalar field — `2012.09834` | No historical match | None in the five supplied logs |
| 78 | Tests of general relativity with GWTC-3 — `2112.06861` | No historical match | None in the five supplied logs |
| 79 | Observation of an ultra-high-energy cosmic neutrino with KM3NeT — journal only in manuscript | No historical match | None in the five supplied logs |
| 80 | Low Energy States and CPT invariance at the Big Bang — `2302.08812` | No historical match | None in the five supplied logs |
| 81 | The Search for Heavy Majorana Neutrinos — `0901.3589` | Current arXiv metadata | [arXiv abstract](https://arxiv.org/abs/0901.3589); current-session metadata receipt |
| 82 | Weak Corrections are Relevant for Dark Matter Indirect Detection — `1009.0224` | Current arXiv metadata | [arXiv abstract](https://arxiv.org/abs/1009.0224); current-session metadata receipt |
