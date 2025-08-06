#!/usr/bin/env python3
"""
家具認識APIのテストスクリプト

使用方法:
    python test_api_sample.py /path/to/image.jpg
"""
import sys
import requests
import json
from pathlib import Path

def test_furniture_detection(image_path: str, confidence_threshold: float = 0.5):
    """画像から家具を検出"""
    
    # APIエンドポイント
    url = "http://localhost:8080/api/detect"
    
    # 画像ファイルの確認
    if not Path(image_path).exists():
        print(f"エラー: 画像ファイルが見つかりません: {image_path}")
        return
    
    # リクエスト送信
    print(f"画像を送信中: {image_path}")
    print(f"信頼度閾値: {confidence_threshold}")
    print("-" * 50)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (Path(image_path).name, f, 'image/jpeg')}
            data = {'confidence_threshold': confidence_threshold}
            
            response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ 検出成功！")
            print(f"ステータス: {result['status']}")
            print(f"処理時間: {result['processing_time_ms']:.2f}ms")
            print()
            
            # サマリー表示
            print("📊 検出サマリー:")
            print(f"  総検出数: {result['summary']['total_detections']}")
            print(f"  ユニーク家具数: {result['summary']['unique_items']}")
            print()
            
            print("  カテゴリ別:")
            for category, count in result['summary']['by_category'].items():
                print(f"    - {category}: {count}個")
            print()
            
            # 個別検出結果
            if result['detections']:
                print("🪑 検出された家具:")
                for i, detection in enumerate(result['detections'], 1):
                    print(f"  {i}. {detection['label']} ({detection['label_ja']})")
                    print(f"     信頼度: {detection['confidence']:.2%}")
                    print(f"     位置: ({detection['bbox']['x1']:.0f}, {detection['bbox']['y1']:.0f}) - "
                          f"({detection['bbox']['x2']:.0f}, {detection['bbox']['y2']:.0f})")
                    print(f"     カテゴリ: {detection['category']}")
                    print()
            else:
                print("⚠️ 家具が検出されませんでした")
            
            # メタデータ
            print("ℹ️ メタデータ:")
            print(f"  画像サイズ: {result['metadata']['image_width']}x{result['metadata']['image_height']}")
            print(f"  モデル: {result['metadata']['model_version']}")
            
        else:
            print(f"❌ エラー: {response.status_code}")
            print(response.json())
            
    except requests.exceptions.ConnectionError:
        print("❌ エラー: APIサーバーに接続できません")
        print("   Docker Composeが起動していることを確認してください:")
        print("   make dev")
    except Exception as e:
        print(f"❌ エラー: {e}")

def main():
    if len(sys.argv) < 2:
        print("使用方法: python test_api_sample.py <画像ファイルパス> [信頼度閾値]")
        print("例: python test_api_sample.py room.jpg 0.5")
        sys.exit(1)
    
    image_path = sys.argv[1]
    confidence_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    
    test_furniture_detection(image_path, confidence_threshold)

if __name__ == "__main__":
    main()