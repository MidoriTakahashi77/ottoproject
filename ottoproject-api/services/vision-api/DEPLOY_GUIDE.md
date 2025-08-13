# Vision API デプロイガイド

## 概要
Vision APIは、YOLOv8を使用した物体検出機能を提供するMLベースのマイクロサービスです。

## 特徴
- **YOLOv8 Medium Model**: 高精度な物体検出
- **プライバシー保護**: 画像の非保存、EXIF情報の自動削除
- **家具検出特化**: 室内の家具や物体の検出に最適化
- **シーン分析**: 部屋タイプの推定と複雑さの評価

## デプロイ要件

### リソース要件
- **CPU**: 4 vCPU（ML処理のため）
- **メモリ**: 4GB RAM（YOLOv8モデル用）
- **ストレージ**: 2GB以上（モデルファイル含む）

### 必要なシークレット
```bash
# Secret Managerに以下のシークレットが必要（他のAPIと共通）
- supabase-url
- supabase-anon-key
- database-url
- redis-url
```

## デプロイ手順

### 1. ローカルテスト
```bash
# プロダクションイメージのビルド
docker build -f Dockerfile.prod -t vision-api:prod .

# ローカルテスト
docker run -d -p 8080:8080 -e PORT=8080 vision-api:prod

# ヘルスチェック
curl http://localhost:8080/api/v1/vision/health

# 画像解析テスト
curl -X POST http://localhost:8080/api/v1/vision/analyze \
  -F "file=@sample.jpg" \
  -F "confidence_threshold=0.5"
```

### 2. Cloud Runへのデプロイ
```bash
# デプロイスクリプトを使用
./deploy.sh [PROJECT_ID]

# または手動でCloud Buildを実行
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=[PROJECT_ID] \
  --substitutions=COMMIT_SHA=$(git rev-parse HEAD)
```

### 3. デプロイ後の確認
```bash
# サービスURLの取得
SERVICE_URL=$(gcloud run services describe vision-api \
  --region=asia-northeast1 \
  --format='value(status.url)')

# ヘルスチェック
curl ${SERVICE_URL}/api/v1/vision/health

# 画像解析テスト
curl -X POST ${SERVICE_URL}/api/v1/vision/analyze \
  -F "file=@test.jpg" \
  -F "confidence_threshold=0.5"
```

## ビルド時間について

### 注意事項
- **初回ビルド**: 15-20分（YOLOv8モデルのダウンロード含む）
- **2回目以降**: 5-10分（キャッシュ利用）
- **コールドスタート**: 最初のリクエストは10-20秒かかる場合あり

### ビルド最適化
1. **マルチステージビルド**: イメージサイズの削減
2. **モデルの事前ダウンロード**: ビルド時にYOLOv8モデルを含める
3. **依存関係のキャッシュ**: requirements.txtの変更がない限りキャッシュ利用

## API エンドポイント

### ヘルスチェック
```
GET /api/v1/vision/health
```

### 画像解析
```
POST /api/v1/vision/analyze
Content-Type: multipart/form-data

Parameters:
- file: 画像ファイル（JPEG, PNG, WebP）
- confidence_threshold: 検出閾値（0.0-1.0、デフォルト: 0.5）
```

### サポートカテゴリ取得
```
GET /api/v1/vision/supported-categories
```

## トラブルシューティング

### ビルドエラー
```bash
# libgl1-mesa-glx not foundエラーの場合
# Dockerfile.prodで以下を確認:
RUN apt-get install -y libgl1 libglx0

# モデルダウンロードエラーの場合
# ネットワーク接続を確認し、再度ビルド
```

### デプロイエラー
```bash
# メモリ不足エラー
# cloudbuild.yamlで以下を確認:
--memory=4Gi  # 最低4GB必要

# タイムアウトエラー
# cloudbuild.yamlで以下を確認:
--timeout=300  # ML処理のため長めに設定
```

### 実行時エラー
```bash
# YOLOモデルロードエラー
# 環境変数を確認:
YOLO_MODEL=yolov8m.pt

# 権限エラー
# 非rootユーザー設定を確認
```

## パフォーマンス最適化

### 推奨設定
- **最小インスタンス数**: 0（コスト削減）
- **最大インスタンス数**: 5（負荷に応じて調整）
- **同時実行数**: 50（ML処理のため制限）
- **CPUスレッド数**: 4（OMP_NUM_THREADS=4）

### コスト削減のヒント
1. **最小インスタンス0**: アイドル時のコストをゼロに
2. **YOLOv8 Mediumモデル**: 精度とコストのバランス
3. **画像の前処理**: クライアント側でリサイズしてから送信

## セキュリティ

### 実装済みの対策
- **EXIF情報削除**: プライバシー保護
- **画像非保存**: メモリ上でのみ処理
- **非rootユーザー実行**: セキュリティ強化
- **ファイルサイズ制限**: 10MB以下

### 推奨事項
- APIキー認証の実装（本番環境）
- レート制限の設定
- CORS設定の適切な構成

## モニタリング

### ヘルスチェック
- エンドポイント: `/api/v1/vision/health`
- モデルロード状態の確認
- レスポンス時間の監視

### ログ確認
```bash
# Cloud Runログの確認
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=vision-api" \
  --limit 50 \
  --project=[PROJECT_ID]
```

## 更新手順

### モデルの更新
```bash
# Dockerfile.prodで使用モデルを変更
ENV YOLO_MODEL=yolov8l.pt  # Large modelに変更

# 再デプロイ
./deploy.sh [PROJECT_ID]
```

### コードの更新
```bash
# 変更をコミット
git add .
git commit -m "Update Vision API"

# デプロイ
./deploy.sh [PROJECT_ID]
```

## サポート

問題が発生した場合は、以下を確認してください：
1. Cloud Runのログ
2. ヘルスチェックエンドポイント
3. YOLOモデルのロード状態
4. メモリ使用量とCPU使用率