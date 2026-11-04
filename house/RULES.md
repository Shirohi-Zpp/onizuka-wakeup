# おうちのルール（短縮版）
道具: `python3 /workspace/house/room.py <命令> ...`（キャラid: genius onizuka nicky graphica lisa shokky sacred）
部屋: genius（ジニアス）/ foyer（大広間）/ lisa（リサっち）

## 1回起きたら、行動は2つまで
行動1つ = 次のどれか1回
- **移動**: `go <行き先> <自分のid>`（元の部屋を出て行き先に入るのが1セット）
- **環境の編集（1項目）**: `place` 置く / `move` 動かす / `remove` 片づける / `floor` 床を変える
- 例: 「玄関へ移動 → ぬいぐるみを置く」でおしまい

## 置ける家具（これ以外は道具が断る）
futon_japanese 布団 / cat_plush ねこ / bear_plush くま / piano ピアノ / television テレビ / potted_plant 観葉植物 / bookshelf 本棚 / computer_desk パソコン机
- 置き方: `place <部屋> <自分のid> <好きな名札> <上の種類> <名前> <x> <y>`
- マス目は部屋ごとに 0〜5（大広間 foyer だけ x は 0〜11）

## 行動に数えないもの
- `where <id>` 自分の居場所を見る、`show <部屋>` いる部屋の様子を見る

## 決まり
- 家具や床をさわれるのは、その部屋の名簿にいるときだけ（道具が自動で断る）
- 読むのは自分のいる部屋だけでOK。じっくり考えなくていい、気分で決めて
- 断られたら、やり直さずにおしまい
