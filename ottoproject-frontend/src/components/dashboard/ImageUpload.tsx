'use client'

import { useState, useRef } from 'react'
import { removeExifData, processImageOnClient } from '@/lib/image-processing'

export default function ImageUpload() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // プレビュー表示
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    // 画像処理
    await processImage(file)
  }

  const processImage = async (file: File) => {
    setIsProcessing(true)
    setResult(null)

    try {
      // EXIF情報を削除
      const cleanBlob = await removeExifData(file)
      
      // 画像メタデータを取得
      const metadata = await getImageMetadata(cleanBlob)
      
      // APIに送信（画像は保存されない）
      const processedResult = await processImageOnClient(cleanBlob, metadata)
      
      setResult(processedResult)
    } catch (error) {
      console.error('画像処理エラー:', error)
      alert('画像の処理中にエラーが発生しました')
    } finally {
      setIsProcessing(false)
    }
  }

  const getImageMetadata = (blob: Blob): Promise<{ width: number; height: number; format: string }> => {
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        resolve({
          width: img.width,
          height: img.height,
          format: blob.type.split('/')[1] || 'jpeg'
        })
      }
      img.src = URL.createObjectURL(blob)
    })
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h3 className="text-sm font-semibold text-yellow-900 mb-2">
            🔒 プライバシー保護について
          </h3>
          <ul className="text-xs text-yellow-700 space-y-1">
            <li>• 画像はサーバーに保存されません</li>
            <li>• GPS位置情報は自動的に削除されます</li>
            <li>• 処理はブラウザ上で実行されます</li>
            <li>• 検出結果（座標とカテゴリ）のみが保存されます</li>
          </ul>
        </div>
      </div>

      <div className="space-y-4">
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
        >
          {preview ? (
            <div className="space-y-4">
              <img 
                src={preview} 
                alt="Preview" 
                className="max-w-full h-64 mx-auto object-contain rounded"
              />
              <p className="text-sm text-gray-600">
                クリックして別の画像を選択
              </p>
            </div>
          ) : (
            <>
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="mt-2 text-sm text-gray-600">
                クリックして画像を選択
              </p>
              <p className="text-xs text-gray-500">
                対応形式: JPEG, PNG, WebP (最大10MB)
              </p>
            </>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileSelect}
          className="hidden"
        />

        {isProcessing && (
          <div className="text-center py-4">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p className="mt-2 text-sm text-gray-600">処理中...</p>
          </div>
        )}

        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-green-900 mb-2">
              処理完了
            </h4>
            <p className="text-xs text-green-700">
              検出された物体: {result.objects?.length || 0} 個
            </p>
            <div className="mt-2 space-y-1">
              {result.objects?.map((obj: any, index: number) => (
                <div key={index} className="text-xs text-gray-600">
                  • {obj.category} (信頼度: {(obj.confidence * 100).toFixed(1)}%)
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}