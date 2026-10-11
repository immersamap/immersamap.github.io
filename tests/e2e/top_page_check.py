"""トップページ（index.html）の E2E チェック。

ビルドもサーバも無いサイトなので、ファイルを直接ブラウザで開いて確かめる。
公開後のサイトに対しても、URL を渡せば同じ確認ができる。

    python tests/e2e/top_page_check.py                       # ローカルの index.html
    python tests/e2e/top_page_check.py https://immersamap.github.io/
    python tests/e2e/top_page_check.py --shots docs/test_results/xxx   # 画面写真も保存

Playwright（同期API）と Chromium が入った Python で動かす。
"""
import json
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
URL = argv[0] if argv else (ROOT / "index.html").as_uri()

PC_SIZES = [(1920, 1080), (1440, 900), (1366, 768), (1280, 720)]
TABS = ["features", "data", "faq", "about", "support"]

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- PC：スクロール無しで1画面に収まる ----
    for w, h in PC_SIZES:
        page = browser.new_page(viewport={"width": w, "height": h})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL)
        page.wait_for_timeout(1200)
        sh = page.evaluate("document.documentElement.scrollHeight")
        sw = page.evaluate("document.documentElement.scrollWidth")
        check(f"PC {w}x{h} 縦スクロール無し", sh <= h, f"scrollHeight={sh}")
        check(f"PC {w}x{h} 横スクロール無し", sw <= w, f"scrollWidth={sw}")
        # 主要な要素が画面内に見えている
        for sel in ["header .brand", "h1", ".actions .cta.solid", "header .support-btn", ".facts", ".credit"]:
            box = page.locator(sel).first.bounding_box()
            check(f"PC {w}x{h} {sel} が画面内", box and box["y"] >= 0 and box["y"] + box["height"] <= h)
        check(f"PC {w}x{h} JSエラー無し", not errors, "; ".join(errors))
        if SHOTS and (w, h) == (1440, 900):
            page.wait_for_timeout(3000)
            page.screenshot(path=f"{SHOTS}_pc.jpg", type="jpeg", quality=80)
        page.close()

    # ---- 境目のつまみ ----
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(URL)
    page.wait_for_timeout(4000)  # 最初の演出が終わるまで待つ
    x0 = page.evaluate("getComputedStyle(document.getElementById('photo')).getPropertyValue('--x')")
    hb = page.locator("#handle").bounding_box()
    page.mouse.move(hb["x"] + hb["width"] / 2, hb["y"] + hb["height"] / 2)
    page.mouse.down()
    page.mouse.move(1440 * 0.8, hb["y"] + hb["height"] / 2, steps=8)
    page.mouse.up()
    x1 = float(page.evaluate("document.getElementById('photo').style.getPropertyValue('--x')").rstrip("%"))
    check("ドラッグで境目が動く", 75 <= x1 <= 85, f"{x0.strip()} → {x1:.1f}%")
    page.locator("#handle").focus()
    page.keyboard.press("ArrowLeft")
    x2 = float(page.evaluate("document.getElementById('photo').style.getPropertyValue('--x')").rstrip("%"))
    check("左キーで境目が4%動く", abs((x1 - 4) - x2) < 0.01, f"{x1:.1f} → {x2:.1f}")
    page.mouse.move(1440 * 0.99, 450)
    page.mouse.down()
    page.mouse.move(1440 * 1.2, 450)
    page.mouse.up()
    check("写真が2枚とも読み込まれる",
          page.evaluate("[...document.querySelectorAll('.photo img')].every(i => i.complete && i.naturalWidth > 0)"))

    # ---- 詳細パネル：各タブ ----
    for name in TABS:
        page.goto(URL)
        page.wait_for_timeout(300)
        trigger = page.locator(f'[data-open="{name}"]:visible').first
        trigger.click()
        page.wait_for_timeout(200)
        visible = page.locator(f'[data-pane="{name}"]').is_visible()
        others = [t for t in TABS if t != name and page.locator(f'[data-pane="{t}"]').is_visible()]
        check(f"パネル「{name}」が開き、他は隠れる", visible and not others, f"他に表示: {others}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        check(f"パネル「{name}」を Esc で閉じる", not page.evaluate("document.getElementById('panel').open"))

    # 旧アンカー（/#faq など）で該当タブが開く
    for h, name in [("faq", "faq"), ("support", "support"), ("howto", "features")]:
        page.goto(URL.split("#")[0] + "#" + h)
        page.wait_for_timeout(300)
        check(f"#{h} で「{name}」タブが開く", page.locator(f'[data-pane="{name}"]').is_visible())

    # ---- 中身：旧トップの文章・SEO が残っている ----
    page.goto(URL)
    html = page.content()
    check("h1 は1つ", page.locator("h1").count() == 1)
    check("canonical", 'rel="canonical" href="https://immersamap.github.io/"' in html)
    check("OGP 画像", 'og:image" content="https://immersamap.github.io/ogp.png"' in html)
    check("robots は index", 'name="robots" content="index,follow' in html)
    ld = json.loads(page.locator('script[type="application/ld+json"]').inner_text())
    faq_ld = next(g for g in ld["@graph"] if g["@type"] == "FAQPage")["mainEntity"]
    summaries = page.locator("#faq summary").all_inner_texts()
    check("よくある質問は7件", len(summaries) == 7, str(len(summaries)))
    check("構造化データの質問と画面の質問が一致",
          [q["name"] for q in faq_ld] == summaries)
    data_text = page.locator("#data").inner_text()
    for word in ["明治後期", "1896–1909", "1936–1942", "2004–", "今昔マップ on the web", "OpenStreetMap"]:
        check(f"収録データに「{word}」", word in data_text)
    for word in ["重ねて見比べる", "年代を切り替える", "現在地・地名から探す", "使い方は、3ステップ。"]:
        check(f"できることに「{word}」", word in page.locator("#features").inner_text())
    check("運営者名", "ImmersaMap（個人運営）" in page.locator("#about").inner_text())
    check("出典（国土地理院）が画面に出ている", "国土地理院" in page.locator(".credit").inner_text())
    ofuse = page.locator('#support a[href="https://ofuse.me/immersamap"]')
    check("OFUSE のリンク（新しいタブ）", ofuse.count() == 1 and ofuse.get_attribute("target") == "_blank")
    check("地図へのリンク", page.locator('a[href="/map/"]').count() >= 2)
    page.close()

    # ---- スマホ ----
    page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(URL)
    page.wait_for_timeout(1200)
    sw = page.evaluate("document.documentElement.scrollWidth")
    check("スマホ 横スクロール無し", sw <= 390, f"scrollWidth={sw}")
    hb = page.locator("header .support-btn")
    check("スマホ 上部に「応援」ボタンが見える", hb.is_visible())
    nav_h = page.locator("header").bounding_box()["height"]
    check("スマホ ヘッダーが1行に収まる", nav_h < 90, f"height={nav_h:.0f}")
    handle = page.locator("#handle").bounding_box()
    copy = page.locator(".copy").bounding_box()
    check("スマホ つまみが本文に重ならない", handle["y"] + handle["height"] < copy["y"])
    if SHOTS:
        page.wait_for_timeout(3000)
        page.screenshot(path=f"{SHOTS}_sp.jpg", full_page=True, type="jpeg", quality=80)
    hb.click()
    page.wait_for_timeout(300)
    check("スマホ 応援タブが開く", page.locator('[data-pane="support"]').is_visible())
    tabs_h = page.locator(".tabs").bounding_box()["height"]
    check("スマホ タブが1行", tabs_h < 50, f"height={tabs_h:.0f}")
    if SHOTS:
        page.screenshot(path=f"{SHOTS}_sp_support.jpg", type="jpeg", quality=80)
    check("スマホ JSエラー無し", not errors, "; ".join(errors))
    page.close()

    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
sys.exit(1 if failed else 0)
