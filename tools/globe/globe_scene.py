# blender -b -P globe_scene.py -- <seqdir> <outdir> [samples] [frame_end]
import bpy,sys,json,math,os
from mathutils import Vector,Matrix
argv=sys.argv[sys.argv.index("--")+1:]
SEQ,OUT=os.path.abspath(argv[0]),os.path.abspath(argv[1]); SAMPLES=int(argv[2]) if len(argv)>2 else 48
meta=json.load(open(f"{SEQ}/meta.json")); N=len(meta); FEND=int(argv[3]) if len(argv)>3 else N
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc=bpy.context.scene; sc.frame_start,sc.frame_end=1,FEND; sc.render.fps=24
sc.render.engine="CYCLES"; sc.cycles.device="GPU"; sc.cycles.samples=SAMPLES; sc.cycles.use_denoising=True
pr=bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type="OPTIX"; pr.get_devices()
for d in pr.devices: d.use=d.type=="OPTIX"
sc.render.resolution_x,sc.render.resolution_y=1080,1920
sc.view_settings.view_transform="AgX"; sc.view_settings.look="AgX - Medium High Contrast"
sc.render.image_settings.file_format="PNG"; sc.render.filepath=f"{OUT}/f_"

def sphere(name,r,seg=512):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,segments=seg,ring_count=seg//2)
    o=bpy.context.object; o.name=name; bpy.ops.object.shade_smooth(); return o
def seq_image(path,colorspace):
    im=bpy.data.images.load(path); im.source="SEQUENCE"; im.colorspace_settings.name=colorspace; return im
def equirect_uv(nt):
    # u=(atan2(y,x)+pi)/2pi, v=(asin(z)+pi/2)/pi  (matches the texture generator's lon/lat convention)
    tc=nt.nodes.new("ShaderNodeTexCoord"); sep=nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"],sep.inputs[0])
    nrm=nt.nodes.new("ShaderNodeVectorMath"); nrm.operation="NORMALIZE"; nt.links.new(tc.outputs["Object"],nrm.inputs[0])
    sepn=nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nrm.outputs[0],sepn.inputs[0])
    at=nt.nodes.new("ShaderNodeMath"); at.operation="ARCTAN2"; nt.links.new(sepn.outputs[1],at.inputs[0]); nt.links.new(sepn.outputs[0],at.inputs[1])
    u=nt.nodes.new("ShaderNodeMath"); u.operation="MULTIPLY_ADD"; nt.links.new(at.outputs[0],u.inputs[0]); u.inputs[1].default_value=1/(2*math.pi); u.inputs[2].default_value=0.5
    asn=nt.nodes.new("ShaderNodeMath"); asn.operation="ARCSINE"; nt.links.new(sepn.outputs[2],asn.inputs[0])
    v=nt.nodes.new("ShaderNodeMath"); v.operation="MULTIPLY_ADD"; nt.links.new(asn.outputs[0],v.inputs[0]); v.inputs[1].default_value=1/math.pi; v.inputs[2].default_value=0.5
    cmb=nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u.outputs[0],cmb.inputs[0]); nt.links.new(v.outputs[0],cmb.inputs[1]); return cmb.outputs[0]
def tex_node(nt,img,uv):
    t=nt.nodes.new("ShaderNodeTexImage"); t.image=img; t.interpolation="Cubic"; t.extension="EXTEND"
    iu=t.image_user; iu.frame_duration=N; iu.frame_start=1; iu.frame_offset=-1; iu.use_auto_refresh=True; iu.use_cyclic=False
    nt.links.new(uv,t.inputs["Vector"]); return t

