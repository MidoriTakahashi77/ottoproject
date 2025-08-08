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

# wgetをインストール（モデルダウンロード用）
RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*

# pip更新
RUN pip install --upgrade pip

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 作業ディレクトリ作成
WORKDIR /app

# YOLOv8モデルのダウンロード（wgetで直接ダウンロード）
RUN wget -q https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O /app/yolov8n.pt

# 本番ステージ
FROM base

# ビルドステージから依存関係をコピー
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# YOLOモデルとキャッシュをコピー
# モデルファイルは /app/yolov8n.pt に保存される
RUN mkdir -p /root/.cache
COPY --from=builder /app/yolov8n.pt* /app/
COPY --from=builder /root/.cache /root/.cache

# アプリケーションコードをコピー
COPY ./app /app/app

# PYTHONPATHを設定
ENV PYTHONPATH=/app:$PYTHONPATH

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
# Cloud RunのPORT環境変数を使用（デフォルト8080）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]