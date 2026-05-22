-- カテゴリ更新: aerial→2つに分割 + 空中写真を全種追加

-- 1. カテゴリ更新
update map_categories set id='aerial_photo', label_ja='空中写真', label_en='Aerial Photo', icon='✈️', sort_order=3
  where id='aerial';

insert into map_categories (id, label_ja, label_en, icon, sort_order)
  values ('terrain', '地形・標高', 'Terrain', '⛰', 4)
  on conflict (id) do nothing;

-- サブカテゴリも更新
update map_categories set parent_id='aerial_photo' where parent_id='aerial';

-- 2. 既存地図のcategoryを更新
update maps set category='aerial_photo' where category='aerial';

-- 3. 地理院タイルを全種・年代新しい順で追加
insert into maps (id, name, era, description, type, tier, category, subcategory,
  is_standard, is_verified, tiles_url, center_lat, center_lng, zoom_default,
  zoom_min, zoom_max, is_public, price, tags)
values
  ('standard-gsi-1988',
   '1988年の空中写真', '1988年',
   '国土画像情報第4回（1988年）。全国をカバー。バブル期直前の日本。',
   'aerial', 'standard', 'aerial_photo', 'aerial_photo',
   true, true,
   'https://cyberjapandata.gsi.go.jp/xyz/gazo4/{z}/{x}/{y}.jpg',
   35.7148, 139.7967, 16, 10, 17, true, 0,
   array['空中写真','1988年','昭和','国土地理院']),

  ('standard-gsi-1984',
   '昭和60年代の空中写真', '1984〜1986年',
   '国土画像情報第3回（1984〜1986年）。全国をカバー。',
   'aerial', 'standard', 'aerial_photo', 'aerial_photo',
   true, true,
   'https://cyberjapandata.gsi.go.jp/xyz/gazo3/{z}/{x}/{y}.jpg',
   35.7148, 139.7967, 16, 10, 17, true, 0,
   array['空中写真','昭和60年','国土地理院']),

  ('standard-gsi-1979',
   '昭和50年代後半の空中写真', '1979〜1983年',
   '国土画像情報第2回（1979〜1983年）。全国をカバー。',
   'aerial', 'standard', 'aerial_photo', 'aerial_photo',
   true, true,
   'https://cyberjapandata.gsi.go.jp/xyz/gazo2/{z}/{x}/{y}.jpg',
   35.7148, 139.7967, 16, 10, 17, true, 0,
   array['空中写真','昭和50年代','国土地理院']),

  ('standard-gsi-hillshade',
   '陰影起伏図', '現代',
   '国土地理院の陰影起伏図。山地・丘陵の立体感を表現。地形理解に最適。',
   'terrain', 'standard', 'terrain', 'terrain',
   true, true,
   'https://cyberjapandata.gsi.go.jp/xyz/hillshademap/{z}/{x}/{y}.png',
   35.3606, 138.7274, 11, 2, 16, true, 0,
   array['地形','陰影','標高','国土地理院'])

on conflict (id) do nothing;

-- 既存の地理院タイルのcategoryも修正
update maps set category='aerial_photo' where id in (
  'standard-gsi-1936','standard-gsi-1945','standard-gsi-1961',
  'standard-gsi-1974','standard-gsi-1984'
);
update maps set category='terrain' where id in (
  'standard-gsi-relief','standard-gsi-hillshade'
);
