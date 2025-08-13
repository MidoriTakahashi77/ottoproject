/**
 * セキュリティ関連のユーティリティ関数
 */

/**
 * リダイレクトURLの検証
 * オープンリダイレクト攻撃を防ぐため、許可されたパスのみを受け入れる
 */
export function validateRedirectUrl(url: string | null): string {
  const DEFAULT_REDIRECT = '/dashboard'
  
  if (!url) {
    return DEFAULT_REDIRECT
  }

  // 許可されたパスのホワイトリスト
  const allowedPaths = [
    '/dashboard',
    '/profile',
    '/settings',
    '/projects',
    '/analytics'
  ]

  // 絶対URLを拒否（外部サイトへのリダイレクトを防ぐ）
  if (url.includes('://') || url.startsWith('//')) {
    console.warn(`Blocked absolute URL redirect attempt: ${url}`)
    return DEFAULT_REDIRECT
  }

  // 相対パスのみ許可
  if (!url.startsWith('/')) {
    console.warn(`Blocked non-relative path redirect: ${url}`)
    return DEFAULT_REDIRECT
  }

  // javascriptスキームなどの危険なプロトコルをブロック
  const dangerousPatterns = [
    'javascript:',
    'data:',
    'vbscript:',
    'file:',
    'about:'
  ]
  
  const lowerUrl = url.toLowerCase()
  if (dangerousPatterns.some(pattern => lowerUrl.includes(pattern))) {
    console.warn(`Blocked dangerous protocol in redirect: ${url}`)
    return DEFAULT_REDIRECT
  }

  // パスの検証（クエリパラメータを除く）
  const pathname = url.split('?')[0].split('#')[0]
  
  // 完全一致または許可されたパスで始まるかチェック
  const isAllowed = allowedPaths.some(allowedPath => 
    pathname === allowedPath || pathname.startsWith(allowedPath + '/')
  )

  if (!isAllowed) {
    console.warn(`Redirect to non-whitelisted path blocked: ${url}`)
    return DEFAULT_REDIRECT
  }

  return url
}

/**
 * ファイルアップロードの検証
 */
export function validateFileUpload(file: File): { 
  valid: boolean
  error?: string 
} {
  // ファイルサイズ制限（10MB）
  const MAX_FILE_SIZE = 10 * 1024 * 1024
  if (file.size > MAX_FILE_SIZE) {
    return { 
      valid: false, 
      error: 'ファイルサイズは10MB以下にしてください' 
    }
  }

  // 許可されたMIMEタイプ
  const allowedMimeTypes = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/webp'
  ]

  if (!allowedMimeTypes.includes(file.type)) {
    return { 
      valid: false, 
      error: '許可されていないファイル形式です' 
    }
  }

  // ファイル名の検証（危険な文字を除去）
  const sanitizedName = sanitizeFileName(file.name)
  if (sanitizedName !== file.name) {
    console.warn(`Filename contains dangerous characters: ${file.name}`)
  }

  return { valid: true }
}

/**
 * ファイル名のサニタイゼーション
 */
export function sanitizeFileName(filename: string): string {
  // 危険な文字を除去
  return filename
    .replace(/[^a-zA-Z0-9._-]/g, '_')  // 英数字、ピリオド、ハイフン、アンダースコア以外を置換
    .replace(/\.{2,}/g, '_')            // 連続するピリオドを置換
    .replace(/^\./, '_')                // 先頭のピリオドを置換
    .substring(0, 255)                  // ファイル名の長さ制限
}

/**
 * HTMLエスケープ処理
 * XSS攻撃を防ぐため、ユーザー入力をHTMLに出力する前にエスケープ
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
    '/': '&#x2F;'
  }
  
  return text.replace(/[&<>"'/]/g, (char) => map[char])
}

/**
 * URLパラメータのサニタイゼーション
 */
export function sanitizeUrlParam(param: string | null): string {
  if (!param) return ''
  
  // URLエンコードされた危険な文字列をデコードしてチェック
  const decoded = decodeURIComponent(param)
  
  // スクリプトインジェクションのパターンをチェック
  const dangerousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+=/i,  // onclick=, onerror= など
    /<iframe/i,
    /<object/i,
    /<embed/i
  ]
  
  if (dangerousPatterns.some(pattern => pattern.test(decoded))) {
    console.warn(`Dangerous pattern detected in URL parameter: ${param}`)
    return ''
  }
  
  return param
}

/**
 * CSRFトークンの生成
 * Double Submit Cookie パターン用
 */
export function generateCSRFToken(): string {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}

/**
 * レート制限チェック（クライアントサイド）
 * 過度なAPI呼び出しを防ぐ
 */
export class RateLimiter {
  private attempts: Map<string, number[]> = new Map()
  
  constructor(
    private maxAttempts: number = 10,
    private windowMs: number = 60000  // 1分
  ) {}
  
  isAllowed(key: string): boolean {
    const now = Date.now()
    const attempts = this.attempts.get(key) || []
    
    // 古い試行を削除
    const validAttempts = attempts.filter(
      timestamp => now - timestamp < this.windowMs
    )
    
    if (validAttempts.length >= this.maxAttempts) {
      return false
    }
    
    validAttempts.push(now)
    this.attempts.set(key, validAttempts)
    
    return true
  }
  
  reset(key: string): void {
    this.attempts.delete(key)
  }
}