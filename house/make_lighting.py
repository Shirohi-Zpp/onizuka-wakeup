# Warm ambient light overlay: soft amber pools on each room floor + faint warm wash, clipped to the house.
# Output layers/layer-lighting.png (composited after walls-front, before labels). Rerun after gen.py.
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import json, os
H=json.load(open("house-structure.json")); W,Hh=H["canvas"]; pr=H["projection"]
P=lambda gx,gy:(pr["origin_screen"][0]+(gx-gy)*pr["tile_w"]/2, pr["origin_screen"][1]+(gx+gy)*pr["tile_h"]/2)
a=Image.new("L",(W,Hh),0); d=ImageDraw.Draw(a)
for r in H["rooms"]:
  gx,gy,w,h=r["grid"]; cx,cy=P(gx+w/2,gy+h/2)
  rx=(w+h)*pr["tile_w"]/4*0.85; ry=rx/2
  for i in range(12):                       # stacked ellipses = radial falloff
    f=1-i/12; d.ellipse([cx-rx*f,cy-ry*f,cx+rx*f,cy+ry*f],fill=int(18+i*5))
a=a.filter(ImageFilter.GaussianBlur(28))
a=ImageChops.add(a,Image.new("L",(W,Hh),14))  # faint overall wash
mask=Image.new("L",(W,Hh),0)
for k in ("floors","walls-back","walls-front"): mask=ImageChops.lighter(mask,Image.open(f"layers/layer-{k}.png").getchannel("A"))
a=ImageChops.multiply(a,mask)
L=Image.new("RGBA",(W,Hh),(255,170,70,0)); L.putalpha(a)
L.save("layers/layer-lighting.png.tmp","PNG"); os.replace("layers/layer-lighting.png.tmp","layers/layer-lighting.png")
print("lighting layer written, max alpha",a.getextrema()[1])
