#!/bin/bash

# Cloud Run デプロイスクリプト
# 使用方法: ./deploy.sh [project-id]

set -e  # エラーで停止

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# プロジェクトID設定
PROJECT_ID=${1:-furniture-detection-api}
REGION="asia-northeast1"
SERVICE_NAME="furniture-detection-api"
IMAGE_NAME="furniture-detection"

echo -e "${GREEN}🚀 家具認識API デプロイスクリプト${NC}"
echo "=================================="

# 1. プロジェクトID確認
echo -e "\n${YELLOW}📋 プロジェクト設定${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# 現在のプロジェクト確認
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}プロジェクトを切り替えます: $CURRENT_PROJECT -> $PROJECT_ID${NC}"
    gcloud config set project $PROJECT_ID
fi

# 2. 必要なAPIの有効化確認
echo -e "\n${YELLOW}🔌 API有効化チェック${NC}"
REQUIRED_APIS=(
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
    "cloudbuild.googleapis.com"
    "firestore.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo "✅ $api - 有効"
    else
        echo "⚠️  $api - 有効化中..."
        gcloud services enable $api
    fi
done

# 3. Artifact Registry リポジトリ確認/作成
echo -e "\n${YELLOW}📦 Artifact Registry 設定${NC}"
REPOSITORY="furniture-detection"
if ! gcloud artifacts repositories describe $REPOSITORY --location=$REGION &>/dev/null; then
    echo "リポジトリを作成します: $REPOSITORY"
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --description="Furniture Detection API Docker images"
else
    echo "✅ リポジトリ存在確認: $REPOSITORY"
fi

# Docker認証設定
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# 4. Firestore確認
echo -e "\n${YELLOW}🗄️ Firestore 確認${NC}"
if ! gcloud firestore databases list --format="value(name)" | grep -q "projects/$PROJECT_ID"; then
    echo "Firestoreデータベースを作成します..."
    gcloud firestore databases create --location=$REGION
else
    echo "✅ Firestoreデータベース確認済み"
fi

# 5. 環境変数ファイル確認
echo -e "\n${YELLOW}⚙️ 環境変数設定${NC}"
if [ ! -f ".env.production" ]; then
    echo "⚠️  .env.production が見つかりません"
    echo "テンプレートから作成します..."
    cp .env.production.example .env.production
    
    # プロジェクトIDを自動設定
    sed -i.bak "s/your-project-id/$PROJECT_ID/g" .env.production
    
    # APIキー生成
    API_KEY=$(openssl rand -hex 32)
    sed -i.bak "s/your-secure-api-key-here-change-this/$API_KEY/g" .env.production
    
    echo "✅ .env.production を作成しました"
    echo "⚠️  APIキー: $API_KEY"
    echo "   （このキーを安全に保管してください）"
else
    echo "✅ .env.production 確認済み"
fi

# 6. Cloud Buildでイメージビルド
echo -e "\n${YELLOW}🔨 Cloud Buildでイメージビルド${NC}"
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"
echo "イメージ: $IMAGE_TAG"

# Cloud Buildを使用してビルド（プラットフォーム互換性を確保）
gcloud builds submit --tag $IMAGE_TAG .

# 8. Cloud Runデプロイ
echo -e "\n${YELLOW}☁️ Cloud Run デプロイ${NC}"

# サービスが存在するか確認
if gcloud run services describe $SERVICE_NAME --region=$REGION &>/dev/null; then
    echo "既存のサービスを更新します..."
    ACTION="update"
else
    echo "新しいサービスをデプロイします..."
    ACTION="deploy"
fi

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --memory 4Gi \
    --cpu 2 \
    --timeout 60 \
    --concurrency 80 \
    --max-instances 10 \
    --min-instances 0 \
    --allow-unauthenticated \
    --set-env-vars="ENV=production,DEBUG=false,LOG_LEVEL=INFO,GCP_PROJECT_ID=$PROJECT_ID,MODEL_SIZE=n,CONFIDENCE_THRESHOLD=0.5,MAX_FILE_SIZE_MB=10,ALLOWED_ORIGINS=*,API_KEY=,ENABLE_CACHE=false,CACHE_TTL_SECONDS=3600"

# 9. サービスURL取得
echo -e "\n${GREEN}✅ デプロイ完了！${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

echo "=================================="
echo -e "${GREEN}🎉 デプロイ成功！${NC}"
echo ""
echo "サービスURL: $SERVICE_URL"
echo ""
echo "テスト方法:"
echo "  curl ${SERVICE_URL}/health"
echo ""
echo "Swagger UI:"
echo "  ${SERVICE_URL}/docs"
echo ""
echo "画像検出テスト:"
echo '  curl -X POST '${SERVICE_URL}'/api/detect \'
echo '    -F "image=@sample.jpg" \'
echo '    -F "confidence_threshold=0.5"'
echo ""
echo "=================================="

# 10. ヘルスチェック
echo -e "\n${YELLOW}🏥 ヘルスチェック実行${NC}"
sleep 5  # サービス起動待ち
if curl -s "${SERVICE_URL}/health" | grep -q "healthy"; then
    echo -e "${GREEN}✅ サービスは正常に動作しています${NC}"
else
    echo -e "${RED}⚠️ ヘルスチェック失敗 - ログを確認してください：${NC}"
    echo "  gcloud logs tail --service-name=$SERVICE_NAME"
fi