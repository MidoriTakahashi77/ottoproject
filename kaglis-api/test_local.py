"""
ローカルテスト用スクリプト
"""
import requests
import sys
from pathlib import Path

def test_health():
    """ヘルスチェックテスト"""
    response = requests.get("http://localhost:8080/health")
    print(f"Health Check: {response.json()}")
    return response.status_code == 200

def test_detection(image_path):
    """画像検出テスト"""
    if not Path(image_path).exists():
        print(f"Error: Image file {image_path} not found")
        return False
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'confidence_threshold': 0.5}
        
        response = requests.post(
            "http://localhost:8080/api/detect",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Processing Time: {result.get('processing_time_ms', 'N/A')}ms")
        print(f"Detections: {len(result['detections'])}")
        
        for detection in result['detections']:
            print(f"  - {detection['label_ja']} ({detection['label']}): {detection['confidence']:.2f}")
        
        print(f"\nSummary:")
        print(f"  Total items: {result['summary']['total_items']}")
        print(f"  Quality: {result['summary']['detection_quality']}")
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("Testing Furniture Detection API...")
    print("-" * 40)
    
    # ヘルスチェック
    if test_health():
        print("✓ Health check passed")
    else:
        print("✗ Health check failed")
        sys.exit(1)
    
    print("-" * 40)
    
    # 画像検出テスト（サンプル画像がある場合）
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Testing with image: {image_path}")
        if test_detection(image_path):
            print("✓ Detection test passed")
        else:
            print("✗ Detection test failed")
    else:
        print("Usage: python test_local.py <image_path>")
        print("Example: python test_local.py sample.jpg")