# --- Earth
earth=sphere("Earth",1.0); m=bpy.data.materials.new("Earth"); m.use_nodes=True; nt=m.node_tree; earth.data.materials.append(m)
bsdf=nt.nodes["Principled BSDF"]; uv=equirect_uv(nt)
col=tex_node(nt,seq_image(f"{SEQ}/color_0000.jpg","sRGB"),uv); msk=tex_node(nt,seq_image(f"{SEQ}/mask_0000.png","Non-Color"),uv)
sepm=nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(msk.outputs["Color"],sepm.inputs[0])
# ocean: deepen and add a little blue variation; land: texture
hsv=nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value=0.92; hsv.inputs["Value"].default_value=0.95
nt.links.new(col.outputs["Color"],hsv.inputs["Color"]); nt.links.new(hsv.outputs[0],bsdf.inputs["Base Color"])
rough=nt.nodes.new("ShaderNodeMapRange"); rough.inputs["To Min"].default_value=0.55; rough.inputs["To Max"].default_value=0.85
nt.links.new(sepm.outputs["Red"],rough.inputs["Value"]); nt.links.new(rough.outputs[0],bsdf.inputs["Roughness"]); bsdf.inputs["Specular IOR Level"].default_value=0.12
# India highlight: soft warm emission on plate 501 land
emis=nt.nodes.new("ShaderNodeMath"); emis.operation="MULTIPLY"; emis.inputs[1].default_value=0.05
nt.links.new(sepm.outputs["Green"],emis.inputs[0])
tr=nt.nodes.new("ShaderNodeMath"); tr.operation="POWER"; tr.inputs[1].default_value=2.4; nt.links.new(sepm.outputs["Blue"],tr.inputs[0])
trs=nt.nodes.new("ShaderNodeMath"); trs.operation="MULTIPLY_ADD"; trs.inputs[1].default_value=0.5; nt.links.new(tr.outputs[0],trs.inputs[0]); nt.links.new(emis.outputs[0],trs.inputs[2])
emis=trs
bsdf.inputs["Emission Color"].default_value=(1.0,0.55,0.18,1); nt.links.new(emis.outputs[0],bsdf.inputs["Emission Strength"])
# --- Clouds (procedural, slowly evolving)
cl=sphere("Clouds",1.012,256); mc=bpy.data.materials.new("Clouds"); mc.use_nodes=True; ct=mc.node_tree; cl.data.materials.append(mc)
cb=ct.nodes["Principled BSDF"]; cb.inputs["Base Color"].default_value=(1,1,1,1); cb.inputs["Roughness"].default_value=1
tc=ct.nodes.new("ShaderNodeTexCoord"); nz=ct.nodes.new("ShaderNodeTexNoise"); nz.noise_dimensions="4D"; nz.inputs["Scale"].default_value=4.5; nz.inputs["Detail"].default_value=12; nz.inputs["Roughness"].default_value=0.62; nz.inputs["Distortion"].default_value=0.35
ct.links.new(tc.outputs["Object"],nz.inputs["Vector"]); nz.inputs["W"].default_value=0
nz.inputs["W"].keyframe_insert("default_value",frame=1); nz.inputs["W"].default_value=0.25; nz.inputs["W"].keyframe_insert("default_value",frame=max(FEND,2))
ramp=ct.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position=0.58; ramp.color_ramp.elements[1].position=0.74
ct.links.new(nz.outputs["Fac"],ramp.inputs["Fac"]); ct.links.new(ramp.outputs["Color"],cb.inputs["Alpha"])
mc.blend_method="BLEND" if hasattr(mc,"blend_method") else None
# --- Atmosphere rim
at=sphere("Atmosphere",1.035,256); ma=bpy.data.materials.new("Atmos"); ma.use_nodes=True; an=ma.node_tree; at.data.materials.append(ma)
for n in list(an.nodes): an.nodes.remove(n)
out=an.nodes.new("ShaderNodeOutputMaterial"); lw=an.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value=0.35
pw=an.nodes.new("ShaderNodeMath"); pw.operation="POWER"; pw.inputs[1].default_value=3.2; an.links.new(lw.outputs["Facing"],pw.inputs[0])
em=an.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value=(0.32,0.58,1.0,1); em.inputs["Strength"].default_value=1.5
tr=an.nodes.new("ShaderNodeBsdfTransparent"); mix=an.nodes.new("ShaderNodeMixShader")
an.links.new(pw.outputs[0],mix.inputs[0]); an.links.new(tr.outputs[0],mix.inputs[1]); an.links.new(em.outputs[0],mix.inputs[2]); an.links.new(mix.outputs[0],out.inputs[0])
at.visible_shadow=False; cl.visible_shadow=True
# --- World: black with faint stars
w=bpy.data.worlds.new("Space"); sc.world=w; w.use_nodes=True; wn=w.node_tree; bg=wn.nodes["Background"]
st=wn.nodes.new("ShaderNodeTexVoronoi"); st.inputs["Scale"].default_value=900; sr=wn.nodes.new("ShaderNodeValToRGB")
sr.color_ramp.elements[0].position=0.0; sr.color_ramp.elements[0].color=(1,1,1,1); sr.color_ramp.elements[1].position=0.035; sr.color_ramp.elements[1].color=(0,0,0,1)
wn.links.new(st.outputs["Distance"],sr.inputs["Fac"]); wn.links.new(sr.outputs["Color"],bg.inputs["Color"]); bg.inputs["Strength"].default_value=0.6
# --- Sun (from the south-west, low, for long terminator shading)
bpy.ops.object.light_add(type="SUN"); sun=bpy.context.object; sun.data.energy=4.2; sun.data.angle=math.radians(0.6)
# --- Camera follows India: behind (south of) India, looking north toward Asia, horizon curving at top
bpy.ops.object.camera_add(); cam=bpy.context.object; sc.camera=cam; cam.data.lens=32; cam.data.sensor_width=36
def ll2v(lat,lon,r=1.0):
    a,b=math.radians(lat),math.radians(lon); return Vector((math.cos(a)*math.cos(b),math.cos(a)*math.sin(b),math.sin(a)))*r
