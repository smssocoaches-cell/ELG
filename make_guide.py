from pathlib import Path
import json,math
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Image,PageBreak,Spacer,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from launch_settings import dial_pitch
P=Path(__file__).parent
r=json.loads((P/'geometry_checks.json').read_text());p=r['parameters'];L=p['length'];W=p['width'];T=p['thickness'];VL=p['vial_length'];VD=p['vial_diameter']
for name,file in [('S','DejaVuSans.ttf'),('B','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('S',normal='S',bold='B',italic='S',boldItalic='B')
NAVY='#183c49';GOLD='#e3ad47';GRAY='#40545e'
body=ParagraphStyle('Body',fontName='S',fontSize=9.2,leading=13.6,spaceAfter=8,textColor=HexColor(NAVY))
small=ParagraphStyle('Small',parent=body,fontSize=8,leading=11,spaceAfter=6)
headstyle=ParagraphStyle('Heading',parent=body,fontName='B',fontSize=11.5,leading=15,spaceBefore=7,spaceAfter=7)
cell=ParagraphStyle('Cell',parent=small,spaceAfter=0)
story=[]
def para(t,sm=False):story.append(Paragraph(t,small if sm else body))
def head(t):story.append(Paragraph(t,headstyle))
def table(rows,widths):
    data=[[Paragraph(str(t),cell) for t in row] for row in rows]
    q=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
    q.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e7eceb')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.8,HexColor(NAVY)),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#c7d0d1'))]))
    story.extend([q,Spacer(1,9)])
titles=['What v0.4 adds','Print list and upgrade','Hardware and kit packing','Assembly sequence','Calibration and angle settings','Draw reference and glider alignment','Bench checks and launch record']
def page(c,d):
    c.saveState();c.setFillColor(HexColor(NAVY));c.rect(0,714,612,78,fill=1,stroke=0)
    c.setFillColor(HexColor(GOLD));c.setFont('B',9);c.drawString(36,763,'SMS SCIENCE OLYMPIAD | ELG LAUNCHER v0.4')
    c.setFillColor(white);c.setFont('B',19);c.drawString(36,734,titles[min(d.page-1,6)])
    c.setFillColor(HexColor(GRAY));c.setFont('S',7.3);c.drawString(36,22,'Prototype | Physical fit, measurement accuracy and load capacity remain unverified.')
    c.drawRightString(576,22,str(d.page));c.restoreState()
para('This revision adds a dedicated <b>numbered bank dial</b>, a larger numbered pitch scale, a defined rubber pullback reference and a removable alignment sight. Each vial retains its own calibration adjustment. The entire ruler top remains exposed.')
story.append(Image(str(P/'ELG_Launcher_v04_Preview.png'),width=540,height=405))
table([['Reading / feature','How to use it'],['Bank: -30 to +30 degrees','Set the bank rotor with its main M4 pivot, lock it, then center its bubble by orienting the ruler.'],['Pitch: 0 to 90 degrees','Set the corrected pitch value from page 5; center both bubbles.'],['Draw / alignment','Read axial hook-to-pin length on the side scale; subtract the relaxed reading for pullback extension. Sight is for unloaded setup only.']],[143,397])
para(f'Current dimensions: wood {W:g} x {T:g} x {L:g} mm; vials {VL:g} x {VD:g} mm. This download includes files and instructions. Source and pack the hardware on page 3 to make a complete physical kit. The user supplies the yardstick.',True)
story.append(PageBreak())

table([['Part','Qty','v0.3 upgrade / function'],['01 + 02 + 03','1 each','Reuse: grip fixed jaw, moving jaw and handle.'],['04 + 05','1 each','Reuse: anchor nose and moving jaw.'],['06','1','Reuse: marker fixed jaw.'],['07','1','REPRINT: marker jaw with sight support and clamp-bolt access.'],['08','1','Reuse: gauge fixed jaw.'],['09','1','REPRINT: bank dial and support integrated with moving jaw.'],['10','1','REPRINT: numbered pitch bracket.'],['11','1','Reuse: pitch rotor calibration base.'],['12 + 13','1 each','Reuse / print first: ruler fit coupon pair.'],['14','2','Reuse both: identical calibration vial carriers.'],['15','1','NEW: bank rotor; identical geometry to part 11.'],['16','1','NEW: removable setup sight with 20 mm height adjustment.']],[62,45,433])
head('Five-piece upgrade')
para('For an existing v0.3 launcher, print <b>07, 09, 10, 15 and 16 once each</b>. Transfer the old roll vial, carrier and M3 hardware to 15. A spare v0.3 part 11 can substitute for 15. Full set: <b>16 STL files / 17 physical prints including coupons</b>.')
head('Print and fit')
para('Print 12 + 13 first and try them on the actual ruler using one clamp bolt. The open-top jaws have 0.6 mm total fitting allowance and close symmetrically; the nominal gap between bottom halves is 0.6 mm when seated on the wood. Reject a fit that bottoms out before gripping or requires forced bending.')
para('Starting profile: PETG, 0.20 mm layers, 5-6 walls, 40-50% infill using a tested filament profile. These are starting choices, not a strength rating. STLs are in millimeters at bed Z=0. 03, 10 and 16 have deliberate print rotations. Inspect slicer previews: 07/09 need supports beneath their bridges and side structures; support the horizontal bores as needed. Keep support scars off dial mating surfaces.',True)
para('Clean bores and nut pockets without forcing screws. Paint-fill the engraved numbers and ticks with contrasting color and wipe the faces clean. The 5-degree ticks provide a reference; scale spacing does not establish accuracy. Do not globally resize STL files because hardware holes would change.',True)
story.append(PageBreak())

