# 海外の空中写真・古地図と英語版の公開 テスト設計

- 仕様・設計: [`docs/spec/release_overseas_en.md`](../spec/release_overseas_en.md)
- 自動テスト:
  - `tests/e2e/release_pages_check.py` … 英語トップ・日本語トップに足したもの・試作のアドレスの転送・リンクの実在（下の表）
  - `tests/e2e/overseas_prototype_check.py` … 海外のページ `/overseas/`・`/en/overseas/`（[テスト設計](overseas_prototype.md)）
  - `tests/e2e/top_page_check.py` … 今の日本語トップ（変えていない部分が壊れていないこと）
- 実行: 引数なしで手元のファイル（`file://`）、`https://immersamap.github.io/` を渡すと公開サイト
- `file://` ではフォルダのリンク（`../en/`）に `index.html` が補われないので、リンクは押さずに、行き先のファイルが実在するかを見る（仕様 R1）

## release_pages_check.py

| ID | 観点 | 確かめること |
|---|---|---|
| R1 | リンクと画像の実在（6ページ） | 日英のトップ・日英の海外のページ・試作のアドレス2つの、ローカルの `src`・`href`・`srcset` がすべて実在する（公開サイトでは HTTP 200）。`/en/` 配下のパスの書き直し漏れを見つける（仕様 R2） |
| E1 | 英語トップ | `<html lang="en">`・題名・index・canonical（`/en/`）・hreflang（ja・en・x-default）。画面とパネル5タブに日本語が残らない（「日本語」のリンクは除く）。h1 は1つ。日本語トップへのリンク・海外（英語）への入口・「Japanese interface」。背景の写真が読める。FAQ 7件と構造化データの質問が一致。パネルの言葉のリンクは日本語の同じタブ（`../#faq`） |
| E2 | 英語トップ・JavaScript なし | 英語の見出しと地図へのボタンが読める |
| J1 | 日本語トップに足したもの | 英語のブラウザでも日本語のまま（自動で切り替えない）。hreflang。English のリンクは `en/`。「海外の空中写真・古地図（試作）」の入口。パネルの English は英語の同じタブ（`en/#support`） |
| M1 | スマホ 360×640・390×844（日英） | ヘッダーの右端が「画面幅 − 16px」以内・横にはみ出さない。言葉のリンクが見え、ヘッダーの地図ボタンは外す |
| M2 | 〃 | パネルのタブが5つとも見える |
| M3 | PC 1440×900・1280×720（日英） | 縦スクロール無し・メニュー1行・ボタンが画面内 |
| T1 | 試作のアドレスの転送 | `overseas-test.html` → `overseas/`、`?lang=en` → `en/overseas/`、`top-test.html` → `/`、`top-test.html?lang=en#faq` → `en/#faq` |
| T2 | 転送・JavaScript なし | meta refresh で `overseas/` へ移る。転送ページは `noindex` |
| — | 全体 | スクリプトエラーが出ない |

## overseas_prototype_check.py で変えたところ

| ID | 変えたこと |
|---|---|
| L1 | 言葉はページで決まる。英語のページは日本語のブラウザでも英語、日本語のページは英語のブラウザでも日本語。言葉のリンクは `hreflang` 付き |
| L4 | 地図を動かし年を選んでから言葉のリンクをたどると、場所・ズーム・種類・年を引き継ぐ（日→英・英→日。仕様 R6） |
| L5 | `#` の異常系: おかしな値・範囲外の緯度・知らない種類は初期表示。正しい値はその場所・種類・年。外したフランスの古地図の共有リンクは、場所を残して空中写真の近い年（仕様 R5） |
| L7 | 日英のページは id の組が同じ。index・canonical・hreflang。JavaScript が無くても見出しと言葉のリンクが見える（仕様 R4） |
| N12 | フランスの古地図を外した: パリでは切り替えを出さない。スイス 1900年の地図 → ケルンは 1891〜1912年 |
