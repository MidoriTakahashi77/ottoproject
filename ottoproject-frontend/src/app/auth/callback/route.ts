import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const origin = requestUrl.origin
  const redirectTo = requestUrl.searchParams.get('redirectTo') || '/dashboard'
  
  if (code) {
    // 標準のSupabaseクライアントを作成
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )
    
    // 認証コードをセッションに交換（PKCEフロー）
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (!error && data.session) {
      // HTTPOnly Cookieにセッション情報を保存
      const response = NextResponse.redirect(`${origin}${redirectTo}`)
      
      // アクセストークンをHTTPOnly Cookieに保存
      response.cookies.set({
        name: 'sb-access-token',
        value: data.session.access_token,
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60, // 1時間
        path: '/',
      })
      
      // リフレッシュトークンをHTTPOnly Cookieに保存
      if (data.session.refresh_token) {
        response.cookies.set({
          name: 'sb-refresh-token',
          value: data.session.refresh_token,
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: 60 * 60 * 24 * 7, // 7日間
          path: '/',
        })
      }
      
      // ユーザーIDをHTTPOnly Cookieに保存（バックエンドAPI用）
      response.cookies.set({
        name: 'sb-user-id',
        value: data.session.user.id,
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7, // 7日間
        path: '/',
      })
      
      // CSRFトークンの設定は不要（SameSite=Laxで基本的な保護あり）
      // 将来的にDouble Submit Cookieパターンを実装する場合は、
      // httpOnly: false にする必要がある
      
      return response
    }
  }

  // 認証に失敗した場合、ホームページにリダイレクト
  const response = NextResponse.redirect(`${origin}/?error=auth_failed`)
  
  // エラー時はCookieをクリア
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
  
  return response
}