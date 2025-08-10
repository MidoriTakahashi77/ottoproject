-- 初期スキーマ作成
CREATE SCHEMA IF NOT EXISTS vision;
CREATE SCHEMA IF NOT EXISTS furniture;
CREATE SCHEMA IF NOT EXISTS spatial;
CREATE SCHEMA IF NOT EXISTS assets;
CREATE SCHEMA IF NOT EXISTS scene3d;

-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 共通テーブル：ユーザープロファイル（Google OAuth用）
-- 注: Supabase使用時はauth.usersテーブルと連携
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    google_id TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 共通テーブル：リクエストログ
CREATE TABLE IF NOT EXISTS public.request_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vision API用テーブル
CREATE TABLE IF NOT EXISTS vision.images (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID,
    storage_url TEXT NOT NULL,
    format VARCHAR(10) NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    hash VARCHAR(64) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS vision.detections (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    image_id UUID REFERENCES vision.images(id),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    objects JSONB NOT NULL,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON public.request_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_request_logs_user_id ON public.request_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_images_user_id ON vision.images(user_id);
CREATE INDEX IF NOT EXISTS idx_images_hash ON vision.images(hash);
CREATE INDEX IF NOT EXISTS idx_detections_image_id ON vision.detections(image_id);