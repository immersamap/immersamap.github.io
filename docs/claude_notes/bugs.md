# immersamap のバグ記録・経緯（CLAUDE.md から移した）

2026-10-29 に CLAUDE.md を短くしたとき、詳しい記録をここへ移した。決まりそのものは CLAUDE.md に残っている。

## 既知の課題（元の文）

- **AI によるGeoJSON自動生成は動いていない。** Supabase の新形式 publishable key が JWT ではないのに
  Edge Function 側が JWT 形式を要求し `UNAUTHORIZED_INVALID_JWT_FORMAT` で停止した。
  現在は Edge Function を呼ぶコードは repo に無く、**別チャットで GeoJSON を作って手で埋め込む**運用
  （例：`kawagoe.html` の「GeoJSONデータ（Claude解析結果）」）。
- **江戸期の古地図の重ね合わせは断念済み。** 当時の絵図は測量されておらず、現在の地図に正確に
  重ならない。対象そのものの性質による制約なので、技術で解決しようとしないこと。
  代わりに国土地理院の空中写真（1930年代〜）に切り替えた経緯がある。
- 空中写真は**年代ごとにカバー範囲が違う**（1930年代=東京・大阪のみ／1940年代=14都市／
  1960年代以降=全国）。この差は `coverage_polygons` でDB管理している。

## バグ再発防止観点

### Supabase の鍵形式変更でAI機能が停止した
- **原因:** 新形式の publishable key は JWT ではないのに、Edge Function 側が JWT 形式の
  anon key を前提にしていた。鍵の「有無」ではなく「形式」が変わったため、設定を見ても気づきにくい
- **設計での注意点:** 外部サービスの鍵は、形式が変わりうる前提で扱う。
  クライアント用（publishable）とサーバ用（service role）を混同しない
- **テスト観点:** 鍵の存在チェックではなく、**実際に1回リクエストを投げて疎通確認する**
- **発生日:** 2026-06 頃（詳細は `docs/spec/SPECIFICATION.md`）

## 作業ルールの例（元の文）

- ユーザーが画面で確かめるものは、どこからもリンクしないページ（`noindex`）として公開サイトに置く。
  例: 以前の `overseas-test.html`。2026-10-27 に `/overseas/` として公開し、今は転送ページ

## 技術スタック（元の文）

- フロントエンド: 素のHTML/JS + **Leaflet 1.9.4**（ビルドツール無し・npm 無し）
- データ: **Supabase**（PostgreSQL + Storage）。テーブルは `maps` / `locations` / `chapters` / `verses` / `coverage_polygons`
- ホスティング: **GitHub Pages**（Jekyll）
- 地図タイル: 国土地理院ほか
- ローカル: `/home/manabu/projects/immersamap`（2026-09-07 に clone）
