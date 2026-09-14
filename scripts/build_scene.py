import bpy, math, random, sys, json, time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
random.seed(42)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.samples=16
s.cycles.use_denoising=False
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.fps=30;s.frame_start=1;s.frame_end=600
s.world=bpy.data.worlds.new('Black space');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1)
s.view_settings.view_transform='Standard'
s.render.film_transparent=False

def emission(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();a=n.new('ShaderNodeEmission');a.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(a.outputs[0],o.inputs[0]);return m
white=emission('White contours',(.65,.69,.67));dim=emission('Fine anatomy',(.22,.26,.25));bright=emission('Facet edges',(.5,.55,.52));amber=emission('Neural activity',(.95,.37,.085));black=emission('Opaque black',(.001,.001,.001))
rim=bpy.data.materials.new('Opaque shell with contour');rim.use_nodes=True;n=rim.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');lw=n.new('ShaderNodeLayerWeight');p=n.new('ShaderNodeMath');p.operation='POWER';p.inputs[1].default_value=17;m=n.new('ShaderNodeMath');m.operation='MULTIPLY';m.inputs[1].default_value=.6;rim.node_tree.links.new(lw.outputs['Facing'],p.inputs[0]);rim.node_tree.links.new(p.outputs[0],m.inputs[0]);rim.node_tree.links.new(m.outputs[0],e.inputs[0]);rim.node_tree.links.new(e.outputs[0],o.inputs[0])
def empty(name,parent=None):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.parent=parent;return o
root=empty('Drosophila / rig')
def mesh(name,verts,faces,mat,parent=root):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(mat);o.parent=parent;return o
def curves(name,paths,mat=white,r=.006,parent=root):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=r;d.bevel_resolution=1
 for pts in paths:
  sp=d.splines.new('POLY');sp.points.add(len(pts)-1)
  for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat);return o
def spline(points,closed=False):
 p=[Vector(v) for v in points]
 if closed and (p[0]-p[-1]).length<.0001:p=p[:-1]
 result=[];count=len(p) if closed else len(p)-1
 for i in range(count):
  a=p[(i-1)%len(p)] if closed or i>0 else p[i];b=p[i];cc=p[(i+1)%len(p)];d=p[(i+2)%len(p)] if closed or i+2<len(p) else cc
  for j in range(8):
   u=j/8;result.append(tuple(.5*((2*b)+(-a+cc)*u+(2*a-5*b+4*cc-d)*u*u+(-a+3*b-3*cc+d)*u*u*u)))
 result.append(result[0] if closed else tuple(p[-1]));return result
def ell(name,loc,scale,mat=rim,parent=root,segments=40,rings=24):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=(0,0,0));o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale=scale;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def ring(name,cx,cy,cz,rx,rz,mat=dim):
 return curves(name,[[(cx+rx*math.cos(a),cy,cz+rz*math.sin(a)) for a in [j*math.tau/100 for j in range(101)]]],mat,.004)
abd=ell('Segmented abdomen',(0,-1.02,1.03),(.56,1.02,.47))
thor=ell('Thorax',(0,.05,1.26),(.58,.64,.56))
head=ell('Head capsule',(0,.91,1.34),(.49,.39,.43))
shells=[head]
for y in [-1.8,-1.57,-1.32,-1.07,-.82,-.57]:
 u=(y+1.02)/1.02;rr=math.sqrt(max(0,1-u*u));ring('Abdominal tergite',0,y,1.03,.563*rr,.473*rr,white)
curves('Thoracic sutures',[[(-.41,-.25,1.64),(-.22,.0,1.8),(0,.17,1.83),(.22,0,1.8),(.41,-.25,1.64)],[(0,-.5,1.58),(0,-.18,1.81),(0,.2,1.81)]],dim,.004)
# Compound eyes: hundreds of hexagonal facets mapped onto ellipsoidal surfaces.
for side in [-1,1]:
 center=Vector((side*.36,1.0,1.44));radii=Vector((.27,.33,.355))
 eye=ell('Compound eye '+str(side),center,radii,black);shells.append(eye)
 paths=[]
 for j in range(-15,16):
  lat=j*.081
  if abs(lat)>1.25:continue
  for i in range(31):
   lon=-1.43+i*.095+(j%2)*.0475
   if lon>1.43:continue
   pts=[]
   for k in range(7):
    a=k*math.tau/6;la=lat+.041*math.sin(a);lo=lon+.045*math.cos(a)/max(.42,math.cos(lat))
    pts.append(tuple(center+Vector((side*radii.x*math.cos(la)*math.cos(lo),radii.y*math.cos(la)*math.sin(lo),radii.z*math.sin(la)))*1.007))
   paths.append(pts)
 facets=curves('Ommatidia '+str(side),paths,bright,.0017);shells.append(facets)
