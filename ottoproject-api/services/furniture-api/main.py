"""
Furniture API - 家具認識API
家具に特化した認識・分析機能
"""
import os
from fastapi import FastAPI
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
    logger.info("Furniture API starting up...")
    yield
    # 終了時の処理
    logger.info("Furniture API shutting down...")

# FastAPIアプリケーション
app = FastAPI(
    title="Furniture API",
    description="家具認識API - 家具検出、属性分析、価格推定",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ヘルスチェック
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "furniture-api",
        "version": "1.0.0"
    }

# ルート
@app.get("/")
async def root():
    return {
        "message": "Furniture API - 家具認識",
        "docs": "/docs",
        "health": "/health"
    }