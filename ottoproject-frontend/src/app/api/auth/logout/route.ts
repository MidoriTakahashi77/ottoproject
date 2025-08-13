import { createClient } from '@supabase/supabase-js'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function POST() {
  const cookieStore = cookies()
  
  // Cookieからトークンを取得
  const accessToken = cookieStore.get('sb-access-token')?.value
  
  // Supabaseクライアントを作成
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      },
      global: {
        headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {}
      }
    }
  )
  
  // Supabaseからサインアウト（エラーは無視）
  try {
    await supabase.auth.signOut()
  } catch (error) {
    console.error('Supabase signOut error:', error)
  }
  
  // レスポンスを作成
  const response = NextResponse.json({ success: true })
  
  // カスタムHTTPOnly Cookieをクリア
  const cookiesToClear = [
    'sb-access-token',
    'sb-refresh-token',
    'sb-user-id'
  ]
  
  cookiesToClear.forEach(cookieName => {
    response.cookies.set({
      name: cookieName,
      value: '',
      maxAge: 0,
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
    })
  })
  
  // Supabase標準のCookieもクリア
  const allCookies = cookieStore.getAll()
  allCookies.forEach(cookie => {
    if (cookie.name.startsWith('sb-') && cookie.name.includes('-auth-token')) {
      response.cookies.set({
        name: cookie.name,
        value: '',
        maxAge: 0,
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/',
      })
    }
  })
  
  return response
}