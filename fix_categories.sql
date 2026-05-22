-- カテゴリ値の修正（aerial→aerial_photo統一）
update maps set category='aerial_photo'
  where category='aerial'
  and tier='standard';

-- story系地図のcategoryを正しく設定
update maps set category='story'
  where id='standard-ryoma-kyoto';

update maps set category='historical'
  where id='standard-kawagoe-edo';

-- sort_orderが未設定のものを補完
update maps set sort_order=1   where id='standard-gsi-seamless';
update maps set sort_order=5   where id='standard-gsi-2023';
update maps set sort_order=15  where id='standard-gsi-2020';
update maps set sort_order=20  where id='standard-gsi-2015';
update maps set sort_order=25  where id='standard-gsi-2010';
update maps set sort_order=30  where id='standard-gsi-2007';
update maps set sort_order=100 where id='standard-gsi-1988';
update maps set sort_order=110 where id='standard-gsi-1984';
update maps set sort_order=120 where id='standard-gsi-1979';
update maps set sort_order=130 where id='standard-gsi-1974';
update maps set sort_order=140 where id='standard-gsi-1961';
update maps set sort_order=150 where id='standard-gsi-1945';
update maps set sort_order=160 where id='standard-gsi-1936';
update maps set sort_order=170 where id='osaka1928';
update maps set sort_order=200 where id='standard-gsi-relief';
update maps set sort_order=210 where id='standard-gsi-hillshade';
update maps set sort_order=10  where id='standard-kawagoe-edo';
update maps set sort_order=20  where id='standard-ryoma-kyoto';
