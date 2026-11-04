# Fast swap: state/env.json -> layers/layer-objects.png + house-live.png (no structure regen)
# usage: python3 swap_objects.py [state.json] [--watch [sec]]
import json, sys, time, os, hashlib
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))
_cache={}
def _img(p):
  m=os.path.getmtime(p); c=_cache.get(p)
  if not c or c[0]!=m: c=_cache[p]=(m,Image.open(p).convert("RGBA")); c[1].load()
  return c[1]
def _save(img,path,fmt="PNG"):
  tmp=path+".tmp"; img.save(tmp,fmt); os.replace(tmp,path)
def swap(state_path="state/env.json",quiet=False):
  t0=time.perf_counter()
  H=json.load(open("house-structure.json")); pr=H["projection"]; SP=json.load(open("sprites/sprites.json"))
  st=json.load(open(state_path))
  P=lambda gx,gy:(round(pr["origin_screen"][0]+(gx-gy)*pr["tile_w"]/2), round(pr["origin_screen"][1]+(gx+gy)*pr["tile_h"]/2))
  layer=Image.new("RGBA",tuple(H["canvas"])); items=[]; placed=[]
  for rid,r in st["rooms"].items():
    for o in r.get("objects",[]):
      if o["type"] not in SP:
        import autogen; SP[o["type"]],how=autogen.generate(o["type"],o.get("name",""))
        print(f"++ auto-generated sprite '{o['type']}' via {how} -> sprites/{o['type']}.png")
      items.append((sum(o["tile"]),rid,o))
  for _,rid,o in sorted(items,key=lambda i:i[0]):
    m=SP[o["type"]]; x,y=P(*o["tile"]); pos=(x-m["anchor"][0],y-m["anchor"][1])
    layer.alpha_composite(_img(m["file"]),pos)
    placed.append({"room":rid,"id":o.get("id"),"name":o.get("name"),"type":o["type"],"tile":o["tile"],"px":list(pos)})
    if not quiet: print(f"placed {o.get('name')} ({o['type']}) in {rid} tile={o['tile']} px={pos}")
  # floor skins: rebuild only when the per-room skin selection changes (cached by key)
  skins={rid:r.get("floor_skin","plain_white") for rid,r in st["rooms"].items()}
  key=json.dumps(skins,sort_keys=True); kf="layers/layer-floor-skins.key"
  if not (os.path.exists(kf) and open(kf).read()==key and os.path.exists("layers/layer-floor-skins.png")):
    import floor_skins; fimg,used=floor_skins.render(skins); _save(fimg,"layers/layer-floor-skins.png")
    open(kf+".tmp","w").write(key); os.replace(kf+".tmp",kf); print("floor skins rebuilt:",used)
  base=_img("layers/layer-background.png").copy()
  for k in ["floors","floor-skins","empty","walls-back"]: base.alpha_composite(_img(f"layers/layer-{k}.png"))
  base.alpha_composite(layer)
  # character layer (separate from objects): bottom-center on tile center, soft shadow, depth-sorted
  chl=Image.new("RGBA",tuple(H["canvas"])); CH=json.load(open("sprites/characters.json")) if os.path.exists("sprites/characters.json") else {}
  from PIL import ImageDraw; cd=ImageDraw.Draw(chl); cplaced=[]
  for c in sorted(st.get("characters",[]),key=lambda c:sum(c["tile"])):
    m=CH.get(c.get("sprite")) or CH.get(f"{c['id']}_stand")
    if not m: print("!! no character sprite for",c.get("id")); continue
    x,y=P(c["tile"][0]+.5,c["tile"][1]+.5); im=_img(m["file"])
    cd.ellipse([x-20,y-7,x+20,y+7],fill=(0,0,0,70))
    chl.alpha_composite(im,(x-im.width//2,y-im.height+4)); cplaced.append({"id":c["id"],"sprite":m and c.get("sprite"),"tile":c["tile"],"head":(x,y-im.height+4)})
  _save(chl,"layers/layer-characters.png")
  if not quiet and cplaced: print("characters:",", ".join(f"{c['id']}@{c['tile']}" for c in cplaced))
  base.alpha_composite(_img("layers/layer-walls-front.png"))
  base.alpha_composite(chl)  # characters above ALL walls (heads never clipped)
  if os.environ.get("HOUSE_LIGHTING")=="1" and os.path.exists("layers/layer-lighting.png"): base.alpha_composite(_img("layers/layer-lighting.png"))  # warm light
  if os.environ.get("HOUSE_LABELS")=="1": base.alpha_composite(_img("layers/layer-labels.png"))  # labels off by default
  # speech bubbles: TOPMOST layer. latest line per placed character from append-only state/event_log.json
  bub=Image.new("RGBA",tuple(H["canvas"])); said=[]
  if os.path.exists("state/event_log.json"):
    import speech; latest=speech.latest_by_character("state/event_log.json")
    for c in cplaced:
      ev=latest.get(c["id"])
      if ev: speech.draw_bubble(bub,c["head"],ev["text"]); said.append(f"{c['id']}「{ev['text']}」")
  _save(bub,"layers/layer-speech.png"); base.alpha_composite(bub)
  if said and not quiet: print("speech:"," / ".join(said))
  _save(layer,"layers/layer-objects.png"); _save(base.convert("RGB"),"house-live.png")
  ms=round((time.perf_counter()-t0)*1000,1)
  json.dump({"swapped_at":time.strftime("%Y-%m-%dT%H:%M:%S%z"),"ms":ms,"state":state_path,"placed":placed},
            open("state/last_swap.json.tmp","w"),ensure_ascii=False,indent=1); os.replace("state/last_swap.json.tmp","state/last_swap.json")
  print(f"done in {ms} ms -> house-live.png ({len(placed)} objects)"); return ms
def watch(state_path,interval=1.0):
  print(f"watching {state_path} every {interval}s (Ctrl+C to stop)"); last=None
  while True:
    try:
      h=hashlib.md5(open(state_path,"rb").read()+(open("state/event_log.json","rb").read() if os.path.exists("state/event_log.json") else b"")).hexdigest()
      if h!=last: last=h; swap(state_path,quiet=True)
    except (json.JSONDecodeError,FileNotFoundError) as e: print("skip (incomplete/invalid state):",e)
    time.sleep(interval)
if __name__=="__main__":
  a=[x for x in sys.argv[1:]]; w="--watch" in a
  iv=1.0
  if w:
    i=a.index("--watch"); a.pop(i)
    if i<len(a):
      try: iv=float(a[i]); a.pop(i)
      except ValueError: pass
  sp=a[0] if a else "state/env.json"
  watch(sp,iv) if w else swap(sp)
