# Animator無料5項目チェック｜自然流入・SNS配信用クリエイティブ（2026-11-14）

状態: **制作済み／SNS未投稿／公開サイトへの反映は別途CI確認**。アカウントへの投稿権限・当日の履歴・14日重複ガードが未照合なので、投稿APIやスケジューラは呼び出さない。

## ユーザーの課題と動線
- 対象: VRChatアバターをUnityで改変し、Animatorの表情・衣装・メニュー反応を手動で調べている制作者。
- 発見: 無料の技術的な解決メモをSNSに掲載。製品訴求より手順・公式根拠を中心にする。
- 価値体験: https://10131010-star.github.io/michishirube-lab/vrchat-animator-check/
- 有料商品の詳細: https://nokino-tools.booth.pm/items/9133855 （980円の掲載報告あり・購入/利益実測は別途）。
- 非保証: 無料版は手動チェックでUnityファイルの自動解析なし。販売中の製品も自動修復をせず、動作環境には未検証条件がある。

## 投稿候補（配信保留）
### A. Write Defaults / トラブル解消（価値8・商品案内2）
> VRChatの衣装や表情が元に戻らないとき、AnimatorのWrite Defaults混在を確認。いきなり全ステートをOn/Offに変更せず、戻すClipやAdditiveなどの例外も見ます。VRChat公式にも注意書きがあります。
>
> 無料5項目セルフチェック（手動・ファイル送信なし）：https://10131010-star.github.io/michishirube-lab/vrchat-animator-check/

出典: https://creators.vrchat.com/avatars/#write-defaults-on-states

### B. Expressions Menuの切り分け
> VRChatのExpressions Menuが反応しないときは、①ControlのParameter名 ②Expression Parametersの型 ③Animator側の設定 ④組み込みParameterとの違いを順に確認。原因を決めつけず1項目ずつ切り分けます。
>
> 無料メモ用チェック：https://10131010-star.github.io/michishirube-lab/vrchat-animator-check/

出典: https://creators.vrchat.com/avatars/expression-menu-and-controls/

### C. Playable Layersを理解する
> VRChatのAnimatorは1つのControllerだけを見ても原因が分からないことがあります。Base/Additive/Gesture/Action/FXの役割と、同じプロパティを複数レイヤーが操作していないか確認。まずは変更前の設定をバックアップ。
>
> 確認順を整理できる無料チェック：https://10131010-star.github.io/michishirube-lab/vrchat-animator-check/

出典: https://creators.vrchat.com/avatars/playable-layers/

## SNS配信前の必須ゲート
1. GitHub `10131010-star/nokino-ai-growth-os` PR #11の運用ルールと既存のBlueskyアカウント・投稿先を確認。今回作成の原稿を別経路で無断送信しない。
2. 過去14日の投稿、キュー、予約枠、重複意味判定を照合。同じ話題・URLを無理に連投しない。
3. 投稿候補の文字数と公式出典・商用表示・製品仕様を公開直前に確認。バージョン互換性や自動修復を保証しない。
4. 許可済み枠に限り投稿し、投稿IDと実URLが取れた場合のみ公開済み。取れなければ未投稿として扱う。

## 計測案
- posted_at, post_url, impressions, link_clicks, free_page_views, free_to_booth_clicks, booth_product_views, orders, revenue_jpy, fees_jpy, net_profit_jpy。
- **初期実測はすべて null**。UTMを付けただけでは実訪問を証明しない。無料ページは現時点で閲覧解析タグを導入していない。アクセス解析の設置はページのプライバシー記載と一緒に判断する。
- 後からUTMを使う場合は、既存運用の計測構成・プライバシー条件を先に確認する。
- 有料広告の出稿・課金は承認されていないため実行しない。既存Amazon広告月5,000円の枠を他媒体に流用しない。
