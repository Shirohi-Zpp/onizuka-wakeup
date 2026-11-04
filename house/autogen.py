# On-the-fly sprite generator: keyword -> Pillow drawer. Saves sprites/<type>.png + registers in sprites.json (atomic).
from PIL import Image, ImageDraw, ImageFont
import json, os, glob, hashlib
TW,TH=80,40; OUT=(20,15,20,255); S=300; A=(150,200)
FP=(glob.glob('/usr/share/fonts/**/NotoSansCJK-Bold.ttc',recursive=True)+glob.glob('/usr/share/fonts/**/NotoSerifCJK-Bold.ttc',recursive=True))[0]
def P(gx,gy,z=0): return (round(A[0]+(gx-gy)*TW/2), round(A[1]+(gx+gy)*TH/2-z))
def box(d,x0,y0,x1,y1,z0,z1,top,fx,fy):
  d.polygon([P(x1,y0,z0),P(x1,y1,z0),P(x1,y1,z1),P(x1,y0,z1)],fill=fx,outline=OUT,width=3)
  d.polygon([P(x0,y1,z0),P(x1,y1,z0),P(x1,y1,z1),P(x0,y1,z1)],fill=fy,outline=OUT,width=3)
  d.polygon([P(x0,y0,z1),P(x1,y0,z1),P(x1,y1,z1),P(x0,y1,z1)],fill=top,outline=OUT,width=3)
dk=lambda c,k=40:tuple(max(0,v-k) for v in c[:3])
lt=lambda c,k=50:tuple(min(255,v+k) for v in c[:3])
def plush(d,body,ears="cat",belly=None,muzzle=False,bow=None):
  cx,cy=P(0.5,0.5); O=body; L=belly or lt(body)
  d.ellipse([cx-24,cy-8,cx+24,cy+8],fill=(0,0,0,70))
  if ears=="cat": d.ellipse([cx+10,cy-30,cx+34,cy-14],fill=O,outline=OUT,width=3)
  d.ellipse([cx-22,cy-40,cx+22,cy+2],fill=O,outline=OUT,width=3)
  d.ellipse([cx-12,cy-26,cx+12,cy-2],fill=L,outline=OUT,width=2)
  for s in (-1,1):
    if ears=="cat": d.polygon([(cx+s*24,cy-80),(cx+s*8,cy-70),(cx+s*22,cy-60)],fill=O,outline=OUT,width=3)
    elif ears=="round":
      d.ellipse([cx+s*20-11,cy-84,cx+s*20+11,cy-62],fill=O,outline=OUT,width=3); d.ellipse([cx+s*20-5,cy-78,cx+s*20+5,cy-68],fill=L)
    elif ears=="long": d.ellipse([cx+s*11-8,cy-112,cx+s*11+8,cy-64],fill=O,outline=OUT,width=3)
    elif ears=="flop": d.ellipse([cx+s*24-9,cy-76,cx+s*24+9,cy-46],fill=dk(O),outline=OUT,width=3)
  d.ellipse([cx-26,cy-78,cx+26,cy-36],fill=O,outline=OUT,width=3)
  for s in (-1,1):
    d.ellipse([cx+s*11-3,cy-64,cx+s*11+3,cy-56],fill=OUT)
    d.ellipse([cx+s*18-4,cy-52,cx+s*18+4,cy-47],fill=(255,140,160))
  if muzzle: d.ellipse([cx-10,cy-56,cx+10,cy-42],fill=L,outline=OUT,width=2); d.ellipse([cx-4,cy-55,cx+4,cy-49],fill=OUT)
  else:
    d.polygon([(cx-3,cy-53),(cx+3,cy-53),(cx,cy-50)],fill=(230,80,100))
    if ears=="cat":
      for s in (-1,1): d.line([(cx+s*14,cy-48),(cx+s*30,cy-50)],fill=OUT,width=1)
  d.line([(cx-4,cy-46),(cx,cy-48),(cx+4,cy-46)],fill=OUT,width=2)
  if bow: d.polygon([(cx-12,cy-40),(cx,cy-35),(cx-12,cy-30)],fill=bow,outline=OUT); d.polygon([(cx+12,cy-40),(cx,cy-35),(cx+12,cy-30)],fill=bow,outline=OUT)
  for s in (-1,1): d.ellipse([cx+s*12-7,cy-8,cx+s*12+7,cy+2],fill=L,outline=OUT,width=2)
def futon(d):
  box(d,0,0,1.3,2.2,0,8,(245,245,240),(200,200,195),(215,215,210)); box(d,0.1,0.75,1.2,2.15,8,20,(80,120,200),(50,85,160),(60,95,175))
  for t in (1.1,1.45,1.8): d.line([P(0.1,t,20),P(1.2,t,20)],fill=(240,200,80),width=3)
  box(d,0.3,0.15,1.0,0.6,8,18,(255,250,230),(220,210,180),(235,225,195))
