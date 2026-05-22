-- ============================================================
-- ImmersaMap v2 スキーマ
-- Supabase SQL Editor に貼り付けて実行してください
-- ============================================================

-- 既存mapsテーブルに列を追加
alter table maps add column if not exists tier text default 'community';
alter table maps add column if not exists category text default 'historical';
alter table maps add column if not exists subcategory text;
alter table maps add column if not exists is_standard boolean default false;
alter table maps add column if not exists is_verified boolean default false;
alter table maps add column if not exists geojson jsonb;
alter table maps add column if not exists layer_config jsonb;
alter table maps add column if not exists rating_avg real default 0;
alter table maps add column if not exists rating_count integer default 0;
alter table maps add column if not exists purchase_count integer default 0;

-- 川越ベクター地図（Standard）
insert into maps (
  id, name, era, description, type,
  tier, category, subcategory,
  is_standard, is_verified,
  tiles_url, thumbnail_url,
  center_lat, center_lng, zoom_default,
  is_public, price
) values (
  'standard-kawagoe-edo',
  '川越城下絵図',
  '江戸時代中〜後期',
  '川越城を中心とした城下町。道路・城郭・地名をAIがベクター化。GPSで現在地と重ねて江戸時代を体験。',
  'historical',
  'standard', 'historical', 'edo',
  true, true,
  null,
  'https://immersamap.github.io/kawagoe.jpg',
  35.923, 139.485, 15,
  true, 0
) on conflict (id) do update set
  tier='standard', category='historical', subcategory='edo',
  is_standard=true, is_verified=true;

-- 地理院タイル（Standard）
insert into maps (id, name, era, description, type, tier, category, subcategory, is_standard, is_verified, tiles_url, center_lat, center_lng, zoom_default, is_public, price)
values
  ('standard-gsi-1936', '戦前の東京', '1936〜1942年', '陸軍撮影の空中写真。東京23区・大阪市をカバー。', 'aerial', 'standard', 'aerial', 'aerial_photo', true, true, 'https://cyberjapandata.gsi.go.jp/xyz/ort_riku10/{z}/{x}/{y}.png', 35.7148, 139.7967, 16, true, 0),
  ('standard-gsi-1945', '終戦直後（米軍空中写真）', '1945〜1950年', '米軍撮影の空中写真。全国をカバー。', 'aerial', 'standard', 'aerial', 'aerial_photo', true, true, 'https://cyberjapandata.gsi.go.jp/xyz/ort_USA10/{z}/{x}/{y}.png', 35.7148, 139.7967, 16, true, 0),
  ('standard-gsi-1961', '高度成長期', '1961〜1969年', '高度経済成長期の全国空中写真。', 'aerial', 'standard', 'aerial', 'aerial_photo', true, true, 'https://cyberjapandata.gsi.go.jp/xyz/ort_old10/{z}/{x}/{y}.png', 35.6362, 139.7966, 16, true, 0),
  ('standard-gsi-1974', '昭和50年代', '1974〜1978年', '国土画像情報。全国をカバー。', 'aerial', 'standard', 'aerial', 'aerial_photo', true, true, 'https://cyberjapandata.gsi.go.jp/xyz/gazo1/{z}/{x}/{y}.jpg', 35.7148, 139.7967, 16, true, 0),
  ('standard-gsi-relief', '色別標高図', '現代', '国土地理院の色別標高図。全国の地形を色で表示。', 'aerial', 'standard', 'aerial', 'terrain', true, true, 'https://cyberjapandata.gsi.go.jp/xyz/relief/{z}/{x}/{y}.png', 35.3606, 138.7274, 11, true, 0)
on conflict (id) do nothing;

-- カテゴリマスターテーブル
create table if not exists map_categories (
  id text primary key,
  label_ja text not null,
  label_en text not null,
  parent_id text,
  icon text,
  sort_order integer default 0
);

insert into map_categories (id, label_ja, label_en, icon, sort_order) values
  ('historical',   '歴史',          'Historical', '🏯', 1),
  ('aerial',       '空中写真・地形', 'Aerial',     '✈️', 2),
  ('fiction',      'フィクション',   'Fiction',    '📺', 3),
  ('original',     '創作・オリジナル','Original',  '🐉', 4),
  ('themed',       'テーマ・特集',   'Themed',     '🌸', 5)
on conflict (id) do nothing;

insert into map_categories (id, label_ja, label_en, parent_id, icon, sort_order) values
  ('ancient',         '古代・中世',       'Ancient',      'historical', '⛩', 1),
  ('edo',             '江戸時代',         'Edo',          'historical', '🏯', 2),
  ('modern_japan',    '明治〜昭和',       'Modern Japan', 'historical', '🚂', 3),
  ('world_history',   '世界史',           'World',        'historical', '🌏', 4),
  ('aerial_photo',    '空中写真',         'Aerial Photo', 'aerial',     '📸', 1),
  ('terrain',         '地形・標高',       'Terrain',      'aerial',     '⛰', 2),
  ('anime_manga',     'アニメ・マンガ',   'Anime/Manga',  'fiction',    '📺', 1),
  ('movie_drama',     '映画・ドラマ',     'Movie/Drama',  'fiction',    '🎬', 2),
  ('novel',           '小説・ライトノベル','Novel',        'fiction',    '📖', 3),
  ('game',            'ゲーム',           'Game',         'fiction',    '🎮', 4),
  ('fantasy',         'ファンタジー',     'Fantasy',      'original',   '🐉', 1),
  ('scifi',           'SF・未来',         'Sci-Fi',       'original',   '🚀', 2),
  ('fictional_world', '架空世界',         'Fictional',    'original',   '🗺', 3),
  ('art_map',         'アート地図',       'Art Map',      'original',   '🎨', 4),
  ('pilgrimage',      '聖地巡礼',         'Pilgrimage',   'themed',     '🌸', 1),
  ('ruins',           '廃墟・遺跡',       'Ruins',        'themed',     '🏚', 2),
  ('local_culture',   '地域文化',         'Culture',      'themed',     '🎌', 3),
  ('research',        '調査・研究',       'Research',     'themed',     '🔍', 4)
on conflict (id) do nothing;

-- レビューテーブル
create table if not exists map_reviews (
  id uuid primary key default gen_random_uuid(),
  map_id text references maps(id) on delete cascade,
  user_id uuid,
  rating integer check (rating between 1 and 5),
  comment text,
  created_at timestamptz default now()
);
alter table map_reviews enable row level security;
create policy "レビュー閲覧" on map_reviews for select using (true);
create policy "レビュー投稿" on map_reviews for insert with check (true);

-- 購入テーブル
create table if not exists map_purchases (
  id uuid primary key default gen_random_uuid(),
  map_id text references maps(id),
  user_id uuid references auth.users(id),
  price_paid integer,
  purchased_at timestamptz default now()
);
alter table map_purchases enable row level security;
create policy "自分の購入履歴" on map_purchases for select using (auth.uid() = user_id);
create policy "購入登録" on map_purchases for insert with check (true);
