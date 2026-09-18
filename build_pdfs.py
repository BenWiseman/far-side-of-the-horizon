#!/usr/bin/env python3
"""Build both reading-copy and XeLaTeX PDFs using only this release tree."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PUB = ROOT / 'pub/paper2'
TMP = ROOT / 'tmp'
PDF = ROOT / 'output/pdf'
LOG = ROOT / 'validation'
for directory in (TMP, PDF, LOG):
    directory.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
# Chromium's Unix singleton socket has a short path limit. The temporary
# directory is private to this build and removed automatically at exit.
short_tmp = tempfile.TemporaryDirectory(prefix='paper2v3-')
env['TMPDIR'] = short_tmp.name

def run(args, cwd, name):
    print(name, flush=True)
    with (LOG / (name + '.log')).open('w') as out:
        result = subprocess.run(args, cwd=cwd, env=env, stdout=out,
                                stderr=subprocess.STDOUT)
    if result.returncode:
        print((LOG / (name + '.log')).read_text()[-6000:], file=sys.stderr)
        raise SystemExit(result.returncode)

texdir = PUB / 'arxiv_src_v3'
texdir.mkdir(exist_ok=True)
for stem in ['graphical_abstract_v3', 'fig1_dictionary', 'fig2_janus',
             'fig3_curvature', 'fig4_tilt', 'fig5_data']:
    shutil.copy2(PUB / (stem + '.pdf'), texdir / (stem + '.pdf'))

for source, stem in [('PAPER2_v3.md', 'Paper2_v3'),
                     ('SUPPLEMENT_v3.md', 'Supplement_v3')]:
    if len(sys.argv) > 1 and sys.argv[1] not in (source, stem):
        continue
    html = Path(source).stem + '_mathjax.html'
    run(['Rscript', 'render_html_mathjax.R', source, html], PUB,
        stem + '_html')
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    if not chrome:
        raise SystemExit('Chrome or Chromium is required for browser PDFs')
    run([chrome, '--headless', '--no-sandbox', '--disable-gpu',
         '--user-data-dir=' + str(Path(short_tmp.name) / ('chrome-' + stem)),
         '--allow-file-access-from-files',
         '--run-all-compositor-stages-before-draw',
         '--virtual-time-budget=20000', '--no-pdf-header-footer',
         '--print-to-pdf=' + str(PDF / (stem + '_browser.pdf')),
         (PUB / html).as_uri()], PUB, stem + '_chrome')
    run(['pandoc', source, '--from=markdown+tex_math_single_backslash',
         '--to=latex', '--standalone', '--pdf-engine=xelatex',
         '--include-in-header=release_header.tex',
         '-V', 'geometry:margin=1in', '-V', 'mainfont=DejaVuSerif.ttf',
         '-V', 'mainfontoptions=BoldFont=DejaVuSerif-Bold.ttf,ItalicFont=DejaVuSerif-Italic.ttf,BoldItalicFont=DejaVuSerif-BoldItalic.ttf',
         '--lua-filter=math_glyphs.lua', '--lua-filter=vector_figures.lua',
         '--lua-filter=group_figures.lua',
         '-o', str(texdir / (stem + '.tex'))], PUB, stem + '_pandoc')
    for pass_number in (1, 2):
        run(['xelatex', '-no-shell-escape', '-halt-on-error',
             '-interaction=nonstopmode', stem + '.tex'], texdir,
            stem + '_xelatex_' + str(pass_number))
    shutil.copy2(texdir / (stem + '.pdf'), PDF / (stem + '_xelatex.pdf'))
print('Built four PDFs. Rendering and visual review are still required.', flush=True)