table([['Hardware','Full kit quantity / dimensions'],['Cross clamps','7 x M4 x '+str(int(r['clamp_bolt_length_mm']))+' mm bolts; 7 M4 nuts; 14 washers, 1 mm thick, <=9 mm OD. Reuse one for the fit coupon.'],['Grip / pitch bracket mounts','4 x M4 x 25 mm button-head screws; heads <=3 mm high and <=7.6 mm diameter. 4 M4 nuts + 4 washers, 1 mm, <=9 mm OD.'],['Two main dial pivots','2 x M4 x 20 mm button-head bolts; 2 M4 nuts; 2 nylon spacers (1 mm, <=9 mm OD); 4 metal washers (1 mm, <=9 mm OD).'],['Two vial calibrators','4 x M3 x 10 mm button-head screws, head <=5.7 mm diameter x 2.4 mm high; 4 standard M3 hex nuts (~5.5 mm AF x 2.4 mm); 4 nylon spacers + 4 metal washers (each 1 mm, <=7 mm OD).'],['Removable sight','2 x M3 x 12 mm button-head screws; 2 M3 nuts; 4 metal washers (1 mm, <=7 mm OD).'],['Bubble vials','2 cylindrical vials, '+str(VL)+' mm long x '+str(VD)+' mm diameter. 4 cable ties, 2.5 mm wide; thin removable bedding if needed.'],['Elastic anchor','1 smooth 4 mm diameter x 40 mm pin; 12 mm sleeve, 4.2 mm ID / 6 mm OD; 2 shaft collars, 4 mm bore, <=8 mm OD x <=6 mm wide. Recess collar set screws.'],['Other kit items','Appropriate glider elastic; side-scale print; contrasting paint/marker; printed parts and this guide. No specific elastic load or dimension is certified here.'],['User / bench supplies','Straight wooden yardstick; actual glider; hex keys/wrenches; caliper; trusted level/angle gauge; stable support blocks; ruler/tape; eye protection.']],[133,407])
head('Upgrade hardware only')
para('Add the bank-pivot set (one M4 x 20 bolt, one nut, one nylon spacer, two metal washers) and the two-screw sight set. Transfer all four M3 carrier screws and both existing vials. Confirm the smooth pin and retainers match the updated 40 mm pin arrangement; shorter retained pins need a separate check.')
para('Hardware dimensions vary. Measure actual head, washer, nut and collar envelopes before assembly. Nut pockets in the carrier bases are about 5.67 mm across flats x 2.55 mm deep. Test the fits before printing the complete set.',True)
story.append(PageBreak())

