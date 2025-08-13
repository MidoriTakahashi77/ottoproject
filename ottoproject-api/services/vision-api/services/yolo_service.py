"""
YOLOv8 物体検出サービス
Ultralytics YOLOv8を使用した物体検出の実装
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from ultralytics import YOLO
import hashlib
import json

logger = logging.getLogger(__name__)

class YOLOService:
    """
    YOLOv8を使用した物体検出サービス
    シングルトンパターンで実装し、モデルの再読み込みを防ぐ
    """
    
    _instance = None
    _model = None
    
    # 家具・室内関連のCOCOクラス
    FURNITURE_CLASSES = {
        56: 'chair',
        57: 'couch',
        58: 'potted plant',
        59: 'bed',
        60: 'dining table',
        61: 'toilet',
        62: 'tv',
        63: 'laptop',
        64: 'mouse',
        65: 'remote',
        66: 'keyboard',
        67: 'cell phone',
        68: 'microwave',
        69: 'oven',
        70: 'toaster',
        71: 'sink',
        72: 'refrigerator',
        73: 'book',
        74: 'clock',
        75: 'vase',
        79: 'hair drier',
        80: 'toothbrush'
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(YOLOService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        YOLOv8モデルを初期化
        """
        try:
            # モデルの保存先
            model_dir = Path("/tmp/yolo_models")
            model_dir.mkdir(exist_ok=True)
            
            # 使用するモデル（n=nano, s=small, m=medium, l=large, x=xlarge）
            model_name = os.getenv("YOLO_MODEL", "yolov8m.pt")  # mediumをデフォルト
            model_path = model_dir / model_name
            
            logger.info(f"YOLOv8モデルを初期化中: {model_name}")
            
            # GPUが利用可能か確認
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"使用デバイス: {device}")
            
            # モデルをロード（初回は自動ダウンロード）
            self._model = YOLO(str(model_path))
            self._model.to(device)
            
            # ウォームアップ（初回推論を高速化）
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            self._model(dummy_image, verbose=False)
            
            logger.info("YOLOv8モデルの初期化完了")
            
        except Exception as e:
            logger.error(f"YOLOv8モデルの初期化エラー: {str(e)}")
            self._model = None
    
    @property
    def is_ready(self) -> bool:
        """モデルが利用可能か確認"""
        return self._model is not None
    
    def detect_objects(
        self,
        image: Image.Image,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        max_detections: int = 100,
        focus_on_furniture: bool = True
    ) -> Dict[str, Any]:
        """
        画像から物体を検出
        
        Args:
            image: PIL Image オブジェクト
            confidence_threshold: 検出の信頼度閾値
            iou_threshold: Non-Maximum Suppressionの閾値
            max_detections: 最大検出数
            focus_on_furniture: 家具関連のオブジェクトを優先
        
        Returns:
            検出結果の辞書
        """
        if not self.is_ready:
            raise RuntimeError("YOLOモデルが初期化されていません")
        
        try:
            # 画像をnumpy配列に変換
            image_np = np.array(image)
            
            # YOLOv8で推論
            results = self._model(
                image_np,
                conf=confidence_threshold,
                iou=iou_threshold,
                max_det=max_detections,
                verbose=False
            )
            
            # 結果を解析
            detections = []
            if results and len(results) > 0:
                result = results[0]  # バッチ処理の最初の結果
                
                if result.boxes is not None:
                    boxes = result.boxes
                    
                    for i in range(len(boxes)):
                        # クラスID、信頼度、バウンディングボックスを取得
                        cls_id = int(boxes.cls[i].item())
                        confidence = float(boxes.conf[i].item())
                        bbox = boxes.xyxy[i].cpu().numpy().astype(int).tolist()
                        
                        # クラス名を取得
                        class_name = result.names.get(cls_id, f"class_{cls_id}")
                        
                        # 家具フィルタリング（オプション）
                        if focus_on_furniture and cls_id not in self.FURNITURE_CLASSES:
                            # 家具以外でも重要なオブジェクトは含める
                            important_classes = ['person', 'laptop', 'book', 'cup', 'bottle']
                            if class_name not in important_classes:
                                continue
                        
                        detection = {
                            "category": class_name,
                            "category_id": cls_id,
                            "confidence": round(confidence, 3),
                            "bbox": bbox,  # [x1, y1, x2, y2]形式
                            "bbox_normalized": self._normalize_bbox(bbox, image.size),
                            "is_furniture": cls_id in self.FURNITURE_CLASSES
                        }
                        detections.append(detection)
            
            # 信頼度でソート
            detections.sort(key=lambda x: x['confidence'], reverse=True)
            
            # 統計情報を追加
            furniture_count = sum(1 for d in detections if d['is_furniture'])
            
            return {
                "success": True,
                "detections": detections,
                "total_objects": len(detections),
                "furniture_objects": furniture_count,
                "model_name": self._model.model_name if hasattr(self._model, 'model_name') else "yolov8",
                "image_size": image.size,
                "device": str(self._model.device) if hasattr(self._model, 'device') else "cpu"
            }
            
        except Exception as e:
            logger.error(f"物体検出エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "detections": [],
                "total_objects": 0
            }
    
    def _normalize_bbox(self, bbox: List[int], image_size: Tuple[int, int]) -> List[float]:
        """
        バウンディングボックスを正規化（0-1の範囲）
        
        Args:
            bbox: [x1, y1, x2, y2]形式のバウンディングボックス
            image_size: (width, height)の画像サイズ
        
        Returns:
            正規化されたバウンディングボックス
        """
        width, height = image_size
        return [
            round(bbox[0] / width, 4),   # x1
            round(bbox[1] / height, 4),  # y1
            round(bbox[2] / width, 4),   # x2
            round(bbox[3] / height, 4)   # y2
        ]
    
    def detect_from_bytes(
        self,
        image_bytes: bytes,
        **kwargs
    ) -> Dict[str, Any]:
        """
        バイトデータから物体検出
        
        Args:
            image_bytes: 画像のバイトデータ
            **kwargs: detect_objectsメソッドへの追加引数
        
        Returns:
            検出結果
        """
        try:
            import io
            image = Image.open(io.BytesIO(image_bytes))
            return self.detect_objects(image, **kwargs)
        except Exception as e:
            logger.error(f"画像読み込みエラー: {str(e)}")
            return {
                "success": False,
                "error": f"画像読み込みエラー: {str(e)}",
                "detections": []
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        モデル情報を取得
        
        Returns:
            モデルの詳細情報
        """
        if not self.is_ready:
            return {"status": "not_initialized"}
        
        return {
            "status": "ready",
            "model": str(self._model.model) if hasattr(self._model, 'model') else "unknown",
            "device": str(self._model.device) if hasattr(self._model, 'device') else "cpu",
            "classes": len(self._model.names) if hasattr(self._model, 'names') else 0,
            "furniture_classes": len(self.FURNITURE_CLASSES),
            "input_size": "640x640"  # YOLOv8のデフォルト
        }
    
    def analyze_scene(self, detections: List[Dict]) -> Dict[str, Any]:
        """
        検出結果からシーンを分析
        
        Args:
            detections: 検出結果のリスト
        
        Returns:
            シーン分析結果
        """
        # カテゴリ別に集計
        category_counts = {}
        furniture_items = []
        
        for detection in detections:
            category = detection['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
            if detection.get('is_furniture', False):
                furniture_items.append({
                    'type': category,
                    'confidence': detection['confidence']
                })
        
        # 部屋のタイプを推定
        room_type = self._estimate_room_type(category_counts)
        
        return {
            "room_type": room_type,
            "furniture_summary": furniture_items,
            "category_distribution": category_counts,
            "dominant_category": max(category_counts, key=category_counts.get) if category_counts else None,
            "scene_complexity": self._calculate_complexity(detections)
        }
    
    def _estimate_room_type(self, category_counts: Dict[str, int]) -> str:
        """
        検出されたオブジェクトから部屋のタイプを推定
        
        Args:
            category_counts: カテゴリ別のカウント
        
        Returns:
            推定された部屋のタイプ
        """
        # 部屋タイプの判定ルール
        if 'bed' in category_counts:
            return 'bedroom'
        elif 'dining table' in category_counts or 'oven' in category_counts:
            return 'kitchen/dining'
        elif 'couch' in category_counts or 'tv' in category_counts:
            return 'living_room'
        elif 'toilet' in category_counts or 'sink' in category_counts:
            return 'bathroom'
        elif 'desk' in category_counts or 'laptop' in category_counts:
            return 'office'
        else:
            return 'unknown'
    
    def _calculate_complexity(self, detections: List[Dict]) -> str:
        """
        シーンの複雑さを計算
        
        Args:
            detections: 検出結果
        
        Returns:
            複雑さレベル（simple, moderate, complex）
        """
        count = len(detections)
        if count <= 3:
            return 'simple'
        elif count <= 8:
            return 'moderate'
        else:
            return 'complex'

# シングルトンインスタンスを作成
_yolo_service = None

def get_yolo_service() -> YOLOService:
    """
    YOLOサービスのシングルトンインスタンスを取得
    
    Returns:
        YOLOService インスタンス
    """
    global _yolo_service
    if _yolo_service is None:
        _yolo_service = YOLOService()
    return _yolo_service