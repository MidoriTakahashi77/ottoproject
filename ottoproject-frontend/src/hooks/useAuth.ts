'use client'

import { useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'

export function useAuth() {
  const router = useRouter()
  
  // トークンをリフレッシュする関数
  const refreshToken = useCallback(async () => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include', // Cookieを含める
      })
      
      if (!response.ok) {
        // リフレッシュ失敗時はログインページへ
        router.push('/')
        return false
      }
      
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      router.push('/')
      return false
    }
  }, [router])
  
  // APIリクエストのラッパー（自動リフレッシュ付き）
  const fetchWithAuth = useCallback(async (
    url: string,
    options: RequestInit = {}
  ): Promise<Response> => {
    // 最初のリクエスト
    let response = await fetch(url, {
      ...options,
      credentials: 'include', // Cookieを含める
    })
    
    // トークンのリフレッシュが必要な場合
    if (response.status === 401 || response.headers.get('X-Token-Needs-Refresh') === 'true') {
      const refreshSuccess = await refreshToken()
      
      if (refreshSuccess) {
        // リフレッシュ成功後、元のリクエストを再試行
        response = await fetch(url, {
          ...options,
          credentials: 'include',
        })
      }
    }
    
    return response
  }, [refreshToken])
  
  // 定期的なトークンリフレッシュ（オプション）
  useEffect(() => {
    // 50分ごとにトークンをリフレッシュ（アクセストークンの有効期限は1時間）
    const interval = setInterval(() => {
      refreshToken()
    }, 50 * 60 * 1000) // 50分
    
    return () => clearInterval(interval)
  }, [refreshToken])
  
  return { fetchWithAuth, refreshToken }
}