"""海外の空中写真の試作（overseas-test.html）の E2E チェック。

テスト設計は docs/test_design/overseas_prototype.md。
配信元（国土地理院・swisstopo・IGN）に実際につないで確かめるので、ネットにつながっている必要がある。

    .venv/bin/python tests/e2e/overseas_prototype_check.py
    .venv/bin/python tests/e2e/overseas_prototype_check.py --shots docs/test_results/xxx   # 画面写真も保存
"""
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
URL = argv[0] if argv else (ROOT / "overseas-test.html").as_uri()

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))


def shot(page, name):
    if SHOTS:
        page.screenshot(path=f"{SHOTS}_{name}.jpg", quality=80)


def st(page):
    return page.evaluate("window.__overseas()")


def go(page, place):
    page.get_by_role("button", name=place, exact=True).click()
    page.wait_for_timeout(500)


def pick(page, layer_id):
    """スライダーを、指定した写真の位置まで動かす。"""
    idx = st(page)["stops"].index(layer_id)
    pick_index(page, idx)


def pick_index(page, idx):
    page.eval_on_selector("#era", "(el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }", idx)


def wait_tiles(page, timeout=15000):
    """表示中の写真のタイルが、読めるか失敗するまで待つ。"""
    page.wait_for_function(
        "() => { const t = window.__overseas().tiles; return t.ok + t.err > 0; }", timeout=timeout)
    page.wait_for_timeout(1500)
    return st(page)["tiles"]


