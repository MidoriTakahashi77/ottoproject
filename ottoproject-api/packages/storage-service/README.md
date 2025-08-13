# Storage Service

統一されたストレージインターフェースを提供するパッケージ。
現在はSupabase Storageを使用していますが、将来的にGCSやS3に切り替え可能な設計になっています。

## インストール

```bash
npm install @ottoproject/storage-service
```

## 使用方法

### TypeScript/JavaScript

```typescript
import StorageFactory from '@ottoproject/storage-service';

// ストレージサービスのインスタンスを取得
const storage = StorageFactory.getStorageService();

// ファイルをアップロード
const result = await storage.upload(
  'images',
  'path/to/image.jpg',
  fileBuffer,
  {
    contentType: 'image/jpeg',
    upsert: true
  }
);

if (result.error) {
  console.error('Upload failed:', result.error);
} else {
  console.log('File uploaded:', result.data.url);
}

// ファイルをダウンロード
const downloadResult = await storage.download('images', 'path/to/image.jpg');

// 署名付きURLを生成
const signedUrlResult = await storage.createSignedUrl(
  'images',
  'path/to/image.jpg',
  {
    expiresIn: 3600, // 1時間
    transform: {
      width: 300,
      height: 300,
      quality: 80
    }
  }
);

// ファイル一覧を取得
const listResult = await storage.list('images', 'path/to/', {
  limit: 10,
  sortBy: {
    column: 'created_at',
    order: 'desc'
  }
});
```

### Python

```python
from storage_service import StorageFactory

# ストレージサービスのインスタンスを取得
storage = StorageFactory.get_storage_service()

# ファイルをアップロード
result = await storage.upload(
    bucket="images",
    path="path/to/image.jpg",
    file=file_bytes,
    options={
        "content_type": "image/jpeg",
        "upsert": True
    }
)

if result["error"]:
    print(f"Upload failed: {result['error']}")
else:
    print(f"File uploaded: {result['data']['url']}")
```

## 環境変数

```bash
# ストレージプロバイダー (supabase, s3, minio)
STORAGE_PROVIDER=supabase

# Supabase設定
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

## バケット構成

Supabase Dashboardで以下のバケットを作成してください：

- `images` - アップロードされた画像
- `processed-results` - 処理結果のJSON
- `3d-models` - 3Dモデルファイル
- `temp-files` - 一時ファイル（24時間で自動削除）

## 移行ガイド

### MinIOからSupabaseへの移行

```typescript
// Before (MinIO直接使用)
const minioClient = new Minio.Client({...});
await minioClient.putObject('bucket', 'path', stream);

// After (Storage Service)
const storage = StorageFactory.getStorageService();
await storage.upload('bucket', 'path', buffer);
```

### 他のストレージプロバイダーへの移行

将来的にS3やMinIOに移行する場合、環境変数を変更するだけで切り替え可能な設計になっています。

コードの変更は不要です。