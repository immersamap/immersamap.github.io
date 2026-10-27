  // 海外の空中写真・古地図（/overseas/・/en/overseas/ で共有。仕様: docs/spec/release_overseas_en.md）
  // ============ 配信元（調査結果: docs/spec/overseas_sources_research.md の 6・7 章） ============
  const GSI = 'https://cyberjapandata.gsi.go.jp/xyz/';
  const SWISS = (year) => `https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage-product/default/${year}/3857/{z}/{x}/{y}.jpeg`;
  const SWISS_1946 = 'https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage-product_1946/default/1946/3857/{z}/{x}/{y}.jpeg';
  const SWISS_MAP = (year) => `https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.zeitreihen/default/${year}1231/3857/{z}/{x}/{y}.png`;
  const IGN = (layer, fmt, tms = 'PM') => `https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${layer}&STYLE=normal&TILEMATRIXSET=${tms}&FORMAT=${fmt}&TILEMATRIX={z}&TILECOL={x}&TILEROW={y}`;
  // ウィーンは {y}/{x} の順。昔の写真は grau（白黒）、最新は farbe（カラー）だけがある
  const WIEN = (layer, style) => `https://mapsneu.wien.gv.at/wmts/${layer}/${style}/google3857/{z}/{y}/{x}.jpeg`;
  const VL = (service, layer) => `https://geo.api.vlaanderen.be/${service}/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=${layer}&STYLE=&TILEMATRIXSET=GoogleMapsVL&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/png`;
  // WMS は { url, layers } で持つ
  const WMS = (url) => (layers) => ({ url, layers });
  const RUHR = (year) => ({ url:`https://geodaten.metropoleruhr.de/lubi/lubi_${year}`, layers:`lubi_${year}` });
  const ES_HIST = WMS('https://www.ign.es/wms/pnoa-historico');
  const ICGC = WMS('https://geoserveis.icgc.cat/servei/catalunya/orto-territorial/wms');
  const EUS = WMS('https://www.geo.euskadi.eus/WMS_ORTOARGAZKIAK');
  const NRW_DOP = WMS('https://www.wms.nrw.de/geobasis/wms_nw_hist_dop');
  const BY_HIST = WMS('https://geoservices.bayern.de/od/wms/hist/v1/histkarten');

  // 言葉で変わるものは [日本語, 英語] の組で持つ。tr() で今の言葉のほうを取り出す
  const a = (href, text) => `<a href="${href}" target="_blank" rel="noopener">${text}</a>`;
  const SRC_GSI   = [a('https://maps.gsi.go.jp/', '国土地理院'), a('https://maps.gsi.go.jp/', 'GSI Japan')];
  const SRC_SWISS = '© ' + a('https://www.swisstopo.admin.ch/', 'swisstopo');
  const SRC_IGN   = a('https://www.ign.fr/', 'IGN') + ' (Licence Ouverte 2.0)';
  const SRC_WIEN  = a('https://data.wien.gv.at/', 'Stadt Wien – data.wien.gv.at') + ' (CC BY 4.0)';
  const RUHR_SRC  = a('https://www.rvr.ruhr/', 'Regionalverband Ruhr') + ' (dl-de/by-2-0)';
  // NRW の 1951〜1969年の写真は、撮影者・所有者・資料番号まで書くことが条件（dl-de/by-2-0）。1970年以降は dl-de/zero-2-0
  const NRW_SRC   = a('https://www.bezreg-koeln.nrw.de/geobasis-nrw', 'Geobasis NRW') + ' (dl-de/zero-2-0)';
  const NRW_OLD   = 'Geobasis NRW, Hansa Luftbild AG, Landesarchiv NRW, RW 0230 (dl-de/by-2-0)';
  const SRC_NRW   = [`${NRW_SRC}。1951〜1969年は ${NRW_OLD}`, `${NRW_SRC}; 1951–1969: ${NRW_OLD}`];
  const SRC_RUHR  = [`${RUHR_SRC}、${NRW_SRC}。1951〜1969年は ${NRW_OLD}`, `${RUHR_SRC}; ${NRW_SRC}; 1951–1969: ${NRW_OLD}`];
  const SRC_ES    = 'PNOA © ' + a('https://www.ign.es/', 'IGN España') + ' (scne.es, CC BY 4.0)';
  const SRC_ES_MAP = '© ' + a('https://www.ign.es/', 'Instituto Geográfico Nacional de España') + ' (CC BY 4.0)';
  const SRC_ICGC  = a('https://www.icgc.cat/', 'Institut Cartogràfic i Geològic de Catalunya') + ' (CC BY 4.0)';
  const SRC_EUS   = a('https://www.geo.euskadi.eus/', 'Eusko Jaurlaritza / Gobierno Vasco. geoEuskadi');
  const SRC_VL    = a('https://www.vlaanderen.be/digitaal-vlaanderen', 'Digitaal Vlaanderen');
  const SRC_BER   = a('https://gdi.berlin.de/', 'Geoportal Berlin') + ' (dl-de/zero-2-0)';
  const SRC_BY    = a('https://www.ldbv.bayern.de/', 'Bayerische Vermessungsverwaltung') + ' (CC BY 4.0)';

  const BW = ['白黒', 'Black & white'];
  const COLOR = ['カラー', 'Color'];
  const PATCHY = ['年ごとに写る範囲が違う', 'Coverage varies by year'];

  // 国（地域）の範囲は [緯度, 経度] の多角形の組。四角は box() で多角形にする
  const box = ([[s, w], [n, e]]) => [[s, w], [n, w], [n, e], [s, e]];
  // 四角だと隣の国まで入るところは、境をおおまかになぞる（国境のすぐ近くは粗い）
  const CH_AREA = [[
    [47.81,8.60],[47.70,9.55],[47.25,9.65],[46.95,10.50],[46.60,10.50],[46.20,10.15],[46.00,9.05],[45.82,9.00],
    [46.05,8.45],[45.90,7.00],[46.10,6.85],[46.40,6.93],[46.45,6.60],[46.40,6.35],[46.30,6.24],[46.15,6.20],[46.13,5.95],[46.50,6.10],[47.00,6.75],
    [47.50,7.00],[47.60,7.60],[47.62,8.20],
  ]];
  const FR_AREA = [[
    [51.10,2.50],[50.75,3.15],[50.30,4.00],[50.17,4.85],[49.55,5.80],[49.47,6.37],[49.10,6.90],[48.97,8.23],
    [47.60,7.55],[47.50,7.00],[47.00,6.75],[46.50,6.10],[46.13,5.95],[46.15,6.20],[46.30,6.24],[46.40,6.35],[46.45,6.60],[46.40,6.93],[46.10,6.85],
    [45.85,6.95],[45.10,7.05],[44.30,6.95],[43.78,7.53],[43.20,7.40],[42.70,3.40],[42.43,3.17],[42.50,1.75],
    [42.80,0.70],[43.00,-0.50],[43.35,-1.78],[43.40,-2.20],[46.00,-2.60],[47.50,-5.20],[48.90,-5.20],
    [49.80,-1.95],[50.20,1.50],[51.10,1.80],
  ], box([[41.3,8.5],[43.1,9.6]])];   // 後ろはコルシカ島
  const NRW_AREA = [[
    [51.85,6.05],[52.05,6.72],[52.22,7.05],[52.35,7.55],[52.15,8.00],[52.30,8.40],[52.53,8.65],[52.40,9.10],[52.10,9.45],
    [51.60,9.45],[51.35,9.15],[51.10,8.70],[50.85,8.15],[50.65,7.60],[50.60,7.20],[50.45,6.95],[50.32,6.45],[50.60,6.00],
    [50.76,6.02],[51.00,5.90],[51.25,6.10],[51.40,6.22],[51.65,6.05],
  ]];
  const BY_AREA = [[
    [50.10,8.98],[50.35,9.75],[50.56,10.45],[50.45,11.30],[50.40,11.90],[50.25,12.25],[49.95,12.45],[49.60,12.45],
    [49.30,12.75],[49.00,13.15],[48.75,13.50],[48.55,13.84],[48.57,13.43],[48.20,12.75],[47.95,12.95],[47.70,13.05],
    [47.53,13.00],[47.70,12.50],[47.68,12.18],[47.50,11.60],[47.40,11.00],[47.27,10.20],[47.55,9.97],[47.55,9.68],
    [47.80,10.05],[48.40,10.10],[48.70,10.40],[49.00,10.25],[49.30,10.10],[49.55,9.90],[49.65,9.40],[49.80,9.10],[49.95,9.05],
  ]];
  // ルール地方連合の配信範囲（デュイスブルク〜ハム、ヴェーゼル〜ハーゲン）。デュッセルドルフ・ヴッパータールは入れない（NRW州として扱う）
  const RUHR_AREA = [[
    [51.84,6.50],[51.85,6.95],[51.80,7.45],[51.78,7.95],[51.55,8.00],[51.45,7.75],[51.25,7.45],[51.29,7.27],[51.37,7.20],
    [51.36,6.92],[51.33,6.70],[51.45,6.55],[51.56,6.40],
  ]];
  // フランドル（ベルギー北部）。南はおおまかな言語境界、北はオランダとの境
  const VL_AREA = [[
    [51.09,2.54],[51.37,3.37],[51.27,3.90],[51.38,4.40],[51.50,4.80],[51.45,5.10],[51.25,5.25],[51.27,5.60],[51.15,5.84],
    [50.90,5.68],[50.75,5.70],[50.75,5.20],[50.70,4.40],[50.78,3.35],[50.72,2.90],[50.95,2.55],
  ]];
  // カタルーニャ。アンドラとフランス（ペルピニャン）を取らない
  const CAT_AREA = [[
    [40.52,0.52],[40.80,0.25],[41.30,0.35],[41.70,0.40],[42.10,0.65],[42.50,0.70],[42.85,0.75],[42.70,1.40],[42.43,1.44],
    [42.43,1.78],[42.50,1.95],[42.45,2.60],[42.45,3.20],[42.00,3.35],[41.60,3.00],[41.20,2.30],[41.00,1.50],[40.60,0.90],
  ]];

  // 年の名前は日本語だけ持ち、英語は start・end から作る（eraName）
  const range = (from, to) => Array.from({ length:to - from + 1 }, (_, i) => from + i);
  const SWISS_YEARS = [1926, 1927, ...range(1929, 2025)];
  // NRW の昔の写真（1965年は配信に無い）。ルール地方にも使う
  const NRW_YEARS = [...range(1951, 1964), ...range(1966, 2024)];
  const nrwPhoto = (y) => ({ id:'nrw_'+y, name:y+'年', sub:y < 1970 ? ['白黒・NRW州（年ごとに写る範囲が違う）', 'Black & white, NRW (coverage varies by year)'] : ['NRW州（年ごとに写る範囲が違う）', 'NRW (coverage varies by year)'],
    start:y, wms:NRW_DOP('nw_hist_dop_'+y), maxNativeZoom:19, blankBytes:1000 });
  const NRW_LATEST = { id:'nrw_current', name:'最新', sub:['NRW州のカラー写真', 'Color, state of NRW'], start:2026,
    wms:{ url:'https://www.wms.nrw.de/geobasis/wms_nw_dop', layers:'nw_dop_rgb' }, maxNativeZoom:19 };
  const NRW_MAPS = [
    { id:'nrw_map_1836', name:'1836〜50年', sub:['プロイセンの最初の地形図（Uraufnahme）', 'First Prussian survey (Uraufnahme)'], start:1836, end:1850,
      wms:WMS('https://www.wms.nrw.de/geobasis/wms_nw_uraufnahme')('nw_uraufnahme_rw'), maxNativeZoom:19, blankBytes:1000 },
    { id:'nrw_map_1891', name:'1891〜1912年', sub:['地形図（Neuaufnahme）', 'Topographic map (Neuaufnahme)'], start:1891, end:1912,
      wms:WMS('https://www.wms.nrw.de/geobasis/wms_nw_neuaufnahme')('nw_neuaufnahme'), maxNativeZoom:19, blankBytes:1000 },
    { id:'nrw_map_1936', name:'1936〜45年', sub:['地形図 1:25,000', 'Topographic map 1:25,000'], start:1936, end:1945,
      wms:WMS('https://www.wms.nrw.de/geobasis/wms_nw_tk25_1936-1945')('nw_tk25_1936-1945'), maxNativeZoom:19, blankBytes:1000 },
  ];
  // スペイン全国の古地図（カタルーニャ・バスクにも使う）と、マドリードの市街図。
  // 地形図 1:50,000 の初版（primera-edicion-mtn の MTN50）は、どの場所でも 4〜12% のタイルで配信元が 500 を返し、穴が開くので入れていない
  const ES_MAPS = [
    { id:'es_map_minutas', name:'1870〜1950年', sub:['地形図の下書き（Minutas）', 'Survey drafts (Minutas)'], start:1870, end:1950,
      wms:WMS('https://www.ign.es/wms/minutas-cartograficas')('Minutas'), maxNativeZoom:18, blankBytes:1000 },
  ];
  const MADRID_PLAN = (layer, year, ja, en) => ({ id:'es_plan_'+year, name:year+'年', sub:[`マドリード中心部だけ・${ja}`, `Central Madrid only, ${en}`],
    start:year, wms:WMS('https://www.ign.es/wms/planos')(layer), maxNativeZoom:19, blankBytes:1000 });
  const MADRID_PLANS = [
    MADRID_PLAN('mancelliMadrid', 1622, 'マンチェッリの図', 'Mancelli plan'),
    MADRID_PLAN('texeira', 1656, 'テイシェイラの図', 'Texeira plan'),
    MADRID_PLAN('chalmadrierMadrid', 1761, 'シャルマンドリエの図', 'Chalmandrier plan'),
    MADRID_PLAN('espinosaMadrid', 1769, 'エスピノサの図', 'Espinosa plan'),
    MADRID_PLAN('geometricoMadrid', 1785, 'トマス・ロペスの図', 'Tomás López plan'),
    MADRID_PLAN('madozMadrid', 1848, 'マドス・コエリョの図', 'Madoz and Coello plan'),
    MADRID_PLAN('ibanezMadrid', 1875, 'イバニェス・イベロの地籍図', 'Ibáñez Íbero cadastral plan'),
    MADRID_PLAN('facundoMadrid', 1900, 'ファクンド・カニャダの図', 'Facundo Cañada plan'),
    MADRID_PLAN('nunezMadrid', 1910, 'ヌニェス・グラネスの図', 'Núñez Granés plan'),
    MADRID_PLAN('ayuntamientoMadrid', 1929, '市の地籍図', 'City cadastral plan'),
    { ...MADRID_PLAN('parcelarioMadrid', 1940, '地籍図', 'Cadastral plan'), id:'es_plan_1940', name:'1940〜60年', end:1960 },
  ];
  const byStart = (list) => [...list].sort((x, y) => x.start - y.start);

  // 国（地域）の判定は上から順に見る。範囲が重なるもの（小さい地域）を、大きい国より先に置く
  // photos: 空中写真、maps: 古地図（無い地域は持たない）
  const COUNTRIES = [
    {
      id:'ch', name:['スイス', 'Switzerland'], flag:'ch', area:CH_AREA,
      photos:[
        ...SWISS_YEARS.map(y => y === 1946
          // 1946年は時系列の層だと低いズームが白くなるので、全域をつないだ専用の層を使う
          ? { id:'ch_1946', name:'1946年', sub:['白黒・ほぼ全域', 'Black & white, almost nationwide'], start:1946, tile:SWISS_1946, maxNativeZoom:17, blankBytes:1000 }
          : { id:'ch_'+y, name:y+'年', sub:PATCHY, start:y, tile:SWISS(y), maxNativeZoom:20, blankBytes:1000 }),
        { id:'ch_current', name:'最新', sub:'SWISSIMAGE', start:2026, tile:SWISS('current'), maxNativeZoom:20, blankBytes:1000 },
      ],
      // 地図の時間旅行（Zeitreihen）: 1844〜2021年の毎年。古い年ほど写る範囲が狭い
      maps:range(1844, 2021).map(y => ({ id:'ch_map_'+y, name:y+'年', sub:['地形図（年ごとに写る範囲が違う）', 'Topographic map (coverage varies by year)'],
        start:y, tile:SWISS_MAP(y), maxNativeZoom:18, blankBytes:1000 })),
      src:SRC_SWISS, mapSrc:SRC_SWISS,
    },
    {
      // 配信はウィーン市内だけ（市外は 404）
      id:'wien', name:['オーストリア・ウィーン', 'Austria · Vienna'], flag:'at', area:[box([[48.118,16.182],[48.323,16.578]])],
      photos:[
        { id:'wien_1938', name:'1938年', sub:BW, start:1938, tile:WIEN('lb1938','grau'), maxNativeZoom:19 },
        { id:'wien_1956', name:'1956年', sub:BW, start:1956, tile:WIEN('lb1956','grau'), maxNativeZoom:19 },
        { id:'wien_1976', name:'1976年', sub:BW, start:1976, tile:WIEN('lb1976','grau'), maxNativeZoom:19 },
        { id:'wien_1992', name:'1992年', sub:BW, start:1992, tile:WIEN('lb1992','grau'), maxNativeZoom:19 },
        { id:'wien_current', name:'最新', sub:COLOR, start:2026, tile:WIEN('lb','farbe'), maxNativeZoom:19 },
      ],
      src:SRC_WIEN,
    },
    {
      // ルール地方連合の写真に、NRW州の写真（同じ年はルール地方連合を使う）を足す。
      // 撮影範囲の外は透明な小さい PNG が返るので、白いタイルと同じく「写真なし」と数える
      id:'ruhr', name:['ドイツ・ルール地方', 'Germany · Ruhr'], flag:'de', area:RUHR_AREA,
      photos:byStart([
        ...[1926,1934,1952,1963,1969,1990,1998].map(y =>
          ({ id:'ruhr_'+y, name:y+'年', sub:y < 1990 ? ['白黒・ルール地方連合', 'Black & white, Ruhr Regional Association'] : ['カラー・ルール地方連合', 'Color, Ruhr Regional Association'],
             start:y, wms:RUHR(y), maxNativeZoom:19, blankBytes:1000 })),
        ...NRW_YEARS.filter(y => ![1952,1963,1969,1990,1998].includes(y)).map(nrwPhoto),
        NRW_LATEST,
      ]),
      maps:NRW_MAPS,
      src:SRC_RUHR, mapSrc:NRW_SRC,
    },
    {
      id:'berlin', name:['ドイツ・ベルリン', 'Germany · Berlin'], flag:'de', area:[box([[52.33,13.08],[52.68,13.77]])],
      photos:[
        { id:'ber_1953', name:'1953年', sub:['白黒・解像度は粗め', 'Black & white, low resolution'], start:1953,
          wms:WMS('https://gdi.berlin.de/services/wms/luftbild_1953_22')('c_luftbilder_1953_22_raster'), maxNativeZoom:18, blankBytes:2000 },
        { id:'ber_current', name:'最新', sub:['2024年・カラー', '2024, color'], start:2026,
          wms:WMS('https://gdi.berlin.de/services/wms/truedop_2024')('truedop_2024'), maxNativeZoom:19 },
      ],
      src:SRC_BER,
    },
    {
      // バイエルンの昔の空中写真は公開の配信が無い。最新の写真と古地図を出す
      id:'by', name:['ドイツ・バイエルン', 'Germany · Bavaria'], flag:'de', area:BY_AREA,
      photos:[
        { id:'by_current', name:'最新', sub:['カラー', 'Color'], start:2026,
          wms:WMS('https://geoservices.bayern.de/od/wms/dop/v1/dop20')('by_dop20c'), maxNativeZoom:19 },
      ],
      maps:[
        // Uraufnahme は土地ごとの細かい図で、ズーム16以上でだけ配信される
        { id:'by_map_1808', name:'1808〜53年', sub:['土地の図（Uraufnahme）', 'Cadastral map (Uraufnahme)'], start:1808, end:1853,
          wms:BY_HIST('by_uraufnahme'), maxNativeZoom:19, blankBytes:1000, minZoom:16 },
        { id:'by_map_1812', name:'1812〜67年', sub:['地形図 1:50,000（Topographischer Atlas）', 'Topographic atlas 1:50,000'], start:1812, end:1867,
          wms:BY_HIST('by_topoatlas'), maxNativeZoom:17, blankBytes:1000 },
        { id:'by_map_1817', name:'1817〜72年', sub:['手描きの地形図 1:25,000（Positionsblätter）', 'Hand-drawn map 1:25,000 (Positionsblätter)'], start:1817, end:1872,
          wms:BY_HIST('by_positionsblatt'), maxNativeZoom:18, blankBytes:1000 },
      ],
      src:SRC_BY, mapSrc:SRC_BY,
    },
    {
      id:'nrw', name:['ドイツ・NRW州', 'Germany · NRW'], flag:'de', area:NRW_AREA,
      photos:[...NRW_YEARS.map(nrwPhoto), NRW_LATEST],
      maps:NRW_MAPS,
      src:SRC_NRW, mapSrc:NRW_SRC,
    },
    {
      id:'vl', name:['ベルギー・フランドル', 'Belgium · Flanders'], flag:'be', area:VL_AREA,
      photos:[
        { id:'vl_1971', name:'1971年', sub:BW, start:1971, tile:VL('OKZ', 'okzpan71vl'), maxNativeZoom:21 },
        { id:'vl_1979', name:'1979〜90年', sub:COLOR, start:1979, end:1990, tile:VL('OKZ', 'okzrgb79_90vl'), maxNativeZoom:21 },
        { id:'vl_current', name:'最新', sub:COLOR, start:2026, tile:VL('OMWRGBMRVL', 'omwrgbmrvl'), maxNativeZoom:21 },
      ],
      src:SRC_VL,
    },
    {
      id:'fr', name:['フランス', 'France'], flag:'fr', area:FR_AREA,
      photos:[
        { id:'fr_1950', name:'1950〜65年', sub:['白黒の空中写真', 'Black & white aerial photos'], start:1950, end:1965, tile:IGN('ORTHOIMAGERY.ORTHOPHOTOS.1950-1965','image/png'), maxNativeZoom:18 },
        { id:'fr_current', name:'最新', sub:'BD ORTHO', start:2026, tile:IGN('ORTHOIMAGERY.ORTHOPHOTOS','image/jpeg'), maxNativeZoom:19 },
      ],
      // 古地図（カッシーニ図・参謀本部図）は利用条件を確かめられるまで外す（2026-10-27 オーナー判断。調査 7.1）
      src:SRC_IGN,
    },
    {
      // カタルーニャはスペインより先に判定する（州の写真のほうが年代が厚い）
      id:'cat', name:['スペイン・カタルーニャ', 'Spain · Catalonia'], flag:'es', area:CAT_AREA,
      photos:[
        ...[['1945-1946',1945,1946],['1956-1957',1956,1957],['1970-1977',1970,1977],['1983-1989',1983,1989],['1990',1990],['1994-1997',1994,1997],['1998',1998]]
          .map(([k, s, e]) => ({ id:'cat_'+s, name:e ? `${s}〜${String(e).slice(2)}年` : s+'年', sub:BW, start:s, end:e,
            wms:ICGC('ortofoto_blanc_i_negre_'+k), maxNativeZoom:19, blankBytes:1000 })),
        { id:'cat_1993', name:'1993年', sub:['カラー・解像度は粗め', 'Color, low resolution'], start:1993, wms:ICGC('ortofoto_color_1993'), maxNativeZoom:16, blankBytes:1000 },
        ...[['2000-2003',2000,2003],['2004-2005',2004,2005],['2006-2007',2006,2007],...range(2008, 2025).map(y => [String(y), y])]
          .map(([k, s, e]) => ({ id:'cat_'+s, name:e ? `${s}〜${String(e).slice(2)}年` : s+'年', sub:COLOR, start:s, end:e,
            wms:ICGC('ortofoto_color_'+k), maxNativeZoom:19, blankBytes:1000 })),
        { id:'cat_current', name:'最新', sub:COLOR, start:2026, wms:ICGC('ortofoto_color_vigent'), maxNativeZoom:19 },
      ].sort((x, y) => x.start - y.start),
      maps:ES_MAPS,
      src:SRC_ICGC, mapSrc:SRC_ES_MAP,
    },
    {
      // バスク州はスペインより先に判定する
      id:'eus', name:['スペイン・バスク州', 'Spain · Basque Country'], flag:'es', area:[box([[42.47,-3.45],[43.46,-1.73]])],
      photos:[
        { id:'eus_1945', name:'1945〜46年', sub:['白黒・米軍の撮影', 'Black & white, US Army survey'], start:1945, end:1946, wms:EUS('ORTO_1945_46_AMERICANO'), maxNativeZoom:19, blankBytes:1000 },
        { id:'eus_1956', name:'1956〜57年', sub:['白黒・米軍の撮影', 'Black & white, US Army survey'], start:1956, end:1957, wms:EUS('ORTO_1956_57_AMERICANO'), maxNativeZoom:19, blankBytes:1000 },
        { id:'eus_1977', name:'1977〜78年', sub:BW, start:1977, end:1978, wms:EUS('ORTO_INTERMINISTERIAL_1977_78'), maxNativeZoom:19, blankBytes:1000 },
        { id:'eus_1984', name:'1984〜85年', sub:BW, start:1984, end:1985, wms:EUS('ORTO_1984_85'), maxNativeZoom:19, blankBytes:1000 },
        ...[1989,1991,1995,2001,2002,2004,2005,...range(2006, 2025)].map(y =>
          ({ id:'eus_'+y, name:y+'年', sub:y < 2001 ? BW : COLOR, start:y, wms:EUS('ORTO_'+y), maxNativeZoom:19, blankBytes:1000 })),
        { id:'eus_current', name:'最新', sub:COLOR, start:2026, wms:EUS('ORTO_EGUNERATUENA_MAS_ACTUALIZADA'), maxNativeZoom:19 },
      ],
      maps:ES_MAPS,
      src:SRC_EUS, mapSrc:SRC_ES_MAP,
    },
    {
      // 枠2つで本土・バレアレスを覆う（北側はピレネーより西だけにして、フランス南部を取らない）
      id:'es', name:['スペイン', 'Spain'], flag:'es', area:[box([[35.9,-9.4],[42.3,4.4]]), box([[42.3,-9.4],[43.8,-1.8]])],
      photos:[
        { id:'es_1956', name:'1956〜57年', sub:['白黒・米軍の撮影・全国', 'Black & white, US Army survey, nationwide'], start:1956, end:1957, wms:ES_HIST('AMS_1956-1957'), maxNativeZoom:18, blankBytes:1000 },
        { id:'es_1973', name:'1973〜86年', sub:['一部の地域だけ', 'Some areas only'], start:1973, end:1986, wms:ES_HIST('Interministerial_1973-1986'), maxNativeZoom:18, blankBytes:1000 },
        { id:'es_1981', name:'1981〜86年', sub:['一部の地域だけ', 'Some areas only'], start:1981, end:1986, wms:ES_HIST('Nacional_1981-1986'), maxNativeZoom:18, blankBytes:1000 },
        { id:'es_1997', name:'1997〜2003年', sub:['カラー・全国', 'Color, nationwide'], start:1997, end:2003, wms:ES_HIST('SIGPAC'), maxNativeZoom:19, blankBytes:1000 },
        { id:'es_current', name:'最新', sub:'PNOA', start:2026,
          wms:{ url:'https://www.ign.es/wms-inspire/pnoa-ma', layers:'OI.OrthoimageCoverage' }, maxNativeZoom:19 },
      ],
      maps:byStart([...ES_MAPS, ...MADRID_PLANS]),
      src:SRC_ES, mapSrc:SRC_ES_MAP,
    },
    {
      id:'jp', name:['日本', 'Japan'], flag:'jp', area:[box([[20,122],[46,154]])],
      photos:[
        { id:'ort_1928',   name:'1928年頃',     sub:['大阪のみ', 'Osaka only'],             start:1928, circa:true, tile:GSI+'ort_1928/{z}/{x}/{y}.png',   maxNativeZoom:18 },
        { id:'ort_riku10', name:'1936〜42年',   sub:['東京・大阪', 'Tokyo and Osaka'],       start:1936, end:1942, tile:GSI+'ort_riku10/{z}/{x}/{y}.png', maxNativeZoom:17 },
        { id:'ort_USA10',  name:'1945〜50年',   sub:['主要都市', 'Major cities'],            start:1945, end:1950, tile:GSI+'ort_USA10/{z}/{x}/{y}.png',  maxNativeZoom:17 },
        { id:'ort_old10',  name:'1961〜69年',   sub:['全国', 'Nationwide'],                  start:1961, end:1969, tile:GSI+'ort_old10/{z}/{x}/{y}.png',  maxNativeZoom:17 },
        { id:'gazo1',      name:'1974〜78年',   sub:['全国', 'Nationwide'],                  start:1974, end:1978, tile:GSI+'gazo1/{z}/{x}/{y}.jpg',      maxNativeZoom:17 },
        { id:'gazo2',      name:'1979〜83年',   sub:['大都市圏', 'Major metropolitan areas'], start:1979, end:1983, tile:GSI+'gazo2/{z}/{x}/{y}.jpg',      maxNativeZoom:17 },
        { id:'gazo3',      name:'1984〜86年',   sub:['大都市圏', 'Major metropolitan areas'], start:1984, end:1986, tile:GSI+'gazo3/{z}/{x}/{y}.jpg',      maxNativeZoom:17 },
        { id:'gazo4',      name:'1987〜90年',   sub:['大都市圏', 'Major metropolitan areas'], start:1987, end:1990, tile:GSI+'gazo4/{z}/{x}/{y}.jpg',      maxNativeZoom:17 },
        { id:'seamless',   name:'最新',         sub:['2004年〜現在', '2004 to present'],     start:2026, tile:GSI+'seamlessphoto/{z}/{x}/{y}.jpg', maxNativeZoom:18 },
      ],
      src:SRC_GSI,
    },
  ];

  // 画面の言葉
  const TEXT = {
    ja:{
      title:'ImmersaMap ｜ 海外の空中写真・古地図（試作）', h1:'海外の空中写真・古地図', badge:'試作',
      lead:'日本とヨーロッパの昔の空中写真と古地図を、同じ画面で見比べる試作です。',
      place:'場所', change:'場所を変える', outside:'対象外の場所', photosOf:(n) => `${n} の写真`, mapsOf:(n) => `${n} の古地図`, photos:'写真',
      kindPhoto:'空中写真', kindMap:'古地図', kindAria:'空中写真と古地図を切り替える',
      opacity:'濃さ', opacityAria:'写真の濃さ', prev:'ひとつ前の年', next:'ひとつ後の年', era:'年',
      chips:'年を選ぶ', src:'出典', base:'背景地図', sheetOpen:'詳しい操作を開く', sheetClose:'詳しい操作を閉じる',
      lang:'English', langAria:'Switch to English', langCode:'en',
      areas:'日本・スイス・フランス・スペイン・ベルギー（フランドル）・ドイツ（NRW州・ベルリン・バイエルン）・ウィーン',
      msg:{
        outside:(a) => `この試作の対象は${a}だけです。「場所を変える」から移動してください。`,
        failed:'読み込めませんでした。配信元が混んでいるか、止まっている可能性があります。',
        blank:'この場所には、この年の写真がありません。別の年を選ぶか、ズームを変えてみてください。',
        blankMap:'この場所には、この年の地図がありません。別の年を選ぶか、ズームを変えてみてください。',
        zoomIn:(z) => `この地図は細かいので、ズーム${z}以上に寄ると出ます（＋で寄る）。`,
      },
    },
    en:{
      title:'ImmersaMap | Historical aerial photos and old maps of Europe and Japan (prototype)', h1:'Historical aerial photos & maps', badge:'Prototype',
      lead:'A prototype for comparing old aerial photos and maps of Japan and Europe on one map.',
      place:'Place', change:'Change place', outside:'Outside coverage', photosOf:(n) => `Photos of ${n}`, mapsOf:(n) => `Old maps of ${n}`, photos:'Photos',
      kindPhoto:'Photos', kindMap:'Old maps', kindAria:'Switch between aerial photos and old maps',
      opacity:'Opacity', opacityAria:'Photo opacity', prev:'Previous year', next:'Next year', era:'Year',
      chips:'Choose a year', src:'Source', base:'Base map', sheetOpen:'Show more', sheetClose:'Show less',
      lang:'日本語', langAria:'日本語に切り替える', langCode:'ja',
      areas:'Japan, Switzerland, France, Spain, Flanders (Belgium), NRW, Berlin and Bavaria (Germany), and Vienna',
      msg:{
        outside:(a) => `This prototype covers only ${a}. Use "Change place" to move.`,
        failed:'Could not load the images. The provider may be busy or down.',
        blank:'There is no photo for this year here. Try another year or zoom level.',
        blankMap:'There is no map for this year here. Try another year or zoom level.',
        zoomIn:(z) => `This detailed map appears when you zoom in to level ${z} or closer (press +).`,
      },
    },
  };

  // 言葉はページごとに決まっている（/overseas/ は日本語、/en/overseas/ は英語）。
  // HTML に静的に書いた <html lang> を読む（file:// ではパスが /en/ で始まらないので、パスでは決めない）
  const lang = document.documentElement.lang === 'en' ? 'en' : 'ja';
  const t = () => TEXT[lang];
  const tr = (v) => Array.isArray(v) ? v[lang === 'en' ? 1 : 0] : v;
  function eraName(e) {
    if (lang === 'ja') return e.name;
    if (e.start === 2026) return 'Latest';
    if (e.circa) return 'c. ' + e.start;
    return e.end ? `${e.start}–${e.end}` : String(e.start);
  }

  // 国旗は絵文字を使わず SVG で描く（Windows は国旗の絵文字を出せず、「CH」のような文字になる）
  const FLAGS = {
    jp:'<svg class="flag" viewBox="0 0 3 2"><rect width="3" height="2" fill="#fff"/><circle cx="1.5" cy="1" r=".6" fill="#bc002d"/></svg>',
    ch:'<svg class="flag sq" viewBox="0 0 32 32"><rect width="32" height="32" fill="#d52b1e"/><path d="M13 6h6v7h7v6h-7v7h-6v-7H6v-6h7z" fill="#fff"/></svg>',
    fr:'<svg class="flag" viewBox="0 0 3 2"><rect width="1" height="2" fill="#002654"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#ce1126"/></svg>',
    at:'<svg class="flag" viewBox="0 0 3 3"><rect width="3" height="3" fill="#c8102e"/><rect y="1" width="3" height="1" fill="#fff"/></svg>',
    de:'<svg class="flag" viewBox="0 0 5 3"><rect width="5" height="1" fill="#000"/><rect y="1" width="5" height="1" fill="#dd0000"/><rect y="2" width="5" height="1" fill="#ffce00"/></svg>',
    be:'<svg class="flag sq" viewBox="0 0 15 13" style="width:18px"><rect width="5" height="13" fill="#000"/><rect x="5" width="5" height="13" fill="#fdda24"/><rect x="10" width="5" height="13" fill="#ef3340"/></svg>',
    es:'<svg class="flag" viewBox="0 0 3 2"><rect width="3" height="2" fill="#aa151b"/><rect y=".5" width="3" height="1" fill="#f1bf00"/></svg>',
  };
  const GLOBE = '<svg class="flag sq" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" fill="none" stroke="#666" stroke-width="1.4"/><path d="M1 8h14M8 1c-3 3.5-3 10.5 0 14M8 1c3 3.5 3 10.5 0 14" fill="none" stroke="#666" stroke-width="1.2"/></svg>';

  // 場所の一覧は国ごとにまとめる（都市が増えても画面のボタンは増えない）
  const PLACE_GROUPS = [
    { flag:'jp', name:['日本', 'Japan'],             places:[{ name:['東京', 'Tokyo'],         center:[35.6812,139.7671] }] },
    { flag:'ch', name:['スイス', 'Switzerland'],     places:[{ name:['チューリッヒ', 'Zurich'], center:[47.3769,8.5417] }] },
    { flag:'fr', name:['フランス', 'France'],        places:[{ name:['パリ', 'Paris'],         center:[48.8584,2.2945] }] },
    { flag:'at', name:['オーストリア', 'Austria'],   places:[{ name:['ウィーン', 'Vienna'],     center:[48.2085,16.3731] }] },
    { flag:'de', name:['ドイツ', 'Germany'],         places:[{ name:['エッセン', 'Essen'],      center:[51.4556,7.0116] }, { name:['ケルン', 'Cologne'], center:[50.9413,6.9583] },
                                                               { name:['ベルリン', 'Berlin'],     center:[52.5163,13.3777] }, { name:['ミュンヘン', 'Munich'], center:[48.1374,11.5755] }] },
    { flag:'be', name:['ベルギー', 'Belgium'],       places:[{ name:['アントワープ', 'Antwerp'], center:[51.2194,4.4025] }, { name:['ヘント', 'Ghent'], center:[51.0543,3.7174] }] },
    { flag:'es', name:['スペイン', 'Spain'],         places:[{ name:['マドリード', 'Madrid'],   center:[40.4169,-3.7035] }, { name:['バルセロナ', 'Barcelona'], center:[41.3870,2.1700] },
                                                               { name:['ビルバオ', 'Bilbao'],     center:[43.2630,-2.9350] }] },
  ];
  const PLACES = PLACE_GROUPS.flatMap(g => g.places.map(p => ({ ...p, zoom:15 })));

  // swisstopo は写真の無い所に、200 で真っ白な小さい JPEG を返す（透明にできない）。
  // ルール地方・スペインの WMS も、範囲外は 200 で中身の無い小さい PNG を返す。
  // fetch で中身の大きさを見て、小さいタイルは隠し、「写真が無い」と数える
  const blankAware = {
    createTile(coords, done) {
      const img = document.createElement('img');
      img.alt = '';
      fetch(this.getTileUrl(coords))
        .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.blob(); })
        .then(blob => {
          if (blob.size < this.options.blankBytes) {
            img.style.visibility = 'hidden';
            this.fire('tileblank');
            done(null, img);
            return;
          }
          img.onload = () => { URL.revokeObjectURL(img.src); done(null, img); };
          img.onerror = () => done(new Error('画像を読めない'), img);
          img.src = URL.createObjectURL(blob);
        })
        .catch(err => done(err, img));
      return img;
    },
  };
  const BlankAwareLayer = L.TileLayer.extend(blankAware);
  const BlankAwareWMS = L.TileLayer.WMS.extend(blankAware);

  // ============ 状態 ============
  const state = {
    // kind: 'photo'（空中写真）か 'map'（古地図）。選んだ年は種類ごとに覚える
    country:null, kind:'photo', eras:[], index:0, want:{ photo:null, map:null }, opacity:80, msg:null,
    overlay:null, retiring:[], tiles:{ok:0, err:0, blank:0},
  };
  const $ = (id) => document.getElementById(id);

  // アドレスの # に「ズーム/緯度/経度/種類/年」を持つ（共有・言葉の切り替えで見ていた所を引き継ぐ）。
  // 例 #15/47.37690/8.54170/map/1900。おかしな値なら無視して初期表示（東京・最新）
  function readHash() {
    const m = /^#(\d{1,2})\/(-?\d{1,2}(?:\.\d+)?)\/(-?\d{1,3}(?:\.\d+)?)\/(photo|map)\/(\d{4})$/.exec(location.hash);
    if (!m) return null;
    const [z, lat, lng, year] = [Number(m[1]), Number(m[2]), Number(m[3]), Number(m[5])];
    if (z < 2 || z > 19 || Math.abs(lat) > 85 || Math.abs(lng) > 180 || year < 1500 || year > 2100) return null;
    return { z, lat, lng, kind:m[4], year };
  }
  const fromHash = readHash();
  if (fromHash) {
    state.kind = fromHash.kind;
    state.want[fromHash.kind] = fromHash.year;
    // 種類がその場所に無いとき（例: 外したフランスの古地図）は、空中写真のいちばん近い年を出す
    if (fromHash.kind === 'map') state.want.photo = fromHash.year;
  }
  const map = L.map('map', {
    center:fromHash ? [fromHash.lat, fromHash.lng] : PLACES[0].center, zoom:fromHash ? fromHash.z : PLACES[0].zoom,
    // ズーム1まで引くと、# に書いた値を読む側（2〜19）が受け付けない。worldCopyJump で中心の経度を -180〜180 に保つ
    minZoom:2, maxZoom:19, zoomControl:false, worldCopyJump:true,
  });
  L.control.zoom({ position:'topright' }).addTo(map);   // 左上は操作板が覆うので右へ
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom:19 }).addTo(map);
  map.attributionControl.setPrefix(false);

  // スマホ（縦は幅600px以下・横は高さ500px以下）では操作板を畳めるシートにする
  const compactQuery = matchMedia('(max-width:600px), (max-height:500px) and (orientation:landscape)');
  function applyCompact() {
    document.body.classList.toggle('compact', compactQuery.matches);
    map.invalidateSize();
  }
  compactQuery.addEventListener('change', applyCompact);
  applyCompact();

  // 点が多角形の中か（横に線を引いて、辺を何回またぐかで判定）
  function inPolygon(lat, lng, poly) {
    let inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const [ai, oi] = poly[i], [aj, oj] = poly[j];
      if ((ai > lat) !== (aj > lat) && lng < (oj - oi) * (lat - ai) / (aj - ai) + oi) inside = !inside;
    }
    return inside;
  }
  function countryAt(latlng) {
    return COUNTRIES.find(c => c.area.some(poly => inPolygon(latlng.lat, latlng.lng, poly))) || null;
  }
  function boundsOf(country) {
    return L.latLngBounds(country.area.flat());
  }

  // スライダーの中身（年の名前）を、今の国と言葉で作る
  function renderEras() {
    const n = state.eras.length;
    const k = kindNow();
    $('country-label').textContent = !state.country ? t().photos : (k === 'map' ? t().mapsOf : t().photosOf)(tr(state.country.name));
    // 古地図のある地域だけ、空中写真と古地図の切り替えを出す
    $('kind').hidden = !state.country?.maps;
    document.querySelectorAll('[data-kind]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.kind === k)));
    $('era').max = Math.max(n - 1, 0);
    $('era').disabled = n === 0;
    $('ticks').innerHTML = state.eras.map((_, i) => `<i style="left:${n > 1 ? i / (n - 1) * 100 : 0}%"></i>`).join('');
    $('end-old').textContent = n ? eraName(state.eras[0]) : '';
    $('end-new').textContent = n ? eraName(state.eras[n - 1]) : '';
    $('chips').innerHTML = '';
    state.eras.forEach((e, i) => {
      const b = document.createElement('button');
      b.className = 'chip';
      b.textContent = eraName(e);
      b.addEventListener('click', () => select(i));
      $('chips').appendChild(b);
    });
    $('where-flag').innerHTML = state.country ? FLAGS[state.country.flag] : GLOBE;
    $('where-name').textContent = state.country ? tr(state.country.name) : t().outside;
    fitWhere();
  }

  // 国名は縮められる（…で切れる）ので、国名が切れていたら「場所を変える」を隠して国名に場所を譲る
  function fitWhere() {
    const name = $('where-name');
    $('where').classList.remove('tight');
    if (name.scrollWidth > name.clientWidth + 1) $('where').classList.add('tight');
  }
  addEventListener('resize', fitWhere);

  // 国が変わったら、その国にある年だけでスライダーを作り直す。
  // 選び直す基準は「利用者が最後に選んだ年」（直前の国で自動で選ばれた年ではない。行き来しても年がずれないように）
  // 古地図の無い地域では、古地図を選んでいても空中写真を出す
  function kindNow() {
    return state.kind === 'map' && state.country?.maps ? 'map' : 'photo';
  }
  function rebuild() {
    const k = kindNow();
    const want = state.want[k];
    state.eras = !state.country ? [] : k === 'map' ? state.country.maps : state.country.photos;
    renderEras();
    let idx = state.eras.length - 1;
    if (want !== null) {
      let best = Infinity;
      state.eras.forEach((e, i) => {
        const d = Math.abs(e.start - want);
        if (d < best) { best = d; idx = i; }
      });
    }
    state.index = Math.max(idx, 0);
    show();
  }

  // お知らせは種類だけ覚えておき、言葉を変えたら書き直す
  function setMessage(key, arg) {
    state.msg = key;
    state.msgArg = arg;
    renderMessage();
  }
  function renderMessage() {
    const m = state.msg && t().msg[state.msg];
    $('msg').hidden = !m;
    $('msg').textContent = !m ? '' : typeof m === 'function' ? m(state.msgArg ?? t().areas) : m;
  }

  // 年の表示だけを変える（スライダーを動かしている最中は、写真は読みに行かない）
  function updateLabel() {
    const n = state.eras.length;
    $('era').value = state.index;
    $('prev').disabled = !n || state.index <= 0;
    $('next').disabled = !n || state.index >= n - 1;
    [...$('chips').children].forEach((b, i) => b.setAttribute('aria-pressed', String(i === state.index)));
    const chip = $('chips').children[state.index];
    if (chip) chip.scrollIntoView({ block:'nearest', inline:'center' });

    const e = state.eras[state.index];
    $('era-name').textContent = e ? eraName(e) : '—';
    $('era-sub').textContent = e ? tr(e.sub) : '';
  }

  function overlayOpacity() {
    return state.opacity / 100;
  }

  function dropRetiring() {
    state.retiring.forEach(l => map.removeLayer(l));
    state.retiring = [];
  }

  // 利用者が年を選んだ（スライダー・◀▶・チップ）。国を移ったときの基準として覚える
  function choose(i) {
    state.index = Math.min(Math.max(i, 0), state.eras.length - 1);
    const k = kindNow();
    state.want[k] = state.eras[state.index]?.start ?? state.want[k];
  }
  function select(i) {
    choose(i);
    show();
  }

  function show() {
    clearTimeout(show.timer);
    updateLabel();
    syncHash();
    // 前の写真は、新しい写真が読み終わるまで残す（背景の地図がちらつかないように）
    if (state.overlay) { state.retiring.push(state.overlay); state.overlay = null; }
    state.tiles = { ok:0, err:0, blank:0 };

    if (!state.country) {
      dropRetiring();
      $('src-layer').textContent = '—';
      setMessage('outside');
      return;
    }
    const e = state.eras[state.index];
    $('src-layer').innerHTML = tr(srcNow());
    setMessage(null);

    const opts = {
      maxZoom:19, maxNativeZoom:Math.min(e.maxNativeZoom, 19), minNativeZoom:e.minNativeZoom ?? 0,
      bounds:boundsOf(state.country), opacity:overlayOpacity(),
    };
    if (e.blankBytes) opts.blankBytes = e.blankBytes;
    let layer;
    if (e.wms) {
      const wmsOpts = { ...opts, layers:e.wms.layers, format:'image/png', transparent:true, version:'1.1.1' };
      layer = e.blankBytes ? new BlankAwareWMS(e.wms.url, wmsOpts) : L.tileLayer.wms(e.wms.url, wmsOpts);
    } else {
      layer = e.blankBytes ? new BlankAwareLayer(e.tile, opts) : L.tileLayer(e.tile, opts);
    }
    // 数えるのは表示中の層だけ（読み終わりを待って残している前の層は数えない）
    const mine = (fn) => () => { if (state.overlay === layer) fn(); };
    layer.on('tileblank', mine(() => { state.tiles.blank++; }));
    // 動かすたびに数え直す（前の場所の結果でお知らせを出さない）
    layer.on('loading', mine(() => {
      state.tiles = { ok:0, err:0, blank:0 };
      setMessage(null);
    }));
    layer.on('tileload', mine(() => { state.tiles.ok++; }));
    layer.on('tileerror', mine(() => { state.tiles.err++; }));
    // 表示中のタイルが1枚も読めなかったときだけ知らせる（一部の欠けは撮影範囲外のことが多い）
    layer.on('load', () => {
      if (state.overlay !== layer) return;
      dropRetiring();
      const c = state.tiles;
      // 細かい地図は、引いた画面では配信が空。「無い」ではなく「寄ると出る」と伝える
      if (e.minZoom && map.getZoom() < e.minZoom) setMessage('zoomIn', e.minZoom);
      else if (c.err > 0 && c.ok === 0) setMessage('failed');
      else if (c.ok > 0 && c.blank === c.ok) setMessage(kindNow() === 'map' ? 'blankMap' : 'blank');
    });
    state.overlay = layer;
    layer.addTo(map);
  }

  function srcNow() {
    return kindNow() === 'map' ? state.country.mapSrc : state.country.src;
  }

  function onMove() {
    const c = countryAt(map.wrapLatLng(map.getCenter()));
    if (c !== state.country) { state.country = c; rebuild(); }
    syncHash();
  }

  // 動かす・種類や年を変えるたびに、自分のアドレスの # と、もう一方の言葉へのリンクを書き直す
  function syncHash() {
    const c = map.wrapLatLng(map.getCenter());
    const e = state.eras[state.index];
    const h = `#${map.getZoom()}/${c.lat.toFixed(5)}/${c.lng.toFixed(5)}/${kindNow()}/${e ? e.start : 2026}`;
    try { history.replaceState(null, '', h); } catch (_) { /* file:// などで書けなくても、リンクは書き直す */ }
    const other = $('lang');
    other.href = other.getAttribute('href').split('#')[0] + h;
  }

  // ============ 操作 ============
  function renderPlaceList() {
    $('place-list').innerHTML = '';
    PLACE_GROUPS.forEach(g => {
      const head = document.createElement('div');
      head.className = 'pl-country';
      head.innerHTML = FLAGS[g.flag] + '<span></span>';
      head.lastChild.textContent = tr(g.name);
      const row = document.createElement('div');
      row.className = 'pl-cities';
      g.places.forEach(p => {
        const b = document.createElement('button');
        b.className = 'chip';
        b.textContent = tr(p.name);
        b.setAttribute('role', 'menuitem');
        b.addEventListener('click', () => { setPlaceList(false); map.setView(p.center, 15); });
        row.appendChild(b);
      });
      const group = document.createElement('div');
      group.className = 'pl-group';
      group.dataset.flag = g.flag;
      group.append(head, row);
      $('place-list').appendChild(group);
    });
  }

  function setPlaceList(open) {
    $('place-list').hidden = !open;
    $('where').setAttribute('aria-expanded', String(open));
    if (!open) return;
    // 今いる国の行に印を付け、そこまで送る（国が増えても探さずに済むように）
    let here = null;
    $('place-list').querySelectorAll('.pl-group').forEach(g => {
      const on = !!state.country && g.dataset.flag === state.country.flag;
      g.classList.toggle('here', on);
      if (on) here = g;
    });
    if (here) here.scrollIntoView({ block:'nearest' });
  }
  $('where').addEventListener('click', () => setPlaceList($('place-list').hidden));
  // 地図は触れた時点で click を止めることがあるので、触れた瞬間（pointerdown）で外側を判定する
  document.addEventListener('pointerdown', (ev) => { if (!$('where-wrap').contains(ev.target)) setPlaceList(false); }, true);
  document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') setPlaceList(false); });

  document.querySelectorAll('[data-kind]').forEach(b => b.addEventListener('click', () => {
    if (state.kind === b.dataset.kind) return;
    state.kind = b.dataset.kind;
    rebuild();
  }));

  // 指で動かしている間は年の表示だけ変え、離したとき（change）か、止まって 250ms 後に写真を読む
  $('era').addEventListener('input', (ev) => {
    choose(Number(ev.target.value));
    updateLabel();
    clearTimeout(show.timer);
    show.timer = setTimeout(show, 250);
  });
  $('era').addEventListener('change', (ev) => select(Number(ev.target.value)));
  $('prev').addEventListener('click', () => select(state.index - 1));
  $('next').addEventListener('click', () => select(state.index + 1));

  function setOpacityAll() {
    [state.overlay, ...state.retiring].forEach(l => l && l.setOpacity(overlayOpacity()));
  }
  $('opacity').addEventListener('input', (ev) => {
    state.opacity = Number(ev.target.value);
    $('opacity-val').textContent = state.opacity + '%';
    setOpacityAll();
  });

  function renderSheetToggle() {
    $('sheet-toggle').textContent = $('panel').classList.contains('open') ? t().sheetClose : t().sheetOpen;
  }
  $('sheet-toggle').addEventListener('click', () => {
    const open = !$('panel').classList.contains('open');
    $('panel').classList.toggle('open', open);
    $('sheet-toggle').setAttribute('aria-expanded', String(open));
    renderSheetToggle();
    if (open) updateLabel();   // 選んだ年のチップを真ん中へ
  });

  // 言葉を当てはめる。写真の層は作り直さない（年も場所もそのまま）
  function applyLang() {
    const x = t();
    document.documentElement.lang = lang;
    document.title = x.title;
    $('h1-text').textContent = x.h1;
    $('badge').textContent = x.badge;
    $('lead').textContent = x.lead;
    $('place-label').textContent = x.place;
    $('where-caret').textContent = x.change;
    $('opacity-eye').textContent = x.opacity;
    $('opacity-control').title = x.opacityAria;
    $('opacity').setAttribute('aria-label', x.opacityAria);
    $('prev').setAttribute('aria-label', x.prev);
    $('next').setAttribute('aria-label', x.next);
    $('era').setAttribute('aria-label', x.era);
    $('chips-label').textContent = x.chips;
    $('src-label').textContent = x.src;
    $('base-label').textContent = x.base;
    renderSheetToggle();
    renderPlaceList();
    renderEras();
    updateLabel();
    renderMessage();
    if (state.country) $('src-layer').innerHTML = tr(srcNow());
    $('kind').setAttribute('aria-label', x.kindAria);
    $('kind-photo').textContent = x.kindPhoto;
    $('kind-map').textContent = x.kindMap;
  }
  applyLang();
  map.on('moveend', onMove);
  onMove();

  // 開いたまま別の共有リンク（# だけ違う）を開くと、ページは読み直されない。# を読み直して地図を動かす
  // （自分で書く # は replaceState なので、hashchange は起きない）
  addEventListener('hashchange', () => {
    const h = readHash();
    if (!h) return;
    state.kind = h.kind;
    state.want[h.kind] = h.year;
    if (h.kind === 'map') state.want.photo = h.year;
    state.country = null;   // 同じ国でも、種類・年を選び直す
    map.setView([h.lat, h.lng], h.z);
    onMove();
  });

  // 自動テスト用に、地図と今の状態を読めるようにしておく
  window.__overseasMap = map;
  window.__overseas = () => ({
    lang, kind:kindNow(), hasMaps:!!state.country?.maps, country:state.country?.id ?? null,
    stops:state.eras.map(e => e.id), index:state.index,
    layer:state.eras[state.index]?.id ?? null, tiles:{ ...state.tiles },
    loadedLayers:(state.overlay ? 1 : 0) + state.retiring.length,
    loading:state.overlay ? state.overlay.isLoading() : false,
  });
