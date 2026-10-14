"""SMS ELG launcher v0.4: numbered bank and pitch dials, draw datum and setup alignment sight. Units mm.
Run: python build_launcher.py --width 30 --thickness 6 --length 900
Prototype only. Geometry checks do not establish load capacity or rule compliance.
"""
from pathlib import Path
import argparse, json, math
import cadquery as cq
import numpy as np
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument('--width', type=float, default=30)
ap.add_argument('--thickness', type=float, default=6)
ap.add_argument('--length', type=float, default=914.4)
ap.add_argument('--vial-length', type=float, default=25)
ap.add_argument('--vial-diameter', type=float, default=8)
ap.add_argument('--pitch-angle', type=float, default=60)
ap.add_argument('--bank-angle', type=float, default=0)
ap.add_argument('--sight-height', type=float, default=0)
ap.add_argument('--skip-export', action='store_true', help='Skip STEP and preview export; still validate actual STL meshes')
ap.add_argument('--pitch-trim', type=float, default=0)
ap.add_argument('--roll-trim', type=float, default=0)
ap.add_argument('--out', default=str(Path(__file__).parent))
a = ap.parse_args()
W,T,L,VL,VD = a.width,a.thickness,a.length,a.vial_length,a.vial_diameter
assert 22 <= W <= 40 and 4 <= T <= 10 and 700 <= L <= 950
assert 20 <= VL <= 26 and 6 <= VD <= 8
assert 0 <= a.pitch_angle <= 90
assert abs(a.bank_angle) <= 30 and 0 <= a.sight_height <= 20
assert abs(a.pitch_trim) <= 8 and abs(a.roll_trim) <= 8
OUT = Path(a.out)
for sub in ['STL','STEP']: (OUT/sub).mkdir(parents=True,exist_ok=True)
CW=W+.6; OW=CW+14; GAP=1.2; JTOP=T-.8; BZ=-6.5; MY=-CW/4
CLAMP_BOLT_LENGTH=5*math.ceil((OW-.6+7.2)/5)

def box(x,y,z,at=(0,0,0)):
    return cq.Workplane('XY').box(x,y,z).translate(at)
def rb(x,y,z,at=(0,0,0),r=1):
    return cq.Workplane('XY').box(x,y,z).edges('|Z').fillet(r).translate(at)
def cyl(r,h,base,axis=(0,0,1)):
    return cq.Workplane(obj=cq.Solid.makeCylinder(r,h,cq.Vector(*base),cq.Vector(*axis)))
def hole(p,r,h,base,axis=(0,0,1)): return p.cut(cyl(r,h,base,axis))
def bolt_x(n): return [0] if n<25 else [-n/2+8,n/2-8]

def jaw(n,side):
    # Two independent halves pinch the long side faces. No part covers the top.
    # Supplied STLs have 0.6 mm total fitting allowance; assembly closes this.
    bw=(OW-GAP)/2
    p=rb(n,bw,12,(0,side*(OW+GAP)/4,-6),r=.6)
    p=p.union(rb(n,7,JTOP+1,(0,side*(CW/2+3.5),(JTOP-1)/2),r=.6))
    for x in bolt_x(n): p=hole(p,2.25,OW+4,(x,-OW/2-2,BZ),(0,1,0))
    return p

def mount_holes(p,xs):
    for x in xs:
        p=hole(p,2.25,20,(x,MY,-19))
        p=hole(p,4.4,3.5,(x,MY,-3.4))
    return p

def grip():
    p=rb(56,14,6,(0,MY,-15),r=2)
    pts=[(-25,-17),(25,-17),(18,-30),(14,-101),(9,-108),(-9,-108),(-14,-101),(-18,-30)]
    h=cq.Workplane('XZ').polyline(pts).close().extrude(10,both=True).edges('|Y').fillet(3).translate((0,MY,0))
    p=p.union(h)
    for x in [-22,22]:
        p=hole(p,2.25,14,(x,MY,-25))
        p=p.cut(box(13,24,24,(x,MY,-30)))
    return p

