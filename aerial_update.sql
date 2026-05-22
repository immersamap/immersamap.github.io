-- 空中写真・地形タイルの完全更新
-- 2007年以降の年度別写真追加、sort_orderで年代管理

alter table maps add column if not exists sort_order integer default 999;

-- 既存空中写真のsort_order設定（新しい年代ほど小さい数字）
update maps set sort_order=100 where id='standard-gsi-1988';
update maps set sort_order=110 where id='standard-gsi-1984';
update maps set sort_order=120 where id='standard-gsi-1979';
update maps set sort_order=130 where id='standard-gsi-1974';
update maps set sort_order=140 where id='standard-gsi-1961';
update maps set sort_order=150 where id='standard-gsi-1945';
update maps set sort_order=160 where id='standard-gsi-1936';
update maps set sort_order=170 where id='osaka1928';
update maps set sort_order=10  where id='standard-gsi-hillshade';
update maps set sort_order=20  where id='standard-gsi-relief';

-- 2007年以降の年度別空中写真を追加（新しい順）
insert into maps (id,name,era,description,type,tier,category,subcategory,
  is_standard,is_verified,tiles_url,center_lat,center_lng,zoom_default,
  zoom_min,zoom_max,is_public,price,sort_order)
values
  ('standard-gsi-2023','2023年度の空中写真','2023年度',
   '国土地理院の年度別空中写真（2023年度）。最新に近い空中写真。',
   'aerial','standard','aerial_photo','aerial_photo',true,true,
   'https://cyberjapandata.gsi.go.jp/xyz/nendophoto2023/{z}/{x}/{y}.png',
   35.7148,139.7967,16,14,18,true,0,5),
  ('standard-gsi-2020','2020年度の空中写真','2020年度',
   '国土地理院の年度別空中写真（2020年度）。',
   'aerial','standard','aerial_photo','aerial_photo',true,true,
   'https://cyberjapandata.gsi.go.jp/xyz/nendophoto2020/{z}/{x}/{y}.png',
   35.7148,139.7967,16,14,18,true,0,15),
  ('standard-gsi-2015','2015年度の空中写真','2015年度',
   '国土地理院の年度別空中写真（2015年度）。',
   'aerial','standard','aerial_photo','aerial_photo',true,true,
   'https://cyberjapandata.gsi.go.jp/xyz/nendophoto2015/{z}/{x}/{y}.png',
   35.7148,139.7967,16,14,18,true,0,20),
  ('standard-gsi-2010','2010年度の空中写真','2010年度',
   '国土地理院の年度別空中写真（2010年度）。',
   'aerial','standard','aerial_photo','aerial_photo',true,true,
   'https://cyberjapandata.gsi.go.jp/xyz/nendophoto2010/{z}/{x}/{y}.png',
   35.7148,139.7967,16,14,18,true,0,25),
  ('standard-gsi-2007','2007年度の空中写真','2007年度',
   '国土地理院の年度別空中写真（2007年度）。年度別の最古。',
   'aerial','standard','aerial_photo','aerial_photo',true,true,
   'https://cyberjapandata.gsi.go.jp/xyz/nendophoto2007/{z}/{x}/{y}.png',
   35.7148,139.7967,16,14,18,true,0,30),
  ('standard-gsi-seamless','最新空中写真（シームレス）','最新（2004年〜）',
   '全国最新写真。複数年度の空中写真をシームレスにつなぎ合わせた最新状態。',
   'aerial','standard','aerial_photo','aerial_photo',true,true,
   'https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg',
   35.7148,139.7967,16,2,18,true,0,1)
on conflict (id) do nothing;
