.PHONY: help up down build logs clean test lint migrate

help:
	@echo "使用可能なコマンド:"
	@echo "  make up        - すべてのサービスを起動"
	@echo "  make down      - すべてのサービスを停止"
	@echo "  make build     - Dockerイメージをビルド"
	@echo "  make logs      - ログを表示"
	@echo "  make clean     - ボリュームを含めて削除"
	@echo "  make test      - テストを実行"
	@echo "  make lint      - リンターを実行"
	@echo "  make migrate   - DBマイグレーションを実行"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf postgres_data redis_data minio_data

test:
	docker-compose exec vision-api pytest
	docker-compose exec furniture-api pytest
	docker-compose exec asset-api npm test

lint:
	docker-compose exec vision-api pylint src/
	docker-compose exec furniture-api pylint src/
	docker-compose exec asset-api npm run lint

migrate:
	docker-compose exec vision-api alembic upgrade head
	docker-compose exec furniture-api alembic upgrade head

# 個別サービスの操作
vision-logs:
	docker-compose logs -f vision-api

furniture-logs:
	docker-compose logs -f furniture-api

asset-logs:
	docker-compose logs -f asset-api

# 開発用：シェルに入る
vision-shell:
	docker-compose exec vision-api /bin/bash

furniture-shell:
	docker-compose exec furniture-api /bin/bash

asset-shell:
	docker-compose exec asset-api /bin/sh

# データベースに接続
db-shell:
	docker-compose exec postgres psql -U ottouser -d ottodb

# Redisに接続
redis-cli:
	docker-compose exec redis redis-cli

# MinIOコンソールのURL表示
minio-console:
	@echo "MinIO Console: http://localhost:9001"
	@echo "Username: minioadmin"
	@echo "Password: minioadmin"