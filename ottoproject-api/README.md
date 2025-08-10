# Otto Project API - 思い出再構成アプリ群API

画像から空間を再構成し、3D/VR/AR体験を提供するAPIシステム

## 🚀 クイックスタート

### 1. 環境変数設定
```bash
cp .env.example .env
# .envファイルを編集してSupabase情報を設定
```

### 2. Docker環境起動
```bash
make up
```

### 3. Supabaseセットアップ
```bash
npx supabase init
npx supabase start
```

### 4. APIアクセス
- Vision API: http://localhost:8001
- Furniture API: http://localhost:8002  
- Asset API: http://localhost:8003
- API Documentation: http://localhost:8001/docs

## 📁 プロジェクト構造

```
ottoproject-api/
├── services/           # 各APIサービス
│   ├── vision-api/    # 画像解析基盤API (Python/FastAPI)
│   ├── furniture-api/ # 家具認識API (Python/FastAPI)
│   ├── spatial-api/   # 空間配置推定API (Python/FastAPI)
│   ├── asset-api/     # アセットマッチングAPI (Hono/Node.js)
│   └── scene3d-api/   # 3D空間構築API (Python/FastAPI)
├── packages/          # 共通パッケージ
│   ├── common-types/  # 共通型定義
│   ├── common-utils/  # 共通ユーティリティ
│   └── common-middleware/ # 共通ミドルウェア
├── scripts/          # ビルド・デプロイスクリプト
├── docs/            # ドキュメント
├── deploy/          # デプロイ設定
├── supabase/        # Supabase設定
└── docker-compose.yml # ローカル開発環境
```

## 🔐 認証

すべてのAPIはGoogle OAuth認証（Supabase Auth経由）で保護されています。

### 認証フロー
1. Google OAuth でログイン
2. SupabaseからJWTトークン取得
3. API呼び出し時にBearer tokenとして使用

```javascript
// 認証例
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google'
})

// API呼び出し
fetch('http://localhost:8001/api/v1/vision/detect', {
  headers: {
    'Authorization': `Bearer ${session.access_token}`
  }
})
```

## 🛠 開発

### 主要コマンド
```bash
make up        # サービス起動
make down      # サービス停止
make logs      # ログ表示
make test      # テスト実行
make migrate   # DBマイグレーション
```

### 個別サービス操作
```bash
make vision-logs     # Vision APIログ
make vision-shell    # Vision APIシェル
make db-shell        # PostgreSQL接続
make redis-cli       # Redis接続
```

## 🚢 デプロイ

本番環境はGoogle Cloud Platform (GCP) Cloud Runにデプロイされます。

```bash
# GCPへのデプロイ
gcloud run deploy vision-api --source services/vision-api
```

## 📚 API仕様

詳細な仕様は[api_specification.md](../api_specification.md)を参照してください。

### 主要エンドポイント

#### Vision API
- `POST /api/v1/vision/upload` - 画像アップロード
- `POST /api/v1/vision/detect` - 物体検出
- `POST /api/v1/vision/segment` - セグメンテーション

#### Furniture API  
- `POST /api/v1/furniture/detect` - 家具検出
- `POST /api/v1/furniture/attributes` - 属性分析

#### Asset API
- `POST /api/v1/assets/search` - 類似検索
- `POST /api/v1/assets/coordinate` - コーディネート提案

## 📝 ライセンス

Copyright (c) 2024 Otto Project