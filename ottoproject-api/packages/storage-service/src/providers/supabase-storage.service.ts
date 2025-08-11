import { createClient, SupabaseClient } from '@supabase/supabase-js';
import {
  IStorageService,
  StorageResult,
  UploadOptions,
  SignedUrlOptions,
  StorageFile,
  ListOptions,
  StorageError
} from '../interfaces/storage.interface';

/**
 * Supabase Storageの実装
 */
export class SupabaseStorageService implements IStorageService {
  private supabase: SupabaseClient;

  constructor(
    supabaseUrl?: string,
    supabaseKey?: string
  ) {
    const url = supabaseUrl || process.env.SUPABASE_URL;
    const key = supabaseKey || process.env.SUPABASE_ANON_KEY;

    if (!url || !key) {
      throw new Error('Supabase URL and Key are required');
    }

    this.supabase = createClient(url, key);
  }

  async upload(
    bucket: string,
    path: string,
    file: Buffer | Blob | File,
    options?: UploadOptions
  ): Promise<StorageResult<{ path: string; url: string }>> {
    try {
      const uploadOptions: any = {
        upsert: options?.upsert ?? false,
        contentType: options?.contentType,
        cacheControl: options?.cacheControl
      };

      const { data, error } = await this.supabase.storage
        .from(bucket)
        .upload(path, file, uploadOptions);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      const url = this.getPublicUrl(bucket, data.path);

      return {
        data: {
          path: data.path,
          url
        },
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async download(
    bucket: string,
    path: string
  ): Promise<StorageResult<Blob>> {
    try {
      const { data, error } = await this.supabase.storage
        .from(bucket)
        .download(path);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      return {
        data: data,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async delete(
    bucket: string,
    paths: string | string[]
  ): Promise<StorageResult<void>> {
    try {
      const pathArray = Array.isArray(paths) ? paths : [paths];
      
      const { error } = await this.supabase.storage
        .from(bucket)
        .remove(pathArray);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      return {
        data: undefined,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async move(
    bucket: string,
    fromPath: string,
    toPath: string
  ): Promise<StorageResult<void>> {
    try {
      const { error } = await this.supabase.storage
        .from(bucket)
        .move(fromPath, toPath);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      return {
        data: undefined,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async copy(
    bucket: string,
    fromPath: string,
    toPath: string
  ): Promise<StorageResult<void>> {
    try {
      const { error } = await this.supabase.storage
        .from(bucket)
        .copy(fromPath, toPath);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      return {
        data: undefined,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async createSignedUrl(
    bucket: string,
    path: string,
    options: SignedUrlOptions
  ): Promise<StorageResult<{ signedUrl: string }>> {
    try {
      const signOptions: any = {
        expiresIn: options.expiresIn
      };

      if (options.download) {
        signOptions.download = options.download;
      }

      if (options.transform) {
        signOptions.transform = options.transform;
      }

      const { data, error } = await this.supabase.storage
        .from(bucket)
        .createSignedUrl(path, signOptions.expiresIn, signOptions);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      return {
        data: {
          signedUrl: data.signedUrl
        },
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  getPublicUrl(bucket: string, path: string): string {
    const { data } = this.supabase.storage
      .from(bucket)
      .getPublicUrl(path);
    
    return data.publicUrl;
  }

  async list(
    bucket: string,
    path?: string,
    options?: ListOptions
  ): Promise<StorageResult<StorageFile[]>> {
    try {
      const listOptions: any = {
        limit: options?.limit ?? 100,
        offset: options?.offset ?? 0
      };

      if (options?.sortBy) {
        listOptions.sortBy = {
          column: options.sortBy.column,
          order: options.sortBy.order
        };
      }

      const { data, error } = await this.supabase.storage
        .from(bucket)
        .list(path, listOptions);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      const files: StorageFile[] = (data || []).map(file => ({
        name: file.name,
        id: file.id,
        size: file.metadata?.size || 0,
        mimetype: file.metadata?.mimetype || 'application/octet-stream',
        created_at: file.created_at,
        updated_at: file.updated_at,
        metadata: file.metadata
      }));

      return {
        data: files,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async exists(bucket: string, path: string): Promise<boolean> {
    try {
      const { data } = await this.supabase.storage
        .from(bucket)
        .list(path.substring(0, path.lastIndexOf('/')), {
          limit: 1,
          search: path.substring(path.lastIndexOf('/') + 1)
        });

      return !!data && data.length > 0;
    } catch {
      return false;
    }
  }

  async createBucket(
    name: string,
    options?: {
      public?: boolean;
      fileSizeLimit?: number;
      allowedMimeTypes?: string[];
    }
  ): Promise<StorageResult<void>> {
    try {
      const { error } = await this.supabase.storage
        .createBucket(name, {
          public: options?.public ?? false,
          fileSizeLimit: options?.fileSizeLimit,
          allowedMimeTypes: options?.allowedMimeTypes
        });

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      return {
        data: undefined,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async deleteBucket(name: string): Promise<StorageResult<void>> {
    try {
      const { error } = await this.supabase.storage
        .deleteBucket(name);

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      return {
        data: undefined,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  async listBuckets(): Promise<StorageResult<string[]>> {
    try {
      const { data, error } = await this.supabase.storage
        .listBuckets();

      if (error) {
        return {
          data: null,
          error: this.mapError(error)
        };
      }

      const bucketNames = (data || []).map(bucket => bucket.name);

      return {
        data: bucketNames,
        error: null
      };
    } catch (error) {
      return {
        data: null,
        error: this.mapError(error)
      };
    }
  }

  private mapError(error: any): StorageError {
    // エラーが存在しない場合
    if (!error) {
      return { 
        message: 'Unknown error', 
        code: 'UNKNOWN_ERROR',
        statusCode: 500
      };
    }
    
    // 文字列エラーの場合
    if (typeof error === 'string') {
      return { 
        message: error, 
        code: 'ERROR',
        statusCode: 500
      };
    }
    
    // オブジェクトエラーの場合（Supabaseエラーまたは通常のError）
    return {
      message: error.message || error.error || 'Unknown error occurred',
      code: error.code || error.error_code || 'UNKNOWN_ERROR',
      statusCode: error.statusCode || error.status || 500
    };
  }
}