def anchor():
    p=jaw(48,-1)
    # The solid nose abuts the wood end at local x=24: a positive back-pull stop.
    nose=rb(26,OW,12+JTOP,(37,0,(JTOP-12)/2),r=.6)
    # Roundbox ends leave a small corner radius; straight central face is x=24.
    tie=box(8,7,12+JTOP,(24,-CW/2-3.5,(JTOP-12)/2))
    p=p.union(tie).union(nose)
    for y in [-10,10]:
        p=p.union(rb(18,6,14,(39,y,T+4),r=1))
    return hole(p,2.25,34,(39,-17,T+4),(0,1,0))

def vial_cradle(p,axis,center):
    x,y,z=center
    if axis=='X':
        p=p.union(rb(VL+6,VD+6,8,(x,y,z-2),r=1.5))
        p=hole(p,(VD+.6)/2,VL+.8,(x-(VL+.8)/2,y,z),(1,0,0))
        return p.cut(box(VL+.8,VD+.6,10,(x,y,z+5)))
    p=p.union(rb(VD+6,VL+6,8,(x,y,z-2),r=1.5))
    p=hole(p,(VD+.6)/2,VL+.8,(x,y-(VL+.8)/2,z),(0,1,0))
    return p.cut(box(VD+.6,VL+.8,10,(x,y,z+5)))

VY=OW/2+59
VZ=-48

def nut_traps(p):
    # Standard M3 hex nuts enter from the rear and sit below the back face.
    for x in [-16,16]:
        p=hole(p,1.75,8,(x,0,-1))
        pocket=cq.Workplane('XY').polygon(6,6.55).extrude(2.55).translate((x,0,0))
        p=p.cut(pocket)
    return p

def roll_frame(p):
    # Local X is vial length, local Y is up, local Z points out of the face.
    return p.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),90).translate((0,VY,VZ))

def numeral(txt,x,y,z,size=4):
    return cq.Workplane('XY').text(str(txt),size,.45,font='DejaVu Sans',kind='bold',combine=True).translate((x,y,z))

def bank_dial():
    p=cyl(44,6,(0,0,0))
    p=hole(p,2.25,10,(0,0,-1))
    # Engrave, so labels remain one printable solid and never touch the rotor.
    for deg in range(-30,31,5):
        ar=math.radians(-deg)
        tick=box(3.5 if deg%10==0 else 2,.65,1,(33,0,6))
        p=p.cut(tick.rotate((0,0,0),(0,0,1),-deg))
        if deg%10==0:
            p=p.cut(numeral(str(deg),39*math.cos(ar),39*math.sin(ar),5.6,3.5))
    p=p.cut(numeral('BANK',-12,30,5.6,4))
    return p

def roll_jaw():
    p=jaw(44,1)
    p=p.union(rb(8,12,6,(-5,OW/2+1,-9),r=.8))
    p=p.union(rb(8,6,84,(-5,OW/2+4,-48),r=.8))
    sy0=OW/2-6;sy1=VY+8
    p=p.union(rb(12,sy1-sy0,6,(-5,(sy0+sy1)/2,-89),r=.8))
    return p.union(roll_frame(bank_dial()))

# Sight is outboard and removable. It is a setup reference, never a glider stop.
SY=OW/2+15

def marker_sight_base():
    p=jaw(16,1).cut(box(.8,7,.6,(0,CW/2+3.5,JTOP-.2)))
    p=p.union(rb(16,SY-OW/2+5,6,(0,(OW/2+SY)/2,-13),r=.7))
    p=p.union(rb(80,4,8,(0,SY,-8),r=.7))
    for x in [-30,30]:
        p=hole(p,1.75,8,(x,SY-4,-8),(0,1,0))
    p=hole(p,5,12,(0,OW/2,BZ),(0,1,0))
    # Open viewing notch exposes a side scale at the marker station.
    p=p.cut(box(12,10,T+2,(0,CW/2+3.5,(T+2)/2+.3)))
    p=p.cut(box(.65,8,.6,(0,CW/2+3.5,.3)))
    return p

def alignment_sight():
    # XZ plane; local lower beam at z=0 becomes T+5+h above wood datum.
    # Two 20 mm vertical slots let the reticle be fitted to the glider reference.
    p=rb(80,3,2,(0,0,1),r=.5)
    for x in [-39,39]: p=p.union(box(2,3,18,(x,0,9)))
    p=p.union(box(80,3,2,(0,0,17)))
    # A central index defines the glider hook's longitudinal station.
    p=p.union(box(.8,3,7,(0,0,4.5)))
    for x in [-30,30]:
        p=p.union(box(10,3,T+40,(x,0,-(T+40)/2+1)))
        slot=(cq.Workplane('XZ').center(x,-T-23).slot2D(23.5,3.5,90).extrude(6,both=True))
        p=p.cut(slot)
    return p

