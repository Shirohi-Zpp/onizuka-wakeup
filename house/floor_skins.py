# Per-room floor skins (Pillow). render(skins) -> RGBA full-canvas layer drawn over each room's floor diamond.
from PIL import Image, ImageDraw
import json, math, random
H=json.load(open("house-structure.json")); W,Hh=H["canvas"]; pr=H["projection"]; OUT=(20,15,20,255)
def P(gx,gy): return (pr["origin_screen"][0]+(gx-gy)*pr["tile_w"]/2, pr["origin_screen"][1]+(gx+gy)*pr["tile_h"]/2)
def quad(d,x0,y0,x1,y1,fill,outline=None,w=1): d.polygon([P(x0,y0),P(x1,y0),P(x1,y1),P(x0,y1)],fill=fill,outline=outline,width=w)
def wood(d,g,rng):
  x0,y0,x1,y1=g; cols=[(196,140,88),(182,126,76),(208,154,100),(188,132,82)]; edge=(120,78,44)
  y=y0; i=0
  while y<y1-1e-6:
    off=(i*0.7)%2.0; x=x0-off
    while x<x1:
      a=max(x,x0); b=min(x+2.0,x1); quad(d,a,y,b,y+0.5,cols[rng.randrange(4)],edge,2)
      gx=a+0.3+rng.random()*(b-a-0.6) if b-a>0.8 else None
      if gx: d.line([P(gx,y+0.15),P(gx+0.35,y+0.15)],fill=(160,108,62),width=1)  # grain
      x+=2.0
    y+=0.5; i+=1
def star(d,c,r,col):
  pts=[]
  for k in range(10):
    a=-math.pi/2+k*math.pi/5; rr=r if k%2==0 else r*0.45
    pts.append((c[0]+rr*math.cos(a), c[1]+rr*math.sin(a)*0.6))
  d.polygon(pts,fill=col,outline=OUT)
def navy_stars(d,g,rng):
  x0,y0,x1,y1=g; quad(d,x0,y0,x1,y1,(32,44,96))
  for gx in range(int(x0),int(x1)):
    for gy in range(int(y0),int(y1)): quad(d,gx,gy,gx+1,gy+1,None,(42,56,112),1)
  n=int((x1-x0)*(y1-y0)*1.6)
  for _ in range(n):
    c=P(x0+0.2+rng.random()*(x1-x0-0.4), y0+0.2+rng.random()*(y1-y0-0.4))
    if rng.random()<0.55: star(d,c,rng.choice([6,8,10]),rng.choice([(255,220,80),(255,240,160),(255,200,60)]))
    else: d.ellipse([c[0]-1.5,c[1]-1.5,c[0]+1.5,c[1]+1.5],fill=(220,230,255))
def flower(d,c,r,petal):
  for k in range(5):
    a=k*2*math.pi/5; px,py=c[0]+r*math.cos(a), c[1]+r*math.sin(a)*0.55
    d.ellipse([px-r*0.7,py-r*0.45,px+r*0.7,py+r*0.45],fill=petal,outline=(150,60,90))
  d.ellipse([c[0]-r*0.45,c[1]-r*0.3,c[0]+r*0.45,c[1]+r*0.3],fill=(255,215,80),outline=(150,60,90))
def pink_floral(d,g,rng):
  x0,y0,x1,y1=g; quad(d,x0,y0,x1,y1,(250,190,205))
  for gx in range(int(x0),int(x1)):
    for gy in range(int(y0),int(y1)):
      quad(d,gx,gy,gx+1,gy+1,None,(240,175,192),1)
      for k in range(2):
        c=P(gx+0.25+0.5*rng.random(), gy+0.25+0.5*rng.random())
        if k==1:
          d.ellipse([c[0]-5,c[1]-2,c[0]+5,c[1]+2],fill=(120,190,110),outline=(70,130,70)); continue
        flower(d,c,rng.choice([6,7,8]),rng.choice([(255,255,255),(255,120,150),(250,90,120)]))
def plain_white(d,g,rng):
  x0,y0,x1,y1=g
  for gx in range(int(x0),int(x1)):
    for gy in range(int(y0),int(y1)): quad(d,gx,gy,gx+1,gy+1,(250,250,248) if (gx+gy)%2 else (242,242,240),(217,217,215))
SKINS={"wood_flooring":wood,"navy_star_carpet":navy_stars,"pink_floral_carpet":pink_floral,"plain_white":plain_white}
ALIASES={"wood":"wood_flooring","木":"wood_flooring","フローリング":"wood_flooring","star":"navy_star_carpet","星":"navy_star_carpet","flower":"pink_floral_carpet","floral":"pink_floral_carpet","花":"pink_floral_carpet","white":"plain_white","白":"plain_white"}
def resolve(name):
  if name in SKINS: return name
  for k,v in ALIASES.items():
    if k in (name or ""): return v
  return "plain_white"
def render(skins):
  img=Image.new("RGBA",(W,Hh)); d=ImageDraw.Draw(img); used={}
  for r in H["rooms"]:
    gx,gy,w,h=r["grid"]; sk=resolve(skins.get(r["id"],"plain_white")); used[r["id"]]=sk
    SKINS[sk](d,(gx,gy,gx+w,gy+h),random.Random(r["id"]+sk))
    m=Image.new("L",(W,Hh),0); ImageDraw.Draw(m).polygon([P(gx,gy),P(gx+w,gy),P(gx+w,gy+h),P(gx,gy+h)],fill=255)
  # clip to all room diamonds, then outlines
  mask=Image.new("L",(W,Hh),0); md=ImageDraw.Draw(mask)
  for r in H["rooms"]:
    gx,gy,w,h=r["grid"]; md.polygon([P(gx,gy),P(gx+w,gy),P(gx+w,gy+h),P(gx,gy+h)],fill=255)
  img.putalpha(Image.fromarray if False else mask) if False else None
  a=img.getchannel("A"); from PIL import ImageChops; img.putalpha(ImageChops.multiply(a,mask))
  d=ImageDraw.Draw(img)
  for r in H["rooms"]:
    gx,gy,w,h=r["grid"]; d.polygon([P(gx,gy),P(gx+w,gy),P(gx+w,gy+h),P(gx,gy+h)],outline=OUT,width=3)
  return img,used
