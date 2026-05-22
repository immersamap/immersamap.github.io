-- ============================================================
-- ImmersaMap カテゴリ更新 + 坂本龍馬マップ追加
-- Supabase SQL Editor に貼り付けて実行
-- ============================================================

-- カテゴリ全更新（fiction+originalをfictionalに統合、storyを新設）
truncate table map_categories;

insert into map_categories (id, label_ja, label_en, icon, sort_order) values
  ('historical', '歴史',           'Historical', '🏯', 1),
  ('story',      '人物・物語',     'Story',      '📖', 2),
  ('aerial',     '空中写真・地形', 'Aerial',     '✈️', 3),
  ('fictional',  '架空・創作',     'Fiction',    '🐉', 4),
  ('themed',     'テーマ・特集',   'Themed',     '🌸', 5);

insert into map_categories (id, label_ja, label_en, parent_id, icon, sort_order) values
  ('ancient',       '古代・中世',         'Ancient',      'historical', '⛩',  1),
  ('edo',           '江戸時代',           'Edo',          'historical', '🏯',  2),
  ('modern_japan',  '明治〜昭和',         'Modern Japan', 'historical', '🚂',  3),
  ('world_history', '世界史',             'World',        'historical', '🌏',  4),
  ('bakumatsu',     '幕末',               'Bakumatsu',    'story',      '⚔️',  1),
  ('meiji_people',  '明治の人物',         'Meiji',        'story',      '👔',  2),
  ('war_history',   '戦争・事件',         'War',          'story',      '🎌',  3),
  ('aerial_photo',  '空中写真',           'Aerial Photo', 'aerial',     '📸',  1),
  ('terrain',       '地形・標高',         'Terrain',      'aerial',     '⛰',   2),
  ('anime_manga',   'アニメ・マンガ',     'Anime/Manga',  'fictional',  '📺',  1),
  ('movie_drama',   '映画・ドラマ',       'Movie/Drama',  'fictional',  '🎬',  2),
  ('game',          'ゲーム',             'Game',         'fictional',  '🎮',  3),
  ('novel',         '小説・ライトノベル', 'Novel',        'fictional',  '📖',  4),
  ('fantasy',       'ファンタジー',       'Fantasy',      'fictional',  '🐉',  5),
  ('scifi',         'SF・未来',           'Sci-Fi',       'fictional',  '🚀',  6),
  ('art_map',       'アート地図',         'Art Map',      'fictional',  '🎨',  7),
  ('pilgrimage',    '聖地巡礼',           'Pilgrimage',   'themed',     '🌸',  1),
  ('ruins',         '廃墟・遺跡',         'Ruins',        'themed',     '🏚',  2),
  ('local_culture', '地域文化',           'Culture',      'themed',     '🎌',  3),
  ('research',      '調査・研究',         'Research',     'themed',     '🔍',  4);

-- tagsカラム追加
alter table maps add column if not exists tags text[] default '{}';

-- 坂本龍馬マップ追加
insert into maps (
  id, name, era, description, type,
  tier, category, subcategory,
  is_standard, is_verified,
  center_lat, center_lng, zoom_default,
  is_public, price, tags
) values (
  'standard-ryoma-kyoto',
  '坂本龍馬ゆかりの地（京都）',
  '幕末 1862〜1867年',
  '寺田屋・近江屋・酢屋など龍馬ゆかりの地を地図上で巡る。暗殺の地から墓所まで幕末の京都をGPSで歩く。',
  'historical',
  'standard', 'story', 'bakumatsu',
  true, true,
  35.0058, 135.7685, 14,
  true, 0,
  array['坂本龍馬', '幕末', '京都', '寺田屋', '近江屋']
) on conflict (id) do update set
  tier='standard', category='story', subcategory='bakumatsu',
  is_standard=true, is_verified=true;

-- 既存地図のcategoryをfictionalに統合（fiction/originalを移行）
update maps set category='fictional' where category in ('fiction','original');