def arc_slot(radius=32,halfangle=8,width=3.5):
    ang=math.radians(halfangle); ro=radius+width/2; ri=radius-width/2
    def pt(r,t): return (-16+r*math.cos(t),r*math.sin(t))
    p=(cq.Workplane('XY').moveTo(*pt(ro,-ang)).threePointArc(pt(ro,0),pt(ro,ang))
       .lineTo(*pt(ri,ang)).threePointArc(pt(ri,0),pt(ri,-ang)).close().extrude(8).translate((0,0,-1)))
    for t in [-ang,ang]:
        x,y=pt(radius,t);p=p.union(cyl(width/2,8,(x,y,-1)))
    return p

def calibration_carrier():
    p=rb(44,34,4,(0,7,2),r=2)
    p=hole(p,1.75,8,(-16,0,-1))
    p=p.cut(arc_slot())
    # Access window clears the pitch-pivot head throughout the trim sweep.
    p=hole(p,8,8,(0,0,-1))
    p=vial_cradle(p,'X',(0,16,8))
    # Two open passages under the vial for 2.5 mm cable ties; no adhesive needed.
    for x in [-VL/2+4,VL/2-4]:
        p=p.cut(box(3.2,36,1.6,(x,7,1.5)))
    return p

def pitch_bracket():
    p=rb(40,OW,6,(0,0,-15.6),r=1.5)
    for x in [-8,8]:
        p=p.union(cyl(5,.6,(x,MY,-12.6)))
        p=hole(p,2.25,10,(x,MY,-20))
    disc=cyl(44,6,(0,-OW/2-3,-49),(0,1,0)).cut(box(100,20,20,(0,-OW/2,-5)))
    p=p.union(disc)
    p=hole(p,2.25,10,(0,-OW/2-5,-49),(0,1,0))
    for deg in range(0,91,5):
        ar=math.radians(deg)
        for rr in ([30.5,31.5,32.5] if deg%10==0 else [31.5,32.5]):
            p=p.union(cyl(.45,.55,(rr*math.cos(ar),-OW/2-3.5,-49-rr*math.sin(ar)),(0,1,0)))
    for deg in range(0,91,10):
        ar=math.radians(deg)
        label=numeral(str(deg),39*math.cos(ar),-39*math.sin(ar),-.4,3.8)
        label=label.rotate((0,0,0),(1,0,0),90).translate((0,-OW/2-3,-49))
        p=p.cut(label)
    label=numeral('PITCH',-12,-20,-.4,4).rotate((0,0,0),(1,0,0),90).translate((0,-OW/2-3,-49))
    p=p.cut(label)
    return p

def pitch_rotor():
    p=cyl(23,4,(0,0,0))
    p=p.union(cq.Workplane('XY').polyline([(19,-2),(30,0),(19,2)]).close().extrude(4))
    p=hole(p,2.25,6,(0,0,-1))
    return nut_traps(p)

