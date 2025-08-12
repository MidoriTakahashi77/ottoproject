# Otto Project API デプロイメントガイド

このガイドでは、Otto Project APIの各サービスをGoogle Cloud Runにデプロイする手順を説明します。

## 📋 目次

1. [前提条件](#前提条件)
2. [初回セットアップ](#初回セットアップ)
3. [各APIのデプロイ手順](#各apiのデプロイ手順)
4. [トラブルシューティング](#トラブルシューティング)
5. [デプロイ済みサービスの確認](#デプロイ済みサービスの確認)

## 前提条件

### 必要なツール

以下のツールがインストールされている必要があります：

- **Docker Desktop**: コンテナのビルドとテスト用
  - [インストール方法](https://docs.docker.com/desktop/)
- **Google Cloud SDK (gcloud)**: Cloud Runへのデプロイ用
  - [インストール方法](https://cloud.google.com/sdk/docs/install)
- **Git**: ソースコード管理用

### Google Cloudの準備

1. Google Cloudプロジェクトを作成または選択
2. 必要なAPIを有効化：
```bash
# プロジェクトIDを設定（例: your-project-id）
export PROJECT_ID=your-project-id

# 必要なAPIを有効化
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID
```

3. gcloudの認証：
```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```

## 初回セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/ottoproject.git
cd ottoproject/ottoproject-api
```

### 2. スクリプトに実行権限を付与

**重要**: デプロイスクリプトには実行権限が必要です。

```bash
# 全てのdeploy.shに実行権限を付与
chmod +x services/*/deploy.sh

# setup-secrets.shにも実行権限を付与
chmod +x services/asset-api/setup-secrets.sh

# 全API一括デプロイスクリプト（オプション）
chmod +x deploy-all.sh
```

### 3. Secret Managerの設定

APIサービスは以下のシークレットを使用します：

- `supabase-url`: SupabaseプロジェクトのURL
- `supabase-anon-key`: Supabaseの匿名キー
- `database-url`: PostgreSQLデータベースURL
- `redis-url`: RedisサーバーURL

#### 方法1: setup-secrets.shを使用（推奨）

```bash
cd services/asset-api
./setup-secrets.sh $PROJECT_ID
```

プロンプトに従って各シークレットの値を入力します。

#### 方法2: 手動で作成

```bash
# 各シークレットを作成
echo "https://your-project.supabase.co" | gcloud secrets create supabase-url --data-file=- --project=$PROJECT_ID
echo "your-anon-key" | gcloud secrets create supabase-anon-key --data-file=- --project=$PROJECT_ID
echo "postgresql://user:pass@host:5432/db" | gcloud secrets create database-url --data-file=- --project=$PROJECT_ID
echo "redis://localhost:6379" | gcloud secrets create redis-url --data-file=- --project=$PROJECT_ID
```

## 各APIのデプロイ手順

### 🚀 Asset API (Bun.js/Hono)

```bash
cd services/asset-api

# ローカルテスト（オプション）
docker build -f Dockerfile.prod -t asset-api:test .
docker run -d -p 8080:8080 --name asset-api-test asset-api:test
curl http://localhost:8080/health
docker stop asset-api-test && docker rm asset-api-test

# Cloud Runへデプロイ
./deploy.sh $PROJECT_ID
```

**仕様**:
- メモリ: 512MB
- CPU: 1
- ポート: 8080

### 🪑 Furniture API (Python/FastAPI)

```bash
cd services/furniture-api

# ローカルテスト（オプション）
docker build -f Dockerfile.prod -t furniture-api:test .
docker run -d -p 8080:8080 --name furniture-api-test furniture-api:test
curl http://localhost:8080/health
docker stop furniture-api-test && docker rm furniture-api-test

# Cloud Runへデプロイ
./deploy.sh $PROJECT_ID
```

**仕様**:
- メモリ: 1GB
- CPU: 2
- ポート: 8080

### 👁️ Vision API (Python/FastAPI + ML)

```bash
cd services/vision-api

# ローカルテスト（オプション）
# 注意: MLモデルを含むため、ビルドに10-15分かかる場合があります
docker build -f Dockerfile.prod -t vision-api:test .
docker run -d -p 8080:8080 --name vision-api-test vision-api:test
curl http://localhost:8080/health
docker stop vision-api-test && docker rm vision-api-test

# Cloud Runへデプロイ
./deploy.sh $PROJECT_ID
```

**仕様**:
- メモリ: 4GB
- CPU: 4
- ポート: 8080
- 注意: YOLOv8モデルを含むため、初回起動時に時間がかかります

## トラブルシューティング

### よくあるエラーと解決方法

#### 1. permission denied: ./deploy.sh

```bash
# 解決方法
chmod +x ./deploy.sh
```

#### 2. Secret Manager エラー

```bash
# シークレットが存在するか確認
gcloud secrets list --project=$PROJECT_ID

# シークレットを作成
echo "your-value" | gcloud secrets create secret-name --data-file=- --project=$PROJECT_ID
```

#### 3. Cloud Build権限エラー

```bash
# Cloud Build Service Accountに必要な権限を付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"
```

#### 4. 403 Forbidden（デプロイ後）

```bash
# パブリックアクセスを許可
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --region=asia-northeast1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID
```

#### 5. Dockerビルドエラー

```bash
# Dockerキャッシュをクリア
docker system prune -a

# 再ビルド
docker build --no-cache -f Dockerfile.prod -t service-name:test .
```

## デプロイ済みサービスの確認

### 全サービスの一覧表示

```bash
gcloud run services list --region=asia-northeast1 --project=$PROJECT_ID
```

### 特定サービスの詳細確認

```bash
# サービスURLを取得
gcloud run services describe asset-api \
  --region=asia-northeast1 \
  --project=$PROJECT_ID \
  --format="value(status.url)"
```

### ヘルスチェック

```bash
# Asset API
curl https://asset-api-xxxxx.a.run.app/health

# Furniture API  
curl https://furniture-api-xxxxx.a.run.app/health

# Vision API
curl https://vision-api-xxxxx.a.run.app/health
```

### ログの確認

```bash
gcloud run services logs read SERVICE_NAME \
  --region=asia-northeast1 \
  --project=$PROJECT_ID \
  --limit=50
```

## デプロイ後の確認事項

### ✅ チェックリスト

- [ ] 各APIのヘルスチェックエンドポイントが200 OKを返す
- [ ] Secret Managerの値が正しく設定されている
- [ ] Cloud Runのメモリ/CPU設定が適切
- [ ] 必要に応じてカスタムドメインを設定
- [ ] Cloud Monitoringでアラートを設定
- [ ] ログが正常に出力されている

## 本番環境への移行

### 推奨事項

1. **シークレットの更新**
   - プレースホルダー値から実際の値に更新
   ```bash
   echo "実際の値" | gcloud secrets versions add secret-name --data-file=-
   ```

2. **CI/CDパイプラインの設定**
   - GitHub Actionsまたは Cloud Build トリガーを設定
   - 自動テストとデプロイを実装

3. **スケーリング設定**
   ```bash
   gcloud run services update SERVICE_NAME \
     --min-instances=1 \
     --max-instances=100 \
     --region=asia-northeast1
   ```

4. **カスタムドメインの設定**
   ```bash
   gcloud run domain-mappings create \
     --service=SERVICE_NAME \
     --domain=api.yourdomain.com \
     --region=asia-northeast1
   ```

## サポート

問題が発生した場合は、以下を確認してください：

1. このドキュメントのトラブルシューティングセクション
2. `services/asset-api/.tmp/deploy-log.md` - Asset APIのデプロイログ
3. Google Cloud Console のログビューア
4. プロジェクトのGitHub Issues

## 更新履歴

- 2025-08-13: 初版作成
- Asset API、Furniture API、Vision APIのデプロイ手順を追加
- トラブルシューティングセクションを追加