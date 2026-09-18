"""Publication-scale redraws for Paper 2 V3 Supplement Figures 1--4.

These files deliberately contain only information that must be read in the
figure.  Captions carry the sources and repeated prose.  Coordinates are in
hundredths of an inch: at width 7 in, 12.5 units are exactly 9 pt.
"""
from pathlib import Path
from html import escape
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pub/paper2"
TEST = ROOT / "tmp/supp_figure_release_tests"
OUT.mkdir(parents=True, exist_ok=True)
TEST.mkdir(parents=True, exist_ok=True)

W = 700
INK, GRAY, LIGHT, PALE = "#111111", "#535353", "#c7c7c7", "#f2f2f2"
HATCH = "url(#hatch)"
MIN = 12.5  # 9 pt at a 7-inch-wide output

def start(h, desc):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" width="7in" height="{h/100:.2f}in" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(desc)}" font-family="Arial, Helvetica, sans-serif">
<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#9a9a9a" stroke-width="1.4"/></pattern></defs><rect width="700" height="{h}" fill="white"/>''']

def text(s, x, y, value, size=MIN, anchor="start", fill=INK, weight="normal", italic=False):
    attr = " font-style=\"italic\"" if italic else ""
    s.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size:.1f}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{attr}>{value}</text>')

def line(s, x1, y1, x2, y2, width=1.2, stroke=INK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>')

def box(s, x, y, w, h, fill="none", stroke=INK, width=1.1):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

def end(s, name):
    s.append("</svg>")
    live_name = name.replace("_textbook", "")
    (OUT / f"{live_name}.svg").write_text("\n".join(s), encoding="utf-8")

def j0(z):
    return math.sin(z) / z if z else 1.0

def j1(z):
    return math.sin(z)/z**2 - math.cos(z)/z if z else 0.0

def power10(exponent):
    """Unicode exponent label for SVG text, e.g. 10⁻⁴ rather than 10⁻4."""
    superscript = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return "10" + str(exponent).translate(superscript)

def p_scalar(k, eta):
    x = k*eta/math.sqrt(3.0)
    phi = 3.0*j1(x)/x if x else 1.0
    return math.sqrt(2.0)/3.0*k*k*abs(phi)*eta*eta

def p_tensor(k, eta):
    z = k*eta
    h, hp = j0(z), -k*j1(z)
    a = -(2.0/eta)*hp - 2.0*k*k*h
    return eta*eta*math.sqrt((a*a + 4.0*k*k*hp*hp)/6.0)

def heading(s, number, title, subtitle=None):
    text(s, 28, 29, f"Figure {number}. {title}", 17, weight="bold")
    if subtitle:
        text(s, 28, 48, subtitle, MIN, fill=GRAY)

def fig1():
    h=580; s=start(h, "Crease dictionary: five possible locations for a CPT identification")
    heading(s, 1, "Where a fold can sit, and what it costs", "Shaded rows are consistent. Hatching marks a failed smooth one-copy fold.")
    xs=[24,132,315,545,676]; headers=["fixed set", "identification", "price", "verdict"]
    for x, head in zip(xs[:-1], headers): text(s,x+6,78,head,13,weight="bold")
    y0, rh=88, 88
    rows=[
      ("no crease", ["elliptic quotient dS/A", "free action: A: x → −x"], ["no crease at all; local correlators", "are the cover’s restriction"], ["invisible locally", "at tree level"], True, "free"),
      ("codimension 1", ["bang mirror", "t → −t fixes the spatial slice"], ["mirror boundary condition; no tension;", "positivity needs a restricted atlas"], ["best-studied", "fold"], True, "bang"),
      ("codimension 2", ["modular fold dS/J (TP₁)", "fixes the bifurcation 2-sphere"], ["Rindler at 2Tᵁ; Δρ = 1/(32π²d⁴),", "divergent at the crease"], ["dead as a smooth", "one-copy fold"], False, "sphere"),
      ("codimension 1", ["brane at fixed y", "+−+ three-brane model"], ["every dS crease: negative", "tension brane (Karch–Randall", "eq. 13, NEC); it carries a ghost"], ["not a healthy", "fold"], False, "brane"),
      ("two copies", ["glue at the bifurcation sphere", "second sheet is the J-image"], ["eternal black hole in the", "Hartle–Hawking state"], ["textbook:", "thermofield", "dynamics"], True, "bridge"),
    ]
    for i,(fixed, ident, cost, verdict, viable, icon) in enumerate(rows):
        y=y0+i*rh; box(s,24,y,652,rh, PALE if viable else "#fbfbfb", LIGHT, .8)
        if not viable:
            # Preserve the failed-fold cue without putting hatch strokes under
            # dense mathematical and bibliographic text.
            box(s,24,y,9,rh,HATCH,"none",0)
        for x in xs[1:-1]: line(s,x,y,x,y+rh,.7,LIGHT)
        # simple monochrome symbols
        cx=78
        if icon=="free": line(s,45,y+43,111,y+43,2,GRAY); line(s,45,y+58,111,y+58,1.6,LIGHT,"4 3")
        elif icon=="bang": line(s,cx,y+20,cx,y+56,2.5,INK); line(s,45,y+43,111,y+43,1.3,GRAY)
        elif icon=="sphere":
            s.append(f'<circle cx="{cx}" cy="{y+42}" r="10" fill="white" stroke="{INK}" stroke-width="1.5"/>')
            for a in range(0,360,60):
                x=cx+18*math.cos(math.radians(a)); yy=y+42+18*math.sin(math.radians(a)); line(s,cx,y+42,x,yy,.8,GRAY)
        elif icon=="brane":
            line(s,49,y+16,49,y+54,2,GRAY); line(s,107,y+16,107,y+54,2,GRAY); line(s,cx,y+14,cx,y+56,3,INK)
        else:
            # two exteriors joined through a throat, distinct from colour
            s.append(f'<path d="M42 {y+32} C61 {y+14}, 95 {y+14}, 114 {y+32} L114 {y+54} C95 {y+72},61 {y+72},42 {y+54}Z" fill="white" stroke="{INK}" stroke-width="1.5"/>')
            line(s,cx,y+29,cx,y+57,1,GRAY)
        text(s,78,y+76,fixed,12.5,"middle",weight="bold")
        for j,v in enumerate(ident): text(s,141,y+29+j*18,v,12.5, fill=INK if j==0 else GRAY, weight="bold" if j==0 else "normal")
        for j,v in enumerate(cost): text(s,324,y+29+j*18,v,12.5)
        for j,v in enumerate(verdict): text(s,554,y+29+j*18,v,12.5,weight="bold" if j==0 else "normal")
    text(s,28,563,"In the two-copy row, the cosmological-horizon analogue is the antipodal static patch.",12.5,fill=GRAY)
    end(s,"fig1_dictionary_textbook")

def fig2():
    h=500; s=start(h,"Bel–Robinson complexity near the bang for exact even scalar and tensor modes")
    heading(s,2,"The bang as a complexity minimum", "Positive Bel–Robinson complexity P. Solid: CPT-regular; dashed: irregular, no CPT.")
    text(s,28,72,"Regular CPT modes: P ∝ η². Irregular no-CPT modes: P ∝ |η|⁻¹.",12.5,fill=GRAY)
    # Shared line key sits in its own band, not over either dataset.
    line(s,58,94,91,94,2.6,INK); text(s,99,98,"regular scalar, CPT",12.5)
    line(s,58,115,91,115,1.2,INK); text(s,99,119,"regular tensor, CPT (×¼)",12.5)
    line(s,355,94,388,94,2.6,INK,"7 5"); text(s,396,98,"irregular scalar, no CPT",12.5)
    line(s,355,115,388,115,1.2,INK,"7 5"); text(s,396,119,"irregular tensor, no CPT",12.5)
    # left logarithmic slope panel
    x,y,w,ph=58,132,270,218; box(s,x,y,w,ph)
    s.append(f'<defs><clipPath id="fig2-left-clip"><rect x="{x}" y="{y}" width="{w}" height="{ph}"/></clipPath></defs>')
    for val,lab in [(-5,"10⁻⁵"),(-4,"10⁻⁴"),(-3,"10⁻³"),(-2,"10⁻²")]:
        xx=x+(val+5)/3*w; line(s,xx,y+ph,xx,y+ph+5,.8); text(s,xx,y+ph+20,lab,12.5,"middle")
    ymin,ymax=-8.0,2.5
    Ylog=lambda val: y+ph-(val-ymin)/(ymax-ymin)*ph
    for val in [-8,-6,-4,-2,0,2]:
        yy=Ylog(val); line(s,x-5,yy,x,yy,.8); text(s,x-10,yy+4,power10(val),12.5,"end")
    text(s,x+w/2,y+ph+44,"|conformal time η|",13,"middle",weight="bold")
    text(s,24,y+ph/2,"P(η)",13,"middle",weight="bold")
    # curves exactly power-law visual encodings; data definition k=20 retained
    for regular, dash, thick, offset in [(True,None,2.6,0.0),(True,None,1.2,-0.22),(False,"7 5",2.6,0.0),(False,"7 5",1.2,0.22)]:
        pts=[]
        for i in range(120):
            xv=-5+3*i/119; yv=(2*xv+3 if regular else -xv-3)+offset
            pts.append(f"{x+(xv+5)/3*w:.1f},{Ylog(yv):.1f}")
        s.append(f'<polyline clip-path="url(#fig2-left-clip)" points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="{thick}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
    # Redraw the frame over clipped curves for a crisp textbook boundary.
    box(s,x,y,w,ph)
    text(s,x+14,y+22,"(a) scaling, k = 20",13,weight="bold")
    # right: exact regular scalar and tensor curves on the two sheets
    rx,ry,rw,rh=388,132,260,218; box(s,rx,ry,rw,rh)
    mid=rx+rw/2; line(s,mid,ry+52,mid,ry+rh-25,1.5,INK,"5 4")
    text(s,rx+14,ry+22,"(b) regular modes, k = 20",13,weight="bold")
    text(s,mid,ry+36,"bang, η = 0",12.5,"middle",weight="bold")
    ex, k = 0.30, 20.0
    X2=lambda eta: rx+(eta+ex)/(2*ex)*rw
    peak=max(p_scalar(k, eta) for eta in [1e-4+i*(ex-1e-4)/400 for i in range(401)])
    Y2=lambda val: ry+rh-val/(1.22*peak)*rh
    for lab, fun, width in [("scalar",p_scalar,2.5),("tensor",p_tensor,1.3)]:
        pts=[]
        for i in range(801):
            eta=-ex+2*ex*i/800
            pts.append(f"{X2(eta):.2f},{Y2(fun(k,max(abs(eta),1e-6))):.2f}")
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="{width}"/>')
    for eta in (-.30,-.15,0,.15,.30):
        line(s,X2(eta),ry+rh,X2(eta),ry+rh+5,.8)
        text(s,X2(eta),ry+rh+20,f"{eta:g}",12.5,"middle")
    text(s,rx+15,ry+rh-14,"anti-verse ←",12.5,weight="bold")
    text(s,rx+rw-15,ry+rh-14,"→ this-verse",12.5,"end",weight="bold")
    text(s,rx+rw/2,ry+rh+44,"conformal time η",13,"middle",weight="bold")
    text(s,rx+rw/2,416,"P/Pmax is exactly even and tends to zero at the bang.",12.5,"middle",weight="bold")
    text(s,28,444,"Regular modes vanish from both sides. Panel (a) scales the tensor by ×¼; panel (b) normalises to its scalar maximum.",12.5,fill=GRAY)
    text(s,28,466,"Linear order only: the metric is degenerate at η = 0, so P(0) = 0 is a two-sided limit, not a value at the bang.",12.5,fill=GRAY)
    end(s,"fig2_janus_textbook")

def fig3():
    h=480; s=start(h,"Discrete curvature values compared with Planck and DESI constraints")
    heading(s,3,"Discrete curvature against 2026 data", "All listed allowed values are negative. Filled ticks are retained by RP³; crossed ticks are deleted.")
    x,y,w,ph=250,94,394,168; box(s,x,y,w,ph)
    mn,mx=-.085,.008
    X=lambda v:x+(v-mn)/(mx-mn)*w
    # ranges: uncertainty bands with slash texture and named vertical central values
    for val,sd,lab,fill in [(-.0106,.0065,"Planck 2018 alone",PALE),(.0023,.0011,"DESI DR2 + CMB",HATCH)]:
        box(s,X(val-sd),y+1,max(2,X(val+sd)-X(val-sd)),ph-2,fill,"none",0)
        line(s,X(val),y+2,X(val),y+ph-2,1.7,INK)
    for tick in [-.08,-.06,-.04,-.02,0]:
        line(s,X(tick),y+ph,X(tick),y+ph+5,.8); text(s,X(tick),y+ph+20,f"{tick:.3f}" if tick else "0",12.5,"middle")
    text(s,x+w/2,y+ph+31,"curvature ΩK",13,"middle",weight="bold")
    # Keep the band key in the empty strip above the plot.  The old second
    # entry collided with the 2024 S³ row label at the left plot edge.
    text(s,28,66,"data bands",13,weight="bold")
    box(s,28,77,28,12,PALE,"none",0); line(s,42,77,42,89,1.5,INK)
    text(s,66,88,"Planck: −0.0106 ± 0.0065",12.5)
    box(s,28,97,28,12,HATCH,"none",0); line(s,42,97,42,109,1.5,INK)
    text(s,66,108,"DESI: +0.0023 ± 0.0011",12.5)
    # (value, N, label); row 2025 explicit all original numbers
    rows=[("2024 S³",[(-.0094031908,""),(-.0033352275,""),(-.0015859689,""),(-.0009135939,""),(-.0005911902,""),(-.0004130203,""),(-.0003045443,""),(-.0002337155,""),(-.0001849621,""),(-.0001499922,""),(-.0001240663,""),(-.0001043178,""),(-.0138049774,"")]),
          ("2025 S³",[(-.076,"3"),(-.039,"4"),(-.024,"5"),(-.016,"6"),(-.012,"7")]),
          ("elliptic RP³",[(-.076,"3"),(-.024,"5"),(-.012,"7")])]
    for i,(lab,vals) in enumerate(rows):
        yy=y+52+i*43; text(s,x-14,yy+4,lab,12.5,"end",weight="bold")
        line(s,x,yy,x+w,yy,.5,LIGHT)
        for val,n in vals:
            line(s,X(val),yy-10,X(val),yy+10,2.8,INK)
            if n: text(s,X(val),yy-16,n,12.5,"middle")
    # deletion marks in elliptic row for original 4 and 6
    yy=y+52+2*43
    for val,n in [(-.039,"4"),(-.016,"6")]:
        line(s,X(val)-7,yy-8,X(val)+7,yy+8,1.7,INK); line(s,X(val)-7,yy+8,X(val)+7,yy-8,1.7,INK)
        text(s,X(val),yy+27,f"N = {n} deleted",12.5,"middle")
    text(s,28,314,"2025 set: N = 3, 4, 5, 6, 7 gives ΩK = −0.076, −0.039, −0.024, −0.016, −0.012.",12.5)
    text(s,28,336,"Nearest allowed value: N = 7, ΩK = −0.012, 13.0σ from DESI DR2 + CMB, but 0.2σ from Planck alone.",12.5)
    text(s,28,358,"The 2025 χ² minimum N = 4 is 37.5σ from DESI DR2 + CMB and is exactly the value the elliptic reading forbids.",12.5)
    text(s,28,393,"No compact reading admits positive ΩK. Exact flatness is 2.09σ from DESI DR2 + CMB.",12.5,fill=GRAY)
    end(s,"fig3_curvature_textbook")

def fig4():
    h=530; s=start(h,"Primordial tilt mechanism prediction compared with eight CMB datasets")
    heading(s,4,"Primordial tilt against 2025–26 CMB data", "All estimates are base-ΛCDM. Circles show the central estimate; bars show ±1σ.")
    x,y,w,ph=220,94,270,282; box(s,x,y,w,ph); mn,mx=.938,.9825; X=lambda v:x+(v-mn)/(mx-mn)*w
    for v in [.940,.950,.960,.970,.980]:
        line(s,X(v),y+ph,X(v),y+ph+5,.8); text(s,X(v),y+ph+20,f"{v:.3f}",12.5,"middle")
    for v,dash,lab in [(.957888,None,"eq. 16: 0.957888"),(.9498,"5 4","amplitude: 0.9498")]:
        line(s,X(v),y,X(v),y+ph,1.7,INK,dash)
    line(s,30,70,58,70,1.7,INK); text(s,66,74,"solid: dimension-zero nₛ = 0.957888",12.5,weight="bold")
    line(s,30,86,58,86,1.7,INK,"5 4"); text(s,66,90,"dashed: amplitude branch nₛ = 0.9498",12.5,weight="bold")
    text(s,548,88,"nₛ ± 1σ",12.5,"middle",weight="bold")
    text(s,678,88,"vs solid (σ)",12.5,"end",weight="bold")
    dat=[("Planck 2018 TT,TE,EE+lowE+lensing",.9649,.0042,"+1.67σ"),("ACT DR6 alone",.9666,.0077,"+1.13σ"),("SPT-3G D1 alone",.9510,.0110,"−0.63σ"),("P-ACT",.9709,.0038,"+3.42σ"),("CMB-SPA",.9679,.0033,"+3.03σ"),("P-ACT-LB",.9743,.0034,"+4.83σ"),("P-ACT-LB2",.9752,.0030,"+5.77σ"),("CMB-SPA + DESI DR2",.9726,.0028,"+5.25σ")]
    for i,(name,v,e,z) in enumerate(dat):
        yy=y+23+i*34; text(s,x-12,yy+4,name,12.5,"end")
        line(s,max(x,X(v-e)),yy,min(x+w,X(v+e)),yy,1.6); line(s,max(x,X(v-e)),yy-4,max(x,X(v-e)),yy+4,1.2); line(s,min(x+w,X(v+e)),yy-4,min(x+w,X(v+e)),yy+4,1.2)
        s.append(f'<circle cx="{X(v):.1f}" cy="{yy}" r="3.4" fill="{INK}"/>')
        text(s,x+w+8,yy+4,f"{v:.4f} ± {e:.4f}",12.5,weight="bold" if z[0]!="−" and float(z[1:-1])>=3 else "normal")
        text(s,678,yy+4,z,12.5,"end",weight="bold" if z[0]!="−" and float(z[1:-1])>=3 else "normal")
    text(s,x+w/2,y+ph+45,"scalar spectral index nₛ",13,"middle",weight="bold")
    text(s,28,437,"Prediction: nₛ = 1 − 7α₃(Mₚ)/π = 0.957888. Amplitude at N₀ = 36 with Standard-Model couplings demands nₛ = 0.9498.",12.5)
    text(s,28,459,"The two values are not on the same one-parameter locus. This is posterior tension with the mechanism,",12.5,fill=GRAY)
    text(s,28,477,"not a formal exclusion.",12.5,fill=GRAY)
    text(s,28,503,"The CPT-symmetric structure fixes no tilt. Freeing Nₑff removes the tension, but needs ΔNₑff ≈ −0.35 to −0.82.",12.5,fill=GRAY)
    end(s,"fig4_tilt_textbook")

def render_assets():
    heights = {
        "fig1_dictionary": 580,
        "fig2_janus": 500,
        "fig3_curvature": 480,
        "fig4_tilt": 530,
    }
    for name, height in heights.items():
        svg = OUT / f"{name}.svg"
        height_pt = height * 0.72
        pdf_html = TEST / f"{name}_pdf.html"
        png_html = TEST / f"{name}_png.html"
        uri = svg.as_uri()
        pdf_html.write_text(
            f'<style>@page{{size:504pt {height_pt:.2f}pt;margin:0}}'
            f'html,body,img{{margin:0;width:504pt;height:{height_pt:.2f}pt;display:block}}</style>'
            f'<img src="{uri}">',
            encoding="utf-8",
        )
        png_height = 2 * height
        png_html.write_text(
            f'<style>html,body,img{{margin:0;width:1400px;height:{png_height}px;display:block;overflow:hidden}}</style>'
            f'<img src="{uri}">',
            encoding="utf-8",
        )
        subprocess.run(
            [
                "google-chrome", "--headless", "--no-sandbox", "--disable-gpu",
                "--no-pdf-header-footer", f"--print-to-pdf={OUT / (name + '.pdf')}",
                f"file://{pdf_html}",
            ],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            [
                "google-chrome", "--headless", "--no-sandbox", "--disable-gpu",
                "--hide-scrollbars", f"--window-size=1400,{png_height}",
                f"--screenshot={OUT / (name + '.png')}", f"file://{png_html}",
            ],
            check=True, capture_output=True, text=True,
        )


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); render_assets()
