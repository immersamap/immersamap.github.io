"""英語トップ（/en/）・日本語トップに足した入口・試作のアドレスの転送・リンクの実在の E2E チェック。

仕様は docs/spec/release_overseas_en.md、テスト設計は docs/test_design/release_overseas_en.md。
海外のページ（/overseas/・/en/overseas/）は tests/e2e/overseas_prototype_check.py で確かめる。

    .venv/bin/python tests/e2e/release_pages_check.py
    .venv/bin/python tests/e2e/release_pages_check.py https://immersamap.github.io/   # 公開サイト
    .venv/bin/python tests/e2e/release_pages_check.py --shots docs/test_results/xxx   # 画面写真も保存
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
argv = sys.argv[1:]
SHOTS = None
if "--shots" in argv:
    i = argv.index("--shots")
    SHOTS = argv[i + 1]
    del argv[i:i + 2]
LIVE = bool(argv)
BASE = argv[0].rstrip("/") + "/" if argv else ROOT.as_uri() + "/"
JA = BASE + "index.html"
EN = BASE + "en/index.html"
TABS = ["features", "data", "faq", "about", "support"]
JA_CHARS = re.compile(r"[぀-ヿ一-鿿]")
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))


def shot(page, name):
    if SHOTS:
        page.screenshot(path=f"{SHOTS}_{name}.jpg", type="jpeg", quality=80)


def open_page(browser, url, **kw):
    page = browser.new_page(locale=kw.pop("locale", "ja-JP"), viewport=kw.pop("viewport", {"width": 1440, "height": 900}), **kw)
    page.errors = []
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    page.goto(url)
    page.wait_for_timeout(800)
    return page


def local_target(page_url, ref):
    """ページの中の相対・絶対パスを、手元のファイルに直す（フォルダなら index.html）。外部なら None。"""
    if ref.startswith(("http:", "https:", "mailto:", "#", "data:")):
        return None
    if ref.startswith("/"):
        path = ROOT / ref.split("#")[0].split("?")[0].lstrip("/")
    else:
        path = Path(urlparse(urljoin(page_url, ref)).path)
    return path / "index.html" if ref.split("#")[0].split("?")[0].endswith("/") or path.is_dir() else path


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- R1 リンクと画像が実在する（/en/ は1階層深い。仕様 R1・R2）----
    pages = [JA, EN, BASE + "overseas/index.html", BASE + "en/overseas/index.html", BASE + "overseas-test.html", BASE + "top-test.html"]
    req = p.request.new_context()
    for url in pages:
        # 転送ページは開くと移ってしまうので、ブラウザで開かずに HTML の文字から src・href・srcset を拾う
        html = req.get(url).text() if LIVE else Path(urlparse(url).path).read_text(encoding="utf-8")
        refs = re.findall(r'\b(?:src|href)="([^"]+)"', html)
        refs += [s.strip().split(" ")[0] for v in re.findall(r'\bsrcset="([^"]+)"', html) for s in v.split(",")]
        missing = []
        for ref in refs:
            if LIVE:
                if ref.startswith(("http:", "https:", "#", "mailto:", "data:")):
                    continue
                r = req.get(urljoin(url, ref))
                if r.status != 200:
                    missing.append(f"{ref} {r.status}")
            else:
                target = local_target(url, ref)
                if target is not None and not target.exists():
                    missing.append(ref)
        name = url.replace(BASE, "/")
        check(f"R1 {name}: ローカルのリンク・画像がすべて実在する（{len(refs)}件）", refs and not missing, ", ".join(missing))

    # ---- E1 英語トップ ----
    page = open_page(browser, EN)
    html = page.content()
    check("E1 英語トップは英語（<html lang=\"en\">・題名）", page.evaluate("document.documentElement.lang") == "en"
          and page.title().startswith("ImmersaMap | Old maps"), page.title())
    check("E1 index・canonical は /en/・hreflang（ja・en・x-default）",
          'content="index,follow' in html and 'rel="canonical" href="https://immersamap.github.io/en/"' in html
          and all(f'hreflang="{h}"' in html for h in ("ja", "en", "x-default")))
    left = JA_CHARS.findall(page.inner_text("body").replace("日本語", ""))
    check("E1 画面に日本語が残っていない（言葉のリンクの「日本語」は除く）", not left, "".join(left))
    check("E1 h1 は1つ", page.locator("h1").count() == 1)
    check("E1 言葉のリンクは日本語トップへ", page.get_attribute("header .lang-btn", "href") == "../"
          and page.get_attribute("header .lang-btn", "hreflang") == "ja")
    check("E1 海外のページ（英語）への入口", page.locator('.actions a[href="overseas/"]').count() == 1)
    check("E1 地図は日本語の画面だと添える", "Japanese interface" in page.inner_text(".copy"))
    check("E1 背景の写真が2枚とも読める",
          page.evaluate("[...document.querySelectorAll('.photo img')].every(i => i.complete && i.naturalWidth > 0)"))
    ld = json.loads(page.locator('script[type="application/ld+json"]').inner_text())
    faq_ld = next(g for g in ld["@graph"] if g["@type"] == "FAQPage")["mainEntity"]
    page.evaluate("location.hash = 'faq'")
    page.wait_for_timeout(300)
    summaries = page.locator("#faq summary").all_inner_texts()
    check("E1 英語の FAQ は7件で、構造化データの質問と画面の質問が一致",
          len(summaries) == 7 and [q["name"] for q in faq_ld] == summaries, str(len(summaries)))
    check("E1 パネルの言葉のリンクは、日本語の同じタブへ", page.get_attribute("#panel-lang", "href") == "../#faq")
    shot(page, "en_faq")
    for tab in TABS:
        page.evaluate(f"location.hash = '{tab}'")
        page.wait_for_timeout(200)
        left = JA_CHARS.findall(page.inner_text("#panel").replace("日本語", ""))
        check(f"E1 パネル「{tab}」に日本語が残っていない", page.is_visible(f"#{tab}") and not left, "".join(left))
    check("E1 スクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()
    page = browser.new_page(java_script_enabled=False)
    page.goto(EN)
    check("E2 JavaScript が無くても英語の見出し・ボタンが読める（英語だけの HTML）",
          "laid over" in page.inner_text("h1") and page.locator('.actions a[href="../map/"]').count() == 1)
    page.close()

    # ---- J1 日本語トップに足したもの ----
    page = open_page(browser, JA, locale="en-US")
    html = page.content()
    check("J1 英語のブラウザでも日本語トップは日本語のまま（自動で切り替えない）", page.evaluate("document.documentElement.lang") == "ja"
          and page.url.endswith("index.html"))
    check("J1 hreflang（ja・en・x-default）", all(f'hreflang="{h}"' in html for h in ("ja", "en", "x-default")))
    check("J1 English のリンクは /en/", page.get_attribute("header .lang-btn", "href") == "en/"
          and page.get_attribute("header .lang-btn", "hreflang") == "en")
    check("J1 海外の空中写真・古地図（試作）への入口", page.locator('.actions a[href="overseas/"]').count() == 1
          and "試作" in page.inner_text('.actions a[href="overseas/"]'))
    page.evaluate("location.hash = 'support'")
    page.wait_for_timeout(300)
    check("J1 パネルの English のリンクは、英語の同じタブへ", page.get_attribute("#panel-lang", "href") == "en/#support")
    check("J1 スクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    shot(page, "ja_pc")
    page.close()

    # ---- M スマホ・PC の収まり（日英のトップ）----
    for url, name in ((JA, "日本語"), (EN, "英語")):
        for w, h in ((360, 640), (390, 844)):
            page = open_page(browser, url, viewport={"width": w, "height": h}, is_mobile=True, has_touch=True)
            rights = page.evaluate("[...document.querySelectorAll('header .brand, header nav > *')]"
                                   ".filter(e => e.checkVisibility()).map(e => e.getBoundingClientRect().right)")
            check(f"M1 {name} {w}px: ヘッダーが画面に入りきる（右端 {w - 16}px 以内）・横にはみ出さない",
                  max(rights) <= w - 16 and page.evaluate("document.documentElement.scrollWidth") <= w, str(rights))
            check(f"M1 {name} {w}px: 言葉のリンクが見え、ヘッダーの地図ボタンは外す",
                  page.is_visible("header .lang-btn") and page.is_hidden("header .cta.hdr"))
            page.click(".actions [data-open=data]")
            page.wait_for_timeout(300)
            tabs = page.evaluate("(() => { const t = document.querySelector('#panel .tabs'); return [t.scrollWidth, t.clientWidth]; })()")
            check(f"M2 {name} {w}px: パネルのタブが5つとも見える", tabs[0] <= tabs[1], str(tabs))
            if w == 390:
                shot(page, f"sp_{'en' if url == EN else 'ja'}_panel")
            page.close()
        for w, h in ((1440, 900), (1280, 720)):
            page = open_page(browser, url, viewport={"width": w, "height": h})
            sh = page.evaluate("document.documentElement.scrollHeight")
            nav = page.locator("header nav").bounding_box()
            acts = page.locator(".actions").bounding_box()
            check(f"M3 {name} PC {w}x{h}: 縦スクロール無し・メニューが1行・ボタンが画面内",
                  sh <= h and nav["height"] < 60 and acts["y"] + acts["height"] <= h, f"sh={sh} nav={nav} acts={acts}")
            if w == 1440 and url == EN:
                shot(page, "en_pc")
            page.close()

    # ---- T 試作のアドレスは新しいアドレスへ転送する ----
    for src, want in (("overseas-test.html", "overseas/"), ("overseas-test.html?lang=en", "en/overseas/"),
                      ("top-test.html", "/"), ("top-test.html?lang=en#faq", "en/#faq")):
        page = browser.new_page()
        page.goto(BASE + src)
        page.wait_for_timeout(1500)
        got = page.url
        ok = got.split("?")[0].endswith(want) or got.replace("index.html", "").endswith(want)
        check(f"T1 {src} は {want} へ転送する", ok and "test" not in got, got)
        page.close()
    url = BASE + "overseas-test.html"
    html = req.get(url).text() if LIVE else Path(urlparse(url).path).read_text(encoding="utf-8")
    page = browser.new_page(java_script_enabled=False)
    page.goto(url)
    page.wait_for_timeout(1500)
    check("T2 JavaScript が無くても meta refresh で転送し、検索には出さない",
          page.url.replace("index.html", "").endswith("overseas/") and 'name="robots" content="noindex"' in html, page.url)
    page.close()

    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
sys.exit(1 if failed else 0)
