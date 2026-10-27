# 試作トップ（top-test.html）テスト設計

- 対象: `top-test.html`（設計: [`docs/design/top_test_prototype.md`](../design/top_test_prototype.md)）
- 自動テスト: `tests/e2e/top_test_check.py`（Playwright・Chromium）
- 実行: `.venv/bin/python tests/e2e/top_test_check.py --shots docs/test_results/<日付>_top_test`
- ローカルでは `file://` で開く。`/map/` などの絶対パスは行き先を開かず、`href` を確かめる
- 言葉はブラウザの設定（`locale`）で変わるので、日本語（`ja-JP`）と英語（`en-US`）の両方で開く

## 正常系

| ID | 観点 | 確かめること |
|---|---|---|
| T1 | 日本語のブラウザ | 日本語で開く。英語の要素が1つも見えていない。言葉のボタンは「English」。海外の入口は `overseas-test.html?lang=ja`、地図は `/map/`、ロゴは `top-test.html?lang=ja` |
| T2 | 英語のブラウザ | 英語で開く（`<html lang>`・題名）。日本語の要素が見えていない。1画面目とパネルの5つのタブに日本語が残っていない（言葉のボタンの「日本語」は除く）。「Japanese interface」「Terms (Japanese)」を添える。説明文と下帯に「Japan」と書く。英語の FAQ は7件 |
| T3 | 切り替え | 押すと英語になり、日本語の要素が見えなくなる。海外の入口とロゴの `?lang=` も変わる。アドレスに `lang=en` を残す（`file://` で残せなくても止まらない） |
| T5 | パネルを開いたまま切り替え | `#faq` でパネルが開く。パネルの上の言葉ボタンで英語になり、パネルは開いたまま FAQ のまま（R2） |
| T9 | 境目のつまみ | 今のトップと同じく、右キーで動く |
| T | 全体 | スクリプトエラーが出ない |

## 異常系・画面の大きさ

| ID | 観点 | 確かめること |
|---|---|---|
| T4 | アドレスの指定 | 日本語のブラウザでも `?lang=en` なら英語。`?lang=xx` はブラウザの言葉になり、エラーにならない |
| T10 | JavaScript が動かない | 英語のブラウザでも、日本語だけが見える（英語は CSS で隠れたまま・見出しは1つ）。押しても動かない言葉のボタンは出さない |
| T6 | スマホ 360×640・390×844（日本語・英語） | ヘッダーの右端が「画面幅 − 16px」以内（R1）。言葉のボタンが見え、ヘッダーの「地図をひらく」は外れている。本文の「地図をひらく」が画面内。横にはみ出さない |
| T7 | PC 1440×900・1280×720（日本語・英語） | 縦スクロールが無い（今のトップと同じ1画面）。メニューが1行。本文のボタンが画面内 |
| T11 | パネルのタブ（上の4つの大きさ × 日本語・英語） | 5つのタブが切れずに全部見える（`.tabs` の scrollWidth ≤ clientWidth）。スマホではパネルが画面いっぱい |

## 公開サイトへの影響

| ID | 確かめること | 方法 |
|---|---|---|
| T8 | 検索に出さない・本物と重ならない | `noindex` がある。構造化データ・canonical・OGP が無い（自動） |
| P1 | 既存のファイルを変えていない | `git diff main --stat` に既存の HTML・`sitemap.xml` が出ない |
| P2 | 今のトップが壊れていない | `tests/e2e/top_page_check.py` が全件 PASS |
| P3 | 直アドレスで開ける | マージ後、`tests/e2e/top_test_check.py https://immersamap.github.io/top-test.html` が全件 PASS |
| P4 | どこからも辿れない | 公開中のトップ・`/map/`・`sitemap.xml` に `top-test` が出てこない |
