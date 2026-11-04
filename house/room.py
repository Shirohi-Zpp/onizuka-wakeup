#!/usr/bin/env python3
"""部屋ごとの環境ファイル rooms/<部屋>/room.json を操作する道具。
決まり: 入室(enter)で名簿に自分を書き、退室(leave)で消す。家具や床の変更は名簿にいる子だけ。
使い方:
  room.py show  <部屋>
  room.py enter <部屋> <キャラid> [gx gy]
  room.py leave <部屋> <キャラid>
  room.py place  <部屋> <キャラid> <家具id> <type> <名前> <gx> <gy>
  room.py move   <部屋> <キャラid> <家具id> <gx> <gy>
  room.py remove <部屋> <キャラid> <家具id>
  room.py floor  <部屋> <キャラid> <床スキン>
  room.py go <行き先の部屋> <キャラid> [gx gy]   (いまの部屋を出て行き先に入る。どこにもいなければ入るだけ)
  room.py where <キャラid>
  room.py build   (全部屋をまとめて state/env.json を作る。描画前に使う)
"""
import json,sys,os,fcntl,datetime
B=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(B,'rooms')
NAMES={'genius':'ジニアス','onizuka':'鬼塚','nicky':'ニッキー','graphica':'グラフィカ','lisa':'リサっち','shokky':'ショッキー','sacred':'セイクリッド'}
def now(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds')
def die(m): print('NG:',m); sys.exit(1)
def path(room):
    p=os.path.join(R,room,'room.json')
    if not os.path.exists(p): die(f'部屋 {room} はないよ（ある部屋: {", ".join(sorted(os.listdir(R)))}）')
    return p
def save(p,d):
    d['updated_at']=now(); t=p+'.tmp'; json.dump(d,open(t,'w'),ensure_ascii=False,indent=1); os.replace(t,p)
def build():
    env={'updated_at':now(),'rooms':{},'characters':[]}
    for room in sorted(os.listdir(R)):
        p=os.path.join(R,room,'room.json')
        if not os.path.exists(p): continue
        d=json.load(open(p))
        env['rooms'][room]={'objects':d.get('objects',[]),'floor_skin':d.get('floor_skin','plain_white')}
        for c in d.get('occupants',[]): env['characters'].append({**c,'room':room})
    os.makedirs(os.path.join(B,'state'),exist_ok=True)
    t=os.path.join(B,'state','env.json.tmp'); json.dump(env,open(t,'w'),ensure_ascii=False,indent=1); os.replace(t,os.path.join(B,'state','env.json'))
def main(a):
    if not a: print(__doc__); return
    cmd=a[0]
    if cmd=='build': build(); print('OK: env.json を作り直したよ'); return
    if cmd=='where':
        print(next((r for r in sorted(os.listdir(R)) if os.path.exists(os.path.join(R,r,'room.json')) and any(c['id']==a[1] for c in json.load(open(os.path.join(R,r,'room.json'))).get('occupants',[]))),'どこにもいない')); return
    if cmd=='go':
        dest,cid=a[1],a[2]; path(dest)
        hl=open(os.path.join(R,'.house.lock'),'w'); fcntl.flock(hl,fcntl.LOCK_EX)
        cur=next((r for r in sorted(os.listdir(R)) if os.path.exists(os.path.join(R,r,'room.json')) and any(c['id']==cid for c in json.load(open(os.path.join(R,r,'room.json'))).get('occupants',[]))),None)
        if cur==dest: die(f'もう {dest} にいるよ')
        if cur: main(['leave',cur,cid])
        main(['enter',dest,cid]+a[3:5]); return
    if len(a)<2: die('部屋名がないよ')
    p=path(a[1]); lk=open(p+'.lock','w'); fcntl.flock(lk,fcntl.LOCK_EX)
    d=json.load(open(p)); occ=d.setdefault('occupants',[]); objs=d.setdefault('objects',[])
    if cmd=='show': print(json.dumps(d,ensure_ascii=False,indent=1)); return
    if len(a)<3: die('キャラidがないよ')
    cid=a[2]; inside=any(c['id']==cid for c in occ)
    if cmd=='enter':
        for other in os.listdir(R):
            q=os.path.join(R,other,'room.json')
            if other!=a[1] and os.path.exists(q) and any(c['id']==cid for c in json.load(open(q)).get('occupants',[])):
                die(f'{cid} はまだ {other} にいるよ。先にそっちを leave してね')
        if inside: die('もう入ってるよ')
        tile=[float(a[3]),float(a[4])] if len(a)>=5 else [2.0,2.0]
        occ.append({'id':cid,'name':NAMES.get(cid,cid),'sprite':f'{cid}_stand','tile':tile})
    elif not inside: die(f'{cid} は {a[1]} の名簿にいないから、さわれないよ。先に enter してね')
    elif cmd=='leave': d['occupants']=[c for c in occ if c['id']!=cid]
    elif cmd=='place':
        oid,typ,name,gx,gy=a[3],a[4],a[5],float(a[6]),float(a[7])
        if any(o['id']==oid for o in objs): die(f'{oid} はもうあるよ')
        objs.append({'id':oid,'name':name,'type':typ,'tile':[gx,gy],'by':cid})
    elif cmd=='move':
        o=next((o for o in objs if o['id']==a[3]),None) or die(f'{a[3]} はこの部屋にないよ'); o['tile']=[float(a[4]),float(a[5])]
    elif cmd=='remove':
        if not any(o['id']==a[3] for o in objs): die(f'{a[3]} はこの部屋にないよ')
        d['objects']=[o for o in objs if o['id']!=a[3]]
    elif cmd=='floor': d['floor_skin']=a[3]
    else: die(f'{cmd} は知らない命令だよ')
    save(p,d); print(f'OK: {cmd} {a[1]} by {cid}')
if __name__=='__main__': main(sys.argv[1:])
