# ImmersaMap 設計仕様書

**プロジェクト**: ImmersaMap（没入する地図体験プラットフォーム）  
**バージョン**: 1.0  
**最終更新**: 2026-05-26  
**ステータス**: ✅ **第1章実装完了**

---

## 📋 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [ビジネス戦略](#ビジネス戦略)
3. [技術スタック](#技術スタック)
4. [UI/UX 設計](#uiux-設計)
5. [実装仕様](#実装仕様)
6. [Supabase スキーマ](#supabase-スキーマ)
7. [ファイル構成](#ファイル構成)
8. [デプロイ](#デプロイ)
9. [今後の章計画](#今後の章計画)
10. [更新履歴](#更新履歴)

---

## プロジェクト概要

### ビジョン

**「古い地名と現在の地名を行き来しながら、歴史的な物語の舞台を時系列で追う、没入型地図体験プラットフォーム」**

### 2つのモード

1. **地図探索モード** (`/map/`)
   - 古地図・空中写真で街の変遷を探索
   - 時間スライダーで年代を選択
   - GeoJSON レイヤーで歴史的データを表示

2. **物語追体験モード** (`/okunohosomichi/`)
   - 日本の歴史文学作品を物語として体験
   - マーカークリック → ポップアップで俳句・説明
   - 再生ボタン → 時系列でシーケンシャル表示
   - 現在公開中：『おくのほそ道』（全3章予定）

### ターゲットユーザー

- **聖地巡礼派**：歴史的地点の位置情報を求める
- **物語没入派**：文学作品の舞台を時系列で追いたい
- **ライトファン**：見た目が美しく、分かりやすい体験を求める

---

## ビジネス戦略

### 最終3作品構成

1. **『太平記』**（新田義貞・楠木正成・足利尊氏）
2. **『おくのほそ道』**（松尾芭蕉） ← **現在実装中**
3. **『羅生門』他**（芥川龍之介）

### コンテンツ制作方針

- **Claude 主体での AI 活用**（追加コストなし）
- 歴史考証より「体験」を重視
- AI 活用の透明性を免責表記で担保

### 収益モデル

- TBD（将来計画）

---

## 技術スタック

### フロントエンド

```
HTML5 + CSS3 + JavaScript（ビルドツール不使用）
├─ Leaflet.js 1.9.4（地図ライブラリ）
├─ Supabase SDK v2（データベース）
└─ Google Fonts（Cinzel, Noto Sans JP, Noto Serif JP）
```

### バックエンド

```
Supabase（PostgreSQL + 認証 + リアルタイム）
├─ テーブル：works, chapters, locations, verses
├─ 公開キー：sb_publishable_0zOqrbsnXgdurLgfGp3fsQ_wBsCjFs3
└─ URL：https://kgafuinoddiapaaljkkw.supabase.co
```

### ホスティング

```
GitHub Pages
├─ リポジトリ：immersamap/immersamap.github.io
├─ URL：https://immersamap.github.io/
└─ デプロイ：自動（main ブランチプッシュ時）
```

### デザイン監修

```
Alex Zhang（Airbnb Senior Design Lead）
├─ 設計レビュー完了（2026-05-26）
├─ 仕様承認：⭐⭐⭐⭐⭐ 5.0/5.0
└─ 推奨案（案A）全採用
```

---

## UI/UX 設計

### Color Palette（色パレット）

```css
--ink: #1a1008;          /* 深いブラウン（背景） */
--ink2: #221408;         /* 少し明るいブラウン */
--parchment: #f2e8d0;    /* 淡いベージュ（本文テキスト） */
--parchment2: #e8d8b0;   /* より薄いベージュ（補助テキスト） */
--sepia: #8b6914;        /* セピア色（補助） */
--gold: #d4a017;         /* ゴールド（重要要素） */
--gold-l: #f0c040;       /* 明るいゴールド（ホバー・アクティブ） */
```

**設計哲学**：「時間旅行」を色で表現
- インク + パーチメント = 古い書籍の雰囲気
- ゴールド系 = 歴史的権威性
- セピア = 古写真のニュアンス

### Typography（フォント）

| 用途 | フォント | 役割 |
|------|---------|------|
| ロゴ・見出し | **Cinzel**（セリフ） | 古い活字の権威性 |
| 本文（日本語） | **Noto Serif JP** | 古い刷物の雰囲気、可読性 |
| UI テキスト | **Noto Sans JP** | 現代的で分かりやすい |

### レイアウト仕様

#### PC 表示（1024px 以上）

```
┌─────────────────────────────────────┐
│ ヘッダー（ナビゲーション）         │ 高さ 60px
├─────────────────────────────────────┤
│                                     │
│            地図領域                 │ 高さ 70vh
│     （国土地理院 + セピア化）       │
│                                     │
├─────────────────────────────────────┤
│  ◀前  第1章  次▶     ▶再生          │ コントロール 高さ ~50px
├─────────────────────────────────────┤
│                                     │
│       下部パネル                    │ 高さ 30vh（スクロール）
│  （地点リスト・詳細情報）           │
│                                     │
└─────────────────────────────────────┘
```

#### モバイル表示（320-767px）

```
┌──────────────────────┐
│ ヘッダー             │
├──────────────────────┤
│                      │
│    地図（50vh）      │
│                      │
├──────────────────────┤
│ コントロール         │
├──────────────────────┤
│  パネル              │
│  （スクロール）      │
│                      │
└──────────────────────┘
```

### インタラクション仕様

#### マーカークリック

```
ユーザーがマーカーをクリック
     ↓
ポップアップがフェードイン表示（0.3秒）
     ↓
ポップアップ内容：地点名 + 俳句（あれば） + 簡潔な説明
     ↓
下部パネルが該当地点にスクロール
```

**ポップアップデザイン**（Alex Zhang 仕様）

```
┌────────────────────────────┐
│   千住宿（ゴールド）        │
├────────────────────────────┤
│ 行く春や鳥啼き魚の目は涙  │ （セピア、左枠）
├────────────────────────────┤
│ 旅立ち初夜を過ごし...      │ （パーチメント2）
└────────────────────────────┘

サイズ：280px × 220px（最大）
背景：rgba(26, 16, 8, 0.95)（インク）
枠線：2px solid #d4a017（ゴールド）
影：box-shadow: 0 8px 24px rgba(0,0,0,0.4)
```

#### 再生ボタン

```
ユーザーが「▶ 再生」をクリック
     ↓
ボタンが「⏸ 一時停止」に変更
     ↓
各地点を順番に自動で処理：
  1. マーカーをポップアップで開く
  2. パネルをスクロール
  3. 地図を地点にズーム（2秒間のアニメーション）
  4. 3秒待機
  5. 次の地点へ
     ↓
すべての地点を終了後、ボタンが「▶ 再生」に戻る
```

### トップページ（ランディング）

```
┌─────────────────────────────────┐
│    IMMERSAMAP ロゴ              │
│  没入する地図体験プラットフォーム │ （ヒーロー画面）
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────┐            │
│  │  🗺️ 地図探索    │  ← ホバー時 │
│  │   モード        │   浮く      │
│  │ [地図を開く]    │            │
│  └─────────────────┘            │
│                                 │
│  ┌─────────────────┐            │
│  │  📖 物語追体験   │            │
│  │   モード        │            │
│  │ [物語を見る]    │            │
│  └─────────────────┘            │
│                                 │
├─────────────────────────────────┤
│ ImmersaMapの特徴                │
│ 公開中の作品                    │
│ etc...                          │
└─────────────────────────────────┘

カード仕様（Alex Zhang 推奨）：
- 配置：2カラム（PC）、1カラム（モバイル）
- アスペクト比：正方形（1:1）
- ホバー効果：translateY(-8px) + box-shadow glow
- アイコン：scale(1.15) 回転エフェクト
```

---

## 実装仕様

### 第1章実装（おくのほそ道 江戸〜千住）

#### 地点数

- **合計 9 地点**（江戸 → 栃木方面へ）

#### 俳句データ

- **地点2（千住宿）**：「行く春や鳥啼き魚の目は涙」
- **地点4（室の八島）**：「よき月夜かな」

#### 地図タイル

- **提供元**：国土地理院
- **URL**：`https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png`
- **セピア化**：`filter: sepia(0.15) contrast(1.05)`

#### マーカーUI

- **表示方式**：ポップアップ（クリック時）
- **ポップアップサイズ**：280px × 220px（最大）
- **背景色**：rgba(26, 16, 8, 0.95)
- **枠線**：2px solid #d4a017
- **アニメーション**：popupFadeIn 0.3秒

#### 再生機能

- **初期表示**：ボタン「▶ 再生」
- **クリック時**：ボタン「⏸ 一時停止」に変更、シーケンス開始
- **各地点での処理**：
  1. ポップアップ自動表示（`marker.openPopup()`）
  2. パネルスクロール
  3. 地点へフライズーム（2秒）
  4. 3秒表示

---

## Supabase スキーマ

### テーブル構造

#### `works` テーブル

```sql
CREATE TABLE works (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  description TEXT,
  is_published BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**行例**：
```
id: 'okunohosomichi'
title: '奥の細道'
author: '松尾芭蕉'
is_published: true
```

#### `chapters` テーブル

```sql
CREATE TABLE chapters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  work_id TEXT REFERENCES works(id),
  chapter_number INT NOT NULL,
  title TEXT NOT NULL,
  overview TEXT,
  is_published BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(work_id, chapter_number)
);
```

**行例**：
```
id: (UUID)
work_id: 'okunohosomichi'
chapter_number: 1
title: '江戸〜千住 旅立ち'
is_published: true
```

#### `locations` テーブル

```sql
CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id UUID REFERENCES chapters(id),
  location_name TEXT NOT NULL,
  latitude DECIMAL(9,6) NOT NULL,
  longitude DECIMAL(9,6) NOT NULL,
  order_in_chapter INT NOT NULL,
  description TEXT,
  has_verse BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**行例**：
```
id: (UUID)
chapter_id: (UUID)
location_name: '千住宿'
latitude: 35.7434
longitude: 139.8157
order_in_chapter: 2
has_verse: true
```

#### `verses` テーブル

```sql
CREATE TABLE verses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id UUID REFERENCES locations(id),
  verse_text TEXT NOT NULL,
  explanation TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(location_id)
);
```

**行例**：
```
id: (UUID)
location_id: (UUID)
verse_text: '行く春や鳥啼き魚の目は涙'
explanation: '春が去りゆく季節に...（200字程度）'
```

### RLS（Row Level Security）

```sql
ALTER TABLE works ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE verses ENABLE ROW LEVEL SECURITY;

-- 全ユーザーが読み取り可能（公開データ）
CREATE POLICY "Public read" ON works FOR SELECT USING (is_published = true);
CREATE POLICY "Public read" ON chapters FOR SELECT USING (is_published = true);
CREATE POLICY "Public read" ON locations FOR SELECT USING (true);
CREATE POLICY "Public read" ON verses FOR SELECT USING (true);
```

---

## ファイル構成

### ディレクトリツリー

```
immersamap.github.io/
├── README.md                          （GitHub README）
├── SPECIFICATION.md                   ← 【本ドキュメント】
├── DESIGN.md                          （UI/UX詳細仕様）
├── CHANGELOG.md                       （更新履歴）
│
├── index.html                         （ランディングページ）
│
├── map/
│   └── index.html                     （地図探索モード）
│
├── okunohosomichi/
│   ├── index.html                     （『おくのほそ道』作品紹介）
│   ├── chapter-1.html                 ✅ 実装完了
│   ├── chapter-2.html                 ⏳ 実装予定
│   └── chapter-3.html                 ⏳ 実装予定
│
├── docs/
│   ├── ARCHITECTURE.md                （技術アーキテクチャ）
│   ├── API.md                         （Supabase API 仕様）
│   └── DEPLOYMENT.md                  （デプロイ手順）
│
├── map-editor.html                    （地図データエディタ）
├── polygon-editor.html                （ポリゴンエディタ）
├── create.html                        （コンテンツ作成補助）
├── kawagoe.html                       （川越事例）
└── kawagoe.jpg
```

---

## デプロイ

### GitHub Pages 自動デプロイ

```
1. ローカルで変更
2. git commit -m "..."
3. git push origin main
4. GitHub Actions が自動実行
5. 数分後、https://immersamap.github.io/ に反映
```

### デプロイ確認方法

```bash
# Deployments タブで確認
https://github.com/immersamap/immersamap.github.io/deployments

# ステータス：Active = デプロイ完了
```

---

## 今後の章計画

### 第2章：千住〜日光（予定）

```
- 地点数：12-15 地点
- 俳句数：3-5 個
- ルート：千住 → 栃木 → 日光
```

### 第3章：日光〜白河（予定）

```
- 地点数：10-12 地点
- 俳句数：2-3 個
- ルート：日光 → 白河の関
```

### 次のプロジェクト：『太平記』（2026年後半予定）

```
- 新田義貞・楠木正成・足利尊氏 関連地点
- 複数の地域にまたがる（全国規模）
- UI：時代背景を反映した配色
```

---

## 更新履歴

### Version 1.0（2026-05-26）

**第1章実装 + Alex Zhang デザインレビュー適用**

| 項目 | 変更内容 | ステータス |
|------|--------|----------|
| 地図タイル | OpenStreetMap → 国土地理院 + セピア化 | ✅ 完了 |
| マーカーUI | パネルスクロール → ポップアップ表示 | ✅ 完了 |
| 地図高さ | 40vh → 70vh（PC）/50vh（モバイル） | ✅ 完了 |
| ポップアップ | デザイン仕様実装（色・枠線・影・アニメーション） | ✅ 完了 |
| 再生機能 | マーカー自動ポップアップ表示 | ✅ 完了 |
| レスポンシブ | モバイル最適化 | ✅ 完了 |

**実装詳細**：
- HTML: 620行
- CSS: カスタムポップアップスタイル
- JavaScript: Supabase 統合、マーカー管理、再生ロジック
- Git Commit: `efe4a5d`

**テスト結果**: ✅ ALL PASS

---

## 更新予定（変更が発生した場合）

本ドキュメントは、以下の変更が発生した際に更新されます：

- [ ] 新しい章の実装
- [ ] UI/UX の改善
- [ ] Supabase スキーマの変更
- [ ] 新しい機能の追加
- [ ] デザイン仕様の更新

**更新フロー**：
```
仕様変更 → ドキュメント更新 → GitHub コミット → デプロイ
```

---

## 参考資料

- [Alex Zhang デザインレビュー](./docs/DESIGN_REVIEW.md)
- [Supabase スキーマ定義](./docs/schema_v2.sql)
- [実装ガイド](./docs/IMPLEMENTATION.md)

---

**最終承認**: Alex Zhang（Airbnb Senior Design Lead）⭐⭐⭐⭐⭐  
**作成日**: 2026-05-26  
**次回レビュー予定**: 2026-06-30（第2章実装後）