parts={
 '01_grip_fixed_jaw':mount_holes(jaw(72,-1),[-22,22]),
 '02_grip_moving_jaw':jaw(72,1),
 '03_grip_handle':grip(),
 '04_anchor_fixed_jaw_and_nose':anchor(),
 '05_anchor_moving_jaw':jaw(48,1),
 '06_marker_fixed_jaw':jaw(16,-1),
 '07_marker_moving_jaw':marker_sight_base(),
 '08_gauge_fixed_jaw':mount_holes(jaw(44,-1),[-8,8]),
 '09_gauge_moving_jaw_roll_bracket':roll_jaw(),
 '10_pitch_bracket':pitch_bracket(),
 '11_pitch_rotor_calibration_base':pitch_rotor(),
 '12_fit_coupon_fixed_jaw':jaw(16,-1),
 '13_fit_coupon_moving_jaw':jaw(16,1),
 '14_calibration_vial_carrier_PRINT_2':calibration_carrier(),
 '15_bank_rotor_calibration_base':pitch_rotor(),
 '16_removable_alignment_sight':alignment_sight(),
}
colors=['#274956','#d7a442','#274956','#274956','#d7a442','#274956','#e4874c','#274956','#274956','#274956','#d7a442','#aaaaaa','#aaaaaa','#d7a442','#d7a442','#e4874c']
rot_print={'03_grip_handle':90,'10_pitch_bracket':-90,'16_removable_alignment_sight':90}
report=[]
for (name,p),color in zip(parts.items(),colors):
    assert len(p.solids().vals())==1 and p.val().isValid(),(name,'invalid/disconnected solid')
    if not a.skip_export: cq.exporters.export(p,str(OUT/'STEP'/f'{name}.step'))
    q=p.rotate((0,0,0),(1,0,0),rot_print[name]) if name in rot_print else p
    bb=q.val().BoundingBox(); q=q.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    path=OUT/'STL'/f'{name}.stl'
    cq.exporters.export(q,str(path),tolerance=.035,angularTolerance=.12)
    m=trimesh.load(path,force='mesh')
    assert m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==1,name
    report.append(dict(part=name,stl_mm=np.round(m.extents,2).tolist(),volume_cm3=round(m.volume/1000,3),watertight=True,connected_solids=1,color=color))

assy=cq.Assembly(name='SMS_ELG_v04_bank_pitch_draw_alignment')
placed=[]
def add(name,p,col):
    assy.add(p,name=name,color=cq.Color(col)); placed.append((name,p,col))
add('wood_ruler',box(L,W,T,(L/2,0,T/2)),'#cbb895')
def pitch_frame(p):
    return (p.rotate((0,0,0),(0,0,1),-a.pitch_angle)
            .rotate((0,0,0),(1,0,0),90).translate((50,-OW/2-3.7,-49)))
def roll_placed(p):
    p=p.rotate((0,0,0),(0,0,1),-a.bank_angle).translate((0,0,7))
    return roll_frame(p).translate((50,-.3,0))
def trimmed(p,angle):
    return p.rotate((-16,0,0),(-16,0,1),angle).translate((0,0,5))
xs=[230,230,230,L-24,L-24,L-400,L-400,50,50,50,50]
for i,row in enumerate(report[:11]):
    name=row['part']; p=parts[name]
    if i==10:
        p=pitch_frame(p)
    else:
        # Close the 0.6 mm fitting allowance symmetrically onto the nominal wood.
        dy=-.3 if i in [1,4,6,8] else .3
        p=p.translate((xs[i],dy,0))
    add(name,p,row['color'])

add('15_bank_rotor_calibration_base',roll_placed(parts['15_bank_rotor_calibration_base']),'#d7a442')
add('16_removable_alignment_sight',parts['16_removable_alignment_sight'].translate((L-400,SY+4,T+5+a.sight_height)),'#e4874c')
# M3 x 12 setup-sight hardware through the two slots.
for j,x in enumerate([-30,30]):
    xp=L-400+x;yp=SY+6.5
    add(f'sight_shank{j}',cyl(1.5,12,(xp,yp-12,-8),(0,1,0)),'#9daab2')
    add(f'sight_head{j}',cyl(2.85,2.4,(xp,yp,-8),(0,1,0)),'#9daab2')
    for k,y in enumerate([SY-3.3,SY+5.5]):
        washer=cyl(3.5,1,(xp,y,-8),(0,1,0)).cut(cyl(1.65,1,(xp,y,-8),(0,1,0)))
        add(f'sight_washer{j}_{k}',washer,'#9daab2')
    nut=cyl(3.18,2.4,(xp,SY-5.7,-8),(0,1,0)).cut(cyl(1.5,2.4,(xp,SY-5.7,-8),(0,1,0)))
    add(f'sight_nut{j}',nut,'#9daab2')

