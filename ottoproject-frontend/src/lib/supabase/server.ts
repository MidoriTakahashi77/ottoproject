import { createClient as createSupabaseClient } from '@supabase/supabase-js'
import { cookies } from 'next/headers'

export function createClient() {
  const cookieStore = cookies()
  
  // Cookieからトークンを取得
  const accessToken = cookieStore.get('sb-access-token')?.value
  
  // サーバーサイドSupabaseクライアントを作成
  const supabase = createSupabaseClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
        detectSessionInUrl: false
      },
      global: {
        headers: {
          // HTTPOnly Cookieから取得したトークンをAuthorizationヘッダーに設定
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
        }
      }
    }
  )

  return supabase
}