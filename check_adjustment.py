"""Sample both dial/trim extremes and sight travel, with modeled hardware.
This is a discrete interference check, not a continuous-motion or load proof.
Run after build_launcher.py. Defaults are intentionally explicit.
"""
from pathlib import Path
import runpy,sys,json,itertools
P=Path(__file__).parent
sys.argv=[str(P/'build_launcher.py'),'--skip-export','--out',str(P/'check_tmp')]
n=runpy.run_path(str(P/'build_launcher.py'))
a=n['a'];dp=a.pitch_angle;db=a.bank_angle
movable=[v for v in n['placed'] if v[0].startswith(('pitch_','roll_','11_','15_','16_'))]
static=[v for v in n['placed'] if v not in movable]
poses=set(itertools.product([0,90],[-30,30],[-8,8],[-8,8],[0]))
poses.update((p,b,0,0,0) for p,b in itertools.product([0,30,60,90],[-30,-15,0,15,30]))
poses.add((60,0,0,0,20));poses.add((60,0,0,0,0))
rows=[]
for angle,bank,pt,rt,h in sorted(poses):
    a.pitch_angle=angle;a.bank_angle=bank
    posed=[]
    for name,p,col in movable:
        if name=='pitch_calibration_carrier': p=n['pitch_frame'](n['trimmed'](n['carrier'],pt))
        elif name=='roll_calibration_carrier': p=n['roll_placed'](n['trimmed'](n['carrier'],rt))
        elif name=='pitch_vial_reference': p=n['pitch_frame'](n['trimmed'](n['vial'],pt))
        elif name=='roll_vial_reference': p=n['roll_placed'](n['trimmed'](n['vial'],rt))
        elif name.startswith(('pitch_','11_')): p=p.rotate((50,0,-49),(50,1,-49),angle-dp)
        elif name.startswith(('roll_','15_')): p=p.rotate((0,n['VY']-.3,n['VZ']),(1,n['VY']-.3,n['VZ']),db-bank)
        elif name.startswith('16_'): p=p.translate((0,0,h))
        posed.append((name,p,col))
    collisions=[];obstructions=[];allparts=posed+static
    for i,(name,p,_) in enumerate(posed):
        ba=p.val().BoundingBox()
        for other,q,_ in allparts[i+1:]:
            bb=q.val().BoundingBox()
            if any(getattr(ba,k+'max')<=getattr(bb,k+'min')+1e-7 or getattr(bb,k+'max')<=getattr(ba,k+'min')+1e-7 for k in ['x','y','z']): continue
            vol=sum(s.Volume() for s in p.intersect(q).solids().vals())
            if vol>.02:collisions.append([name,other,round(vol,3)])
        vol=sum(s.Volume() for s in p.intersect(n['clearance']).solids().vals())
        if vol>.001:obstructions.append([name,round(vol,3)])
    row=dict(pitch_deg=angle,bank_deg=bank,pitch_trim_deg=pt,roll_trim_deg=rt,sight_height_mm=h,collisions=collisions,top_obstructions=obstructions)
    rows.append(row)
    print(json.dumps(row),flush=True)
    assert not collisions and not obstructions,row
(P/'adjustment_checks.json').write_text(json.dumps(dict(parameters={'width':30,'thickness':6,'length':914.4,'vial_length':25,'vial_diameter':8},sampled_poses=rows,passed=True,continuous_sweep=False),indent=2))
print(f'{len(rows)} sampled poses passed.')
