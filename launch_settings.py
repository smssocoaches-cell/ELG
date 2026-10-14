"""v0.4 geometric settings helper. No external dependencies; lengths in mm.
Pitch is elevation of ruler x axis; positive bank raises ruler +Y edge.
Not an aerodynamic angle-of-attack model or an elastic-force model.
"""
import math, argparse, json

def dial_pitch(elevation_deg, bank_deg):
    if not 0 <= elevation_deg <= 90 or abs(bank_deg)>30:
        raise ValueError('Use elevation 0..90 and bank -30..30 degrees')
    t,b=map(math.radians,(elevation_deg,bank_deg))
    return math.degrees(math.atan2(math.sin(t),math.cos(t)*math.cos(b)))

def axial_length(ruler_length, hook_x):
    return ruler_length+15-hook_x

def pullback_extension(relaxed_hook_x, loaded_hook_x):
    return relaxed_hook_x-loaded_hook_x

def test_geometry():
    # Independent 3D forward rotation: both modeled vial axes must be level.
    checked=0
    for t in [0,15,30,45,60,75,85,90]:
        for b in [-30,-15,0,15,30]:
            p=math.radians(dial_pitch(t,b));bt=math.radians(b);tt=math.radians(t)
            def rotate(v):
                x,y,z=v
                y,z=y*math.cos(bt)-z*math.sin(bt), y*math.sin(bt)+z*math.cos(bt)
                return (x*math.cos(tt)-z*math.sin(tt),y,x*math.sin(tt)+z*math.cos(tt))
            assert abs(rotate((math.cos(p),0,-math.sin(p)))[2])<1e-12
            assert abs(rotate((0,math.cos(bt),-math.sin(bt)))[2])<1e-12
            checked+=1
    assert axial_length(914.4,514.4)==415
    assert pullback_extension(700,500)==200
    return checked

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--elevation',type=float,default=60)
    ap.add_argument('--bank',type=float,default=20)
    ap.add_argument('--length',type=float,default=914.4)
    ap.add_argument('--hook-x',type=float)
    ap.add_argument('--relaxed-hook-x',type=float)
    ap.add_argument('--self-test',action='store_true')
    a=ap.parse_args()
    if a.self_test: print('Forward-vector checks passed:',test_geometry())
    result={'desired_elevation_deg':a.elevation,'bank_dial_deg':a.bank,'pitch_dial_deg':round(dial_pitch(a.elevation,a.bank),3)}
    if a.hook_x is not None:
        result['hook_to_pin_axial_mm']=round(axial_length(a.length,a.hook_x),3)
        if a.relaxed_hook_x is not None: result['pullback_extension_mm']=round(pullback_extension(a.relaxed_hook_x,a.hook_x),3)
    print(json.dumps(result,indent=2))
