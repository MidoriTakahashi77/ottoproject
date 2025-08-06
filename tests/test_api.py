"""
APIエンドポイントのテスト
"""
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io
import numpy as np

from app.main import app

client = TestClient(app)

def create_test_image(width=640, height=480):
    """テスト用画像を生成"""
    # ランダムな画像を生成
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # バイトストリームに変換
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

class TestHealthCheck:
    """ヘルスチェックのテスト"""
    
    def test_root_endpoint(self):
        """ルートエンドポイントのテスト"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """ヘルスエンドポイントのテスト"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_loaded" in data

class TestDetectionAPI:
    """検出APIのテスト"""
    
    def test_detect_with_valid_image(self):
        """正常な画像での検出テスト"""
        img_data = create_test_image()
        
        response = client.post(
            "/api/detect",
            files={"image": ("test.jpg", img_data, "image/jpeg")},
            data={"confidence_threshold": 0.5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "detections" in data
        assert "summary" in data
        assert isinstance(data["detections"], list)
    
    def test_detect_with_invalid_format(self):
        """不正な形式のファイルでのテスト"""
        response = client.post(
            "/api/detect",
            files={"image": ("test.txt", b"not an image", "text/plain")},
            data={"confidence_threshold": 0.5}
        )
        
        assert response.status_code == 400
    
    def test_detect_with_large_file(self):
        """大きすぎるファイルでのテスト"""
        # 11MBのダミーデータ
        large_data = b"x" * (11 * 1024 * 1024)
        
        response = client.post(
            "/api/detect",
            files={"image": ("large.jpg", large_data, "image/jpeg")},
            data={"confidence_threshold": 0.5}
        )
        
        assert response.status_code == 413
    
    def test_detect_with_custom_threshold(self):
        """カスタム閾値でのテスト"""
        img_data = create_test_image()
        
        response = client.post(
            "/api/detect",
            files={"image": ("test.jpg", img_data, "image/jpeg")},
            data={"confidence_threshold": 0.8}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 高い閾値では検出数が減る可能性がある
        assert "detections" in data
    
    @pytest.mark.parametrize("image_format,content_type", [
        ("JPEG", "image/jpeg"),
        ("PNG", "image/png"),
        ("WEBP", "image/webp"),
    ])
    def test_detect_with_different_formats(self, image_format, content_type):
        """異なる画像形式でのテスト"""
        # 画像生成
        img = Image.new('RGB', (640, 480), color='red')
        img_byte_arr = io.BytesIO()
        
        # WebPは一部環境で未対応の可能性
        try:
            img.save(img_byte_arr, format=image_format)
        except Exception:
            pytest.skip(f"{image_format} not supported")
        
        img_byte_arr.seek(0)
        
        response = client.post(
            "/api/detect",
            files={"image": (f"test.{image_format.lower()}", img_byte_arr, content_type)},
            data={"confidence_threshold": 0.5}
        )
        
        assert response.status_code == 200