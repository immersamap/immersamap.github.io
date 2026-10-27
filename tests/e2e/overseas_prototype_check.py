"""海外の空中写真の試作（overseas-test.html）の E2E チェック。

テスト設計は docs/test_design/overseas_prototype.md。
配信元（国土地理院・swisstopo・IGN）に実際につないで確かめるので、ネットにつながっている必要がある。

    .venv/bin/python tests/e2e/overseas_prototype_check.py
    .venv/bin/python tests/e2e/overseas_prototype_check.py https://immersamap.github.io/   # 公開サイト
    .venv/bin/python tests/e2e/overseas_prototype_check.py --shots docs/test_results/xxx   # 画面写真も保存
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
# 引数はサイトの一番上（例 https://immersamap.github.io/）。無ければ手元のファイル
BASE = argv[0].rstrip("/") + "/" if argv else ROOT.as_uri() + "/"
URL_JA = BASE + "overseas/index.html"
URL_EN = BASE + "en/overseas/index.html"

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
    """「場所を変える」を開いて、一覧から都市を選ぶ。"""
    page.click("#where")
    page.locator("#place-list").get_by_role("menuitem", name=place, exact=True).click()
    page.wait_for_timeout(500)


def pick(page, layer_id):
    """スライダーを、指定した写真の位置まで動かす。"""
    idx = st(page)["stops"].index(layer_id)
    pick_index(page, idx)


def pick_index(page, idx):
    # 指を離したときと同じく change を送る（input だけでは、止まって 250ms 経つまで写真を読まない）
    page.eval_on_selector("#era", "(el, v) => { el.value = v; el.dispatchEvent(new Event('change')); }", idx)


def wait_tiles(page, timeout=15000):
    """表示中の写真のタイルが、読めるか失敗するまで待つ。"""
    try:
        page.wait_for_function(
            "() => { const t = window.__overseas().tiles; return t.ok + t.err > 0; }", timeout=timeout)
    except Exception:
        # 配信元が1枚も返さないまま時間切れ。ここで止めずに、その時点の数（ok=0）を返して各 check で FAIL にする
        return st(page)["tiles"]
    # 表示中のタイルが全部そろうまで待つ（遅い WMS でも、読みかけの画面写真にしない）
    try:
        page.wait_for_function("() => !window.__overseas().loading", timeout=timeout)
    except Exception:
        pass   # 読み終わらなくても、その時点の数で判定する（判定は各 check が行う）
    page.wait_for_timeout(500)
    return st(page)["tiles"]


def go_to(page, lat, lon, zoom=15):
    page.evaluate(f"window.__overseasMap.setView([{lat}, {lon}], {zoom})")
    page.wait_for_timeout(500)


def new_page(browser, query="", en=False, **kw):
    # 言葉はブラウザの設定で決まるので、指定が無ければ日本語のブラウザとして開く
    kw.setdefault("locale", "ja-JP")
    page = browser.new_page(viewport=kw.pop("viewport", {"width": 1366, "height": 800}), **kw)
    page.errors = []
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    page.goto((URL_EN if en else URL_JA) + query)
    page.wait_for_function("typeof window.__overseas === 'function'")
    page.wait_for_timeout(500)
    return page


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- N1 起動したとき ----
    page = new_page(browser)
    s = st(page)
    check("N1 起動時は日本・日本語・最新", s["country"] == "jp" and s["lang"] == "ja" and s["layer"] == "seamless", str(s))
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

    # ---- N5 国を移ると、移った先にある年のうち近いものを選ぶ（A/B の切り替えはやめた）----
    check("N5 年代の並べ方（A/B）の切り替えは無い", page.locator("[data-mode]").count() == 0)
    go(page, "東京")
    check("N5 フランス 1950〜65年 → 日本は近い 1945〜50年", st(page)["layer"] == "ort_USA10", st(page)["layer"])
    pick(page, "gazo1")
    go(page, "チューリッヒ")
    check("N5 日本 1974〜78年 → スイスは 1974年", st(page)["layer"] == "ch_1974", st(page)["layer"])
    go(page, "ウィーン")
    check("N5 スイス 1974年 → ウィーンは近い 1976年", st(page)["layer"] == "wien_1976", st(page)["layer"])
    # 基準は「利用者が選んだ年」。行き来・対象外を経ても、選んだ年に戻る（UIレビュー4回目 R1）
    go(page, "チューリッヒ")
    pick(page, "ch_1927")
    go(page, "パリ")
    go(page, "チューリッヒ")
    check("N5 スイス 1927年 → パリ → スイスに戻ると 1927年のまま", st(page)["layer"] == "ch_1927", st(page)["layer"])
    go(page, "ウィーン")
    pick(page, "wien_1956")
    go_to(page, 48.2085, 16.62)   # ウィーン市の枠の外
    check("N5 ウィーンの外へ出ると対象外", st(page)["country"] is None, str(st(page)["country"]))
    go(page, "ウィーン")
    check("N5 対象外を経てウィーンに戻ると 1956年のまま", st(page)["layer"] == "wien_1956", st(page)["layer"])
    go(page, "東京")

    # ---- N10 国の範囲（隣の国を取り込まない。UIレビュー4回目 R2）----
    for name, lat, lon, want in [
        ("シュトゥットガルト", 48.78, 9.18, None), ("トリノ", 45.07, 7.69, None), ("ブリュッセル", 50.85, 4.35, "vl"),
        ("アンドラ", 42.51, 1.52, None), ("ミラノ", 45.46, 9.19, None), ("ルクセンブルク", 49.61, 6.13, None),
        ("ストラスブール", 48.58, 7.75, "fr"), ("リール", 50.63, 3.06, "fr"), ("ニース", 43.70, 7.27, "fr"),
        ("ブレスト", 48.39, -4.49, "fr"), ("アジャクシオ", 41.93, 8.74, "fr"), ("エビアン", 46.40, 6.59, "fr"),
        ("ジュネーブ", 46.20, 6.14, "ch"), ("バーゼル", 47.56, 7.59, "ch"), ("ルガーノ", 46.00, 8.95, "ch"),
        ("ローザンヌ", 46.52, 6.63, "ch"), ("サンモリッツ", 46.49, 9.84, "ch")]:
        page.evaluate(f"window.__overseasMap.setView([{lat}, {lon}], 13)")
        got = st(page)["country"]
        check(f"N10 {name} は {want or '対象外'}", got == want, str(got))
    go(page, "東京")

    # ---- N11 足した地域（2026-10-27 5回目）: 判定・写真・古地図 ----
    for name, lat, lon, want in [
        ("バルセロナ", 41.387, 2.170, "cat"), ("ジローナ", 41.98, 2.82, "cat"), ("アンドラ", 42.51, 1.52, None),
        ("ビルバオ", 43.263, -2.935, "eus"), ("アントワープ", 51.219, 4.403, "vl"), ("ヘント", 51.054, 3.717, "vl"),
        ("マーストリヒト", 50.85, 5.69, None), ("リエージュ", 50.63, 5.57, None), ("ケルン", 50.941, 6.958, "nrw"),
        ("ミュンスター", 51.96, 7.63, "nrw"), ("アーヘン", 50.78, 6.08, "nrw"), ("フェンロー", 51.37, 6.17, None),
        ("フランクフルト", 50.11, 8.68, None), ("エッセン", 51.456, 7.012, "ruhr"), ("ベルリン", 52.516, 13.378, "berlin"),
        ("ミュンヘン", 48.137, 11.576, "by"), ("ニュルンベルク", 49.452, 11.077, "by"), ("ザルツブルク", 47.80, 13.04, None),
        ("ウルム", 48.40, 9.99, None), ("デュッセルドルフ", 51.2254, 6.7763, "nrw"), ("ヴッパータール", 51.26, 7.15, "nrw"),
        ("クレーフェルト", 51.33, 6.56, "nrw"), ("デュイスブルク", 51.43, 6.76, "ruhr"), ("ドルトムント", 51.51, 7.47, "ruhr"),
        ("ハム", 51.68, 7.82, "ruhr"), ("ハーゲン", 51.36, 7.47, "ruhr"), ("ヴェーゼル", 51.66, 6.62, "ruhr")]:
        page.evaluate(f"window.__overseasMap.setView([{lat}, {lon}], 13)")
        got = st(page)["country"]
        check(f"N11 {name} は {want or '対象外'}", got == want, str(got))
    for place, lid in [("バルセロナ", "cat_1945"), ("ビルバオ", "eus_1945"), ("アントワープ", "vl_1971"),
                       ("ケルン", "nrw_1951"), ("ベルリン", "ber_1953"), ("ミュンヘン", "by_current")]:
        go(page, place)
        if st(page)["kind"] != "photo":
            page.click("[data-kind=photo]")
        pick(page, lid)
        t = wait_tiles(page, 30000)
        check(f"N11 {place} の写真 {lid} が読める", t["ok"] > 0 and t["err"] == 0 and t["blank"] < t["ok"], str(t))
        shot(page, lid)
    # ルール地方連合の範囲の外（デュッセルドルフ）は NRW 州として、NRW 州の 1952年が出る（UIレビュー5回目 S1）
    go_to(page, 51.2254, 6.7763)
    pick(page, "nrw_1952")
    t = wait_tiles(page, 30000)
    check("N11 デュッセルドルフは NRW 州の 1952年が写る", st(page)["country"] == "nrw" and t["ok"] > 0 and t["blank"] < t["ok"], str(t))
    go(page, "エッセン")
    s = st(page)
    check("N11 ルール地方はルール地方連合の写真に NRW 州の写真を足す（76）",
          len(s["stops"]) == 76 and "ruhr_1926" in s["stops"] and "nrw_1975" in s["stops"], str(len(s["stops"])))

    # ---- N12 古地図（空中写真と古地図の切り替え）----
    go(page, "東京")
    check("N12 古地図の無い日本では切り替えを出さない", page.is_hidden("#kind") and not st(page)["hasMaps"])
    go(page, "ウィーン")
    check("N12 ウィーンにも切り替えを出さない", page.is_hidden("#kind"))
    go(page, "チューリッヒ")
    check("N12 スイスでは切り替えを出す", page.is_visible("#kind") and st(page)["hasMaps"])
    page.click("[data-kind=map]")
    s = st(page)
    check("N12 古地図にすると古地図の年だけになる（スイス 1844〜2021年の178）",
          s["kind"] == "map" and len(s["stops"]) == 178 and s["stops"][0] == "ch_map_1844", str(len(s["stops"])))
    for place, lid, zoom in [("チューリッヒ", "ch_map_1900", None),
                             ("ケルン", "nrw_map_1891", None), ("ミュンヘン", "by_map_1817", 14), ("マドリード", "es_plan_1656", None),
                             ("マドリード", "es_map_minutas", None), ("バルセロナ", "es_map_minutas", None)]:
        go(page, place)
        if zoom:
            page.evaluate(f"window.__overseasMap.setZoom({zoom})")
            page.wait_for_timeout(500)
        pick(page, lid)
        t = wait_tiles(page, 30000)
        check(f"N12 {place} の古地図 {lid} が読める", st(page)["kind"] == "map" and t["ok"] > 0 and t["err"] == 0 and t["blank"] < t["ok"], str(t))
        shot(page, lid)
    # 種類ごとに選んだ年を覚える。古地図の無い国では空中写真を出し、戻ると古地図に戻る
    go(page, "チューリッヒ")
    pick(page, "ch_map_1900")
    go(page, "ケルン")
    check("N12 スイス 1900年の地図 → ケルンは近い 1891〜1912年の地図", st(page)["layer"] == "nrw_map_1891", st(page)["layer"])
    go(page, "パリ")
    check("N12 フランスの古地図は外した（利用条件の確認待ち）。切り替えも出さない",
          not st(page)["hasMaps"] and page.is_hidden("#kind") and st(page)["kind"] == "photo", str(st(page)))
    go(page, "東京")
    # 年は空中写真で最後に選んだ年に近いもの（前の確認で選んだ年による）なので、種類と「日本の写真の層」だけを見る
    s = st(page)
    check("N12 古地図の無い日本では空中写真を出す", s["kind"] == "photo" and s["layer"] in s["stops"] and s["country"] == "jp", str(s))
    go(page, "チューリッヒ")
    check("N12 スイスに戻ると古地図の 1900年に戻る", st(page)["kind"] == "map" and st(page)["layer"] == "ch_map_1900", st(page)["layer"])
    check("N12 古地図の出典を出す", "swisstopo" in page.inner_text("#src-layer") and "の古地図" in page.inner_text("#country-label"))
    # バイエルンの Uraufnahme はズーム16より引くと配信が無い → 地図が無いお知らせ
    go(page, "ミュンヘン")
    page.evaluate("window.__overseasMap.setZoom(14)")
    page.wait_for_timeout(500)
    pick(page, "by_map_1808")
    wait_tiles(page, 30000)
    check("N12 引いた画面で細かい古地図を選ぶと「ズーム16以上に寄ると出ます」（「無い」とは言わない。UIレビュー5回目 S2）",
          "ズーム16以上に寄ると出ます" in page.inner_text("#msg"), page.inner_text("#msg"))
    page.evaluate("window.__overseasMap.setZoom(16)")
    page.wait_for_timeout(500)
    t = wait_tiles(page, 30000)
    check("N12 寄るとバイエルンの細かい古地図（1808〜53年）が出る", t["ok"] > 0 and t["blank"] < t["ok"] and page.is_hidden("#msg"), str(t))
    page.click("[data-kind=photo]")
    go(page, "東京")
    check("N12 スクリプトエラーが無い", not page.errors, "; ".join(page.errors))

    # ---- N6 濃さ ----
    page.eval_on_selector("#opacity", "el => { el.value = 30; el.dispatchEvent(new Event('input')); }")
    op = page.evaluate("() => getComputedStyle(document.querySelector('.leaflet-tile-pane .leaflet-layer:last-child')).opacity")
    check("N6 濃さ 30% が写真に効く", abs(float(op) - 0.3) < 0.01, op)
    check("N6 濃さの表示が 30%", page.inner_text("#opacity-val") == "30%")
    check("N 全体を通してスクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()

    # ---- N8 追加した地域（ウィーン・ルール地方・スペイン）----
    page = new_page(browser)
    go(page, "ウィーン")
    s = st(page)
    check("N8 ウィーンに切り替わる（1938・1956・1976・1992年＋最新）",
          s["country"] == "wien" and s["stops"] == ["wien_1938", "wien_1956", "wien_1976", "wien_1992", "wien_current"], str(s))
    pick(page, "wien_1938")
    t = wait_tiles(page)
    check("N8 ウィーン 1938年のタイルが読める", t["ok"] > 0 and t["err"] == 0 and t["blank"] == 0, str(t))
    check("N8 ウィーンの出典を出す", "Stadt Wien" in page.inner_text("#src-layer"))
    shot(page, "wien_A_1938")

    go(page, "エッセン")
    s = st(page)
    # 5回目で NRW 州の写真を足したので、7世代＋最新の8から 76 になった
    check("N8 エッセンでルール地方に切り替わる（ルール地方連合7世代＋NRW州＋最新）", s["country"] == "ruhr" and len(s["stops"]) == 76, str(len(s["stops"])))
    pick(page, "ruhr_1926")
    t = wait_tiles(page)
    check("N8 ルール地方 1926年のタイルが読める（WMS）", t["ok"] > 0 and t["err"] == 0 and t["blank"] < t["ok"], str(t))
    check("N8 ルール地方の出典を出す", "Regionalverband Ruhr" in page.inner_text("#src-layer"))
    shot(page, "essen_A_1926")

    go(page, "マドリード")
    s = st(page)
    check("N8 マドリードでスペインに切り替わる", s["country"] == "es" and len(s["stops"]) == 5, str(s))
    pick(page, "es_1956")
    t = wait_tiles(page)
    check("N8 スペイン 1956〜57年のタイルが読める（WMS）", t["ok"] > 0 and t["err"] == 0 and t["blank"] < t["ok"], str(t))
    shot(page, "madrid_A_1956")
    pick(page, "es_1973")
    t = wait_tiles(page)
    check("N8 撮影範囲外の空のタイルを「写真なし」と数えてお知らせを出す",
          t["blank"] > 0 and t["blank"] == t["ok"] and "この年の写真がありません" in page.inner_text("#msg"), str(t))

    go(page, "バルセロナ")
    check("N8 バルセロナはフランスではなくカタルーニャ（スペイン）", st(page)["country"] == "cat", st(page)["country"])
    go_to(page, 42.6987, 2.8956)   # ペルピニャン（フランス）
    check("N8 ペルピニャンはフランス", st(page)["country"] == "fr", st(page)["country"])
    go_to(page, 43.3183, -1.9812)  # サン・セバスティアン（スペイン北部）
    check("N8 サン・セバスティアンはバスク州（スペイン）", st(page)["country"] == "eus", st(page)["country"])
    check("N8 スクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()

    # ---- N9 年を選ぶ操作（◀▶・年のチップ・指で動かす間は読まない・今と比べる）----
    page = new_page(browser)
    go(page, "チューリッヒ")
    pick(page, "ch_1946")
    wait_tiles(page)
    page.click("#prev")
    check("N9 ◀ で1つ前の年（1945年）", st(page)["layer"] == "ch_1945", st(page)["layer"])
    page.click("#next")
    page.click("#next")
    check("N9 ▶ で1つ後の年（1947年）", st(page)["layer"] == "ch_1947", st(page)["layer"])
    page.locator("#chips button", has_text="1946年").click()
    check("N9 年のチップで 1946年を選べる", st(page)["layer"] == "ch_1946", st(page)["layer"])
    wait_tiles(page)
    check("N9 前の写真は、新しい写真が読み終わったら外す", st(page)["loadedLayers"] == 1, str(st(page)))

    asked = set()
    page.on("request", lambda r: asked.add(r.url.split("/default/")[1].split("/")[0])
            if "swissimage-product/default/" in r.url else None)
    # 最新（99）から 1947年（20）まで一気になぞる
    page.eval_on_selector("#era", """el => { for (let v = 99; v >= 20; v--) { el.value = v; el.dispatchEvent(new Event('input')); } }""")
    page.wait_for_timeout(2500)
    check("N9 指で動かしている間は途中の年を読まない（止まった年だけ読む）",
          asked == {"1947"} and st(page)["layer"] == "ch_1947", f"{sorted(asked)} {st(page)['layer']}")

    check("N9 スクリプトエラーが無い", not page.errors, "; ".join(page.errors))
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
    check("E1 対象外では場所のボタンに「対象外の場所」と出す", "対象外" in page.inner_text("#where"))
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

    # ---- E4 スマホの幅（縦 390×844）----
    page = new_page(browser, viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    sw = page.evaluate("document.documentElement.scrollWidth")
    box = page.locator("#panel").bounding_box()
    check("E4 スマホで横にはみ出さない", sw <= 390, str(sw))
    check("E4 操作板が画面に収まる", box["x"] >= 0 and box["x"] + box["width"] <= 390 and box["y"] + box["height"] <= 844, str(box))
    check("M1 畳んだシートは低く、地図が画面の8割以上見える", box["y"] >= 844 * 0.8, str(box))
    small = [sel for sel in ["#prev", "#next"]
             if min(page.locator(sel).bounding_box()["width"], page.locator(sel).bounding_box()["height"]) < 44]
    check("M2 ◀▶ は 44px 以上", not small, str(small))
    wb = page.locator("#where").bounding_box()
    zoom = page.locator(".leaflet-control-zoom").bounding_box()
    check("M3 場所のボタンは左上で、国旗と国名を出す",
          wb["y"] < 60 and wb["height"] >= 40 and page.locator("#where svg.flag").count() == 1 and "日本" in page.inner_text("#where"),
          f"{wb} {page.inner_text('#where')}")
    lg = page.locator("#lang").bounding_box()
    check("M3 場所のボタンと言葉のボタンが重ならない", lg["x"] >= wb["x"] + wb["width"], f"{lg} {wb}")
    check("M7 言葉のボタンは右上で、ズームの上にある", lg["y"] < 60 and lg["height"] >= 40 and lg["y"] + lg["height"] <= zoom["y"], f"{lg} {zoom}")
    ob = page.locator(".opacity-control").bounding_box()
    check("M5 濃さの縦スライダーが地図の右側にあり、シートやズームと重ならない",
          ob["x"] + ob["width"] <= 390 and ob["y"] >= zoom["y"] + zoom["height"] and ob["y"] + ob["height"] <= box["y"], f"{ob} {zoom} {box}")
    oc = page.locator("#opacity").bounding_box()
    check("M5 濃さのスライダーは指の効く幅が 40px 以上", oc["width"] >= 40, str(oc))
    ends = page.locator(".ends").bounding_box()
    check("M6 畳んでいても両端の年が見える", page.is_visible("#end-old") and ends["y"] + ends["height"] <= 844, str(ends))
    shot(page, "sp_tokyo")
    # 空中写真・古地図の切り替えが出る地域でも、畳んだシートで地図が8割以上見える（出典が1行のとき）
    go(page, "チューリッヒ")
    kb = page.locator("#kind").bounding_box()
    pb = page.locator("#panel").bounding_box()
    check("M8 切り替えが出ても、畳んだシートは低い（地図が8割以上）", page.is_visible("#kind") and pb["y"] >= 844 * 0.8, f"{pb}")
    check("M8 切り替えのボタンは高さ 28px・幅 44px 以上で、画面内", kb["height"] >= 28 and kb["width"] / 2 >= 44 and kb["x"] + kb["width"] <= 390, str(kb))
    page.click("[data-kind=map]")
    page.wait_for_timeout(300)
    check("M8 指で古地図に切り替えられる", st(page)["kind"] == "map")
    shot(page, "sp_zurich_map")
    page.click("[data-kind=photo]")
    go(page, "東京")
    page.click("#where")
    check("M3 一覧は国ごと（国旗付きで7か国）", page.locator("#place-list .pl-country svg.flag").count() == 7)
    check("M3 一覧で今いる国（日本）に印が付く",
          page.locator("#place-list .pl-group.here").count() == 1 and "日本" in page.inner_text("#place-list .pl-group.here"))
    lb = page.locator("#place-list").bounding_box()
    check("M3 一覧が画面内に収まる", lb["x"] >= 0 and lb["x"] + lb["width"] <= 390 and lb["y"] + lb["height"] <= 844, str(lb))
    shot(page, "sp_place_list")
    page.locator("#place-list").get_by_role("menuitem", name="チューリッヒ").click()
    page.wait_for_timeout(500)
    check("M3 都市を選ぶと一覧が閉じ、ボタンがスイスに変わる",
          page.is_hidden("#place-list") and "スイス" in page.inner_text("#where") and st(page)["country"] == "ch", page.inner_text("#where"))
    page.click("#where")
    page.mouse.click(200, lb["y"] + lb["height"] + 30)   # 一覧のすぐ下の地図
    check("M3 一覧の外を触ると閉じる", page.is_hidden("#place-list"))
    check("M4 畳んでいる間は年のチップを隠す", page.is_hidden("#chips"))
    page.click("#sheet-toggle")
    check("M4 開くと年のチップが出る", page.is_visible("#chips"))
    page.locator("#chips button", has_text="1946年").tap()
    wait_tiles(page)
    check("M4 年のチップを指で叩いて 1946年を選べる", st(page)["layer"] == "ch_1946", st(page)["layer"])
    shot(page, "sp_zurich_open")
    page.close()

    # ---- E5 小さいスマホ（360×640）: 開くと濃さまでたどり着ける ----
    page = new_page(browser, viewport={"width": 360, "height": 640}, is_mobile=True, has_touch=True)
    page.click("#sheet-toggle")
    mb = page.locator("#chips").bounding_box()
    check("E5 小さい画面で開くと、送らなくても年のチップが見える", mb and mb["y"] + mb["height"] <= 640, str(mb))
    shot(page, "sp_small_open")
    ob = page.locator(".opacity-control").bounding_box()
    check("E5 小さい画面でも濃さのスライダーが画面内", ob and 0 <= ob["y"] and ob["y"] + ob["height"] <= 640, str(ob))
    pb = page.locator("#panel").bounding_box()
    check("E5 開いたシートが濃さのスライダーにかぶらない", pb["y"] >= ob["y"] + ob["height"], f"{pb} {ob}")
    page.click("#where")
    page.locator("#place-list").get_by_role("menuitem", name="チューリッヒ").click()
    page.wait_for_timeout(500)
    sb = page.evaluate("(() => { const p = document.getElementById('panel'); return p.scrollHeight > p.clientHeight; })()")
    page.eval_on_selector("#panel", "el => el.scrollTop = el.scrollHeight")
    cb = page.locator("#chips").bounding_box()
    check("E5 シートに入りきらない分はシートの中で送れる（年のチップまで届く）",
          page.is_visible("#chips") and cb["y"] >= pb["y"] and (not sb or cb["y"] + cb["height"] <= 640), f"{cb} {pb}")
    check("E5 横にはみ出さない", page.evaluate("document.documentElement.scrollWidth") <= 360)
    page.close()

    # ---- E6 横画面（844×390）: 操作板は左の帯 ----
    page = new_page(browser, viewport={"width": 844, "height": 390}, is_mobile=True, has_touch=True)
    box = page.locator("#panel").bounding_box()
    check("E6 横画面では操作板が左の幅300pxに収まる", box["x"] == 0 and box["width"] <= 300 and box["height"] <= 390, str(box))
    check("E6 横画面の帯は中身の高さだけ（下の地図を覆わない）", box["height"] < 300, str(box))
    era = page.locator("#era").bounding_box()
    check("E6 横画面でも年のスライダーが画面内", era["y"] + era["height"] <= 390, str(era))
    check("E6 横にはみ出さない", page.evaluate("document.documentElement.scrollWidth") <= 844)
    shot(page, "sp_landscape")
    page.close()

    # ---- L 英語の画面 ----
    JA = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")

    def japanese_left(page):
        """英語のときに、画面に残っている日本語（言葉のボタンの「日本語」は除く）。"""
        text = page.inner_text("#panel") + page.inner_text(".opacity-control")
        return JA.findall(text)

    def follow_lang(page):
        """言葉の切り替えリンクの行き先を開く。file:// ではフォルダに index.html が補われないので、足してから開く（仕様 R1）。"""
        href = page.evaluate("document.getElementById('lang').href")
        path, _, frag = href.partition("#")
        if path.endswith("/"):
            path += "index.html"
        page.goto(path + ("#" + frag if frag else ""))
        page.wait_for_function("typeof window.__overseas === 'function'")
        page.wait_for_timeout(800)
        return href

    # 英語のページは、英語のブラウザでなくても英語。日本語のページは、英語のブラウザでも日本語（自動で切り替えない）
    page = new_page(browser, en=True)
    s = st(page)
    check("L1 英語のページは英語（日本語のブラウザでも）", s["lang"] == "en" and page.evaluate("document.documentElement.lang") == "en", str(s))
    page.close()
    page = new_page(browser, locale="en-US")
    check("L1 日本語のページは英語のブラウザでも日本語（検索エンジンに英語として読まれないように）", st(page)["lang"] == "ja")
    page.close()

    page = new_page(browser, en=True, locale="en-US")
    s = st(page)
    check("L1 場所・年・題名が英語", "Japan" in page.inner_text("#where") and page.inner_text("#era-name") == "Latest"
          and "Historical aerial photos" in page.title(), page.inner_text("#where"))
    check("L1 画面に日本語が残っていない", not japanese_left(page), "".join(japanese_left(page)))
    check("L1 言葉のボタンは「日本語」で、日本語のページへのリンク",
          page.inner_text("#lang") == "日本語" and page.get_attribute("#lang", "hreflang") == "ja", page.get_attribute("#lang", "href"))
    eye = page.evaluate("(() => { const e = document.getElementById('opacity-eye').getBoundingClientRect(),"
                        " c = document.getElementById('opacity-control').getBoundingClientRect();"
                        " return [e.left, e.right, c.left, c.right]; })()")
    check("L1 濃さの見出し（Opacity）が枠からはみ出さない", eye[0] >= eye[2] and eye[1] <= eye[3], str(eye))
    shot(page, "en_tokyo")
    go(page, "Zurich")
    check("L2 一覧の都市も英語（Zurich でスイスへ）", st(page)["country"] == "ch" and "Switzerland" in page.inner_text("#where"))
    pick(page, "ch_1926")
    wait_tiles(page)
    check("L2 写真が無いお知らせも英語", "There is no photo" in page.inner_text("#msg"), page.inner_text("#msg"))
    pick(page, "ch_1946")
    wait_tiles(page)
    check("L2 年の名前は数字だけ（1946）", page.inner_text("#era-name") == "1946", page.inner_text("#era-name"))
    go(page, "Essen")
    check("L2 ルール地方の出典の言葉も英語", "1951–1969:" in page.inner_text("#src-layer"), page.inner_text("#src-layer"))
    go(page, "Madrid")
    pick(page, "es_1973")
    check("L2 期間は 1973–1986 の形", page.inner_text("#era-name") == "1973–1986", page.inner_text("#era-name"))
    check("L2 移動しても日本語が残っていない", not japanese_left(page), "".join(japanese_left(page)))
    page.click("[data-kind=map]")
    check("L2 古地図の切り替えも英語", page.inner_text("#kind") .replace("\n", " ").strip() in ("Photos Old maps", "PhotosOld maps")
          and "Old maps of Spain" in page.inner_text("#country-label"), page.inner_text("#kind"))
    check("L2 古地図に切り替えても日本語が残っていない", not japanese_left(page), "".join(japanese_left(page)))
    page.click("[data-kind=photo]")
    go_to(page, 40.7128, -74.006, 14)
    check("L3 対象外のお知らせも英語", "This prototype covers only" in page.inner_text("#msg")
          and "Outside coverage" in page.inner_text("#where"), page.inner_text("#msg"))
    check("L 英語の画面でスクリプトエラーが無い", not page.errors, "; ".join(page.errors))

    # L4 動かしてから切り替える: 場所・種類・年を引き継いで、もう一方の言葉のページが開く（仕様 R6）
    go(page, "Vienna")
    pick(page, "wien_1956")
    page.evaluate("window.__overseasMap.setView([48.2, 16.36], 14)")
    page.wait_for_timeout(500)
    href = follow_lang(page)
    s = st(page)
    c = page.evaluate("(() => { const m = window.__overseasMap, c = m.getCenter(); return [m.getZoom(), c.lat, c.lng]; })()")
    check("L4 「日本語」で日本語のページへ。動かしたあとの場所・ズーム・年を引き継ぐ",
          s["lang"] == "ja" and s["layer"] == "wien_1956" and c[0] == 14 and abs(c[1] - 48.2) < 0.001 and abs(c[2] - 16.36) < 0.001,
          f"{href} {c} {s['layer']}")
    go(page, "チューリッヒ")
    page.click("[data-kind=map]")
    pick(page, "ch_map_1900")
    href = follow_lang(page)
    s = st(page)
    check("L4 「English」で英語のページへ。古地図の 1900年を引き継ぐ", s["lang"] == "en" and s["kind"] == "map" and s["layer"] == "ch_map_1900", f"{href} {s['layer']}")
    check("L4 切り替えのあとでスクリプトエラーが無い", not page.errors, "; ".join(page.errors))
    page.close()

    # L5 アドレスの # の異常系（仕様 §6・R5）
    for frag, want_country, want_layer, name in [
            ("#abc", "jp", "seamless", "おかしな値は無視して初期表示（東京・最新）"),
            ("#15/95.0/8.5/map/1900", "jp", "seamless", "範囲外の緯度は無視"),
            ("#15/47.37690/8.54170/sketch/1900", "jp", "seamless", "知らない種類は無視"),
            ("#15/47.37690/8.54170/map/1900", "ch", "ch_map_1900", "正しい値なら、その場所・種類・年で開く"),
            ("#15/48.85840/2.29450/map/1880", "fr", "fr_1950", "外したフランスの古地図の共有リンクは、場所を残して空中写真の近い年（1950〜65年）")]:
        page = new_page(browser, query=frag)
        s = st(page)
        check(f"L5 {frag}: {name}", s["country"] == want_country and s["layer"] == want_layer and not page.errors, f"{s['country']} {s['layer']}")
        page.close()

    # L5 書いた # を読み直せる（実装後レビュー P1・P2）
    page = new_page(browser)
    page.evaluate("window.__overseasMap.setZoom(1)")
    page.wait_for_timeout(500)
    check("L5 ズーム1までは引けない（# に書いた値を読み直せる範囲 2〜19）", page.evaluate("window.__overseasMap.getZoom()") == 2)
    page.evaluate("window.__overseasMap.setView([47.3769, 8.5417 + 360], 13)")   # 地球を1周した先のチューリッヒ
    page.wait_for_timeout(600)
    h = page.evaluate("location.hash")
    check("L5 地球を1周しても、国はスイスで、# の経度は -180〜180", st(page)["country"] == "ch" and "/8.54" in h, h)
    page.evaluate("location.hash = '#14/52.51630/13.37770/photo/1953'")
    page.wait_for_timeout(800)
    check("L5 開いたまま別の共有リンク（# だけ違う）を開くと、その場所・年へ動く", st(page)["layer"] == "ber_1953", str(st(page)["layer"]))
    page.close()

    # L7 日英のページは、地図と操作の部分（id の組）が同じ（仕様 §4・R4）。見出し・説明・切り替えリンクは静的に書く
    ids = {}
    for en in (False, True):
        page = new_page(browser, en=en)
        ids[en] = page.evaluate("[...document.querySelectorAll('[id]')].map(e => e.id).sort()")
        html = page.content()
        static_title = re.search(r"<title>([^<]+)</title>", (ROOT / ("en/overseas/index.html" if en else "overseas/index.html")).read_text(encoding="utf-8")).group(1)
        check(f"L7 {'英語' if en else '日本語'}のページ: 描画後の題名が HTML の題名と同じ（実装後レビュー P3）",
              page.title() == static_title.replace("&amp;", "&"), page.title())
        check(f"L7 {'英語' if en else '日本語'}のページ: index・canonical・hreflang（ja・en・x-default）",
              'content="index,follow"' in html and 'rel="canonical"' in html
              and all(f'hreflang="{h}"' in html for h in ("ja", "en", "x-default")))
        page.close()
    check("L7 日英のページの id の組が同じ", ids[False] == ids[True], str(set(ids[False]) ^ set(ids[True])))
    for en, word in ((False, "海外の空中写真・古地図"), (True, "Historical aerial photos")):
        page = browser.new_page(java_script_enabled=False)   # JS が無いので、準備の待ち（new_page）は使えない
        page.goto(URL_EN if en else URL_JA)
        check(f"L7 JavaScript が無くても{'英語' if en else '日本語'}の見出しと切り替えリンクが見える",
              word in page.inner_text("h1") and page.locator("#lang[href]").count() == 1)
        page.close()

    # 英語・スマホ: いちばん長い国名（Austria · Vienna）でも、場所のボタンが言葉のボタンにかからない
    for loc, place, w in [("en-US", "Vienna", 390), ("ja-JP", "ウィーン", 390), ("en-US", "Vienna", 360), ("ja-JP", "ウィーン", 360),
                          ("en-US", "Bilbao", 360), ("ja-JP", "バルセロナ", 360), ("en-US", "Antwerp", 360), ("ja-JP", "ミュンヘン", 360)]:
        page = new_page(browser, en=loc == "en-US", locale=loc, viewport={"width": w, "height": 740}, is_mobile=True, has_touch=True)
        go(page, place)
        wait_tiles(page)
        wb = page.locator("#where").bounding_box()
        lg = page.locator("#lang").bounding_box()
        check(f"L6 {w}px・{loc}: 長い国名でも場所のボタンと言葉のボタンが重ならず、国名も切れない",
              lg["x"] >= wb["x"] + wb["width"] and page.evaluate("document.documentElement.scrollWidth") <= w
              and page.evaluate("(() => { const e = document.getElementById('where-name'); return e.scrollWidth <= e.clientWidth; })()"),
              f"{wb} {lg}")
        if loc == "en-US" and w == 390:
            shot(page, "sp_en_vienna")
        page.close()

    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
sys.exit(1 if failed else 0)
