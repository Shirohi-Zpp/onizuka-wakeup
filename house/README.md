# Home – 家の構造マップ / House structure map (oblique box-room view)

視点: 斜め見下ろし(アイソメ2:1)の箱型ルーム、Habbo / Mother2風。View: oblique isometric box rooms, Habbo-style.
- `house-structure.png` 1280x720. 生成 / generate: `python3 gen.py`
- 合成順 / composite order (alpha, same canvas): background → floors → empty_slots → (objects → characters) → walls → labels → (lighting)
- グリッド→画面座標の式は `house-structure.json` の `projection` に記載 (place objects by tile gx,gy).
- 内装・オブジェクトは後で追加 / Interiors & objects come later.
- 10分更新: 状態JSONを読み objects / characters / lighting レイヤーだけ差し替え。増築時のみ gen.py でベース再生成。
  10-min updates: read state JSON, swap object/character/lighting layers only; regenerate base only on structural change.

## 高速差し替え / Fast object swap
1. `state/env.json` を編集 (rooms.<id>.objects に {type, tile:[gx,gy]} を追加/削除) / edit the state JSON.
2. `python3 swap_objects.py [state.json]` → `layers/layer-objects.png` と `house-live.png` を再生成 (~0.1秒, 構造再生成なし / no structure regen).
- 合成順 / order: background → floors → empty → walls-back → **objects** → characters → walls-front → labels → lighting
  (奥の壁は物の後ろ、仕切り壁は手前 / back walls behind objects, partitions in front).
- スプライト / sprites: `sprites/*.png` + `sprites/sprites.json` (anchor = tile corner P(gx,gy)). 新しい種類は `make_sprites.py` に追加。

## 自動更新 / Auto-update (no chat round-trip)
- 常駐監視 / watcher: `python3 watch_house.py` または `python3 swap_objects.py --watch 1` — `state/env.json` の内容ハッシュを1秒ごとに確認し、変化時だけ objects レイヤーを再合成 (~50–110 ms)。壁・床は再生成しない。
- 出力は一時ファイル→rename で原子的に置換 / atomic writes: `house-live.png`, `layers/layer-objects.png`, `state/last_swap.json` (時刻・ms・配置一覧)。
- 最速の確認 / fastest feedback: `/workspace/house/house-live.png` をそのまま開く(唯一のライブ出力)。
- Pages は閲覧・共有用で、差し替えエンジンではありません。Pages/チャットへの反映は別ステップ(Botの往復)なので遅くなります。
  Pages is for viewing/sharing, not the swap engine; pushing to Pages/chat is a separate, slower bot round-trip.

## スプライト自動生成 / Auto-generated sprites
- env.json に未知の type があっても止まりません。`autogen.py` が type+name のキーワード(例: bear/teddy/熊/くま, cat/猫, rabbit/うさぎ, dog/犬, panda, futon/布団)で Pillow 描画し、`sprites/<type>.png` と `sprites.json` に登録(キャッシュ)して配置します。
- 該当なしは名前の頭文字入りのカラー箱(汎用プロップ)を生成。キーワードは `autogen.py` の RULES に追加。
- Unknown types are auto-drawn once (keyword → drawer, else a generic labeled crate), cached, then placed. First time +~20 ms; afterwards normal speed.

## 既定の内装 / Default interior
- 指定がなければ壁も床も白(素の部屋)。部屋ごとの識別はラベルで。/ Unspecified rooms are plain white walls + white floors; labels identify rooms.
- 内装(壁色・床材・壁紙)も、将来はオブジェクトと同じく発注/カタログ方式で差し替え可能(未実装)。構造は再生成不要で floors/walls レイヤーの着せ替えになる想定。
  Interiors (wall color, floor style, wallpaper) can later be ordered/fulfilled like objects — not implemented yet; planned as floor/wall layer re-skins without structural changes.
- ピアノ・テレビも Pillow 描画スプライト (`autogen.py` の piano/ピアノ, tv/television/テレビ ルール) / Piano & TV are Pillow-drawn sprites, auto-used for those keywords.
- 追加スプライト / more Pillow sprites: potted_plant(観葉植物), pendant_lamp(ペンダントランプ・天井から吊り下げ+床の光), computer_desk(パソコンデスク), bookshelf(本棚)。家具カタログ(皆が注文して配置)は構想のみ・未実装 / shared furniture catalog = future concept only.
- 照明: 吊り下げペンダントランプは没。代わりに暖色の光を床に落とす layers/layer-lighting.png (make_lighting.py) を walls-front の後・labels の前に合成。/ Pendant lamp dropped; warm floor-glow lighting overlay instead. 順序: ... walls-front → lighting → labels。gen.py 後は make_lighting.py も再実行。
- 床スキン / floor skins (部屋ごと・アイテム同様に差し替え可): `state/env.json` の `rooms.<id>.floor_skin` を wood_flooring / navy_star_carpet / pink_floral_carpet / plain_white に変更 → `swap_objects.py`(watch 中なら自動)。描画は `floor_skins.py`、出力 `layers/layer-floor-skins.png`(選択が変わった時だけ再描画)。順序: floors → floor-skins → empty → ... 家具カタログは構想のみ。
- ラベル(部屋名・入口)は既定で非表示。部屋は JSON で識別。表示したい時は HOUSE_LABELS=1 python3 swap_objects.py / Labels off by default; rooms are identified via JSON.
- キャラクター層 / character layer: env.json の characters[] ({id, room, sprite, tile}) → layers/layer-characters.png (objects の上・前壁の下)。スプライトは sprites/characters/<bot>_<pose>.png (ジニアス作の全身ドット x2)。ポーズ=sprite id 差し替え、誰が選ぶかは未定。
- レイヤー順(最新)/ order: background → floors → floor-skins → empty → walls-back → objects → walls-front → **characters** → lighting (labels off)。キャラは全ての壁より上。
- 吹き出し / speech: `python3 speech.py <char_id> "眠い〜"` で state/event_log.json に追記(append-only, ts/character/room/text)。各キャラの最新1行だけが頭上の吹き出しに表示、layers/layer-speech.png は最上位(照明より上)。watch 中はログ変更でも自動更新。
- 照明は既定でオフ(HOUSE_LIGHTING=1 で make_lighting.py の暖色レイヤーを合成)/ Lighting off by default.
