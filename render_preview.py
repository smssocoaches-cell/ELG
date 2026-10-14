from pathlib import Path
import json, math, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

P=Path(__file__).parent
scene=json.loads((P/'preview_meshes.json').read_text())
report=json.loads((P/'geometry_checks.json').read_text())
NAVY='#173648'; TEAL='#2c4656'; GOLD='#e3ad47'; BG='#f4f3ee'

def render(ax,names,center=None,ext=None,elev=24,azim=-64):
    selected=[o for o in scene if o['name'] in names]
    allv=[]; polys=[]; colors=[]; depths=[]
    el,az=math.radians(elev),math.radians(azim)
    cam=np.array([math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)])
    right=np.array([-math.sin(az),math.cos(az),0]); up=np.cross(cam,right)
    for o in selected:
        v=np.array(o['vertices']); f=np.array(o['faces']); tri=v[f]
        if o['name']=='wood_ruler' and center is not None:
            # Crop only the long reference ruler for closeups.
            v[:,0]=np.clip(v[:,0],center[0]-ext[0]/2,center[0]+ext[0]/2)
            tri=v[f]
        n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-9)
        light=np.clip(.65+.35*np.abs(n@np.array([.3,-.4,.866])),.4,1)
        col=np.array(to_rgb(o['color']))[None,:]*light[:,None]
        polys.extend(np.stack([tri@right,tri@up],axis=-1));colors.extend(col);depths.extend(tri@cam)
        allv.append(v)
    verts=np.vstack(allv)
    if center is None:
        lo=verts.min(0);hi=verts.max(0);center=(lo+hi)/2;ext=(hi-lo)*1.12
    xy=np.stack([verts@right,verts@up],axis=-1);lo=xy.min(0);hi=xy.max(0);pad=(hi-lo)*.09
    # A per-pixel depth buffer avoids painter-order artifacts on long ruler
    # triangles that span behind and in front of several separate fittings.
    ww=1800 if len(names)>8 else 900
    hh=max(100,int(ww*(hi[1]-lo[1])/(hi[0]-lo[0])))
    zb=np.full((hh,ww),-np.inf);rgb=np.ones((hh,ww,4),dtype=float);rgb[:,:,:3]=to_rgb(BG)
    scale=np.array([(ww-1)/(hi[0]-lo[0]),(hh-1)/(hi[1]-lo[1])])
    for tri,col,zz in zip(polys,colors,depths):
        t=(tri-lo)*scale
        xa,ya=np.maximum(np.floor(t.min(0)).astype(int),0)
        xb,yb=np.minimum(np.ceil(t.max(0)).astype(int),[ww-1,hh-1])
        den=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
        if abs(den)<1e-9 or xb<xa or yb<ya:continue
        xx,yy=np.meshgrid(np.arange(xa,xb+1)+.5,np.arange(ya,yb+1)+.5)
        a=((t[1,1]-t[2,1])*(xx-t[2,0])+(t[2,0]-t[1,0])*(yy-t[2,1]))/den
        b=((t[2,1]-t[0,1])*(xx-t[2,0])+(t[0,0]-t[2,0])*(yy-t[2,1]))/den
        d=1-a-b;z=a*zz[0]+b*zz[1]+d*zz[2]
        sl=zb[ya:yb+1,xa:xb+1]
        mask=(a>=-1e-6)&(b>=-1e-6)&(d>=-1e-6)&(z>sl)
        sl[mask]=z[mask];rg=rgb[ya:yb+1,xa:xb+1];rg[mask,:3]=col;rg[mask,3]=1
    ax.imshow(rgb,origin='lower',extent=[lo[0],hi[0],lo[1],hi[1]],interpolation='lanczos')
    ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1])
    ax.set_aspect('equal');ax.set_axis_off();ax.set_facecolor(BG)


params=report['parameters'];W=params['width'];T=params['thickness'];L=params['length']
names=[o['name'] for o in scene]
gauge=[n for n in names if n=='wood_ruler' or n.startswith(('08_','09_','10_','11_','15_','gauge_','dial_','pitch_','roll_','bank_'))]
sight=[n for n in names if n=='wood_ruler' or n.startswith(('06_','07_','16_','marker_','sight_'))]
fig=plt.figure(figsize=(16,12),facecolor=BG)
fig.text(.04,.952,'SMS  /  ELASTIC LAUNCHED GLIDER',fontsize=12,fontweight='bold',color=TEAL)
fig.text(.04,.902,'Set the draw. Set the elevation. Set the bank.',fontsize=25,fontweight='bold',color=NAVY)
fig.text(.04,.863,'v0.4 prototype | numbered dials | independent vial calibration | removable setup sight',fontsize=12,color=TEAL)
ax=fig.add_axes([.03,.65,.94,.18]);render(ax,names,elev=25,azim=-77)
fig.text(.04,.622,'Full ruler top stays exposed. Alignment sight shown fitted for unloaded setup.',fontsize=11,fontweight='bold',color=NAVY)
for x,az,title,sub in [(.04,10,'BANK: -30 TO +30 DEG','M4 dial setting; separate M3 vial calibration.'),(.53,-88,'PITCH: 0 TO 90 DEG','Numbered scale; correct for bank when setting elevation.')]:
    ax=fig.add_axes([x,.292,.43,.30]);render(ax,gauge,(50,0,-20),(100,190,150),elev=18,azim=az)
    fig.text(x,.28,title,fontsize=13,fontweight='bold',color=NAVY)
    fig.text(x,.25,sub,fontsize=10,color=TEAL)
ax=fig.add_axes([.025,.036,.32,.18]);render(ax,sight,(L-400,0,0),(110,120,80),elev=15,azim=-83)
fig.text(.39,.178,'GLIDER ALIGNMENT / UNLOADED SETUP ONLY',fontsize=12,fontweight='bold',color=NAVY)
fig.text(.39,.148,'Adjust the sight to a fixed fuselage reference; transfer alignment marks.',fontsize=10.5,color=TEAL)
fig.text(.39,.119,'Remove the sight before stretching the elastic or launching.',fontsize=10.5,color=TEAL)
fig.text(.39,.075,'Also included: anchor-based draw scale, angle lookup, full build guide.',fontsize=10.5,color=TEAL)
fig.text(.04,.015,'Rendered from CAD with simplified hardware. Digital geometry checks do not establish fit, load capacity or measurement accuracy.',fontsize=9,color=TEAL)
fig.savefig(P/'ELG_Launcher_v04_Preview.png',dpi=160,facecolor=BG);plt.close(fig)
# Front views show readable number positions on the actual CAD.
fig,axs=plt.subplots(1,2,figsize=(14,6),facecolor=BG)
render(axs[0],[n for n in gauge if n!='wood_ruler'],elev=0,azim=0)
render(axs[1],[n for n in gauge if n!='wood_ruler'],elev=0,azim=-90)
axs[0].set_title('Bank dial, looking toward the nose',color=NAVY)
axs[1].set_title('Pitch dial, side view',color=NAVY)
fig.savefig(P/'ELG_Dial_Detail.png',dpi=160,facecolor=BG,bbox_inches='tight')
