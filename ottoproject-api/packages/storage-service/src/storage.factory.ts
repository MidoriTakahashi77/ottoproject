import { IStorageService, StorageProvider } from './interfaces/storage.interface';
import { SupabaseStorageService } from './providers/supabase-storage.service';

/**
 * ストレージサービスのファクトリークラス
 * 環境変数に基づいて適切なストレージプロバイダーを返す
 */
export class StorageFactory {
  private static instance: IStorageService | null = null;

  /**
   * ストレージサービスのインスタンスを取得
   * シングルトンパターンで実装
   */
  static getStorageService(
    provider?: StorageProvider,
    config?: any
  ): IStorageService {
    // 既存のインスタンスがあり、プロバイダーが変更されていない場合はそれを返す
    if (this.instance && !provider) {
      return this.instance;
    }

    // プロバイダーの決定（環境変数から読み取り、指定がなければSupabase）
    const selectedProvider = provider || 
      (process.env.STORAGE_PROVIDER as StorageProvider) || 
      StorageProvider.SUPABASE;

    // プロバイダーに応じてインスタンスを作成
    switch (selectedProvider) {
      case StorageProvider.SUPABASE:
        this.instance = new SupabaseStorageService(
          config?.supabaseUrl || process.env.SUPABASE_URL,
          config?.supabaseKey || process.env.SUPABASE_ANON_KEY
        );
        break;


      case StorageProvider.S3:
        // TODO: S3実装時に追加
        throw new Error('S3 storage provider not implemented yet');

      case StorageProvider.MINIO:
        // TODO: MinIO実装時に追加
        throw new Error('MinIO storage provider not implemented yet');

      default:
        throw new Error(`Unknown storage provider: ${selectedProvider}`);
    }

    console.log(`Storage service initialized with provider: ${selectedProvider}`);
    return this.instance;
  }

  /**
   * 現在のストレージプロバイダーを取得
   */
  static getCurrentProvider(): StorageProvider {
    return (process.env.STORAGE_PROVIDER as StorageProvider) || StorageProvider.SUPABASE;
  }

  /**
   * インスタンスをリセット（主にテスト用）
   */
  static reset(): void {
    this.instance = null;
  }
}