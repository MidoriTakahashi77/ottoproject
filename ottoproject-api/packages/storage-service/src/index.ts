/**
 * ストレージサービスパッケージのエントリーポイント
 */

export * from './interfaces/storage.interface';
export * from './storage.factory';
export * from './providers/supabase-storage.service';

// デフォルトエクスポート
import { StorageFactory } from './storage.factory';
export default StorageFactory;