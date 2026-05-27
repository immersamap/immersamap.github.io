-- ============================================================
-- 古地図位置合わせ機能のためのスキーマ拡張
-- Supabase SQL Editor で実行してください
-- ============================================================

-- 1. maps テーブルに画像オーバーレイ用カラムを追加
alter table maps add column if not exists image_url     text;
alter table maps add column if not exists image_bounds  jsonb;  -- [[south, west], [north, east]]
alter table maps add column if not exists image_rotation real default 0;
alter table maps add column if not exists image_opacity real default 0.8;
alter table maps add column if not exists source        text;   -- 出典（例：国会図書館デジタルコレクション URL）
alter table maps add column if not exists gcps          jsonb;  -- GCP配列（再編集用）

-- 2. Storage バケットの作成
--    ※ SQL Editor では Storage は直接作れないので、Supabaseダッシュボードで：
--    Storage → New bucket → 名前: historical-maps、Public: ON にしてください
--    あるいは下記SQLでも作成可能：
insert into storage.buckets (id, name, public)
  values ('historical-maps', 'historical-maps', true)
  on conflict (id) do nothing;

-- 3. ストレージのRLSポリシー（誰でも読み込み可、書き込みも今は誰でも）
--    将来Auth導入時に書き込みポリシーを絞り込む
drop policy if exists "historical maps public read"  on storage.objects;
drop policy if exists "historical maps public write" on storage.objects;
drop policy if exists "historical maps public update" on storage.objects;
drop policy if exists "historical maps public delete" on storage.objects;

create policy "historical maps public read"
  on storage.objects for select
  using (bucket_id = 'historical-maps');

create policy "historical maps public write"
  on storage.objects for insert
  with check (bucket_id = 'historical-maps');

create policy "historical maps public update"
  on storage.objects for update
  using (bucket_id = 'historical-maps');

create policy "historical maps public delete"
  on storage.objects for delete
  using (bucket_id = 'historical-maps');

-- 4. maps テーブルのRLS（既に有効ならスキップ）
--    historicalカテゴリの公開地図は誰でも読める設定
do $$
begin
  if not exists (
    select 1 from pg_policies
    where tablename = 'maps' and policyname = 'maps public read'
  ) then
    execute 'create policy "maps public read" on maps for select using (is_public = true)';
  end if;
  if not exists (
    select 1 from pg_policies
    where tablename = 'maps' and policyname = 'maps public write'
  ) then
    execute 'create policy "maps public write" on maps for insert with check (true)';
  end if;
  if not exists (
    select 1 from pg_policies
    where tablename = 'maps' and policyname = 'maps public update'
  ) then
    execute 'create policy "maps public update" on maps for update using (true)';
  end if;
end $$;

alter table maps enable row level security;
