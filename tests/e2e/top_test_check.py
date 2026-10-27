"""試作トップ（top-test.html）の E2E チェック。

テスト設計は docs/test_design/top_test_prototype.md。
ローカルでは Web サーバーを立てず、ファイルを直接ブラウザで開いて確かめる。公開後は URL を渡す。

    .venv/bin/python tests/e2e/top_test_check.py
    .venv/bin/python tests/e2e/top_test_check.py https://immersamap.github.io/top-test.html
    .venv/bin/python tests/e2e/top_test_check.py --shots docs/test_results/xxx   # 画面写真も保存
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
argv = sys.argv[1:]
SHOTS = None
if "--shots" in argv:
    i = argv.index("--shots")
    SHOTS = argv[i + 1]
    del argv[i:i + 2]
URL = argv[0] if argv else (ROOT / "top-test.html").as_uri()

TABS = ["features", "data", "faq", "about", "support"]
JA = re.compile(r"[぀-ヿ一-鿿]")
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))


def shot(page, name):
    if SHOTS:
        page.screenshot(path=f"{SHOTS}_{name}.jpg", type="jpeg", quality=80)


def open_page(browser, query="", locale="ja-JP", **kw):
    page = browser.new_page(locale=locale, viewport=kw.pop("viewport", {"width": 1440, "height": 900}), **kw)
    page.errors = []
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    page.goto(URL + query)
    page.wait_for_timeout(800)
    return page


def lang(page):
    return page.evaluate("document.documentElement.lang")


def visible_other(page, other):
    """もう一方の言葉の要素のうち、画面に見えているものの数。"""
    return page.evaluate(f"[...document.querySelectorAll('[data-lang=\"{other}\"]')].filter(e => e.checkVisibility()).length")


def japanese_left(page, scope):
    """英語のときに、見えている文字に残っている日本語。言葉のボタンの「日本語」は除く（innerText は見えている文字だけ）。"""
    text = page.evaluate(f"document.querySelector('{scope}').innerText")
    return JA.findall(text.replace("日本語", ""))


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- T1 日本語のブラウザ ----
    page = open_page(browser)
    check("T1 日本語のブラウザでは日本語", lang(page) == "ja" and "重ねて見る" in page.inner_text("h1:visible"))
    check("T1 英語の要素が1つも見えていない", visible_other(page, "en") == 0, str(visible_other(page, "en")))
    check("T1 言葉のボタンは「English」", page.inner_text("header [data-lang-toggle]") == "English")
    check("T1 海外の入口は日本語を引き継ぐ", page.get_attribute("#to-overseas", "href") == "overseas-test.html?lang=ja")
    check("T1 地図をひらくは /map/", page.get_attribute(".actions .cta.solid", "href") == "/map/")
    check("T1 ロゴは試作トップへ戻る（本物のトップへ飛ばない）", page.get_attribute("#brand", "href") == "top-test.html?lang=ja")
    shot(page, "pc_ja")

    # ---- T8 検索に出さない・本物と重ならない ----
    html = page.content()
    check("T8 noindex がある", page.locator('meta[name="robots"][content*="noindex"]').count() == 1)
    check("T8 構造化データ・canonical・OGP を載せない",
          "application/ld+json" not in html and 'rel="canonical"' not in html and "og:" not in html)

    # ---- T9 境目のつまみ（今のトップと同じ）----
    page.wait_for_timeout(3000)   # 最初の揺れが終わるまで
    page.focus("#handle")
    before = int(page.get_attribute("#handle", "aria-valuenow"))
    page.keyboard.press("ArrowRight")
    after = int(page.get_attribute("#handle", "aria-valuenow"))
    check("T9 境目のつまみが右キーで動く", after > before, f"{before} -> {after}")

    # ---- T3 切り替え ----
    page.click("header [data-lang-toggle]")
    page.wait_for_timeout(200)
    check("T3 押すと英語になる", lang(page) == "en" and "laid over" in page.inner_text("h1:visible"))
    check("T3 日本語の要素が1つも見えていない", visible_other(page, "ja") == 0, str(visible_other(page, "ja")))
    check("T3 海外の入口とロゴも英語を引き継ぐ",
          page.get_attribute("#to-overseas", "href") == "overseas-test.html?lang=en"
          and page.get_attribute("#brand", "href") == "top-test.html?lang=en")
    check("T3 切り替えた言葉をアドレスに残す（file:// で残せなくても止まらない）",
          "lang=en" in page.url or page.url.startswith("file:"), page.url)
    check("T 日本語の画面でスクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()

    # ---- T2 英語のブラウザ：本文とパネルの全タブに日本語が残らない ----
    page = open_page(browser, locale="en-US")
    check("T2 英語のブラウザでは英語", lang(page) == "en" and page.title().startswith("ImmersaMap | Old maps"), page.title())
    check("T2 日本語の要素が1つも見えていない", visible_other(page, "ja") == 0)
    left = japanese_left(page, ".stage")
    check("T2 1画面目に日本語が残っていない", not left, "".join(left))
    check("T2 地図は日本語の画面だと添える", "Japanese interface" in page.inner_text(".copy"))
    check("T2 見られるのは日本だと、説明文と下帯に書く",
          "in Japan" in page.inner_text(".lead:visible") and "of Japan" in page.inner_text(".facts"))
    check("T2 規約は日本語のページだと添える", "Terms (Japanese)" in page.inner_text(".credit"))
    shot(page, "pc_en")
    for tab in TABS:
        page.evaluate(f"location.hash = '{tab}'")
        page.wait_for_timeout(300)
        left = japanese_left(page, "#panel")
        check(f"T2 パネル「{tab}」に日本語が残っていない", page.is_visible(f"#{tab}") and not left, "".join(left))
        if tab == "faq":
            check("T2 英語の FAQ は7件", page.locator("#faq details:visible").count() == 7)
            shot(page, "pc_en_faq")
    check("T 英語の画面でスクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()

    # ---- T5 パネルを開いたまま言葉を変える（パネルはモーダルなので、パネルの上のボタンで）----
    page = open_page(browser, query="#faq")
    check("T5 #faq でパネルが開く", page.evaluate("document.getElementById('panel').open") and page.is_visible("#faq"))
    page.click("#panel [data-lang-toggle]")
    page.wait_for_timeout(200)
    check("T5 パネルの上のボタンで英語になり、パネルは開いたまま FAQ のまま",
          lang(page) == "en" and page.evaluate("document.getElementById('panel').open")
          and page.is_visible("#faq") and page.locator("#faq details:visible").count() == 7)
    page.close()

    # ---- T4 アドレスの指定（異常系を含む）----
    page = open_page(browser, query="?lang=en")
    check("T4 日本語のブラウザでも ?lang=en なら英語", lang(page) == "en")
    page.close()
    page = open_page(browser, query="?lang=xx", locale="en-US")
    check("T4 ?lang= がおかしな値ならブラウザの言葉（英語）", lang(page) == "en" and not page.errors)
    page.close()

    # ---- T10 JavaScript が動かないときは日本語だけ ----
    page = open_page(browser, locale="en-US", java_script_enabled=False)
    check("T10 JavaScript が無いと日本語だけが見える（英語は隠れたまま）",
          page.locator("[data-lang=en]:visible").count() == 0 and page.locator("h1:visible").count() == 1)
    check("T10 JavaScript が無いと、押しても動かない言葉のボタンは出さない", page.locator("[data-lang-toggle]:visible").count() == 0)
    page.close()

    # ---- T6 スマホ：ヘッダーが入りきる。T7 PC：1画面に収まる ----
    for w, h in [(360, 640), (390, 844)]:
        for loc in ["ja-JP", "en-US"]:
            page = open_page(browser, locale=loc, viewport={"width": w, "height": h}, is_mobile=True, has_touch=True)
            rights = page.evaluate("[...document.querySelectorAll('header .brand, header nav > *')]"
                                   ".filter(e => e.checkVisibility()).map(e => e.getBoundingClientRect().right)")
            check(f"T6 {w}px・{loc}: ヘッダーが画面に入りきる（右端 {w - 16}px 以内）", max(rights) <= w - 16, str(rights))
            check(f"T6 {w}px・{loc}: 言葉のボタンが見え、ヘッダーの地図ボタンは外す",
                  page.is_visible("header [data-lang-toggle]") and page.is_hidden("header .cta.hdr"))
            cta = page.locator(".actions .cta.solid").bounding_box()
            check(f"T6 {w}px・{loc}: 本文の「地図をひらく」が見える", cta and cta["x"] + cta["width"] <= w, str(cta))
            check(f"T6 {w}px・{loc}: 横にはみ出さない", page.evaluate("document.documentElement.scrollWidth") <= w)
            if w == 390:
                shot(page, f"sp_{loc[:2]}")
            page.click(".actions [data-open=data]")
            page.wait_for_timeout(300)
            tabs = page.evaluate("(() => { const t = document.querySelector('#panel .tabs'); return [t.scrollWidth, t.clientWidth]; })()")
            check(f"T11 {w}px・{loc}: パネルのタブが全部見える（切れない）", tabs[0] <= tabs[1], str(tabs))
            pb = page.locator("#panel").bounding_box()
            check(f"T11 {w}px・{loc}: パネルは画面いっぱい", pb["x"] <= 0.5 and pb["width"] >= w - 0.5, str(pb))
            if w == 360 and loc == "ja-JP":
                shot(page, "sp_ja_panel")
            page.close()
    for loc in ["ja-JP", "en-US"]:
        for w, h in [(1440, 900), (1280, 720)]:
            page = open_page(browser, locale=loc, viewport={"width": w, "height": h})
            sh = page.evaluate("document.documentElement.scrollHeight")
            nav = page.locator("header nav").bounding_box()
            acts = page.locator(".actions").bounding_box()
            check(f"T7 PC {w}x{h}・{loc}: 縦スクロール無し・メニューが1行・ボタンが画面内",
                  sh <= h and nav["height"] < 60 and acts["y"] + acts["height"] <= h, f"sh={sh} nav={nav} acts={acts}")
            page.click(".actions [data-open=data]")
            page.wait_for_timeout(300)
            tabs = page.evaluate("(() => { const t = document.querySelector('#panel .tabs'); return [t.scrollWidth, t.clientWidth]; })()")
            check(f"T11 PC {w}x{h}・{loc}: パネルのタブが全部見える（切れない）", tabs[0] <= tabs[1], str(tabs))
            page.close()

    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
sys.exit(1 if failed else 0)
