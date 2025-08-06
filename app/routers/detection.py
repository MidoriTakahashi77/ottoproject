"""
家具検出APIエンドポイント
"""
import time
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from PIL import Image
import io

from app.models.schemas import DetectionResponse, ErrorResponse, ImageInfo, DetectionSummary, Detection
from app.services.detector import FurnitureDetector

logger = logging.getLogger(__name__)

router = APIRouter()

# 許可される画像形式
ALLOWED_FORMATS = {'image/jpeg', 'image/png', 'image/webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/detect", response_model=DetectionResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    413: {"model": ErrorResponse, "description": "File too large"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"}
})
async def detect_furniture(
    request: Request,
    image: UploadFile = File(..., description="検出対象の画像"),
    confidence_threshold: float = Query(0.5, ge=0.0, le=1.0, description="信頼度閾値"),
    enable_segmentation: bool = Query(False, description="セグメンテーション有効化（未実装）")
):
    """
    画像から家具を検出
    
    - **image**: JPEG, PNG, WebP形式の画像ファイル（最大10MB）
    - **confidence_threshold**: 検出の信頼度閾値（0.0-1.0）
    - **enable_segmentation**: セグメンテーションを有効化（現在未実装）
    
    家具として検出されるカテゴリ：
    椅子、ソファ、ベッド、テーブル、テレビ、冷蔵庫など
    """
    start_time = time.time()
    
    # ファイル形式チェック
    if image.content_type not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format. Allowed: {', '.join(ALLOWED_FORMATS)}"
        )
    
    # ファイルサイズチェック
    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    try:
        # 画像を開く
        img = Image.open(io.BytesIO(contents))
        
        # RGB変換（透過画像対応）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 画像情報取得
        image_info = ImageInfo(
            width=img.width,
            height=img.height,
            format=image.content_type.split('/')[-1]
        )
        
        # detectorを取得
        detector = request.app.state.detector()
        if detector is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # 検出実行
        detections = detector.detect(img, confidence_threshold)
        
        # Detection型に変換
        formatted_detections = [
            Detection(
                detection_id=d["detection_id"],
                label=d["label"],
                label_ja=d["label_ja"],
                confidence=d["confidence"],
                bbox=d["bbox"]
            )
            for d in detections
        ]
        
        # サマリー生成
        summary_data = detector.get_summary(detections)
        summary = DetectionSummary(
            total_items=summary_data["total_items"],
            items_by_category=summary_data["items_by_category"],
            detection_quality=summary_data["detection_quality"]
        )
        
        # 処理時間計算
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # レスポンス作成
        response = DetectionResponse(
            status="success",
            processing_time_ms=processing_time_ms,
            image_info=image_info,
            detections=formatted_detections,
            summary=summary
        )
        
        logger.info(f"Detection completed: {len(formatted_detections)} items found in {processing_time_ms}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Detection failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )