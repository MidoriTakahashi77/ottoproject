"""
Vision API - 画像解析基盤API
Google OAuth認証（Supabase経由）で保護されたエンドポイントを提供
"""
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時の処理
    logger.info("Vision API starting up...")
    logger.info("Initializing ML models...")
    # TODO: YOLOv8モデルのロード
    yield
    # 終了時の処理
    logger.info("Vision API shutting down...")

# FastAPIアプリケーション
app = FastAPI(
    title="Vision API",
    description="画像解析基盤API - 物体検出、セグメンテーション、深度推定",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ヘルスチェック
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "service": "vision-api",
        "version": "1.0.0"
    }

# ルート
@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Vision API - 画像解析基盤",
        "docs": "/docs",
        "health": "/health"
    }

# APIバージョン情報
@app.get("/api/v1/info")
async def api_info():
    """API情報を返す"""
    return {
        "api": "Vision API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/v1/vision/upload",
            "detect": "/api/v1/vision/detect",
            "segment": "/api/v1/vision/segment",
            "depth": "/api/v1/vision/depth"
        }
    }

# TODO: 認証ミドルウェアの追加
# TODO: 画像アップロードエンドポイント
# TODO: 物体検出エンドポイント
# TODO: セグメンテーションエンドポイント
# TODO: 深度推定エンドポイント