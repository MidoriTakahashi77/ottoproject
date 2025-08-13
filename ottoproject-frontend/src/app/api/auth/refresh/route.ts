import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function POST() {
  const cookieStore = cookies()
  
  // リフレッシュトークンを取得
  const refreshToken = cookieStore.get('sb-refresh-token')?.value
  
  if (!refreshToken) {
    return NextResponse.json(
      { error: 'No refresh token found' },
      { status: 401 }
    )
  }
  
  // Supabaseクライアントを作成
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  try {
    // リフレッシュトークンを使用して新しいセッションを取得
    const { data, error } = await supabase.auth.refreshSession({
      refresh_token: refreshToken
    })
    
    if (error || !data.session) {
      console.error('Token refresh failed:', error)
      
      // リフレッシュ失敗時はCookieをクリア
      const response = NextResponse.json(
        { error: 'Token refresh failed' },
        { status: 401 }
      )
      
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
    
    // 新しいトークンをHTTPOnly Cookieに保存
    const response = NextResponse.json({ success: true })
    
    // アクセストークンを更新
    response.cookies.set({
      name: 'sb-access-token',
      value: data.session.access_token,
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60, // 1時間
      path: '/',
    })
    
    // リフレッシュトークンも更新（新しいものが発行された場合）
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
    
    return response
    
  } catch (error) {
    console.error('Unexpected error during token refresh:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}