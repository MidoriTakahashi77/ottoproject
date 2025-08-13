/**
 * プライバシー保護のための画像処理ライブラリ
 * 画像からEXIF情報を削除し、サーバーに保存せずに処理
 */

/**
 * 画像からEXIF情報を削除
 * Canvas APIを使用して画像を再描画し、メタデータを除去
 */
export function removeExifData(file: File): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.onload = () => {
      // Canvas のサイズを画像に合わせる
      canvas.width = img.width
      canvas.height = img.height
      
      // 画像を描画（これによりEXIF情報が削除される）
      ctx?.drawImage(img, 0, 0)
      
      // Blobに変換
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
        } else {
          reject(new Error('Failed to process image'))
        }
      }, 'image/jpeg', 0.9)
    }
    
    img.onerror = () => {
      reject(new Error('Failed to load image'))
    }
    
    // 画像を読み込み
    img.src = URL.createObjectURL(file)
  })
}

/**
 * 画像をBase64エンコードしてAPIに送信
 * 画像はサーバーに保存されず、処理結果のみが返される
 */
export async function processImageOnClient(
  blob: Blob,
  metadata: { width: number; height: number; format: string }
): Promise<any> {
  // Base64エンコード
  const base64 = await blobToBase64(blob)
  
  // APIエンドポイント（実際のAPIに合わせて調整）
  const apiUrl = process.env.NEXT_PUBLIC_VISION_API_URL || 'http://localhost:8001'
  
  try {
    // JWTトークンを取得（Supabaseから）
    const token = await getAuthToken()
    
    const response = await fetch(`${apiUrl}/api/v1/vision/detect`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: base64,
        metadata: metadata,
        // プライバシー設定を明示的に指定
        privacy_mode: true,
        no_storage: true,
        remove_pii: true
      })
    })
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    const result = await response.json()
    
    // 結果には座標とカテゴリのみが含まれる（画像URLは含まれない）
    return {
      objects: result.objects,
      processing_time_ms: result.processing_time_ms
    }
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

/**
 * BlobをBase64文字列に変換
 */
function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      resolve(reader.result as string)
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

/**
 * Supabaseから認証トークンを取得
 */
async function getAuthToken(): Promise<string> {
  // 動的インポートでクライアントサイドのみで実行
  const { createClient } = await import('@/lib/supabase/client')
  const supabase = createClient()
  
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session?.access_token) {
    throw new Error('Not authenticated')
  }
  
  return session.access_token
}

/**
 * 画像のサイズを検証
 */
export function validateImageSize(file: File): { valid: boolean; error?: string } {
  const MAX_SIZE = 10 * 1024 * 1024 // 10MB
  const MIN_WIDTH = 480
  const MIN_HEIGHT = 480
  
  if (file.size > MAX_SIZE) {
    return { valid: false, error: 'ファイルサイズは10MB以下にしてください' }
  }
  
  // 最小解像度のチェックは画像読み込み後に実施
  return { valid: true }
}

/**
 * 画像の解像度を取得
 */
export function getImageDimensions(file: File): Promise<{ width: number; height: number }> {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({ width: img.width, height: img.height })
    }
    img.src = URL.createObjectURL(file)
  })
}