# Oblique (isometric box-room, Habbo-style) house generator. python3 gen.py
from PIL import Image, ImageDraw, ImageFont
import json, glob, os
W,H=1280,720; TW,TH=80,40; OX,OY=640,170; WH=130; PH=34; T=0.25; SLAB=18
OUT=(20,15,20,255)
fp=(glob.glob('/usr/share/fonts/**/NotoSansCJK-Bold.ttc',recursive=True)+glob.glob('/usr/share/fonts/**/NotoSerifCJK-Bold.ttc',recursive=True))[0]
font=ImageFont.truetype(fp,28); small=ImageFont.truetype(fp,18)
def P(gx,gy,z=0): return (round(OX+(gx-gy)*TW/2), round(OY+(gx+gy)*TH/2-z))
rooms=[("genius","ジニアスの部屋",(0,0,6,6),((250,250,248),(242,242,240))),
       ("lisa","リサっちの部屋",(6,0,12,6),((250,250,248),(242,242,240))),
       ("foyer","大広間",(0,6,12,12),((250,250,248),(242,242,240)))]
mk=lambda:Image.new("RGBA",(W,H),(0,0,0,0))
poly=lambda d,pts,c,w=3:d.polygon(pts,fill=c,outline=OUT,width=w)
# background
bg=Image.new("RGBA",(W,H),(40,44,70,255)); d=ImageDraw.Draw(bg)
for i in range(0,W,40):
  for j in range(0,H,40):
    if (i//40+j//40)%2: d.rectangle([i,j,i+39,j+39],fill=(46,50,80,255))
# floors
fl=mk(); d=ImageDraw.Draw(fl)
poly(d,[P(0,12),P(12,12),P(12,12,-SLAB),P(0,12,-SLAB)],(215,215,212,255))
poly(d,[P(12,0),P(12,12),P(12,12,-SLAB),P(12,0,-SLAB)],(195,195,192,255))
for _,_,(x0,y0,x1,y1),(c1,c2) in rooms:
  for gx in range(x0,x1):
    for gy in range(y0,y1):
      d.polygon([P(gx,gy),P(gx+1,gy),P(gx+1,gy+1),P(gx,gy+1)],fill=(c1 if (gx+gy)%2 else c2)+(255,),outline=tuple(v-25 for v in c2)+(255,))
  d.polygon([P(x0,y0),P(x1,y0),P(x1,y1),P(x0,y1)],outline=OUT,width=3)
# walls
wl=mk(); d=ImageDraw.Draw(wl)
WX,WY,TOP=(250,250,248,255),(232,232,230,255),(255,255,255,255)  # default interior = white
def prism(ax,ay,bx,by,h,cols=(WX,WY,TOP)):
  for a,b,c,e,col in [((bx,ay),(bx,by),(bx,by,h),(bx,ay,h),cols[0]),((ax,by),(bx,by),(bx,by,h),(ax,by,h),cols[1])]:
    poly(d,[P(*a),P(*b),P(*c),P(*e)],col)
  poly(d,[P(ax,ay,h),P(bx,ay,h),P(bx,by,h),P(ax,by,h)],cols[2])
segs=[]
segs.append((-T,-T,0,12,WH)); segs.append((0,-T,12,0,WH))      # back walls
def hseg(gy,a,b,gaps):
  pts=[a]+[v for g in gaps for v in g]+[b]
  for i in range(0,len(pts),2): segs.append((pts[i],gy-T/2,pts[i+1],gy+T/2,PH))
def vseg(gx,a,b,gaps):
  pts=[a]+[v for g in gaps for v in g]+[b]
  for i in range(0,len(pts),2): segs.append((gx-T/2,pts[i],gx+T/2,pts[i+1],PH))
hseg(6,0,6-T/2,[(2.4,3.6)]); hseg(6,6+T/2,12,[(8.4,9.6)]); vseg(6,0,6+T/2,[(2.4,3.6)])
for s in [x for x in segs if x[4]==WH]: prism(*s)
def wdoor(on, a,b, z0,z1, col):  # rect on inner face of back wall
  pts=[(0,a,z0),(0,b,z0),(0,b,z1),(0,a,z1)] if on=="L" else [(a,0,z0),(b,0,z0),(b,0,z1),(a,0,z1)]
  poly(d,[P(*p) for p in pts],col)
wdoor("L",8.4,9.6,0,95,(30,25,35,255))                # entrance door
d.polygon([P(0,8.4),P(0.6,8.4),P(0.6,9.6),P(0,9.6)],fill=(205,205,200,255),outline=OUT)  # doormat
for on,a,b in [("L",2,4),("R",2,4),("R",8,10),("L",3+6+0.0,3+6.0) ]:
  if a==b: continue
  wdoor(on,a,b,55,105,(150,215,250,255)); 
  m=(a+b)/2; pts=[(0,m,55),(0,m,105)] if on=="L" else [(m,0,55),(m,0,105)]
  d.line([P(*pts[0]),P(*pts[1])],fill=OUT,width=3)
  sill=[(0,a,52),(0,b,52),(0.3,b,52),(0.3,a,52)] if on=="L" else [(a,0,52),(b,0,52),(b,0.3,52),(a,0.3,52)]
  poly(d,[P(*p) for p in sill],(140,90,50,255),2)
wb=wl; wf=mk(); d=ImageDraw.Draw(wf)
for s in sorted([x for x in segs if x[4]!=WH],key=lambda s:s[2]+s[3]): prism(*s)
wl=Image.alpha_composite(wb,wf)
# labels
lb=mk(); d=ImageDraw.Draw(lb)
def pill(cx,cy,t,f):
  bb=d.textbbox((0,0),t,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]
  d.rounded_rectangle([cx-tw//2-14,cy-th//2-10,cx+tw//2+14,cy+th//2+12],12,fill=(255,255,255,240),outline=OUT,width=3)
  d.text((cx-tw//2,cy-th//2-bb[1]),t,font=f,fill=OUT)
for _,n,(x0,y0,x1,y1),_ in rooms: pill(*P((x0+x1)/2,(y0+y1)/2),n,font)
ex,ey=P(0,9,110); pill(ex-70,ey-30,"入口 ENTRANCE",small)
# empty slots
em=mk(); d=ImageDraw.Draw(em); slots={}
for rid,_,(x0,y0,x1,y1),_ in rooms:
  slots[rid]=[]
  for gx,gy in [(x0+1,y0+1),(x1-2,y0+1),(x0+1,y1-2),(x1-2,y1-2)]:
    q=[P(gx+.2,gy+.2),P(gx+.8,gy+.2),P(gx+.8,gy+.8),P(gx+.2,gy+.8)]
    d.polygon(q,outline=(20,15,20,120),width=2)
    xs=[p[0] for p in q]; ys=[p[1] for p in q]; slots[rid].append({"tile":[gx,gy],"screen_bounds":[min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]})
L={"walls_back":wb,"walls_front":wf,"background":bg,"floors":fl,"empty_slots":em,"walls":wl,"labels":lb}
for k,v in L.items(): v.save(f"layers/layer-{k.replace('_slots','').replace('_','-')}.png")
wl.save("layers/layer-walls.png")
full=bg
for k in ["floors","empty_slots","walls_back","walls_front"]+(["labels"] if os.environ.get("HOUSE_LABELS")=="1" else []): full=Image.alpha_composite(full,L[k])
full.convert("RGB").save("house-structure.png")
def bbox(pts): xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; return [min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]
def door(gx0,gy0,gx1,gy1,h): return {"screen_bounds":bbox([P(gx0,gy0),P(gx1,gy1),P(gx0,gy0,h),P(gx1,gy1,h)]),"grid":[[gx0,gy0],[gx1,gy1]]}
json.dump({"house":"home","style":"oblique-isometric-box-pop","default_interior":{"walls":"white","floors":"white","note":"used when no interior is specified; per-room colors/wallpaper may later come from an order/catalog system (not implemented)"},"projection":{"type":"isometric 2:1","tile_w":TW,"tile_h":TH,"origin_screen":[OX,OY],"screen_x":"OX+(gx-gy)*tile_w/2","screen_y":"OY+(gx+gy)*tile_h/2 - z","grid_size":[12,12],"back_wall_height":WH,"partition_height":PH},
 "canvas":[W,H],
 "rooms":[{"id":r,"name":n,"grid":[x0,y0,x1-x0,y1-y0],"bounds":bbox([P(x0,y0),P(x1,y0),P(x1,y1),P(x0,y1)]),"floor_polygon":[P(x0,y0),P(x1,y0),P(x1,y1),P(x0,y1)],"object_slots":slots[r]} for r,n,(x0,y0,x1,y1),_ in rooms],
 "connections":[{"from":"outside","to":"foyer","door":door(0,8.4,0,9.6,95),"note":"door in foyer back-left wall"},
  {"from":"foyer","to":"genius","door":door(2.4,6,3.6,6,PH)},{"from":"foyer","to":"lisa","door":door(8.4,6,9.6,6,PH)},{"from":"genius","to":"lisa","door":door(6,2.4,6,3.6,PH)}],
 "layers":["walls","floors","labels","objects","characters","lighting"],
 "layer_files":{"background":"layers/layer-background.png","floors":"layers/layer-floors.png","empty_slots":"layers/layer-empty.png","walls":"layers/layer-walls.png (= walls_back + walls_front, legacy)","walls_back":"layers/layer-walls-back.png","walls_front":"layers/layer-walls-front.png","objects":"layers/layer-objects.png (built by swap_objects.py)","lighting":"layers/layer-lighting.png (make_lighting.py)","floor_skins":"layers/layer-floor-skins.png (floor_skins.py via swap_objects.py; per-room rooms.<id>.floor_skin)","labels":"layers/layer-labels.png"},
 "composite_order":["background","floors","floor_skins","empty_slots","walls_back","objects","walls_front","characters","speech"],"lighting_optional":"off by default; HOUSE_LIGHTING=1 to composite layers/layer-lighting.png after characters","lighting":"warm amber floor-glow overlay (make_lighting.py, alpha-over, clipped to house); pendant lamp fixture abandoned","live_output":"house-live.png","state_file":"state/env.json",
 "update_model":"rooms fixed; swap objects/state layers; regenerate base only on structural change"},open("house-structure.json","w"),ensure_ascii=False,indent=1)
