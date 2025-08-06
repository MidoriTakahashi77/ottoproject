"""
YOLOv8を使用した家具検出サービス
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
    """家具検出クラス"""
    
    # YOLOv8のCOCOクラスから家具関連を抽出
    FURNITURE_CLASSES = {
        'chair': '椅子',
        'couch': 'ソファ',
        'bed': 'ベッド',
        'dining table': 'ダイニングテーブル',
        'toilet': 'トイレ',  # 家具として扱うか要検討
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
        画像から家具を検出
        
        Args:
            image: PIL Image
            confidence_threshold: 信頼度閾値
            
        Returns:
            検出結果のリスト
        """
        try:
            # NumPy配列に変換
            img_array = np.array(image)
            
            # YOLOv8で推論
            results = self.model(img_array, conf=confidence_threshold)
            
            # 結果の処理
            detections = []
            for r in results:
                if r.boxes is not None:
                    boxes = r.boxes
                    for i, box in enumerate(boxes):
                        # クラス名を取得
                        class_id = int(box.cls)
                        class_name = self.model.names[class_id]
                        
                        # 家具カテゴリのみフィルタリング
                        if class_name.lower() in self.FURNITURE_CLASSES:
                            # バウンディングボックスの座標
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
        検出結果のサマリーを生成
        
        Args:
            detections: 検出結果リスト
            
        Returns:
            サマリー情報
        """
        total_items = len(detections)
        items_by_category = {}
        
        for detection in detections:
            label = detection['label']
            items_by_category[label] = items_by_category.get(label, 0) + 1
        
        # 検出品質の判定
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