def look(cam_pos,target,up):
    f=(target-cam_pos).normalized(); r=f.cross(up).normalized(); u=r.cross(f)
    return Matrix(((r.x,u.x,-f.x),(r.y,u.y,-f.y),(r.z,u.z,-f.z))).to_4x4()
for i in range(FEND):
    md=meta[str(i)]; la,lo=md["india_lat"],md["india_lon"]
    if os.environ.get("CAM")=="fixed":
        cl,co,cr=map(float,os.environ["CAM_POS"].split(",")); tl,to=map(float,os.environ["CAM_TGT"].split(","))
        cpos=ll2v(cl,co,cr*(1-0.06*i/max(FEND-1,1))); tgt=ll2v(tl,to,1.0); a,b=math.radians(tl),math.radians(to)
    else:
        cpos=ll2v(la+4.0,lo+1.0,2.45); tgt=ll2v(la+21.0,lo+4.0,1.0)
        a,b=math.radians(la+21.0),math.radians(lo+4.0)
    north=Vector((-math.sin(a)*math.cos(b),-math.sin(a)*math.sin(b),math.cos(a)))
    M=look(cpos,tgt,north); M.translation=cpos; cam.matrix_world=M
    cam.keyframe_insert("location",frame=i+1); cam.keyframe_insert("rotation_euler",frame=i+1)
    # sun stays fixed relative to the camera so lighting doesn't drift
    sd=(ll2v(tl+10,to-40) if os.environ.get('CAM')=='fixed' else ll2v(la+25,lo-35)).normalized(); sun.rotation_euler=(-sd).to_track_quat("-Z","Y").to_euler(); sun.keyframe_insert("rotation_euler",frame=i+1)
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/scene.blend")
only=os.environ.get("FRAMES")
if only:
    for f in map(int,only.split(",")):
        sc.frame_set(f); sc.render.filepath=f"{OUT}/f_{f:04d}"; bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
