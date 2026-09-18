#!/usr/bin/env python3
"""Compact 7-inch Figure 5 for Paper 2 V3.

All values come from the provenance-rich legacy generator
pub/paper2/fig5_data.py. This script changes presentation only.
"""
from pathlib import Path
from html import escape
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'pub/paper2'
TEST = ROOT / 'tmp/fig5_release_tests'
W, H = 504, 630  # pt: exactly 7.00 by 8.75 inches
INK, MID, GRID, PALE = '#15181d', '#56616b', '#c6ccd2', '#eef1f3'
NAVY, GREEN, PURPLE, RED = '#174d79', '#326b45', '#6b4c91', '#9b3029'
NH, IH, LCDM, FC, W0WA = 58.8, 98.9, 64.2, 53.0, 163.0
X = [0.,10.,20.,30.,40.,50.,58.8,70.,85.,100.,120.,150.,180.,220.,260.,300.]
DL = [0.,.212,.642,1.168,1.760,2.405,3.012,3.834,5.014,6.281,8.098,11.086,14.373,19.195,24.490,30.228]
DW = [0.,.096,.295,.541,.821,1.129,1.420,1.817,2.393,3.018,3.923,5.436,7.131,9.667,12.512,15.656]
DT = [0.,.294,.835,1.476,2.182,2.941,3.645,4.588,5.925,7.342,9.351,12.602,16.125,21.221,26.743,32.664]
FITS = [('1',-0.803,.054,.054,-.72,.21,.21), ('2',-.719,.084,.084,-.95,.26,.29), ('3',-.861,.042,.044,-.60,.19,.17)]

def n(v): return f'{v:.2f}'
def add(s, v): s.append(v)
def txt(s, x, y, value, size=10, anchor='start', weight='normal', fill=INK, rotate=None):
    tr = '' if rotate is None else f' transform="rotate({rotate} {n(x)} {n(y)})"'
    add(s, f'<text x="{n(x)}" y="{n(y)}" font-size="{size}pt" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{tr}>{escape(value)}</text>')
