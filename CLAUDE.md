# ImmersaMap プロジェクト固有ルール

> 共通ルールは `/home/manabu/projects/CLAUDE.md` を参照。ここには本プロジェクト固有の事情のみ記載する。

## プロジェクト概要

古地図・空中写真を現在の地図に重ね合わせて、「今この場所は過去どうだったか」を体験する地図アプリ。
2つのモードを持つ。

| モード | パス | 内容 |
|---|---|---|
| 地図探索 | `/map/` | 空中写真8世代（1930年代〜現在）を時間スライダーで切り替え |
| 物語追体験 | `/okunohosomichi/`, `/ryoma/` | 文学作品の舞台をマーカーと時系列で追う |

- 公開URL: https://immersamap.github.io/
- リポジトリ: https://github.com/immersamap/immersamap.github.io （Organization `immersamap`／**Public**）
- ローカル: `/home/manabu/projects/immersamap`（2026-09-07 に clone）

## 技術スタック

- フロントエンド: 素のHTML/JS + **Leaflet 1.9.4**（ビルドツール無し・npm 無し）
- データ: **Supabase**（PostgreSQL + Storage）。テーブルは `maps` / `locations` / `chapters` / `verses` / `coverage_polygons`
- ホスティング: **GitHub Pages**（Jekyll）
- 地図タイル: 国土地理院ほか

## ⚠ このリポジトリ固有の重要な制約

### 1. `main` への push は、そのまま本番公開

GitHub Pages が `main` を直接配信している。**マージした瞬間に世界に公開される**。
ローカルで動いた＝公開された、ではないし、逆に「まだ試しに」のつもりの push も即公開になる。

### 2. サイトのファイルは**リポジトリ直下から動かせない**

共通ルールの `src/` 分離は、このプロジェクトには**適用しない**。
`index.html` や `map/index.html` は公開URLと1対1で対応しているため、移動すると
公開URLが404になり、検索エンジンの登録・共有済みリンクも壊れる。

- ✅ ドキュメントは `docs/` へ分離済み（`_config.yml` の `exclude` で非公開化）
- ❌ HTML・画像・`*.sql` を `src/` 等へ移動してはならない

### 3. 非公開にしたいファイルは `_config.yml` の `exclude` に足す

リポジトリが Public なので、**`exclude` は「配信されない」だけで「読めない」わけではない**。
GitHub 上ではソースが誰にでも見える。秘密にすべき値を置く場所ではない。

## セキュリティ

### Supabase の鍵について

各HTMLに `sb_publishable_...` が直書きされているが、これは**ブラウザに露出する前提の公開鍵**なので
仕様どおりであり、漏洩ではない。**守りは鍵ではなくRLSポリシー側にある。**

### 書き込みの権限（2026-10-19 ユーザー確認）

本番の Supabase は**閲覧のみ**で、誰でも書き換えられる状態ではない（ユーザー確認）。
リポジトリの `historical_maps_setup.sql` には insert/update/delete を `true` で許すポリシーが残っているが、
**これは古い内容で、本番とは違う。** このファイルを本番に流し直さないこと（流すと全開放に戻る）。

- 「誰でも地図を書き込める」機能は、**もっと先で検討する**（ユーザー決定）。それまで書き込みは開けない
- 広告（AdSense）は**一旦見送り**（2026-10-19 ユーザー決定）。再開するときは、Esri の衛星写真（非商用のみ）と
  今昔マップの埋め込み（1日1000PV 超のページでは不可）の扱いを先に決める

## 既知の課題

- **AI によるGeoJSON自動生成は動いていない。** Supabase の新形式 publishable key が JWT ではないのに
  Edge Function 側が JWT 形式を要求し `UNAUTHORIZED_INVALID_JWT_FORMAT` で停止した。
  現在は Edge Function を呼ぶコードは repo に無く、**別チャットで GeoJSON を作って手で埋め込む**運用
  （例：`kawagoe.html` の「GeoJSONデータ（Claude解析結果）」）。
- **江戸期の古地図の重ね合わせは断念済み。** 当時の絵図は測量されておらず、現在の地図に正確に
  重ならない。対象そのものの性質による制約なので、技術で解決しようとしないこと。
  代わりに国土地理院の空中写真（1930年代〜）に切り替えた経緯がある。
- 空中写真は**年代ごとにカバー範囲が違う**（1930年代=東京・大阪のみ／1940年代=14都市／
  1960年代以降=全国）。この差は `coverage_polygons` でDB管理している。

## 作業ルール

1. 作業は必ず feature ブランチで行う（`feature/xxx` / `fix/xxx` / `docs/xxx`）
2. ビルド工程が無いので、**ローカル確認は静的サーバで行う**

   ```bash
   cd /home/manabu/projects/immersamap
   python3 -m http.server 8080     # → http://localhost:8080/map/
   ```

   ※ Jekyll の `exclude` はこの方法では効かないため、ローカルでは docs/ も見える。公開時の挙動とは異なる。
3. 地図の描画崩れは目視でしか分からないため、変更後は**スクリーンショットを取り**
   `docs/test_results/` に残す
4. マージ後は**必ず公開サイトを開いて確認する**（Pages のビルドに数十秒かかる）

## バグ再発防止観点

### Supabase の鍵形式変更でAI機能が停止した
- **原因:** 新形式の publishable key は JWT ではないのに、Edge Function 側が JWT 形式の
  anon key を前提にしていた。鍵の「有無」ではなく「形式」が変わったため、設定を見ても気づきにくい
- **設計での注意点:** 外部サービスの鍵は、形式が変わりうる前提で扱う。
  クライアント用（publishable）とサーバ用（service role）を混同しない
- **テスト観点:** 鍵の存在チェックではなく、**実際に1回リクエストを投げて疎通確認する**
- **発生日:** 2026-06 頃（詳細は `docs/spec/SPECIFICATION.md`）
