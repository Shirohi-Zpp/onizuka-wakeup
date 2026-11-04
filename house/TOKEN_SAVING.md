# トークン節約のアイデア / Token-saving tips

1. 物の変更で壁・床を再生成しない。objects レイヤー+合成だけ(`swap_objects.py`)。
2. 監視(`watch_house.py`)を常駐させ、毎回Botに頼まない。env.json を書けば自動反映。
3. 差し替えのたびにPNGをチャットへ添付しない。固定パス `/workspace/house/house-live.png`(将来は Pages)を案内するだけ。
4. 「画像を作り直して」より state JSON の小さな編集で依頼する。
5. スプライトはキャッシュ済み。既知の type を再生成しない(`sprites/sprites.json` を確認)。
6. 地図やスプライトに AI 画像生成を使わない。Pillow で十分・決定的・高速。
7. 毎ターンコード全体を読まない。HANDOFF.md と house-structure.json で足りる。
8. 複数の変更は env.json への1回の書き込みにまとめる。
9. キャラのポーズは state のスプライトIDを変えるだけ。新規画像生成しない。
10. 報告は `state/last_swap.json`(配置・ms)を1行要約すれば十分。

EN: Swap layers not structure; keep the watcher running; point to the stable PNG path instead of attaching images; edit small JSON; reuse cached sprites; Pillow over AI image gen; read HANDOFF.md not the whole codebase; batch edits; poses = sprite id swaps.