# Identical, separately adjustable cartridges. Calibration does not rotate the
# pitch dial or disturb the clamp that locates the horizontal level.
carrier=parts['14_calibration_vial_carrier_PRINT_2']
for label,xf,trim in [('pitch',pitch_frame,a.pitch_trim),('roll',roll_placed,a.roll_trim)]:
    add(label+'_calibration_carrier',xf(trimmed(carrier,trim)),'#e3ad47')
    vial=cyl(VD/2,VL,(-VL/2,16,8),(1,0,0))
    add(label+'_vial_reference',xf(trimmed(vial,trim)),'#91bb73')
    for j,x in enumerate([-16,16]):
        # Nylon spacer + metal outer washer sandwich the carrier.
        for desc,z,col in [('nylon_spacer',4,'#e3e6de'),('outer_washer',9,'#9daab2')]:
            washer=cyl(3.5,1,(x,0,z)).cut(cyl(1.65,1,(x,0,z)))
            add(f'{label}_{desc}{j}',xf(washer),col)
        add(f'{label}_trim_shank{j}',xf(cyl(1.5,10,(x,0,0))),'#9daab2')
        add(f'{label}_trim_head{j}',xf(cyl(2.85,2.4,(x,0,10))),'#9daab2')
        nut=(cq.Workplane('XY').polygon(6,6.35).extrude(2.4)
             .cut(cyl(1.5,2.4,(0,0,0))).translate((x,0,.1)))
        add(f'{label}_trim_nut{j}',xf(nut),'#9daab2')

# Main pitch pivot: fully modeled so the carrier window and dial are checked.
pivot_hardware=[
 ('spacer',cyl(4.5,1,(0,0,-1)).cut(cyl(2.2,1,(0,0,-1)))),
 ('front_washer',cyl(4.5,1,(0,0,4)).cut(cyl(2.2,1,(0,0,4)))),
 ('rear_washer',cyl(4.5,1,(0,0,-8)).cut(cyl(2.2,1,(0,0,-8)))),
 ('shank',cyl(2,20,(0,0,-15))),
 ('head',cyl(3.5,2.8,(0,0,5))),
 ('nut',cyl(4.1,3.2,(0,0,-11.2)).cut(cyl(2,3.2,(0,0,-11.2))))]
for name,p in pivot_hardware:
    add('pitch_pivot_'+name,pitch_frame(p),'#9daab2')
    add('roll_pivot_'+name,roll_placed(p),'#9daab2')
add('elastic_smooth_pin',cyl(2,40,(L+15,-19.7,T+4),(0,1,0)),'#9daab2')
sleeve=cyl(3,12,(L+15,-5.7,T+4),(0,1,0)).cut(cyl(2.1,12,(L+15,-5.7,T+4),(0,1,0)))
add('elastic_pin_sleeve',sleeve,'#bcc5c9')
for j,yy in enumerate([-19.7,14.3]):
    collar=cyl(4,6,(L+15,yy,T+4),(0,1,0)).cut(cyl(2.15,6,(L+15,yy,T+4),(0,1,0)))
    add('pin_retaining_collar'+str(j),collar,'#9daab2')

# Reference clamp hardware: actual shank/head/washer/nut envelopes, below wood.
HW='#9daab2'
for label,xc,n in [('grip',230,72),('anchor',L-24,48),('marker',L-400,16),('gauge',50,44)]:
    outer=OW/2-.3
    for j,dx in enumerate(bolt_x(n)):
        x=xc+dx
        add(f'{label}_bolt{j}',cyl(2,CLAMP_BOLT_LENGTH,(x,-outer-1,BZ),(0,1,0)),HW)
        add(f'{label}_head{j}',cyl(3.5,2.8,(x,-outer-3.8,BZ),(0,1,0)),HW)
        for side in [-1,1]:
            y=-outer-1 if side<0 else outer
            w=cyl(4.5,1,(x,y,BZ),(0,1,0)).cut(cyl(2.2,1,(x,y,BZ),(0,1,0)))
            add(f'{label}_washer{j}_{side}',w,HW)
        nut=cyl(4.1,3.2,(x,outer+1,BZ),(0,1,0)).cut(cyl(2.2,3.2,(x,outer+1,BZ),(0,1,0)))
        add(f'{label}_nut{j}',nut,HW)

