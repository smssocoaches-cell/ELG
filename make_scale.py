"""Exact-size axial hook-to-pin scale for the default generated CAD.
Print at 100%; attach to SIDE, with position zero at the ruler's front end.
"""
from pathlib import Path
import json,math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("ScaleSans","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("ScaleBold","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
P=Path(__file__).parent
p=json.loads((P/'geometry_checks.json').read_text())['parameters']
L=p['length'];H=min(4,p['thickness']-.8)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{L}mm" height="{H}mm" viewBox="0 0 {L} {H}">',f'<rect width="{L}" height="{H}" fill="white" stroke="#183c49" stroke-width="0.15"/>']
for s in range(math.floor(L)+1):
    d=s+15;long=d%10==0;h=1.6 if long else .9 if d%5==0 else .5
    svg.append(f'<path d="M{s} 0v{h}" stroke="#183c49" stroke-width="0.15"/>')
    if long:svg.append(f'<text x="{s}" y="{H-.25}" font-family="DejaVu Sans" font-size="1.5" text-anchor="middle" fill="#183c49">{d}</text>')
svg.append('</svg>');(P/'ELG_Axial_Draw_Scale.svg').write_text('\n'.join(svg))
c=canvas.Canvas(str(P/'ELG_Axial_Draw_Scale_Print_100pct.pdf'),pagesize=(612,792))
c.setTitle('ELG v0.4 axial hook-to-pin scale - print at 100 percent')
c.setFont('ScaleBold',16);c.drawString(24,758,'ELG v0.4 | Axial draw scale')
c.setFont('ScaleSans',9)
for i,t in enumerate(['PRINT AT 100% / ACTUAL SIZE. Disable Fit to page. Check the 100 mm bar below.',
 'Readout = distance along ruler from hook station to anchor-pin center (mm).',
 'This is not the rubber path length. Pullback extension = loaded reading - relaxed reading.',
 'Attach to the SIDE with segment 1 start at the wooden ruler front end. Values grow rearward.',
 'Overlap successive strips by 10 mm using matching ticks; trim only after checking alignment.']):c.drawString(24,735-i*13,t)
for i,start in enumerate(range(0,math.ceil(L),190)):
    end=min(start+200,L);y=620-i*74
    c.setFont('ScaleBold',9);c.drawString(24,y+19,f'Segment {i+1}: {start:g} to {end:g} mm behind front end | readout {start+15:g} to {end+15:g}')
    c.setLineWidth(.35);c.rect(24,y,(end-start)*mm,H*mm)
    c.setFont('ScaleSans',1.5*mm)
    for s in range(start,math.floor(end)+1):
        d=s+15;h=1.6 if d%10==0 else .9 if d%5==0 else .5;x=24+(s-start)*mm
        c.line(x,y+H*mm,x,y+(H-h)*mm)
        if d%10==0:c.drawCentredString(x,y+.25*mm,str(d))
    if i==0:c.setFont('ScaleSans',8);c.drawString(24,y-15,'FRONT END: readout starts at 15 mm; the pin center is 15 mm beyond the wood.')
c.setFont('ScaleBold',10);c.drawString(24,210,'Size check: the line below must measure exactly 100 mm.')
c.line(24,191,24+100*mm,191)
for x in [24,24+100*mm]:c.line(x,186,x,196)
c.setFont('ScaleSans',9)
for i,t in enumerate(['Default wood length: '+str(L)+' mm. The scale is specific to this anchor geometry.',
 'Align marker center with the selected readout. Keep tape and paper below the top plane.',
 'Ruler axes: rear x = 0, front x = L; hook station = xH; axial reading D = L + 15 - xH.',
 'For actual straight endpoint distance include measured vertical and lateral offsets.',
 'Do not infer elastic force from length; record the rubber ID, relaxed zero and measured load separately.']):c.drawString(24,158-i*14,t)
c.save()
print('Scale SVG and 100% print PDF created.')
