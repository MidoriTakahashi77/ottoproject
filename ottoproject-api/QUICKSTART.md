# クイックスタートガイド

Otto Project APIを最速でデプロイする手順です。詳細は[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)を参照してください。

## 🚀 5分でデプロイ

### 1. 環境変数の設定

```bash
# あなたのGoogle CloudプロジェクトIDに置き換えてください
export PROJECT_ID=your-project-id
```

### 2. 必要なAPIの有効化

```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com \
  containerregistry.googleapis.com secretmanager.googleapis.com \
  --project=$PROJECT_ID
```

### 3. 実行権限の付与

```bash
# ottoproject-apiディレクトリで実行
chmod +x services/*/deploy.sh services/asset-api/setup-secrets.sh
```

### 4. シークレットの作成（プレースホルダー使用）

```bash
# 開発環境用のプレースホルダー値でシークレットを作成
for secret in supabase-url supabase-anon-key database-url redis-url; do
  echo "placeholder-value" | gcloud secrets create $secret \
    --data-file=- --project=$PROJECT_ID 2>/dev/null || true
done
```

### 5. 各APIのデプロイ

#### Asset API（最も軽量）
```bash
cd services/asset-api
./deploy.sh $PROJECT_ID
```

#### Furniture API
```bash
cd ../furniture-api  
./deploy.sh $PROJECT_ID
```

#### Vision API（MLモデル含む - 時間がかかります）
```bash
cd ../vision-api
./deploy.sh $PROJECT_ID
```

## ✅ デプロイ確認

```bash
# サービス一覧
gcloud run services list --region=asia-northeast1 --project=$PROJECT_ID

# ヘルスチェック（URLは上記コマンドで確認）
curl https://[SERVICE-NAME]-xxxxx.a.run.app/health
```

## ⚠️ 注意事項

- Vision APIは機械学習モデルを含むため、ビルドとデプロイに15-20分かかる場合があります
- 初回デプロイ時は403エラーが出る場合があります。その場合は以下を実行：

```bash
gcloud run services add-iam-policy-binding [SERVICE-NAME] \
  --region=asia-northeast1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID
```

## 🔍 トラブルシューティング

問題が発生した場合は[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md#トラブルシューティング)を参照してください。