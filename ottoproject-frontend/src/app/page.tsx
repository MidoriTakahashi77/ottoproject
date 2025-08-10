import LoginButton from '@/components/auth/LoginButton'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            思い出再構成アプリ
          </h1>
          <p className="text-gray-600">
            お部屋の写真から、思い出の空間を再現します
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-blue-900 mb-2">
              🔒 プライバシー保護
            </h2>
            <ul className="text-xs text-blue-700 space-y-1">
              <li>• 画像はサーバーに保存されません</li>
              <li>• GPS位置情報は自動削除されます</li>
              <li>• 処理結果のみが保存されます</li>
            </ul>
          </div>
          
          <div className="flex justify-center pt-4">
            <LoginButton />
          </div>
        </div>
        
        <p className="text-xs text-gray-500 text-center mt-6">
          続行することで、利用規約とプライバシーポリシーに同意したものとみなされます
        </p>
      </div>
    </main>
  )
}
