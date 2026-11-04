# Draws iso pixel sprites. Each sprite: PNG + anchor (pixel in sprite that sits on the tile point P(gx,gy)).
from PIL import Image, ImageDraw
import json
TW,TH=80,40; OUT=(20,15,20,255); S=300; A=(150,200)  # canvas, anchor
def P(gx,gy,z=0): return (round(A[0]+(gx-gy)*TW/2), round(A[1]+(gx+gy)*TH/2-z))
def box(d,x0,y0,x1,y1,z0,z1,top,fx,fy):
  d.polygon([P(x1,y0,z0),P(x1,y1,z0),P(x1,y1,z1),P(x1,y0,z1)],fill=fx,outline=OUT,width=3)
  d.polygon([P(x0,y1,z0),P(x1,y1,z0),P(x1,y1,z1),P(x0,y1,z1)],fill=fy,outline=OUT,width=3)
  d.polygon([P(x0,y0,z1),P(x1,y0,z1),P(x1,y1,z1),P(x0,y1,z1)],fill=top,outline=OUT,width=3)
meta={}
def save(name,img,note):
  bb=img.getbbox(); img.crop(bb).save(f"sprites/{name}.png")
  meta[name]={"file":f"sprites/{name}.png","anchor":[A[0]-bb[0],A[1]-bb[1]],"anchor_is":"grid point P(gx,gy) of placement tile corner","note":note}
# futon: footprint 1.3 x 2.2 tiles from anchor
im=Image.new("RGBA",(S,S)); d=ImageDraw.Draw(im)
box(d,0,0,1.3,2.2,0,8,(245,245,240),(200,200,195),(215,215,210))          # shikibuton
box(d,0.1,0.75,1.2,2.15,8,20,(80,120,200),(50,85,160),(60,95,175))        # kakebuton (indigo)
for t in (1.1,1.45,1.8):                                                  # stripes
  d.line([P(0.1,t,20),P(1.2,t,20)],fill=(240,200,80),width=3)
box(d,0.3,0.15,1.0,0.6,8,18,(255,250,230),(220,210,180),(235,225,195))    # pillow
save("futon_japanese",im,"footprint 1.3x2.2 tiles")
# cat plush: footprint ~0.6 tile, anchor at tile corner, sprite centered on tile center
im=Image.new("RGBA",(S,S)); d=ImageDraw.Draw(im)
cx,cy=P(0.5,0.5); O=(250,170,70); Ol=(255,205,130)
d.ellipse([cx-24,cy-8,cx+24,cy+8],fill=(0,0,0,70))                                   # shadow
d.ellipse([cx+10,cy-30,cx+34,cy-14],fill=O,outline=OUT,width=3)                      # tail
d.ellipse([cx-22,cy-40,cx+22,cy+2],fill=O,outline=OUT,width=3)                       # body
d.ellipse([cx-12,cy-26,cx+12,cy-2],fill=Ol,outline=OUT,width=2)                      # belly
for s in (-1,1):
  d.polygon([(cx+s*24,cy-80),(cx+s*8,cy-70),(cx+s*22,cy-60)],fill=O,outline=OUT,width=3)  # ears
d.ellipse([cx-26,cy-78,cx+26,cy-36],fill=O,outline=OUT,width=3)                      # head
for s in (-1,1):
  d.polygon([(cx+s*20,cy-74),(cx+s*12,cy-68),(cx+s*19,cy-64)],fill=(255,150,170))
  d.ellipse([cx+s*11-3,cy-62,cx+s*11+3,cy-54],fill=OUT)                              # eyes
  d.ellipse([cx+s*17-4,cy-52,cx+s*17+4,cy-47],fill=(255,140,160))                    # cheeks
  d.line([(cx+s*14,cy-48),(cx+s*30,cy-50)],fill=OUT,width=1)                         # whiskers
d.polygon([(cx-3,cy-53),(cx+3,cy-53),(cx,cy-50)],fill=(230,80,100))
d.line([(cx-4,cy-46),(cx,cy-48),(cx+4,cy-46)],fill=OUT,width=2)
for s in (-1,1): d.ellipse([cx+s*12-7,cy-8,cx+s*12+7,cy+2],fill=Ol,outline=OUT,width=2)  # paws
save("cat_plush",im,"1x1 tile, sits at tile center")
json.dump(meta,open("sprites/sprites.json","w"),indent=1)
print("sprites:",list(meta))
