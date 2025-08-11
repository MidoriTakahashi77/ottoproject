/**
 * ストレージサービスの共通インターフェース
 * 将来的にSupabase StorageからGCSへの移行を容易にするための抽象化層
 */

export interface UploadOptions {
  contentType?: string;
  cacheControl?: string;
  upsert?: boolean;
  metadata?: Record<string, string>;
}

export interface SignedUrlOptions {
  expiresIn: number; // seconds
  download?: boolean | string;
  transform?: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'avif' | 'auto';
  };
}

export interface StorageFile {
  name: string;
  id?: string;
  size: number;
  mimetype: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, string>;
}

export interface ListOptions {
  limit?: number;
  offset?: number;
  sortBy?: {
    column: 'name' | 'created_at' | 'updated_at';
    order: 'asc' | 'desc';
  };
}

export interface StorageError {
  message: string;
  code?: string;
  statusCode?: number;
}

export type StorageResult<T> = 
  | { data: T; error: null }
  | { data: null; error: StorageError };

/**
 * ストレージサービスインターフェース
 */
export interface IStorageService {
  /**
   * ファイルをアップロード
   */
  upload(
    bucket: string,
    path: string,
    file: Buffer | Blob | File,
    options?: UploadOptions
  ): Promise<StorageResult<{ path: string; url: string }>>;

  /**
   * ファイルをダウンロード
   */
  download(
    bucket: string,
    path: string
  ): Promise<StorageResult<Blob>>;

  /**
   * ファイルを削除
   */
  delete(
    bucket: string,
    paths: string | string[]
  ): Promise<StorageResult<void>>;

  /**
   * ファイルを移動/リネーム
   */
  move(
    bucket: string,
    fromPath: string,
    toPath: string
  ): Promise<StorageResult<void>>;

  /**
   * ファイルをコピー
   */
  copy(
    bucket: string,
    fromPath: string,
    toPath: string
  ): Promise<StorageResult<void>>;

  /**
   * 署名付きURLを生成
   */
  createSignedUrl(
    bucket: string,
    path: string,
    options: SignedUrlOptions
  ): Promise<StorageResult<{ signedUrl: string }>>;

  /**
   * 公開URLを取得
   */
  getPublicUrl(
    bucket: string,
    path: string
  ): string;

  /**
   * ファイル一覧を取得
   */
  list(
    bucket: string,
    path?: string,
    options?: ListOptions
  ): Promise<StorageResult<StorageFile[]>>;

  /**
   * ファイルが存在するか確認
   */
  exists(
    bucket: string,
    path: string
  ): Promise<boolean>;

  /**
   * バケットを作成
   */
  createBucket(
    name: string,
    options?: {
      public?: boolean;
      fileSizeLimit?: number;
      allowedMimeTypes?: string[];
    }
  ): Promise<StorageResult<void>>;

  /**
   * バケットを削除
   */
  deleteBucket(
    name: string
  ): Promise<StorageResult<void>>;

  /**
   * バケット一覧を取得
   */
  listBuckets(): Promise<StorageResult<string[]>>;
}

/**
 * ストレージプロバイダーの種類
 */
export enum StorageProvider {
  SUPABASE = 'supabase',
  S3 = 's3',
  MINIO = 'minio'
}