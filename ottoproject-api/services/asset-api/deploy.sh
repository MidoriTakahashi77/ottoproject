#!/bin/bash

# Asset API デプロイスクリプト
# 使用方法: ./deploy.sh [PROJECT_ID]

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# プロジェクトID
PROJECT_ID=${1:-$(gcloud config get-value project)}

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}エラー: プロジェクトIDが指定されていません${NC}"
    echo "使用方法: ./deploy.sh [PROJECT_ID]"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Asset API Cloud Run デプロイ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}プロジェクト: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}サービス: asset-api${NC}"
echo -e "${YELLOW}リージョン: asia-northeast1${NC}"
echo ""

# 確認
read -p "デプロイを続行しますか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "デプロイをキャンセルしました"
    exit 1
fi

# Secret Managerにシークレットが存在するか確認
echo -e "\n${YELLOW}シークレットの確認...${NC}"
REQUIRED_SECRETS=("supabase-url" "supabase-anon-key" "database-url" "redis-url")

for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! gcloud secrets describe $secret --project=$PROJECT_ID &>/dev/null; then
        echo -e "${RED}警告: シークレット '$secret' が存在しません${NC}"
        echo "作成例: echo 'YOUR_SECRET_VALUE' | gcloud secrets create $secret --data-file=-"
    else
        echo -e "${GREEN}✓ $secret${NC}"
    fi
done

# Cloud Buildの実行
echo -e "\n${YELLOW}Cloud Buildを開始しています...${NC}"
gcloud builds submit \
    --config=cloudbuild.yaml \
    --project=$PROJECT_ID \
    --substitutions=COMMIT_SHA=$(git rev-parse HEAD)

# デプロイ結果の確認
echo -e "\n${YELLOW}デプロイ状況を確認しています...${NC}"
SERVICE_URL=$(gcloud run services describe asset-api \
    --region=asia-northeast1 \
    --project=$PROJECT_ID \
    --format='value(status.url)')

# パブリックアクセス権限の設定（念のため）
echo -e "\n${YELLOW}パブリックアクセス権限を設定しています...${NC}"
gcloud run services add-iam-policy-binding asset-api \
    --region=asia-northeast1 \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID \
    --quiet 2>/dev/null || true

if [ -n "$SERVICE_URL" ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}デプロイが完了しました！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\nサービスURL: ${SERVICE_URL}"
    echo -e "\nヘルスチェック: ${SERVICE_URL}/health"
    echo ""
    
    # ヘルスチェック実行
    echo -e "${YELLOW}ヘルスチェックを実行しています...${NC}"
    sleep 5
    if curl -s "${SERVICE_URL}/health" | grep -q "healthy"; then
        echo -e "${GREEN}✓ APIは正常に動作しています${NC}"
    else
        echo -e "${RED}✗ ヘルスチェックに失敗しました${NC}"
    fi
else
    echo -e "${RED}デプロイに失敗しました${NC}"
    exit 1
fi