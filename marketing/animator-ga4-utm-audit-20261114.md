# VRChat Animator集客・UTM実装引き継ぎ（2026-11-14 JST）

## 変更した公開ページ（公開状況はPagesの成功後に確定）
- 無料手動チェック: https://10131010-star.github.io/michishirube-lab/vrchat-animator-check/
- BOOTH販売中の商品: https://nokino-tools.booth.pm/items/9133855 （販売表示980円 / v0.1.0-rc3先行版）
- 新規ランディングページを作らず、既存3つのBOOTH CTAのみUTMを標準化。公開後に再度確認する
- 無料ページ側のGoatCounterはページ閲覧・結果生成・3種類のBOOTHリンククリック・共有画面起動を匿名集計するコードを維持。**GA4タグやWebストリームの新設なし**
- 診断内容、回答、ユーザー個人情報は送信しない。UTMは集客元の識別子にすぎずクリック/購入の証拠ではない

### 無料チェック→BOOTHへのCTA（3箇所）
共通パラメータ: `utm_source=michishirube_freecheck&utm_medium=referral&utm_campaign=animator_pro_launch`。

- 5項目チェック下 `utm_content=check_section`
- 検証用Controller例 `utm_content=verified_demo`
- 有料版紹介フッター `utm_content=footer`

検証コマンド: `node tests/animator-utm-links.cjs`。これは**静的なURL構造テスト**。GA4による流入・イベント収集が成功した証拠ではない。遷移先のGA4では `Session manual source/medium` と `Session manual campaign name` を調べる。GA4とGoatCounterのユーザー数/クリック数を直接同一視しない。

### 既知の外部公開済みSNS投稿（重複防止参照）
- 2026-11-12 発売告知: https://bsky.app/profile/yoshimoto1010.bsky.social/post/3n22cnf7ayl22
- 2026-11-14 公開投稿として作業履歴に記録されたURL: https://bsky.app/profile/did:plc:cvbscsljudtg2v2w5y6nfdnv/post/3n27o6jusyk2e （本文/着地URLの新規照合は未完了）

## Bluesky新案（両方とも未投稿／既存配信枠の重複・頻度・権限確認が必要）
### 案1｜Transition条件が見つからないとき
> Animatorの遷移が動かないときは、TransitionのConditionsにあるParameter名とController側のParametersを照合。EntryやAny Stateも見落とさず確認します。検証用Controllerでは未定義Parameterを検出しましたが、個別アバターの原因確定ではありません。
>
> 手動で確認点を整理できる無料5項目チェック：https://10131010-star.github.io/michishirube-lab/vrchat-animator-check/?utm_source=bluesky&utm_medium=organic&utm_campaign=animator_pro_launch&utm_content=missing_parameter_tip

### 案2｜未使用に見えるParameterの安全確認
> Animatorで「未使用」に見えるParameterも、いきなり削除しないでください。Transition以外のBehaviourやAnimationから利用される場合があります。まず参照元を確認し、バックアップ後に少しずつ変更するのが安全です。
>
> 5項目の確認メモ（無料・自動修復なし）：https://10131010-star.github.io/michishirube-lab/vrchat-animator-check/?utm_source=bluesky&utm_medium=organic&utm_campaign=animator_pro_launch&utm_content=unused_parameter_tip

- 内容：どちらも実例/確認手順が先、有料商品の購入を強制しない。Ver 2022.3.22f1 / SDK 3.10.5の検証範囲を超える保証はしない
- 最終チェック：最新14日の投稿と予約投稿、権利、リンク、アカウント、本人が承認した投稿頻度。重複があれば保留
- **投稿実績：今回0件**。投稿成功URLを新規に発行していない

## 実測値の扱い
- オーナーからGA4の過去7日間基準値（2026-11-14 09:34 JST）の共有あり。共有時点の実測は私人が管理する売上台帳側に記録し、公開サイトに管理データを埋め込まない
- GA4の`view_item`やページ表示と、BOOTHの注文・売上・利益は別物。注文はBOOTHの販売管理画面を一次情報とする
- ソース `(direct)/(none)` には、未タグ付けのSNS流入が混在する可能性あり。SNS流入0と断定しない
- 未取得の `freecheck_views`, `freecheck_completion`, `outbound_clicks`, `booth_sessions_by_source`, `orders`, `net_profit` は `null` のままとする
- BOOTH公式GA4連携資料: https://booth.pm/announcements/639 （一つのショップにGA4 IDは一つ。すでに商品ページのイベントが記録されているので新しいウェブストリーム追加は不要）
- GA4手動UTM仕様: https://support.google.com/analytics/answer/11242870?hl=ja

## 次の計測仮説
仮説: `source=michishirube_freecheck / medium=referral / campaign=animator_pro_launch` のBOOTHセッションを区別できれば、無料チェック起点の検討をDirect流入と分けて追える。判定: デプロイ後、外部ブラウザで1回だけ実リンク遷移して管理可能なGA4を確認。計測反映が保証されるわけではない。実顧客の閲覧・購入やSNS効果の実測は別途。
