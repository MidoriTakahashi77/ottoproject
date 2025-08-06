"""
FastAPI メインアプリケーション
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.routers import detection
from app.services.detector import FurnitureDetector

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# グローバル変数でdetectorを保持
detector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    global detector
    logger.info("Starting up...")
    # YOLOv8モデルの初期化
    detector = FurnitureDetector()
    logger.info("Model loaded successfully")
    yield
    logger.info("Shutting down...")

# FastAPIアプリケーション初期化
app = FastAPI(
    title="家具認識API",
    description="画像から家具を検出するAPIサービス",
    version="0.1.0",
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

# ルーター登録
app.include_router(detection.router, prefix="/api", tags=["detection"])

@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "service": "furniture-detection-api",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """詳細ヘルスチェック"""
    global detector
    return {
        "status": "healthy",
        "model_loaded": detector is not None,
        "model_type": detector.model_name if detector else None
    }

# detectorをappの状態として保存
app.state.detector = lambda: detector