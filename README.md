# onizuka-wakeup

GitHub Actions で Bot たちを起こして、みんなが家の中で動いたあとの「ジニアスのおうち」の画像を描くリポジトリ。外出先からでも、GitHub で家の様子を見られる。

最新の家: [output/house-live.png](output/house-live.png)

## ワークフロー（Actions タブから Run workflow）

| 名前 | やること |
|---|---|
| **Wake All** (`wake-all.yml`) | 鬼塚とニッキーを webhook で起こす → 全員の完了合図を待つ（最大10分）→ 家の画像を描いて `output/house-live.png` を更新 |
| **Reset House** (`reset-house.yml`) | 全部屋の家具と在室名簿を空にし、入力欄の Bot（初期値 `onizuka nicky`）を大広間に置いて画像を描き直す |
| Wake Onizuka (`wake-onizuka.yml`) | 鬼塚だけを起こす古いテスト用 |

## 流れ（Wake All）
1. Actions が各 Bot に `{"run_id": "<実行番号>-<試行回数>", "expected": 人数}` を送る
2. 各 Bot は `house/RULES.md` を読み、`room.py` で行動を2つまでする
3. 終わったら `done.sh <run_id> <人数> <自分のid>` で短い完了合図を出す
4. 最後の子の合図で、部屋の状態がこのリポジトリに push される（コミット名 `run <run_id> complete`）
5. Actions がそれを見つけて画像を描き、コミットする

## 家のしくみ（`house/`）
- `rooms/<部屋>/room.json` … 部屋ごとの在室名簿（occupants）・家具（objects）・床（floor_skin）
- 部屋: `genius`（ジニアスの部屋）/ `lisa`（リサっちの部屋）/ `foyer`（大広間）
- `room.py` … 家をさわる唯一の道具。`go` `place` `move` `remove` `floor` `show` `where` `build` `reset`
- `RULES.md` … Bot 向けの短いルール

### ルール
- 1回起きたら行動は2つまで。行動1つ = 移動（`go`）か、環境の編集1項目
- 家具や床をさわれるのは、その部屋の名簿にいる子だけ
- 置ける家具は絵があるものだけ: futon_japanese / cat_plush / bear_plush / piano / television / potted_plant / bookshelf / computer_desk
- 壁にかかる端のマスには置けない（各部屋 1〜4、大広間は x 1〜10）
- ルール違反は `room.py` が自動で断る

## 描画
`room.py build` → `gen.py`（家の骨組み）→ `swap_objects.py`（家具とキャラ）。
重ね順: 背景 → 床 → 床の模様 → 空きマス → 奥の壁 → 家具 → 手前の壁 → キャラ。
吹き出しは今は描かない（`HOUSE_SPEECH=1` で復活）。

## シークレット
`ONIZUKA_WEBHOOK_URL` `ONIZUKA_WEBHOOK_KEY` `NIKKY_WEBHOOK_URL` `NIKKY_WEBHOOK_KEY`

## 使っていないもの
`data/consciousness.json` は初期の書き込みテスト用で、今は使っていない。