def ln(s,x1,y1,x2,y2,col=INK,w=1,dash=None):
    d='' if dash is None else f' stroke-dasharray="{dash}"'; add(s,f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{col}" stroke-width="{w}"{d}/>')
def box(s,x,y,w,h,fill='none',stroke=None):
    st='' if stroke is None else f' stroke="{stroke}"'; add(s,f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{fill}"{st}/>')
def dot(s,x,y,r,fill,stroke=None,w=1):
    st='' if stroke is None else f' stroke="{stroke}" stroke-width="{w}"'; add(s,f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill}"{st}/>')
def poly(s,pts,col,w=1.8,dash=None):
    d='' if dash is None else f' stroke-dasharray="{dash}"'; add(s,f'<polyline points="{" ".join(n(x)+","+n(y) for x,y in pts)}" fill="none" stroke="{col}" stroke-width="{w}"{d}/>')
def mx(v,l,w,lo,hi): return l+w*(v-lo)/(hi-lo)
def my(v,t,h,lo,hi): return t+h*(hi-v)/(hi-lo)
def profile(data,l,r,t,b):
    out=[]
    for i,(x,y) in enumerate(zip(X,data)):
        if x<=200 and y<=10: out.append((mx(x,l,r-l,0,200),my(y,t,b-t,0,10))); continue
        xp,yp=X[i-1],data[i-1]; cross=xp+(10-yp)*(x-xp)/(y-yp)
        if xp<cross<=200: out.append((mx(cross,l,r-l,0,200),t))
        break
    return out

def panel_a(s):
    # Two semantic groups replace five stacked two-line labels.  The values,
    # point/limit encodings and sub-NO-floor band are unchanged; the extra
    # height is reserved for row spacing and a dedicated axis strip.
    l,r,t,b=171,486,49,198
    rows=[('NO · m₁ = 0',NH,'point',NAVY,'58.8 meV',78),
          ('IO · m₃ = 0',IH,'point',RED,'98.9 meV',101),
          ('Feldman–Cousins',FC,'limit',INK,'< 53 meV',151),
          ('DESI DR2 · ΛCDM',LCDM,'limit',INK,'< 64.2 meV',172),
          ('DESI DR2 · w₀wₐCDM',W0WA,'limit',INK,'< 163 meV',193)]
    txt(s,18,18,'(a) Neutrino-mass markers and published DESI DR2 bounds',11,weight='bold')
    txt(s,18,33,'circles: exact-rule markers · triangles: published 95% upper limits',10,fill=MID)
    for tick in (0,50,100,150,200):
        x=mx(tick,l,r-l,0,200); ln(s,x,t,x,b,GRID,.6); txt(s,x,216,str(tick),10,'middle')
    box(s,l,t,mx(NH,l,r-l,0,200)-l,b-t,PALE); ln(s,l,t,l,b,INK,.8); ln(s,l,b,r,b,INK,.8)
    txt(s,175,61,'shaded: below the NO floor',10,fill=MID)
    txt(s,18,59,'EXACT RULE',10,weight='bold',fill=MID)
    txt(s,18,134,'PUBLISHED LIMITS',10,weight='bold',fill=MID)
    ln(s,18,116,155,116,'#d5dadd',.8)
    for label,v,kind,col,shown,y in rows:
        txt(s,18,y+4,label,10); x=mx(v,l,r-l,0,200); ln(s,l,y,x,y,col,1.3,None if kind=='point' else '3 2')
        if kind=='point': dot(s,x,y,3.3,col)
        else: add(s,f'<path d="M {n(x)} {n(y)} l 5 -3 l 0 6 z" fill="{col}"/>')
        if v > 140: txt(s,x+10,y-5,shown,10,weight='bold',fill=col)
        else: txt(s,x+7,y+3,shown,10,weight='bold',fill=col)
    txt(s,(l+r)/2,234,'Σmν  (meV)',10,'middle','bold')

def panel_b(s):
    l,r,t,b=58,486,303,397
    txt(s,18,260,'(b) Geometry-only mass profiles',11,weight='bold')
    txt(s,18,274,'BAO + Pantheon+ + ωcb prior + θ*. No CMB lensing or primary-CMB amplitude.',10,fill=MID)
    txt(s,18,288,'Each profile: relative to its own minimum, not a substitute for panel (a).',10,fill=MID)
    for tick in (0,50,100,150,200):
        x=mx(tick,l,r-l,0,200); ln(s,x,t,x,b,GRID,.6); txt(s,x,b+14,str(tick),10,'middle')
    for tick in (0,2,4,6,8,10):
        y=my(tick,t,b-t,0,10); ln(s,l,y,r,y,GRID,.6); txt(s,l-7,y+3,str(tick),10,'end')
    box(s,l,t,r-l,b-t,'none',INK); txt(s,(l+r)/2,b+28,'Σmν  (meV)',10,'middle','bold'); txt(s,18,(t+b)/2,'Δχ²',10,'middle','bold',rotate=-90)
    threshold=my(2.71,t,b-t,0,10); ln(s,l,threshold,r,threshold,MID,1,'4 3'); txt(s,r-3,threshold-4,'2.71 (95%)',10,'end',fill=MID)
    for data,col,dash in ((DL,NAVY,None),(DW,PURPLE,'5 3'),(DT,GREEN,'1.5 2.5')): poly(s,profile(data,l,r,t,b),col,1.8,dash)
    for x,label,col,dash in ((58,'ΛCDM',NAVY,None),(188,'w₀wₐCDM',PURPLE,'5 3'),(331,'two-sheet toy',GREEN,'1.5 2.5')): ln(s,x,443,x+22,443,col,1.8,dash); txt(s,x+27,446,label,10)

def panel_c(s):
    l,r,t,b=74,486,486,592; xlo,xhi,ylo,yhi=-1.08,-.60,-1.30,.25
    txt(s,18,470,'(c) Exact-Λ stance and published DESI DR2 + CMB fits',11,weight='bold')
    for tick in (-1.0,-.9,-.8,-.7,-.6):
        x=mx(tick,l,r-l,xlo,xhi); ln(s,x,t,x,b,GRID,.6); txt(s,x,b+14,f'{tick:.1f}'.replace('-','−'),10,'middle')
    for tick in (-1.2,-.8,-.4,0,.2):
        y=my(tick,t,b-t,ylo,yhi); ln(s,l,y,r,y,GRID,.6); txt(s,l-7,y+3,f'{tick:.1f}'.replace('-','−'),10,'end')
    box(s,l,t,r-l,b-t,'none',INK); txt(s,(l+r)/2,624,'w₀',10,'middle','bold'); txt(s,24,(t+b)/2,'wₐ',10,'middle','bold',rotate=-90)
    div=mx(-1,l,r-l,xlo,xhi); ln(s,div,t,div,b,MID,1,'4 3'); txt(s,div+4,t+11,'w₀ = −1',10,fill=MID)
    ex,ey=mx(-1,l,r-l,xlo,xhi),my(0,t,b-t,ylo,yhi); dot(s,ex,ey,4.5,'#fff',NAVY,1.7); dot(s,ex,ey,1.5,NAVY); txt(s,155,521,'exact Λ: (−1, 0)',10,'start','bold',NAVY)
    for ident,w0,lo0,hi0,wa,loa,hia in FITS:
        x,y=mx(w0,l,r-l,xlo,xhi),my(wa,t,b-t,ylo,yhi); ln(s,mx(w0-lo0,l,r-l,xlo,xhi),y,mx(w0+hi0,l,r-l,xlo,xhi),y,INK,1); ln(s,x,my(wa-loa,t,b-t,ylo,yhi),x,my(wa+hia,t,b-t,ylo,yhi),INK,1); dot(s,x,y,3.2,INK); txt(s,x+7,y-5,ident,10,weight='bold')
    txt(s,310,500,'1 DES-Dovekie',10,fill=MID); txt(s,310,513,'2 Union3.1 (corr.)',10,fill=MID); txt(s,310,526,'3 Unite; bars: quoted 1σ',10,fill=MID)

def write_svg():
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">','<title>Figure 5, compact publication layout</title>','<desc>Three compact panels: neutrino mass markers and bounds, caveated geometry-only profiles, and the exact Lambda stance with DESI DR2 plus CMB fits.</desc>',f'<rect width="{W}" height="{H}" fill="#fff"/>']
    panel_a(s); panel_b(s); panel_c(s); s.append('</svg>'); (OUT/'fig5_data.svg').write_text('\n'.join(s),encoding='utf-8')

def render():
    TEST.mkdir(parents=True, exist_ok=True)
    image_uri = (OUT / 'fig5_data.svg').as_uri()
    (TEST/'fig5_data.html').write_text(f'''<style>@page{{size:{W}pt {H}pt;margin:0}}html,body,img{{margin:0;width:{W}pt;height:{H}pt;display:block}}</style><img src="{image_uri}">''',encoding='utf-8')
    (TEST/'fig5_final_size_test.html').write_text(f'''<style>@page{{size:letter;margin:.45in}}body{{margin:0;font-family:Helvetica,Arial,sans-serif}}h1{{font-size:12pt;margin:0 0 5pt}}p{{font-size:9pt;margin:0 0 10pt;color:#56616b}}img{{display:block;width:{W}pt;height:{H}pt}}</style><h1>Figure 5 spacious V5, final-size test</h1><p>Figure at its 7-inch source width. Essential labels are 10 pt in source and 8.03 pt at the manuscript's 5.6225-inch placement.</p><img src="{image_uri}">''',encoding='utf-8')
    for html,pdf in ((TEST/'fig5_data.html',OUT/'fig5_data.pdf'),(TEST/'fig5_final_size_test.html',TEST/'fig5_final_size_test.pdf')):
        subprocess.run(['google-chrome','--headless','--no-sandbox','--disable-gpu','--no-pdf-header-footer',f'--print-to-pdf={pdf}',f'file://{html}'],check=True,capture_output=True,text=True)
    subprocess.run(['google-chrome','--headless','--no-sandbox','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=2','--window-size=672,840',f'--screenshot={OUT/"fig5_data.png"}',f'file://{OUT/"fig5_data.svg"}'],check=True,capture_output=True,text=True)
    subprocess.run(['pdftocairo','-png','-r','144','-singlefile',str(TEST/'fig5_final_size_test.pdf'),str(TEST/'fig5_final_size_test')],check=True)

if __name__=='__main__': write_svg(); render()
