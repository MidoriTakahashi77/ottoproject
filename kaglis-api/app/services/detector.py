"""
Furniture detection service using YOLOv8
"""
import os
import logging
from typing import List, Dict, Any
import uuid
from ultralytics import YOLO
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class FurnitureDetector:
    """Furniture detection class"""
    
    # Extract furniture-related classes from YOLOv8 COCO classes
    FURNITURE_CLASSES = {
        'chair': '椅子',
        'couch': 'ソファ',
        'bed': 'ベッド',
        'dining table': 'ダイニングテーブル',
        'toilet': 'トイレ',  # Consider as furniture
        'tv': 'テレビ',
        'laptop': 'ノートパソコン',
        'mouse': 'マウス',
        'keyboard': 'キーボード',
        'cell phone': '携帯電話',
        'microwave': '電子レンジ',
        'oven': 'オーブン',
        'toaster': 'トースター',
        'sink': 'シンク',
        'refrigerator': '冷蔵庫',
        'book': '本',
        'clock': '時計',
        'vase': '花瓶',
        'potted plant': '鉢植え',
    }
    
    # より厳密な家具カテゴリ（メイン家具のみ）
    MAIN_FURNITURE = {
        'chair', 'couch', 'bed', 'dining table', 'tv', 
        'refrigerator', 'oven', 'sink'
    }
    
    def __init__(self, model_size: str = 'n'):
        """
        初期化
        Args:
            model_size: モデルサイズ（n, s, m, l, x）
        """
        self.model_size = model_size
        self.model_name = f'yolov8{model_size}.pt'
        
        try:
            # YOLOv8モデルのロード
            self.model = YOLO(self.model_name)
            logger.info(f"Loaded YOLOv8 model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(self, image: Image.Image, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Detect furniture from image
        
        Args:
            image: PIL Image
            confidence_threshold: Confidence threshold
            
        Returns:
            List of detection results
        """
        try:
            # Convert to NumPy array
            img_array = np.array(image)
            
            # YOLOv8 inference
            results = self.model(img_array, conf=confidence_threshold)
            
            # Process results
            detections = []
            for r in results:
                if r.boxes is not None:
                    boxes = r.boxes
                    for i, box in enumerate(boxes):
                        # Get class name
                        class_id = int(box.cls)
                        class_name = self.model.names[class_id]
                        
                        # Filter only furniture categories
                        if class_name.lower() in self.FURNITURE_CLASSES:
                            # Bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            
                            detection = {
                                "detection_id": str(uuid.uuid4()),
                                "label": class_name,
                                "label_ja": self.FURNITURE_CLASSES.get(class_name.lower(), class_name),
                                "confidence": float(box.conf),
                                "bbox": {
                                    "x": float(x1),
                                    "y": float(y1),
                                    "width": float(x2 - x1),
                                    "height": float(y2 - y1)
                                },
                                "is_main_furniture": class_name.lower() in self.MAIN_FURNITURE
                            }
                            detections.append(detection)
            
            # 信頼度でソート
            detections.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"Detected {len(detections)} furniture items")
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            raise
    
    def get_summary(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate detection result summary
        
        Args:
            detections: Detection results list
            
        Returns:
            Summary information
        """
        total_items = len(detections)
        items_by_category = {}
        
        for detection in detections:
            label = detection['label']
            items_by_category[label] = items_by_category.get(label, 0) + 1
        
        # Determine detection quality
        if total_items == 0:
            quality = "none"
        elif total_items < 3:
            quality = "low"
        elif total_items < 10:
            quality = "medium"
        else:
            quality = "high"
        
        # 平均信頼度
        avg_confidence = np.mean([d['confidence'] for d in detections]) if detections else 0
        
        return {
            "total_items": total_items,
            "items_by_category": items_by_category,
            "detection_quality": quality,
            "average_confidence": float(avg_confidence)
        }