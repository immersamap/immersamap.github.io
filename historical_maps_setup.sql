-- ============================================================
-- 古地図位置合わせ機能のためのスキーマ拡張
-- Supabase SQL Editor で実行してください
-- ============================================================
-- 前提: Storage バケット 'map-tiles' (Public) が既に作成済みであること
-- 古地図画像は map-tiles バケット内の historical/ プレフィックスに保存されます

-- 1. maps テーブルに画像オーバーレイ用カラムを追加
alter table maps add column if not exists image_url     text;
alter table maps add column if not exists image_bounds  jsonb;   -- [[south,west],[north,east]]
alter table maps add column if not exists image_rotation real default 0;
alter table maps add column if not exists image_opacity real default 0.8;
alter table maps add column if not exists source        text;
alter table maps add column if not exists gcps          jsonb;
alter table maps add column if not exists coverage_label text;   -- カバー範囲（例：東京、関東一円）

-- 2. Storage の RLS ポリシー（map-tiles バケット用）
--    既存バケットに後から追加しても安全な書き方
drop policy if exists "map-tiles public read"   on storage.objects;
drop policy if exists "map-tiles public write"  on storage.objects;
drop policy if exists "map-tiles public update" on storage.objects;
drop policy if exists "map-tiles public delete" on storage.objects;

create policy "map-tiles public read"
  on storage.objects for select
  using (bucket_id = 'map-tiles');

create policy "map-tiles public write"
  on storage.objects for insert
  with check (bucket_id = 'map-tiles');

create policy "map-tiles public update"
  on storage.objects for update
  using (bucket_id = 'map-tiles');

create policy "map-tiles public delete"
  on storage.objects for delete
  using (bucket_id = 'map-tiles');

-- 3. maps テーブルのRLS（既に有効ならスキップされる）
do $$
begin
  if not exists (
    select 1 from pg_policies where tablename = 'maps' and policyname = 'maps public read'
  ) then
    execute 'create policy "maps public read" on maps for select using (is_public = true)';
  end if;
  if not exists (
    select 1 from pg_policies where tablename = 'maps' and policyname = 'maps public write'
  ) then
    execute 'create policy "maps public write" on maps for insert with check (true)';
  end if;
  if not exists (
    select 1 from pg_policies where tablename = 'maps' and policyname = 'maps public update'
  ) then
    execute 'create policy "maps public update" on maps for update using (true)';
  end if;
end $$;

alter table maps enable row level security;
