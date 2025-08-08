"""
Furniture detection API endpoint
"""
import time
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse
from PIL import Image
import io

from app.models.schemas import DetectionResponse, ErrorResponse, ImageInfo, DetectionSummary, Detection
from app.services.detector import FurnitureDetector
from app.middleware.auth import get_api_key
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed image formats
ALLOWED_FORMATS = {'image/jpeg', 'image/png', 'image/webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/detect", response_model=DetectionResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    403: {"model": ErrorResponse, "description": "Forbidden - Invalid API Key"},
    413: {"model": ErrorResponse, "description": "File too large"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"}
})
async def detect_furniture(
    request: Request,
    image: UploadFile = File(..., description="Image to detect"),
    confidence_threshold: float = Query(0.5, ge=0.0, le=1.0, description="Confidence threshold"),
    enable_segmentation: bool = Query(False, description="Enable segmentation (not implemented)"),
    api_key: str = Depends(get_api_key)
):
    """
    Detect furniture from image
    
    - **image**: JPEG, PNG, WebP image file（max 10MB）
    - **confidence_threshold**: Detection confidence threshold(0.0-1.0)
    - **enable_segmentation**: Enable segmentation (currently not implemented)
    
    Categories detected as furniture: 
    Chair, sofa, bed, table, TV, refrigerator, etc.
    """
    start_time = time.time()
    
    # File format check
    if image.content_type not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format. Allowed: {', '.join(ALLOWED_FORMATS)}"
        )
    
    # File size check
    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    try:
        # Open image
        img = Image.open(io.BytesIO(contents))
        
        # RGB conversion（Handle transparent images）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get image info
        image_info = ImageInfo(
            width=img.width,
            height=img.height,
            format=image.content_type.split('/')[-1]
        )
        
        # Get detector
        detector = request.app.state.detector()
        if detector is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # Execute detection
        detections = detector.detect(img, confidence_threshold)
        
        # Convert to Detection type
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
        
        # Generate summary
        summary_data = detector.get_summary(detections)
        summary = DetectionSummary(
            total_items=summary_data["total_items"],
            items_by_category=summary_data["items_by_category"],
            detection_quality=summary_data["detection_quality"]
        )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Create response
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