para('<b>1. Grip.</b> Attach 03 beneath 01 with two recessed M4 x 25 screws at x = +/-22 mm. Use washers and nuts underneath. Heads must remain below the ruler seat. Add 02 and two cross-clamp screws. Locate the grip center 230 mm from the rear wooden end.')
para('<b>2. Anchor.</b> Fit 04 + 05 with two cross screws at center x = L - 24 mm. Push the nose stop squarely against the wooden front end, then tighten evenly. Fit the sleeve between the two ears and the 40 mm smooth pin through both ears. Secure one collar on each end with at least 1 mm clearance to the outer ear faces; recess the set screws. The pin center is 15 mm beyond the wood and 4 mm above its top.')
para('<b>3. Gauge base.</b> Attach 10 beneath 08 with two M4 x 25 screws at x = +/-8 mm before seating the wood. Join 08 and 09 with two cross screws. Locate the gauge center 50 mm from the rear end. Its dials hang beside/below the ruler; none of the hardware may cross the top surface.')
para('<b>4. Dial rotors.</b> Insert two M3 nuts into the rear pockets of each of 11 and 15 before installing them. Use the M4 pivot stack shown below. Fit 11 to pitch bracket 10 and 15 to bank bracket 09. Leave the pivots just loose enough to set angles; lock them before use.')
table([['From dial front toward rear','Stack order'],['Main pivot, both dials','M4 head -> metal washer -> 4 mm rotor -> 1 mm nylon spacer -> 6 mm fixed dial -> rear metal washer -> M4 nut. M4 x 20 enters from the front.'],['Vial carrier, at both screws','M3 head -> metal washer -> 4 mm carrier -> 1 mm nylon spacer -> 4 mm rotor with captured rear nut. M3 x 10 enters from front.']],[170,370])
para('<b>5. Vial carriers.</b> Install each 14 with its two M3 screws, spacers and washers. Secure each vial with two cable ties routed through the 3.2 x 1.6 mm passages below it. Keep the vial center marks visible and the tie heads to the side. Snug only; do not crush the vial or distort the carrier.')
para('<b>6. Marker and sight.</b> Fit 06 + 07 using the single cross screw. Example marker center is x = L - 400 mm, giving D = 415 mm. Install 16 outside the support rail, with washers against both sides of the joint and the M3 x 12 screws through the vertical slots. Nuts sit on the inner side. Its lower sight line adjusts from T + 5 to T + 25 mm above the ruler-bottom datum (5-25 mm above the ruler top).')
para('<b>7. Finish.</b> Install the side scale below the top plane, calibrate both vials (page 5), and mark dial/trim witness lines. Verify wrench access, full nut engagement and clearance after tightening. Part 16 is removed before any elastic-tension test or launch; keep its loose screws/nuts together.',True)
story.append(PageBreak())

head('Calibrate zero independently from setting launch angles')
para('Support the ruler on blocks so none of its projecting fittings touch the bench. Use a trusted independent instrument on the ruler top to establish zero elevation and zero bank. Tighten the wood clamps to their normal seating first. Set BOTH numbered dials to zero and lock their M4 pivots.')
para('For each vial, loosen its two M3 screws slightly. Rotate the carrier about the round hole until the bubble centers, then gently tighten the curved-slot screw and the pivot screw while observing the bubble. Designed trim is +/-8 degrees. Add a witness line; do not use these screws for normal launch settings. Repeat after three lift/reseat cycles and after changing a vial or clamp.')
head('Set both dials, then orient the ruler until both bubbles center')
para('Bank is rotation about the long ruler axis. Positive bank raises the bank-bracket side (+Y) when facing the anchor. Set the bank dial to the desired value phi. At nonzero bank, the pitch bubble is coupled to bank: for desired ruler elevation theta, set pitch dial p = atan2[sin(theta), cos(theta) x cos(phi)]. Angles use the same units; the result below is in degrees.')
rows=[['Desired elevation','Bank 0','Bank +/-10','Bank +/-20','Bank +/-30']]
for t in [30,45,60,75,85]:rows.append([str(t)+' deg']+[f'{dial_pitch(t,b):.1f}' for b in [0,10,20,30]])
table(rows,[132,102,102,102,102])
para('<b>Example:</b> for 60-degree elevation and +20-degree bank, set bank +20 and pitch approximately 61.5. Lock both M4 pivots, then orient the ruler until both bubbles center. Check actual elevation and bank with the independent reference. Values between the 5-degree ticks require interpolation; do not assume tenths-of-a-degree mechanical accuracy.')
para('Bank sensitivity decreases as the ruler approaches vertical; exactly vertical cannot establish bank from gravity. The dial can geometrically reach 90 degrees, but that is not a validated two-angle measurement pose. Choose a usable flight setting by bench verification.',True)
para('The helper <b>launch_settings.py</b> reproduces the table. Its ideal geometric relation was checked against an independent 3D rotation of both vial axes. Vial sensitivity, play and calibration errors remain physical quantities to measure.',True)
head('What the angle readings mean')
para('These are launcher-orientation settings. They do not measure aerodynamic angle of attack, which depends on wing chord and incoming airflow. The sight can document a glider reference relative to the ruler; use that same reference on subsequent launches. <link href="https://www.grc.nasa.gov/WWW/K-12/Aero2000/studweb/glossary/aoa.html" color="#276079">NASA angle-of-attack definition</link>.',True)
story.append(PageBreak())

head('A length reference you can reproduce')
para('Use coordinates increasing toward the nose: rear wood end x = 0, front wood end x = L, anchor-pin center x = L + 15. If the glider hook is at station xH, the <b>axial hook-to-pin length is D = L + 15 - xH</b>. The included side scale displays D directly. Align the marker center notch with the desired value, then align the hook with that station.')
para('Print the separate scale PDF at 100% / Actual size. Check its 100 mm test bar with a ruler. Cut along strip borders, overlap adjacent segments by 10 mm using identical ticks, and put segment 1 at the FRONT wooden end. Values increase toward the rear. Attach below the top plane. Use the open viewing notch in part 07 to see the strip at the marker center; the ruler top remains readable and its reading can always be converted using D = L + 15 - xH.')
para('For the exact elastic/hook combination, note the just-taut relaxed hook reading D0 using negligible tension and a recorded hook height. Record loaded D. <b>Axial pullback extension = D - D0.</b> Example: D0 = 160 mm and D = 415 mm gives 255 mm axial pullback. This is not total rubber-loop length, stretch ratio or a force measurement.')
para('If the hook and pin are at different heights or lateral positions, actual straight endpoint distance is sqrt[D^2 + (zH-zA)^2 + (yH-yA)^2]. Rubber contact around the sleeve and at the hook adds its own geometry. Keep those offsets and contact locations consistent; directly measure the rubber working span if that quantity is required.',True)
head('Use the removable sight to establish the glider reference')
para('<b>Unloaded setup only.</b> With the ruler supported and level, hold the glider in its chosen hand-launch posture, above the ruler. Choose two fixed fuselage reference points roughly 60-80 mm apart; mark the ruler centerline in ink and align the fuselage above it from the same viewing direction.')
para('Set the sight height so its lower horizontal line matches those two reference points in side view; its center vertical index identifies the hook station. Record the glider ID, chosen points, hook height and their ruler-relative alignment. The equal-height line is a parallel-reference aid; it does not assume the fuselage line equals the wing chord. For a chosen nonparallel posture, record both point heights separately.')
para('Transfer visible alignment witness marks to the glider/ruler side as appropriate. Remove 16 and its loose hardware before stretching. Reproduce the posture using the recorded marks and hand grip; recheck on the bench periodically. The sight does not constrain the glider during a launch or guarantee its bank. Check wing/tail clearance with the actual glider through its intended release motion.',True)
head('Before release')
para('Same glider and rubber -> sight removed -> retained anchor/clamps -> chosen D -> corrected pitch and bank settings -> both bubbles centered -> glider aligned to its recorded marks -> consistent hand release. Record any slip, contact or release variation.',True)
story.append(PageBreak())

head('Bench acceptance before flight trials')
table([['Check','Record / action'],['Top and grip','Straightedge across full ruler top; no part/hardware crosses it. Check side-clamp lift retention and nose seating under low tension.'],['Angles','Check zero and intended combined settings with an independent reference. Record the measured error and three reseating results. Recheck after tightening, movement or a bump.'],['Pin and glider path','Verify both collars are secure, sleeve is smooth and rubber remains seated. With sight removed, move the actual glider through the release path without tension; then begin low-tension trials.'],['Repeatability','Choose a tolerable variation for your experiment. Repeat the same setup; record draw, measured angles and flight result. Tighten or redesign if settings drift.'],['Stop conditions','Stop on cracks, clamp slip, pin movement, vial/carrier movement or glider contact. Geometry checks do not establish allowable force, torque, fatigue life or print strength.']],[126,414])
head('Calibration / launch record')
table([['Field','Value'],['Date / operator / reference instrument',''],['Ruler dimensions / glider ID / rubber ID',''],['Relaxed D0 / loaded D / extension D-D0',''],['Hook height / two fuselage reference points',''],['Desired elevation / bank / corrected pitch dial',''],['Measured elevation / bank / reseating spread',''],['Sight removed / pin retained / clamp witness marks',''],['Flight time / observed release variation / changes','']],[279,261])
para('Included digital checks cover single valid CAD solids, watertight positive-volume STL meshes, default assembly intersections with simplified hardware, and the protected space above the full ruler footprint. adjustment_checks.json records discrete sampled dial/trim/sight poses. validation_summary.json records dimension examples and reused parts. These do not prove continuous travel or physical performance.',True)
para('The official 2027 rules page announces release on September 8, 2026 at 9:00 a.m. Central. Final Division B event-rule compliance remains unverified in this September 7 revision. <link href="https://soinc.org/rules-2027" color="#276079">Official Science Olympiad 2027 rules page</link>.',True)
doc=SimpleDocTemplate(str(P/'ELG_Launcher_v04_Assembly_and_Calibration_Guide.pdf'),pagesize=(612,792),leftMargin=36,rightMargin=36,topMargin=96,bottomMargin=42,title='SMS ELG Launcher v0.4 - Assembly and Calibration',author='SMS Science Olympiad')
doc.build(story,onFirstPage=page,onLaterPages=page)
print('Assembly and calibration guide created.')