def generic(d,name,typ):
  h=hashlib.md5(typ.encode()).digest(); c=(120+h[0]%120,120+h[1]%120,120+h[2]%120)
  box(d,0.2,0.2,0.8,0.8,0,38,lt(c,40),c,dk(c))
  f=ImageFont.truetype(FP,22); ch=(name or typ)[:1].upper(); x,y=P(0.5,0.5,38)
  bb=d.textbbox((0,0),ch,font=f); d.text((x-(bb[2]-bb[0])//2-bb[0],y-(bb[3]-bb[1])//2-bb[1]),ch,font=f,fill=OUT)
def piano(d):  # upright piano, back against gy=0 wall, keys face +y
  K=(40,30,35); Kf=(25,18,22); Kt=(70,55,60)
  for x in (0.1,1.5): box(d,x,0.55,x+0.1,0.75,0,30,Kt,K,Kf)            # legs
  box(d,0,0,1.6,0.45,0,72,Kt,K,Kf)                                      # body
  box(d,0,0.45,1.6,0.8,30,38,(250,250,245),(210,210,205),(60,45,50))     # keybed (white top)
  for i in range(1,16): d.line([P(i*0.1,0.47,38),P(i*0.1,0.78,38)],fill=OUT,width=1)
  for i in (1,2,4,5,6,8,9,11,12,13,15):
    d.polygon([P(i*0.1-0.03,0.47,38),P(i*0.1+0.03,0.47,38),P(i*0.1+0.03,0.64,38),P(i*0.1-0.03,0.64,38)],fill=OUT)
  d.polygon([P(0.2,0.45,50),P(1.4,0.45,50),P(1.4,0.45,64),P(0.2,0.45,64)],fill=(250,240,200),outline=OUT,width=2)  # music sheet
  d.line([P(0.3,0.45,57),P(1.3,0.45,57)],fill=(120,100,90),width=1)
  box(d,0.5,1.05,1.1,1.35,0,22,(200,60,80),(150,40,60),(170,45,65))     # bench
def television(d):  # CRT TV on low stand, screen faces +y
  box(d,0,0,1.2,0.6,0,24,(200,160,110),(160,120,80),(180,140,95))        # stand
  box(d,0.1,0.05,1.1,0.6,24,74,(120,125,135),(80,85,95),(100,105,115))   # tv body
  scr=[P(0.2,0.6,32),P(0.85,0.6,32),P(0.85,0.6,68),P(0.2,0.6,68)]
  d.polygon(scr,fill=(120,220,255),outline=OUT,width=3)
  d.polygon([P(0.25,0.6,52),P(0.5,0.6,52),P(0.5,0.6,64),P(0.25,0.6,64)],fill=(220,250,255))   # glare
  for z in (40,46): d.line([P(0.3,0.6,z),P(0.8,0.6,z)],fill=(80,170,220),width=2)
  for z,c in ((60,(255,90,90)),(48,(255,210,60))): x,y=P(0.97,0.6,z); d.ellipse([x-4,y-4,x+4,y+4],fill=c,outline=OUT)   # knobs
  a,b=P(0.6,0.3,74),P(0.5,0.1,110); d.line([a,b],fill=OUT,width=3); a2=P(0.6,0.3,74); b2=P(0.9,0.5,108); d.line([a2,b2],fill=OUT,width=3)  # antenna
def potted_plant(d):
  box(d,0.3,0.3,0.7,0.7,0,22,(235,140,90),(200,100,60),(170,80,50))      # pot
  d.polygon([P(0.33,0.33,22),P(0.67,0.33,22),P(0.67,0.67,22),P(0.33,0.67,22)],fill=(90,60,40))
  x,y=P(0.5,0.5,22)
  for dx,dy,w,h,c in [(-22,-46,20,34,(60,160,70)),(4,-50,20,36,(60,160,70)),(-12,-66,22,40,(80,190,80)),(-30,-30,22,22,(80,190,80)),(10,-32,24,22,(100,205,90)),(-8,-40,18,24,(110,215,100))]:
    d.ellipse([x+dx,y+dy,x+dx+w,y+dy+h],fill=c,outline=OUT,width=3)
  d.line([(x-2,y-30),(x,y-2)],fill=(40,110,50),width=3)
def pendant_lamp(d):  # hangs from ceiling: cord from top, shade at z~95, glow on floor
  cx,cy=P(0.5,0.5); d.ellipse([cx-34,cy-14,cx+34,cy+14],fill=(255,230,120,90))
  d.ellipse([cx-18,cy-7,cx+18,cy+7],fill=(255,240,160,120))
  top=P(0.5,0.5,175); sh=P(0.5,0.5,112); d.line([top,sh],fill=OUT,width=3)
  d.rectangle([top[0]-8,top[1]-4,top[0]+8,top[1]+2],fill=(240,240,240),outline=OUT,width=2)  # ceiling cap
  x,y=P(0.5,0.5,95)
  d.ellipse([x-8,y-4,x+8,y+12],fill=(255,250,200),outline=OUT,width=2)                         # bulb
  d.polygon([(x-6,y-18),(x+6,y-18),(x+24,y+2),(x-24,y+2)],fill=(240,90,70),outline=OUT,width=3)  # shade
  d.ellipse([x-24,y-3,x+24,y+7],fill=(255,240,170),outline=OUT,width=2)
def computer_desk(d):  # desk against gy=0 wall, faces +y
  W=(205,160,110); Wd=(165,120,80); Wt=(225,185,135)
  for x in (0,1.3):
    box(d,x,0,x+0.1,0.7,0,34,Wt,Wd,W)                                      # side panels
  box(d,0,0,1.4,0.7,34,40,Wt,Wd,W)                                          # top
  box(d,0.55,0.1,0.85,0.25,40,44,(80,85,95),(50,55,65),(60,65,75))          # monitor foot
  box(d,0.3,0.1,1.1,0.18,46,86,(70,75,85),(40,45,55),(60,65,75))            # monitor
  d.polygon([P(0.36,0.18,52),P(1.04,0.18,52),P(1.04,0.18,80),P(0.36,0.18,80)],fill=(90,200,250),outline=OUT,width=2)
  for z in (60,66,72): d.line([P(0.42,0.18,z),P(0.8,0.18,z)],fill=(230,250,255),width=2)
  box(d,0.35,0.35,1.0,0.55,40,43,(240,240,240),(190,190,190),(210,210,210)) # keyboard
  box(d,1.1,0.4,1.2,0.52,40,43,(240,240,240),(190,190,190),(210,210,210))   # mouse
  box(d,0.45,0.85,0.95,1.25,0,22,(90,140,220),(60,100,180),(70,115,200))    # chair seat
  box(d,0.45,1.15,0.95,1.25,22,48,(90,140,220),(60,100,180),(70,115,200))   # chair back
def bookshelf(d):  # back against gx=0 wall, faces +x, length along gy
  W=(170,115,70); Wd=(130,85,50); Wt=(200,145,95)
  box(d,0,0,0.45,1.4,0,100,Wt,W,Wd)
  cols=[(220,70,70),(70,140,220),(250,200,60),(90,180,90),(170,100,200),(240,140,60)]
  for k,z in enumerate((8,40,72)):
    d.polygon([P(0.45,0.08,z),P(0.45,1.32,z),P(0.45,1.32,z+26),P(0.45,0.08,z+26)],fill=(90,55,30),outline=OUT,width=2)
    g=0.12+0.07*k
    for i in range(6 if k!=1 else 4):
      h=18+((i*7+k*5)%8); c=cols[(i+k*2)%6]
      d.polygon([P(0.45,g,z),P(0.45,g+0.14,z),P(0.45,g+0.14,z+h),P(0.45,g,z+h)],fill=c,outline=OUT,width=1); g+=0.17
RULES=[  # (keywords, drawer)
 (("bookshelf","bookcase","shelf","本棚"), lambda d,n,t: bookshelf(d)),
 (("computer","desk","pc_","パソコン","デスク","机"), lambda d,n,t: computer_desk(d)),
 (("plant","植物","観葉","鉢"), lambda d,n,t: potted_plant(d)),
 (("piano","ピアノ"), lambda d,n,t: piano(d)),
 (("television","tv","テレビ"), lambda d,n,t: television(d)),
 (("futon","布団","ふとん"), lambda d,n,t: futon(d)),
 (("bear","teddy","熊","くま","クマ"), lambda d,n,t: plush(d,(170,110,60),"round",(235,195,145),muzzle=True,bow=(230,60,80))),
 (("rabbit","bunny","うさぎ","ウサギ","兎"), lambda d,n,t: plush(d,(250,250,250),"long",(255,205,215))),
 (("dog","puppy","犬","いぬ","イヌ"), lambda d,n,t: plush(d,(235,200,140),"flop",muzzle=True)),
 (("cat","kitty","猫","ねこ","ネコ"), lambda d,n,t: plush(d,(250,170,70),"cat",(255,205,130))),
 (("panda","パンダ"), lambda d,n,t: plush(d,(250,250,250),"round",(250,250,250),muzzle=True)),
]
def generate(typ,name="",path="sprites/sprites.json"):
  key=f"{typ} {name}".lower(); im=Image.new("RGBA",(S,S)); d=ImageDraw.Draw(im); how="generic"
  for kws,fn in RULES:
    if any(k in key for k in kws): fn(d,name,typ); how=kws[0]; break
  else: generic(d,name,typ)
  bb=im.getbbox(); f=f"sprites/{typ}.png"; im.crop(bb).save(f+".tmp","PNG"); os.replace(f+".tmp",f)
  SP=json.load(open(path)); SP[typ]={"file":f,"anchor":[A[0]-bb[0],A[1]-bb[1]],"anchor_is":"grid point P(gx,gy) of placement tile corner","note":f"auto-generated ({how})"}
  json.dump(SP,open(path+".tmp","w"),ensure_ascii=False,indent=1); os.replace(path+".tmp",path)
  return SP[typ],how
