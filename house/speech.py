# Speech bubbles + room event log. Append: python3 speech.py <char_id> "<text>"  (room auto from env.json)
import json, os, sys, time, glob
from PIL import ImageDraw, ImageFont
LOG="state/event_log.json"
FP=next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'] if os.path.exists(p)),None) or glob.glob('/usr/share/fonts/**/Noto*CJK-Bold.ttc',recursive=True)[0]
FONT=ImageFont.truetype(FP,14)
def load(path=LOG): return json.load(open(path)) if os.path.exists(path) else {"events":[]}
def append(char_id,text,room=None,path=LOG):
  if room is None:
    env=json.load(open("state/env.json")); room=next((c.get("room") for c in env.get("characters",[]) if c["id"]==char_id),None)
  log=load(path); ev={"ts":time.strftime("%Y-%m-%dT%H:%M:%S%z"),"character":char_id,"room":room,"type":"say","text":text}
  log["events"].append(ev); json.dump(log,open(path+".tmp","w"),ensure_ascii=False,indent=1); os.replace(path+".tmp",path); return ev
def latest_by_character(path=LOG):
  out={}
  for ev in load(path)["events"]:
    if ev.get("type","say")=="say": out[ev["character"]]=ev   # later entries win
  return out
def draw_bubble(img,head,text):
  d=ImageDraw.Draw(img); x,y=head; bb=d.textbbox((0,0),text,font=FONT); tw,th=bb[2]-bb[0],bb[3]-bb[1]
  w,h=tw+16,th+12; bx=min(max(x-w//2,4),img.width-w-4); by=max(y-h-14,4)
  d.rounded_rectangle([bx,by,bx+w,by+h],8,fill=(255,255,255,250),outline=(20,15,20,255),width=2)
  d.polygon([(x-6,by+h-1),(x+6,by+h-1),(x,by+h+9)],fill=(255,255,255,250))
  d.line([(x-6,by+h),(x,by+h+9),(x+6,by+h)],fill=(20,15,20,255),width=2)
  d.text((bx+8,by+6-bb[1]),text,font=FONT,fill=(20,15,20,255))
if __name__=="__main__":
  os.chdir(os.path.dirname(os.path.abspath(__file__))); print(append(sys.argv[1]," ".join(sys.argv[2:])))
