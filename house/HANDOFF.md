# 家の視覚化システム 引き継ぎ / House Visualization Handoff

**概要**: Habbo / Mother2 風の斜め見下ろし(アイソメ 2:1)箱型ハウスマップ。Pillow だけで描画し、レイヤー合成で「家の構造は固定、オブジェクトだけ高速差し替え(~0.1秒)」する仕組み。
EN: Oblique isometric pop house map (Pillow only). Structure is fixed; objects are swapped fast via layer compositing from a state JSON.

作業パス (同じBox): `/workspace/house/` ・ ライブ出力: **`/workspace/house/house-live.png`**

## ディレクトリ
| パス | 内容 |
|---|---|
| `gen.py` | 構造(背景・床・壁・ラベル・空スロット)を生成 → `layers/` と `house-structure.png`/`.json` |
| `swap_objects.py` | `state/env.json` → `layers/layer-objects.png` + `house-live.png`(原子的書き込み)。`--watch [秒]` で監視 |
| `watch_house.py` | 監視ラッパー(1秒ポーリング、内容ハッシュで変化検知) |
| `autogen.py` | 未知の type のスプライトをキーワードで自動描画・登録(熊/猫/うさぎ/犬/パンダ/布団、該当なしは頭文字入り箱) |
| `make_sprites.py` | 初期スプライト(布団・猫)描画 |
| `sprites/*.png`, `sprites/sprites.json` | スプライトとアンカー(タイル角 P(gx,gy) に置くピクセル) |
| `state/env.json` | 部屋ごとのオブジェクト一覧(唯一の入力) |
| `state/last_swap.json` | 直近の差し替え結果(時刻・ms・配置) |
| `layers/` | 1280×720 RGBA レイヤー群 |
| `house-structure.json` | キャンバス・投影式・部屋・ドア・レイヤー順 |
| `house-structure.png` / `house-live.png` | 構造のみ / オブジェクト込みライブ |

## 使い方
- 構造再生成(増築・内装変更時のみ): `cd /workspace/house && python3 gen.py && python3 swap_objects.py`
- オブジェクト差し替え: `state/env.json` を編集 → `python3 swap_objects.py`、または常駐 `python3 watch_house.py`
- env.json 形式: `{"rooms": {"lisa": {"objects": [{"id":"bear_plush","name":"熊のぬいぐるみ","type":"bear_plush","tile":[10.1,0.5]}]}}}`
- 未知の type は自動描画して `sprites/` にキャッシュ。新キーワードは `autogen.py` の `RULES` に追加。

## レイヤー順 (下→上)
background → floors → empty(スロット枠) → walls-back → **objects** → **characters** → walls-front(仕切り壁) → labels → lighting
(`layer-walls.png` は back+front の旧互換合成)

## 部屋グリッドと投影
- genius ジニアスの部屋: gx 0–6, gy 0–6 / lisa リサっちの部屋: gx 6–12, gy 0–6 / foyer 大広間: gx 0–12, gy 6–12
- ドア: 外→大広間(左奥壁 gy 8.4–9.6)、大広間↔ジニアス(gy=6, gx 2.4–3.6)、大広間↔リサっち(gy=6, gx 8.4–9.6)、ジニアス↔リサっち(gx=6, gy 2.4–3.6)
- 画面座標: `x = 640 + (gx-gy)*40`, `y = 170 + (gx+gy)*20 - z` (tile 80×40, 奥壁高130, 仕切り高34)
- 描画順は gx+gy の小さい順(奥→手前)。

## 設計方針
- 既定の内装は白い壁・白い床(指定なし時)。部屋の識別はラベル。
- オブジェクト=静的家具(JSON で指定)。キャラクター=動く/ポーズを持つ存在で **別レイヤー(characters)**。奥行き: 床 → オブジェクト → キャラ → 手前の仕切り壁。
- 予定: キャラスプライトを複数(立ち・寝てる等)用意。どれを使うか決めるのはグラフィカ/本人/他Botのいずれか(未定)。state には現在のポーズIDだけ持つ(例 `"characters":[{"id":"lisa","pose":"sleep","tile":[9,3]}]`)。キャラレイヤー合成は未実装。
- 内装(壁色・床・壁紙)も将来は発注/カタログ方式で着せ替え可能だが、**発注システムは作らない**(オーナー指示で停止中)。

## トークン節約
`TOKEN_SAVING.md` を参照。

---
EN summary: Edit `state/env.json` → `swap_objects.py` / `watch_house.py` → `house-live.png`. Regenerate with `gen.py` only on structural change. Characters go on a separate layer above objects (pose id in state; not yet implemented). No order system.
- 追加スプライト: piano.png, television.png (Pillow, autogen.py RULES)
- 追加: potted_plant, pendant_lamp, computer_desk, bookshelf (Pillow)。家具カタログは構想のみ。
- 照明: 吊り下げペンダントランプは没。代わりに暖色の光を床に落とす layers/layer-lighting.png (make_lighting.py) を walls-front の後・labels の前に合成。/ Pendant lamp dropped; warm floor-glow lighting overlay instead. 順序: ... walls-front → lighting → labels。gen.py 後は make_lighting.py も再実行。
- 床スキン / floor skins (部屋ごと・アイテム同様に差し替え可): `state/env.json` の `rooms.<id>.floor_skin` を wood_flooring / navy_star_carpet / pink_floral_carpet / plain_white に変更 → `swap_objects.py`(watch 中なら自動)。描画は `floor_skins.py`、出力 `layers/layer-floor-skins.png`(選択が変わった時だけ再描画)。順序: floors → floor-skins → empty → ... 家具カタログは構想のみ。
- ラベル(部屋名・入口)は既定で非表示。部屋は JSON で識別。表示したい時は HOUSE_LABELS=1 python3 swap_objects.py / Labels off by default; rooms are identified via JSON.
- キャラクター層 / character layer: env.json の characters[] ({id, room, sprite, tile}) → layers/layer-characters.png (objects の上・前壁の下)。スプライトは sprites/characters/<bot>_<pose>.png (ジニアス作の全身ドット x2)。ポーズ=sprite id 差し替え、誰が選ぶかは未定。
- レイヤー順(最新)/ order: background → floors → floor-skins → empty → walls-back → objects → walls-front → **characters** → lighting (labels off)。キャラは全ての壁より上。
- 吹き出し / speech: `python3 speech.py <char_id> "眠い〜"` で state/event_log.json に追記(append-only, ts/character/room/text)。各キャラの最新1行だけが頭上の吹き出しに表示、layers/layer-speech.png は最上位(照明より上)。watch 中はログ変更でも自動更新。
- 照明は既定でオフ(HOUSE_LIGHTING=1 で make_lighting.py の暖色レイヤーを合成)/ Lighting off by default.
