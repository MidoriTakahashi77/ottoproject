import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify } from 'jose'

// 保護されたルート
const protectedRoutes = ['/dashboard']

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // 静的ファイルやAPIルートはスキップ
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/static') ||
    pathname.includes('.')
  ) {
    return NextResponse.next()
  }

  // レスポンスオブジェクトを作成
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  // Cookieからアクセストークンを取得
  const accessToken = request.cookies.get('sb-access-token')?.value
  const refreshToken = request.cookies.get('sb-refresh-token')?.value
  
  let isValidSession = false
  let needsRefresh = false
  
  // JWTトークンの検証
  if (accessToken) {
    try {
      // 環境変数の存在チェック
      const jwtSecret = process.env.SUPABASE_JWT_SECRET
      if (!jwtSecret) {
        console.error('SUPABASE_JWT_SECRET is not set')
        return NextResponse.redirect(new URL('/', request.url))
      }
      
      // Supabase JWTの検証（JWT Secretを使用）
      const secret = new TextEncoder().encode(jwtSecret)
      const { payload } = await jwtVerify(accessToken, secret)
      
      // トークンの有効期限チェック
      const exp = payload.exp as number
      const now = Math.floor(Date.now() / 1000)
      
      if (exp > now) {
        isValidSession = true
        // 有効期限が5分以内の場合、リフレッシュフラグを立てる
        if (exp - now < 300) {
          needsRefresh = true
        }
      }
    } catch (error) {
      console.error('JWT verification failed:', error)
      isValidSession = false
    }
  }

  // トークンリフレッシュが必要な場合
  if (needsRefresh && refreshToken) {
    // リフレッシュ処理はクライアントサイドまたはAPI Routeで実行
    // ここではリフレッシュが必要なことを示すヘッダーを追加
    response.headers.set('X-Token-Needs-Refresh', 'true')
  }

  // 保護されたルートへのアクセスチェック
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route))
  
  if (isProtectedRoute && !isValidSession) {
    // 未認証の場合はログインページへリダイレクト
    const redirectUrl = new URL('/', request.url)
    redirectUrl.searchParams.set('redirectTo', pathname)
    return NextResponse.redirect(redirectUrl)
  }

  // ログイン済みユーザーがホームページにアクセスした場合
  if (pathname === '/' && isValidSession) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // 無効なトークンの場合、Cookieをクリア
  if (!isValidSession && accessToken) {
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
  }

  return response
}

export const config = {
  matcher: [
    /*
     * 以下を除くすべてのリクエストパスにマッチ:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}