for side in [-1,1]:
 a=ell('Antenna pedicel',(side*.16,1.27,1.37),(.075,.09,.065));shells.append(a)
 paths=[[(side*.16,1.28,1.4),(side*.28,1.45,1.57),(side*.35,1.57,1.72)]]
 for j in range(8):
  u=j/9;paths.append([(side*(.2+.15*u),1.33+.24*u,1.46+.26*u),(side*(.29+.15*u),1.33+.24*u,1.5+.26*u)])
 shells.append(curves('Arista',paths,white,.003))
shells.append(ell('Proboscis',(0,1.24,1.11),(.1,.18,.09)))
# Sparse curved bristles, attached to the body rather than a texture.
hair=[]
for j in range(210):
 u=random.uniform(-1.4,1.4);a=random.uniform(.15,math.pi-.15)
 y=-.3+u*.68;rx=.54 if y<-.35 else .58;z=1.1+.47*math.sin(a);x=rx*math.cos(a)
 b=Vector((x,y,z));normal=Vector((x*.8,-.18,math.sin(a))).normalized();length=random.uniform(.055,.15)
 hair.append([tuple(b),tuple(b+normal*length*.6),tuple(b+normal*length+Vector((0,-.025,0)))])
curves('Thorax and abdomen setae',hair,dim,.0018)
# Real wing geometry and venation parented to hinge objects.
wings=[]
for side in [-1,1]:
 pivot=empty('Wing hinge '+str(side),root);pivot.location=(side*.3,-.12,1.65);wings.append(pivot)
 outline=[(0,0,0),(.32,-.15,.01),(.61,-.65,.005),(.79,-1.27,-.035),(.78,-1.82,-.06),(.61,-2.02,-.075),(.4,-1.96,-.065),(.13,-1.37,-.025),(-.04,-.62,0),(0,0,0)]
 pts=spline([(side*x,y,z) for x,y,z in outline],True)
 # Dark membrane gives physical occlusion, fine lines supply the blueprint detail.
 mesh('Wing membrane',pts[:-1],[tuple(range(len(pts)-1))],black,pivot)
 curves('Wing perimeter',[pts],white,.005,pivot)
 veins=[[(0,0,0),(.28,-.44,.009),(.49,-.94,-.008),(.7,-1.8,-.049)],[(.01,-.04,.01),(.19,-.69,.012),(.4,-1.52,-.033),(.6,-1.98,-.058)],[(.02,-.08,.012),(.07,-.76,.009),(.2,-1.43,-.013),(.42,-1.94,-.05)],[(.19,-.69,.015),(.42,-.76,.015),(.62,-.77,.013)],[(.28,-1.15,.006),(.53,-1.19,.004),(.77,-1.25,-.013)],[(.4,-1.52,-.021),(.65,-1.59,-.022)]]
 curves('Longitudinal and cross veins',[spline([(side*x,y,z+.012) for x,y,z in path]) for path in veins],bright,.0035,pivot)
 for j in range(50):
  u=j/50;curves('Wing fringe', [[(side*(.62+.15*math.sin(u*math.pi)), -.7-u*1.1,-.025),(side*(.65+.15*math.sin(u*math.pi)),-.71-u*1.1,-.025)]],dim,.001,pivot)
 ell('Haltere stalk',(side*.57,-.51,1.25),(.025,.14,.025),white)
 ell('Haltere club',(side*.6,-.64,1.26),(.07,.09,.06))
# Articulated legs: rigid segments with keyed transforms, six independent chains.
legs=[]
def rod(name,r):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=1);o=bpy.context.object;o.name=name;o.parent=root;o.data.materials.append(rim)
 for p in o.data.polygons:p.use_smooth=True
 curves(name+' edge', [[(r,0,-.5),(r,0,.5)],[(-r,0,-.5),(-r,0,.5)]],dim,.0018,o)
 return o
for side in [-1,1]:
 for j in range(3):
  pieces=[rod('Leg %s.%s / %s'%(side,j,k),r) for k,r in enumerate([.043,.029,.018,.012,.009])]
  joints=[ell('Leg joint',(0,0,0),(.045,)*3) for _ in range(3)]
  legs.append((side,j,pieces,joints))
