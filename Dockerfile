# マルチステージビルド - ベースイメージ
FROM python:3.10-slim as base

# 環境変数設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ビルドステージ
FROM base as builder

# pip更新
RUN pip install --upgrade pip

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# YOLOv8モデルのダウンロード（ビルド時にキャッシュ）
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# 本番ステージ
FROM base

# ビルドステージから依存関係をコピー
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# YOLOモデルをコピー
COPY --from=builder /root/.cache/ultralytics /root/.cache/ultralytics

# アプリケーションコードをコピー
COPY ./app /app/app

# 非rootユーザーの作成（セキュリティ向上）
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /root/.cache

# ユーザー切り替え
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Cloud Runはポート8080を期待
EXPOSE 8080

# アプリケーション起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]