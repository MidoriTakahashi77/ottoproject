# Makefile for Furniture Detection API

.PHONY: help build up down logs test clean

# デフォルトターゲット
help:
	@echo "使用可能なコマンド:"
	@echo "  make build       - Dockerイメージをビルド"
	@echo "  make up          - サービスを起動"
	@echo "  make down        - サービスを停止"
	@echo "  make dev         - 開発環境を起動（ホットリロード）"
	@echo "  make logs        - ログを表示"
	@echo "  make test        - テストを実行"
	@echo "  make clean       - コンテナとボリュームを削除"
	@echo "  make shell       - APIコンテナにシェル接続"
	@echo "  make format      - コードフォーマット"
	@echo "  make lint        - リンターを実行"

# Dockerイメージビルド
build:
	docker-compose build

# サービス起動（本番モード）
up:
	docker-compose up -d
	@echo "API: http://localhost:8080"
	@echo "API Docs: http://localhost:8080/docs"
	@echo "Firestore UI: http://localhost:4400"

# 開発環境起動（ホットリロード）
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# サービス停止
down:
	docker-compose down

# ログ表示
logs:
	docker-compose logs -f api

# テスト実行
test:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile test run --rm test

# クリーンアップ
clean:
	docker-compose down -v
	docker system prune -f

# APIコンテナにシェル接続
shell:
	docker-compose exec api /bin/bash

# コードフォーマット
format:
	docker-compose exec api black /app/app --line-length 100

# リンター実行
lint:
	docker-compose exec api flake8 /app/app --max-line-length 100

# 本番用イメージビルド（Cloud Run用）
build-prod:
	docker build -t furniture-detection-api:latest .

# ローカルでCloud Runイメージテスト
test-prod:
	docker run -p 8080:8080 furniture-detection-api:latest

# APIテスト（サンプル画像必要）
test-api:
	@echo "Testing API with sample image..."
	@curl -X POST "http://localhost:8080/api/detect" \
		-H "accept: application/json" \
		-H "Content-Type: multipart/form-data" \
		-F "image=@sample.jpg" \
		-F "confidence_threshold=0.5" | python -m json.tool

# ヘルスチェック
health:
	@curl -s http://localhost:8080/health | python -m json.tool