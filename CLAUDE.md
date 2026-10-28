# ImmersaMap プロジェクト固有ルール

> 共通ルールは `/home/manabu/projects/CLAUDE.md` を参照。ここには本プロジェクト固有の事情のみ記載する。

古地図・空中写真を今の地図に重ねる地図アプリ。素のHTML/JS＋Leaflet（ビルド・npm 無し）、データは Supabase、配信は GitHub Pages（Jekyll）。

| ページ | パス |
|---|---|
| 地図探索（空中写真8世代） | `/map/` |
| 物語追体験 | `/okunohosomichi/`, `/ryoma/` |
| 海外の空中写真・古地図（試作の表示のまま公開） | `/overseas/`, `/en/overseas/`（JS・CSS は `overseas/` に1つ） |
| 英語トップ | `/en/`（`/map/` は日本語のまま案内） |

- 公開URL: https://immersamap.github.io/
- リポジトリ: https://github.com/immersamap/immersamap.github.io （Organization `immersamap`／**Public**）

## ⚠ 壊すと困ること

- **`main` への push・マージは、そのまま本番公開**（Pages が `main` を直接配信）。「試しに」の push も即公開になる
- **サイトのファイルはリポジトリ直下から動かさない。** 共通ルールの `src/` 分離は適用しない。HTML・画像・`*.sql` を移すと公開URLが404になり、共有済みリンクも壊れる。ドキュメントは `docs/`（`_config.yml` の `exclude` で非配信）
- 非公開にしたいファイルは `_config.yml` の `exclude` に足す。ただし Public なので**配信されないだけで、GitHub 上では誰でも読める**。秘密の値を置かない
- **`historical_maps_setup.sql` を本番に流し直さない。** insert/update/delete を `true` で許す古いポリシーが残っていて、流すと全開放に戻る。本番の Supabase は閲覧のみ（2026-10-19 ユーザー確認）
- 各HTMLの `sb_publishable_...` は公開前提の鍵で、漏洩ではない。守りは RLS ポリシー側

## オーナーが決めたこと

- 「誰でも地図を書き込める」機能は、もっと先で検討する。それまで書き込みは開けない
- 広告（AdSense）は一旦見送り（2026-10-19）。再開するときは、Esri の衛星写真（非商用のみ）と今昔マップの埋め込み（1日1000PV 超のページでは不可）の扱いを先に決める
- **ローカルで Web サーバーは立てない**（2026-10-27）。自動テストは HTML を `file://` で直接開いて流す（`tests/e2e/*.py`）。
  ユーザーが画面で確かめるものは、**どこからもリンクしないページ（`noindex`）として公開サイトに置き、直アドレスで見てもらう**。置く前に、既存ページ・`sitemap.xml` を変えていないことを確かめる
- **英語版は `/en/` に置き、言葉はページ（URL）で決める**（2026-10-27）。ブラウザの言葉で自動に切り替え・転送しない（日本語の検索順位が落ちる）。日英のページには canonical と hreflang（ja・en・x-default）を互いに書く
- `/en/` 配下は1階層深い。画像・リンクは相対パスで書き、`tests/e2e/release_pages_check.py` の R1 で確かめる
- フランスの古地図（カッシーニ図・参謀本部図）は、利用条件を IGN に確認できるまで載せない（2026-10-27）

## 作業のしかた

- 地図の描画崩れは目視でしか分からない。変更後はスクリーンショットを取り `docs/test_results/` に残す
- マージ後は必ず公開サイトを開いて確認する（Pages のビルドに数十秒かかる）

## 知っておくこと

- **AI による GeoJSON 自動生成は動いていない**（Supabase の新形式の鍵が JWT でなく Edge Function が止まった）。今は別チャットで GeoJSON を作って手で埋め込む（例 `kawagoe.html`）
- **江戸期の古地図の重ね合わせは断念済み。** 絵図は測量されておらず重ならない。技術で解決しようとしない
- 空中写真は年代ごとにカバー範囲が違う。差は `coverage_polygons` で管理
- 外部サービスの鍵は形式が変わりうる。疎通は鍵の有無でなく実際に1回リクエストして確かめる（2026-06 頃）

詳しい経緯・バグの記録は `docs/claude_notes/bugs.md`
