FROM oven/bun:1-alpine

WORKDIR /app

# パッケージファイルをコピー
COPY package.json ./
COPY bun.lockb* ./

# 依存関係インストール（高速）
RUN bun install --frozen-lockfile || bun install

# アプリケーションコードをコピー
COPY . .

EXPOSE 8000

CMD ["bun", "run", "src/index.ts"]