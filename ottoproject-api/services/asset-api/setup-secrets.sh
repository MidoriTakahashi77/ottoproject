#!/bin/bash

# Secret Manager セットアップスクリプト
# Asset API用のシークレットを作成

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ID=${1:-$(gcloud config get-value project)}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Secret Manager セットアップ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}プロジェクト: ${PROJECT_ID}${NC}"
echo ""

# Supabase URL
echo -e "${YELLOW}Supabase URLを入力してください:${NC}"
read -r SUPABASE_URL
if [ -z "$SUPABASE_URL" ]; then
    SUPABASE_URL="https://your-project.supabase.co"
    echo -e "${YELLOW}デフォルト値を使用: ${SUPABASE_URL}${NC}"
fi

# Supabase Anon Key
echo -e "${YELLOW}Supabase Anon Keyを入力してください:${NC}"
read -r SUPABASE_ANON_KEY
if [ -z "$SUPABASE_ANON_KEY" ]; then
    SUPABASE_ANON_KEY="your-anon-key"
    echo -e "${YELLOW}デフォルト値を使用: ${SUPABASE_ANON_KEY}${NC}"
fi

# Database URL
echo -e "${YELLOW}Database URLを入力してください (例: postgresql://user:pass@host:5432/db):${NC}"
read -r DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    DATABASE_URL="postgresql://ottouser:ottopass@localhost:5432/ottodb"
    echo -e "${YELLOW}デフォルト値を使用: ${DATABASE_URL}${NC}"
fi

# Redis URL
echo -e "${YELLOW}Redis URLを入力してください (例: redis://localhost:6379):${NC}"
read -r REDIS_URL
if [ -z "$REDIS_URL" ]; then
    REDIS_URL="redis://localhost:6379"
    echo -e "${YELLOW}デフォルト値を使用: ${REDIS_URL}${NC}"
fi

echo ""
echo -e "${YELLOW}シークレットを作成しています...${NC}"

# Supabase URL
echo -n "$SUPABASE_URL" | gcloud secrets create supabase-url \
    --data-file=- \
    --project=$PROJECT_ID \
    2>/dev/null || echo -e "${YELLOW}supabase-url は既に存在します${NC}"

# Supabase Anon Key
echo -n "$SUPABASE_ANON_KEY" | gcloud secrets create supabase-anon-key \
    --data-file=- \
    --project=$PROJECT_ID \
    2>/dev/null || echo -e "${YELLOW}supabase-anon-key は既に存在します${NC}"

# Database URL
echo -n "$DATABASE_URL" | gcloud secrets create database-url \
    --data-file=- \
    --project=$PROJECT_ID \
    2>/dev/null || echo -e "${YELLOW}database-url は既に存在します${NC}"

# Redis URL
echo -n "$REDIS_URL" | gcloud secrets create redis-url \
    --data-file=- \
    --project=$PROJECT_ID \
    2>/dev/null || echo -e "${YELLOW}redis-url は既に存在します${NC}"

echo ""
echo -e "${GREEN}✅ シークレットの作成が完了しました${NC}"
echo ""
echo -e "${YELLOW}作成されたシークレット:${NC}"
gcloud secrets list --project=$PROJECT_ID