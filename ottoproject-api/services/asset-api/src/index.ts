/**
 * Asset API - アセットマッチングAPI
 * Hono Framework使用
 * TypeScriptではclassを使用せず、関数とインターフェースで実装
 */
import { Hono } from 'hono'
import { serve } from '@hono/node-server'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'

// Honoアプリケーション作成
const app = new Hono()

// ミドルウェア設定
app.use('*', cors())
app.use('*', logger())

// ヘルスチェック
app.get('/health', (c) => {
  return c.json({
    status: 'healthy',
    service: 'asset-api',
    version: '1.0.0'
  })
})

// ルート
app.get('/', (c) => {
  return c.json({
    message: 'Asset API - アセットマッチング',
    docs: '/docs',
    health: '/health'
  })
})

// API情報
app.get('/api/v1/info', (c) => {
  return c.json({
    api: 'Asset API',
    version: '1.0.0',
    endpoints: {
      search: '/api/v1/assets/search',
      coordinate: '/api/v1/assets/coordinate',
      compatibility: '/api/v1/assets/compatibility'
    }
  })
})

// TODO: Supabase認証ミドルウェア
// TODO: 類似アセット検索エンドポイント
// TODO: コーディネート提案エンドポイント
// TODO: 相性分析エンドポイント

// サーバー起動
const port = parseInt(process.env.API_PORT || '8000')
const host = process.env.API_HOST || '0.0.0.0'

console.log(`Asset API starting on http://${host}:${port}`)

serve({
  fetch: app.fetch,
  port
})