def span(o,a,b):
 a,b=Vector(a),Vector(b);d=b-a;o.location=(a+b)/2;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y');o.scale=(1,1,d.length)
def key(o):
 for k in ['location','rotation_quaternion','scale']:o.keyframe_insert(k)
# Stylized connectome shown during the neural shot.
brain=empty('Neural visualization',root);brain.location=(0,.93,1.37)
neuralpaths=[]
for side in [-1,1]:
 for j in range(65):
  p0=Vector((side*random.uniform(.2,.4),random.uniform(-.15,.12),random.uniform(-.21,.23)))
  p1=Vector((side*.12,random.uniform(-.1,.1),random.uniform(-.13,.13)))
  p2=Vector((random.uniform(-.04,.04),-.12,random.uniform(-.09,.09)))
  neuralpaths.append(spline([tuple(p0),tuple(p0*.5+p1*.5+Vector((0,.025,0))),tuple(p1),tuple(p2)]))
brainwire=curves('Connectome fibers',neuralpaths,dim,.0012,brain)
pulses=[ell('Neural pulse',(0,0,0),(.012,)*3,amber,brain,12,8) for i in range(24)]
neural=[brainwire]+pulses
camdata=bpy.data.cameras.new('Edit camera');cam=bpy.data.objects.new('Edit camera',camdata);s.collection.objects.link(cam);s.camera=cam;cam.rotation_mode='QUATERNION';camdata.lens=52;camdata.clip_start=.015
floor=curves('Contact plane',[[(-4,-3,.0),(4,-3,0),(4,3,0),(-4,3,0),(-4,-3,0)]],dim,.003,None)
def smooth(u):u=max(0,min(1,u));return u*u*(3-2*u)
def mix(a,b,u):return Vector(a).lerp(Vector(b),u)
for f in range(1,601):
 s.frame_set(f);t=(f-1)/30
 walk=12<=t<14.2;groom=14.2<=t<16;launch=smooth((t-16.25)/1.4)
 root.location=(0,max(0,min(1.0,(t-12)*.45)) if t>=12 else 0,launch*1.65)
 root.rotation_mode='QUATERNION';root.rotation_quaternion=(1,0,0,0);key(root)
 for side,j,pieces,joints in legs:
  ph=(t-12)*12+j*2.09+(math.pi if side>0 else 0);lift=max(0,math.sin(ph))*.19 if walk else 0;stride=math.cos(ph)*.16 if walk else 0
  a=(side*.4,.35-j*.46,1.12);b=(side*(.78+j*.09),.75-j*.68,.65);foot=(side*(1.1+j*.11),1.15-j*1.11+stride,lift+.07)
  if groom and j==0:
   rub=math.sin(t*16)*.09;b=(side*.43,.9,.93);foot=(side*(.07+abs(rub)),1.18,.9+rub)
  if launch>0:
   foot=mix(foot,(side*.65,.28-j*.55,.69),launch);b=mix(b,(side*.73,.4-j*.55,.85),launch)
  toe=Vector(foot)+Vector((side*.05,.07,-.025));tip=toe+Vector((side*.015,.065,-.008));claw=tip+Vector((-side*.025,.032,.007));chain=[a,b,foot,toe,tip,claw]
  for o,aa,bb in zip(pieces,chain,chain[1:]):span(o,aa,bb);key(o)
  for o,loc in zip(joints,[a,b,foot]):o.location=loc;o.keyframe_insert('location')
 for side,pivot in zip([-1,1],wings):
  spread=.08
  if 4<=t<8:spread=.4+.24*math.sin((t-4)*3.1)
  elif t>=16:spread=.65
  pivot.rotation_euler=(math.sin(t*(18 if t>=16 else 4))*(.36 if t>=16 else .08),0,side*spread)
  pivot.keyframe_insert('rotation_euler')
 for o in shells:o.hide_render=8<=t<12;o.keyframe_insert('hide_render')
 for o in neural:o.hide_render=not(8<=t<12);o.keyframe_insert('hide_render')
 for i,o in enumerate(pulses):
  path=neuralpaths[i*5%len(neuralpaths)];u=((t-8)*.8+i*.11)%1;v=u*(len(path)-1);idx=min(len(path)-2,int(v));o.location=mix(path[idx],path[idx+1],v-idx);o.keyframe_insert('location')
 floor.hide_render=not(12<=t<16.8);floor.keyframe_insert('hide_render')
 if t<4:
  u=smooth(t/4);target=mix((.52,1.06,1.46),(0,.35,1.15),u);pos=mix((1.08,1.72,1.85),(4.2,5.9,3.25),u)
 elif t<8:
  u=smooth((t-4)/4);target=mix((.3,-.7,1.55),(.7,-1.0,1.55),u);pos=mix((2.8,-3.2,4.8),(1.5,-1.5,3.2),u)
 elif t<12:
  u=smooth((t-8)/4);target=Vector((0,.93,1.37));pos=mix((1.95,3.2,2.25),(-1.7,2.6,1.7),u)
 elif t<16:
  u=smooth((t-12)/4);target=Vector((0,.3,1.0))+root.location;pos=mix((4.5,5.5,2.8),(2.7,3.8,2.0),u)+root.location
 else:
  u=smooth((t-16)/4);target=Vector((0,-.2,1.2))+root.location;pos=mix((4.6,5.9,3.0),(-3.8,6.3,3.5),u)+root.location
 cam.location=pos;cam.rotation_quaternion=(target-pos).to_track_quat('-Z','Y');key(cam)