def new_page(browser, **kw):
    page = browser.new_page(viewport=kw.pop("viewport", {"width": 1366, "height": 800}), **kw)
    page.errors = []
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    page.goto(URL)
    page.wait_for_function("typeof window.__overseas === 'function'")
    page.wait_for_timeout(500)
    return page


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- N1 起動したとき ----
    page = new_page(browser)
    s = st(page)
    check("N1 起動時は日本・A・最新", s["country"] == "jp" and s["mode"] == "A" and s["layer"] == "seamless", str(s))
    check("N1 日本の年代は9つ", len(s["stops"]) == 9, str(len(s["stops"])))

    # ---- N2 日本の写真が読める ----
    for lid in ["ort_USA10", "gazo1"]:
        pick(page, lid)
        t = wait_tiles(page)
        check(f"N2 日本 {lid} のタイルが読める", t["ok"] > 0 and t["err"] == 0, str(t))
    shot(page, "tokyo_A_1974")

    # ---- N3 スイス ----
    go(page, "チューリッヒ")
    s = st(page)
    check("N3 チューリッヒでスイスに切り替わる", s["country"] == "ch", str(s["country"]))
    check("N3 スイスの年代は100（1926〜2025年＋最新）", len(s["stops"]) == 100, str(len(s["stops"])))
    pick(page, "ch_1946")
    t = wait_tiles(page)
    check("N3 スイス 1946年のタイルが読める", t["ok"] > 0 and t["err"] == 0, str(t))
    check("N3 写真がある時はお知らせを出さない", page.is_hidden("#msg"))
    shot(page, "zurich_A_1946")

    # 写真の無い所に swisstopo が返す白いタイル（1926年のチューリッヒ）
    pick(page, "ch_1926")
    t = wait_tiles(page)
    check("N7 白いタイルを写真の無い所として数える", t["blank"] > 0 and t["blank"] == t["ok"], str(t))
    check("N7 写真が無ければお知らせを出す",
          page.is_visible("#msg") and "この年の写真がありません" in page.inner_text("#msg"))
    hidden = page.evaluate("() => [...document.querySelectorAll('.leaflet-tile-pane .leaflet-layer:last-child img')].every(i => i.style.visibility === 'hidden')")
    check("N7 白いタイルは隠す（地図に白い膜をかけない）", hidden)
    shot(page, "zurich_A_1926_blank")
    pick(page, "ch_1960")
    t = wait_tiles(page)
    check("N7 写真のある年に戻すとお知らせが消える", page.is_hidden("#msg") and t["blank"] < t["ok"], str(t))

    # ---- N4 フランス ----
    go(page, "パリ")
    s = st(page)
    check("N4 パリでフランスに切り替わる", s["country"] == "fr" and s["stops"] == ["fr_1950", "fr_current"], str(s))
    pick(page, "fr_1950")
    t = wait_tiles(page)
    check("N4 フランス 1950〜65年のタイルが読める", t["ok"] > 0 and t["err"] == 0, str(t))
    check("N4 出典に IGN を出す", "IGN" in page.inner_text("#src-layer"))
    shot(page, "paris_A_1950")

    # ---- N5 B: 年代でそろえる ----
    page.click("#mode-b")
    s = st(page)
    check("N5 B は11の年代（1920〜2020年代）", len(s["stops"]) == 11, str(len(s["stops"])))
    check("N5 B フランスは 1950・60・2020年代だけ写真がある",
          [i for i, x in enumerate(s["stops"]) if x] == [3, 4, 10], str(s["stops"]))
    check("N5 A→B で近い年（1950年代）を選び直す", s["index"] == 3, str(s["index"]))
    pick_index(page, 0)
    s = st(page)
    check("N5 写真の無い年代では写真を外す", s["layer"] is None, str(s))
    check("N5 写真の無い年代ではお知らせを出す",
          page.is_visible("#msg") and "ありません" in page.inner_text("#msg"))
    shot(page, "paris_B_1920s_none")

    go(page, "チューリッヒ")
    s = st(page)
    check("N5 B スイスは全年代に写真がある", all(s["stops"]), str(s["stops"]))
    check("N5 B スイス 1940年代は 1949年の写真", s["stops"][2] == "ch_1949", str(s["stops"][2]))
    pick_index(page, 2)
    wait_tiles(page)
    shot(page, "zurich_B_1940s")

    go(page, "東京")
    s = st(page)
    # 年代にかかる写真は全部候補にする（1945〜50年は 1950年代にも、1987〜90年は 1990年代にも入る）
    check("N5 B 日本は 2000・2010年代だけが空く",
          [i for i, x in enumerate(s["stops"]) if not x] == [8, 9], str(s["stops"]))

    # ---- N6 濃さ ----
    page.eval_on_selector("#opacity", "el => { el.value = 30; el.dispatchEvent(new Event('input')); }")
    op = page.evaluate("() => getComputedStyle(document.querySelector('.leaflet-tile-pane .leaflet-layer:last-child')).opacity")
    check("N6 濃さ 30% が写真に効く", abs(float(op) - 0.3) < 0.01, op)
    check("N6 濃さの表示が 30%", page.inner_text("#opacity-val") == "30%")
    check("N 全体を通してスクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()

    # ---- E1 対象外の国 ----
    page = new_page(browser)
    page.evaluate("window.__overseasMap.setView([40.7128, -74.006], 14)")   # ニューヨーク
    page.wait_for_timeout(500)
    s = st(page)
    check("E1 対象外の国では写真を出さない", s["country"] is None and s["layer"] is None, str(s))
    check("E1 対象外の国ではお知らせを出す",
          page.is_visible("#msg") and "日本・スイス・フランス" in page.inner_text("#msg"))
    check("E1 対象外の国ではスライダーを止める", page.is_disabled("#era"))
    shot(page, "out_of_area_newyork")
    go(page, "パリ")
    check("E1 対象の国へ戻ると写真が出る", st(page)["layer"] == "fr_current", str(st(page)))
    check("E1 スクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()

    # ---- E2 配信元が全部失敗する ----
    page = new_page(browser)
    page.route("**/wmts.geo.admin.ch/**", lambda r: r.abort())
    go(page, "チューリッヒ")
    pick(page, "ch_1960")
    t = wait_tiles(page)
    check("E2 注入が効いている（タイルが全部失敗）", t["ok"] == 0 and t["err"] > 0, str(t))
    check("E2 全部失敗したらお知らせを出す",
          page.is_visible("#msg") and "読み込めませんでした" in page.inner_text("#msg"))
    shot(page, "error_all_failed")
    check("E2 画面は止まらない（パリへ移動できる）",
          (go(page, "パリ") or True) and st(page)["country"] == "fr")
    page.close()

    # ---- E3 一部だけ失敗する（撮影範囲外の欠けを想定）----
    page = new_page(browser)
    n = {"i": 0}

    def half(route):
        n["i"] += 1
        if n["i"] % 2:
            route.fulfill(status=404, body="")
        else:
            route.continue_()
    page.route("**/data.geopf.fr/**", half)
    go(page, "パリ")
    pick(page, "fr_1950")
    t = wait_tiles(page)
    check("E3 注入が効いている（一部が失敗）", t["ok"] > 0 and t["err"] > 0, str(t))
    check("E3 一部の失敗ではお知らせを出さない", page.is_hidden("#msg"))
    page.close()

    # ---- E4 スマホの幅 ----
    page = new_page(browser, viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    sw = page.evaluate("document.documentElement.scrollWidth")
    box = page.locator("#panel").bounding_box()
    check("E4 スマホで横にはみ出さない", sw <= 390, str(sw))
    check("E4 操作板が画面に収まる", box["x"] >= 0 and box["x"] + box["width"] <= 390 and box["y"] + box["height"] <= 844, str(box))
    shot(page, "sp_tokyo")
    page.close()

    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
sys.exit(1 if failed else 0)
