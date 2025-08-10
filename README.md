# Kaglis - 家具認識アプリケーション

## プロジェクト構成

```
ottoproject/
├── kaglis-api/       # バックエンドAPI (Python/FastAPI)
│   ├── app/          # APIアプリケーション
│   ├── Dockerfile    # コンテナ設定
│   └── deploy.sh     # デプロイスクリプト
│
└── kaglis-frontend/  # フロントエンド (未実装)
```

## kaglis-api

家具認識APIサービス
- YOLOv8を使用した物体検出
- Cloud Runにデプロイ済み
- APIエンドポイント: https://furniture-detection-api-[ID]-an.a.run.app

### APIの使用方法

```bash
# ヘルスチェック
curl https://furniture-detection-api-[ID]-an.a.run.app/health

# 画像から家具を検出
curl -X POST https://furniture-detection-api-[ID]-an.a.run.app/api/detect \
  -F "image=@image.jpg" \
  -F "confidence_threshold=0.5"
```

### デプロイ方法

```bash
cd kaglis-api
./deploy.sh kaglis
```

## kaglis-frontend (作成予定)

Webフロントエンドアプリケーション
- 画像アップロード機能
- リアルタイム検出結果表示
- 検出結果の可視化

## 開発環境のセットアップ

### API (kaglis-api)

```bash
cd kaglis-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### フロントエンド (作成予定)

```bash
cd kaglis-frontend
npm install
npm run dev
```

## 技術スタック

- **バックエンド**: Python, FastAPI, YOLOv8, Google Cloud Run
- **フロントエンド**: (未定 - React/Vue.js/Next.js)
- **インフラ**: Google Cloud Platform (Cloud Run, Firestore, Artifact Registry)

## ライセンス

Private Project