import bpy,math,json,time
from pathlib import Path
from mathutils import Vector,Quaternion
rootdir=Path(__file__).resolve().parents[1]
timing=json.loads((rootdir/'config'/'timing.json').read_text())
a,b=timing['cuts'][2:4]
beats=[12+(x-a)/(b-a)*4 for x in timing['lowrider']]
s=bpy.context.scene;root=bpy.data.objects['Drosophila / rig']
def pulse(t):
 v=0
 for hit in beats:
  u=t-hit
  if 0<=u<.4:v+=math.sin(math.pi*min(1,u/.4))**1.4
 return min(1,v)
def span(o,a,b):
 a,b=Vector(a),Vector(b);d=b-a;o.location=(a+b)/2;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y');o.scale=(1,1,d.length)
def key(o):
 for prop in ['location','rotation_quaternion','scale']:o.keyframe_insert(prop)
# Cache keyed original transforms before replacing the ground-scene motion.
positions={}
for f in range(361,481):s.frame_set(f);positions[f]=root.location.copy()
for f in range(361,481):
 s.frame_set(f);t=(f-1)/30
 if t<14.05:continue
 p=pulse(t);q=Quaternion((1,0,0),.38*p);base=positions[f];anchor=Vector((0,-.8,.4))
 root.rotation_quaternion=q;root.location=base+anchor-q@anchor+Vector((0,0,.06*p));key(root)
 cam=s.camera;blend=min(1,max(0,(t-14.05)/.3));blend=blend*blend*(3-2*blend)
 target=Vector((0,1.1,1.45));wide=Vector((4.8,7,3.4));rotation=(target-wide).to_track_quat('-Z','Y')
 cam.location=cam.location.lerp(wide,blend);cam.rotation_quaternion=cam.rotation_quaternion.slerp(rotation,blend);key(cam)
 for side in [-1,1]:
  for j in range(3):
   aa=Vector((side*.4,.35-j*.46,1.12));knee=Vector((side*(.78+j*.09),.75-j*.68,.65-.1*p))
   # Feet stay on the ground as the body pitches; foreleg joints articulate.
   worldfoot=base+Vector((side*(1.1+j*.11),1.15-j*1.11,.07))
   foot=q.inverted()@(worldfoot-root.location)
   toe=foot+q.inverted()@Vector((side*.05,.07,-.025));tip=toe+q.inverted()@Vector((side*.015,.065,-.008));claw=tip+q.inverted()@Vector((-side*.025,.032,.007))
   chain=[aa,knee,foot,toe,tip,claw]
   for k,(u,v) in enumerate(zip(chain,chain[1:])):
    o=bpy.data.objects[f'Leg {side}.{j} / {k}'];span(o,u,v);key(o)
   # Original joint spheres follow the same leg ordering as construction.
   legindex=(0 if side==-1 else 3)+j
   for k,loc in enumerate([aa,knee,foot]):
    idx=legindex*3+k;name='Leg joint' if idx==0 else f'Leg joint.{idx:03}'
    ob=bpy.data.objects[name];ob.location=loc;ob.keyframe_insert('location')

s.frame_set(1)
s.render.filepath='//../work/frames/'
(ROOT/'assets').mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets'/'Drosophila.blend'))
print('Scene rebuilt. Rendering is a separate step.')
