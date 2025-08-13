import { createClient as createSupabaseClient } from '@supabase/supabase-js'

// カスタムストレージアダプター（HTTPOnly Cookie用）
const customStorage = {
  getItem: (key: string) => {
    // サーバーで設定されたCookieは読み取れないが、
    // セッション情報はAPIエンドポイント経由で取得
    return null
  },
  setItem: (key: string, value: string) => {
    // HTTPOnly Cookieはクライアントから設定不可
    // サーバーサイドで処理
  },
  removeItem: (key: string) => {
    // HTTPOnly Cookieはクライアントから削除不可
    // ログアウトAPIで処理
  }
}

export function createClient() {
  return createSupabaseClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      auth: {
        storage: customStorage,
        autoRefreshToken: false, // 自動リフレッシュは無効化（サーバーサイドで処理）
        persistSession: false, // クライアントサイドでのセッション永続化を無効
        detectSessionInUrl: true
      }
    }
  )
}