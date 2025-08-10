# 家具認識API

画像から家具を自動検出し、種類と位置情報を返すAPIサービス

## 機能

- 画像から家具を自動検出
- 検出した家具の種類と位置（バウンディングボックス）を返却
- 日本語ラベル対応
- REST API形式（JSON）

## 技術スタック

- **ML Framework**: YOLOv8 (Ultralytics)
- **API Framework**: FastAPI (Python 3.10)
- **Infrastructure**: Google Cloud Run
- **Container**: Docker

## セットアップ

### 前提条件
- Docker & Docker Compose
- Make（オプション）
- Google Cloud SDK（本番デプロイ時）

### Docker Composeでの開発

#### 1. 環境設定
```bash
# 環境変数ファイルをコピー
cp .env.example .env
```

#### 2. 開発環境起動（推奨）
```bash
# Makefileを使用
make dev

# または直接Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

#### 3. 本番モード起動
```bash
# サービス起動
make up
# または
docker-compose up -d
```

#### 4. API確認
- API: http://localhost:8080
- API Docs (Swagger): http://localhost:8080/docs
- Firestore Emulator UI: http://localhost:4400
- Swagger UI (専用): http://localhost:8082

### 便利なコマンド

```bash
# ログ確認
make logs

# テスト実行
make test

# コンテナにシェル接続
make shell

# コードフォーマット
make format

# ヘルスチェック
make health

# クリーンアップ
make clean
```

## API使用方法

### 家具検出エンドポイント

**POST** `/api/detect`

```bash
curl -X POST "http://localhost:8080/api/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@sample.jpg" \
  -F "confidence_threshold=0.5"
```

### レスポンス例

```json
{
  "status": "success",
  "timestamp": "2024-01-01T00:00:00",
  "processing_time_ms": 1234,
  "image_info": {
    "width": 1920,
    "height": 1080,
    "format": "jpeg"
  },
  "detections": [
    {
      "detection_id": "uuid",
      "label": "chair",
      "label_ja": "椅子",
      "confidence": 0.95,
      "bbox": {
        "x": 100,
        "y": 200,
        "width": 150,
        "height": 200
      }
    }
  ],
  "summary": {
    "total_items": 5,
    "items_by_category": {
      "chair": 2,
      "couch": 1,
      "bed": 2
    },
    "detection_quality": "high"
  }
}
```

## デプロイ

### Google Cloud Runへのデプロイ

```bash
# GCPプロジェクト設定
export PROJECT_ID="your-project-id"
export REGION="asia-northeast1"

# APIの有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# イメージビルド&プッシュ
gcloud builds submit --tag gcr.io/${PROJECT_ID}/furniture-detection-api

# Cloud Runデプロイ
gcloud run deploy furniture-detection-api \
  --image gcr.io/${PROJECT_ID}/furniture-detection-api \
  --platform managed \
  --region ${REGION} \
  --memory 4Gi \
  --cpu 2 \
  --timeout 60 \
  --concurrency 10 \
  --max-instances 5 \
  --allow-unauthenticated
```

## 検出可能な家具カテゴリ

- 椅子 (chair)
- ソファ (couch)
- ベッド (bed)
- テーブル (dining table)
- テレビ (tv)
- 冷蔵庫 (refrigerator)
- オーブン (oven)
- シンク (sink)
- その他の家具・家電

## パフォーマンス

- レスポンス時間: 2-4秒（CPU推論）
- 検出精度: 75-85%（YOLOv8n使用時）
- 同時処理: 最大10リクエスト

## ライセンス

MIT License