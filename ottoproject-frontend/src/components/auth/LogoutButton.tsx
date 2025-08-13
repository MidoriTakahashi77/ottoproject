'use client'

import { useRouter } from 'next/navigation'

export default function LogoutButton() {
  const router = useRouter()
  
  const handleLogout = async () => {
    // サーバーサイドのログアウトAPIを呼び出してHTTPOnly Cookieをクリア
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Cookieを含める
    })
    
    if (response.ok) {
      // LocalStorageもクリア（念のため）
      if (typeof window !== 'undefined') {
        // Supabase関連のLocalStorageアイテムを削除
        const keysToRemove: string[] = []
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i)
          if (key && (key.includes('supabase') || key.includes('auth'))) {
            keysToRemove.push(key)
          }
        }
        keysToRemove.forEach(key => localStorage.removeItem(key))
      }
      
      // ホームページへリダイレクト
      router.push('/')
      router.refresh()
    } else {
      console.error('Logout failed')
    }
  }

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
    >
      ログアウト
    </button>
  )
}