# Recessed M4 button mounting screws: 3 mm head fits a 3.4 mm deep recess.
for label,xc,pxs in [('handle',230,[-22,22]),('dial',50,[-8,8])]:
    for j,dx in enumerate(pxs):
        x=xc+dx; y=MY+.3
        add(f'{label}_mount_head{j}',cyl(3.8,3,(x,y,-3.4)),HW)
        add(f'{label}_mount_shank{j}',cyl(2,25,(x,y,-28.4)),HW)
        z=-19 if label=='handle' else -19.6
        washer=cyl(4.5,1,(x,y,z)).cut(cyl(2.2,1,(x,y,z)))
        add(f'{label}_mount_washer{j}',washer,HW)
        nut=cyl(4.1,3.2,(x,y,z-3.2)).cut(cyl(2.2,3.2,(x,y,z-3.2)))
        add(f'{label}_mount_nut{j}',nut,HW)

collisions=[]
for i,(na,p,_) in enumerate(placed):
    ba=p.val().BoundingBox()
    for nb,q,_ in placed[i+1:]:
        bb=q.val().BoundingBox()
        if any(getattr(ba,k+'max') <= getattr(bb,k+'min')+1e-7 or getattr(bb,k+'max') <= getattr(ba,k+'min')+1e-7 for k in ['x','y','z']): continue
        vol=sum(s.Volume() for s in p.intersect(q).solids().vals())
        if vol>.02: collisions.append((na,nb,round(vol,3)))
assert not collisions,collisions

# The entire ruler footprint is a protected space above z=T. Test CAD, not art.
clearance=box(L,W,250,(L/2,0,T+125))
obstructions=[]
for name,p,_ in placed:
    if name=='wood_ruler': continue
    vol=sum(s.Volume() for s in p.intersect(clearance).solids().vals())
    if vol>.001: obstructions.append((name,vol))
assert not obstructions,obstructions
if not a.skip_export: assy.export(str(OUT/'ELG_Launcher_Assembly.step'))
data={'version':'0.4','parameters':vars(a),'parts':report,'assembly_intersections_mm3':collisions,
      'ruler_top_keepout_obstructions':obstructions,'keepout_mm':{'x':[0,L],'y':[-W/2,W/2],'z':[T,T+250]},
      'jaw_top_below_ruler_mm':.8,'nominal_closed_base_gap_mm':.6,
      'clamp_bolt_length_mm':CLAMP_BOLT_LENGTH,
      'bank_range_deg':[-30,30],'pitch_range_deg':[0,90],'sight_height_range_mm':[0,20],
      'calibration_range_deg':[-8,8],'trim_pivot_spacing_mm':32,'print_quantities':{'14_calibration_vial_carrier_PRINT_2':2},
      'checked':'Valid CAD, one solid per print, watertight positive-volume meshes, assembled collisions including vials, trim/pivot/clamp/mount hardware, full ruler top keepout at the specified angles.',
      'not_checked':'Physical fit, strength, clamp friction, fatigue, calibration accuracy, glider clearance, elastic retention or rules compliance. Cable ties and retaining-collar set screws are not modeled. Nut/bolt threads and washer compression are simplified.'}
(OUT/'geometry_checks.json').write_text(json.dumps(data,indent=2))
scene=[]
for name,p,col in ([] if a.skip_export else placed):
    v,f=p.val().tessellate(.5)
    scene.append(dict(name=name,color=col,vertices=[list(vv.toTuple()) for vv in v],faces=f))
# Preview-only white infill represents paint rubbed into the engraved labels.
if not a.skip_export:
    for kind in ['bank','pitch']:
        for deg in (range(-30,31,10) if kind=='bank' else range(0,91,10)):
            ar=math.radians(-deg)
            if kind=='bank':
                mark=roll_frame(numeral(str(deg),39*math.cos(ar),39*math.sin(ar),5.6,3.5)).translate((50,-.3,0))
            else:
                mark=numeral(str(deg),39*math.cos(ar),39*math.sin(ar),-.4,3.8).rotate((0,0,0),(1,0,0),90).translate((50,-OW/2-3+.3,-49))
            v,f=mark.val().tessellate(.08)
            scene.append(dict(name=kind+'_paint_label_'+str(deg),color='#f8eee0',vertices=[list(vv.toTuple()) for vv in v],faces=f))
(OUT/'preview_meshes.json').write_text(json.dumps(scene))
print(json.dumps({'parts':len(report),'watertight':True,'collisions':collisions,'top_obstructions':obstructions,'out':str(OUT)}))
