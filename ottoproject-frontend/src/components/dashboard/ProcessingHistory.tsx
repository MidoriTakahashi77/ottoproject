'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

interface ProcessingRequest {
  id: string
  request_type: string
  status: string
  image_metadata: {
    width: number
    height: number
    format: string
  }
  created_at: string
  completed_at?: string
}

export default function ProcessingHistory({ userId }: { userId: string }) {
  const [history, setHistory] = useState<ProcessingRequest[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [userId])

  const fetchHistory = async () => {
    const supabase = createClient()
    
    const { data, error } = await supabase
      .from('processing_requests')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(10)
    
    if (error) {
      console.error('履歴の取得に失敗:', error)
    } else {
      setHistory(data || [])
    }
    
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center">
          まだ処理履歴がありません
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="space-y-4">
        {history.map((item) => (
          <div key={item.id} className="border-b border-gray-200 pb-4 last:border-0">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {item.request_type === 'detection' ? '物体検出' : item.request_type}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {item.image_metadata.width} × {item.image_metadata.height} px
                  ({item.image_metadata.format})
                </p>
              </div>
              <div className="text-right">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  item.status === 'completed' 
                    ? 'bg-green-100 text-green-800'
                    : item.status === 'processing'
                    ? 'bg-yellow-100 text-yellow-800'
                    : item.status === 'failed'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {item.status === 'completed' ? '完了' 
                    : item.status === 'processing' ? '処理中'
                    : item.status === 'failed' ? '失敗'
                    : '待機中'}
                </span>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(item.created_at).toLocaleString('ja-JP')}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}