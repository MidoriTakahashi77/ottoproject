"""
Firestoreキャッシュサービス
"""
import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from google.cloud import firestore
from google.api_core import exceptions

logger = logging.getLogger(__name__)

class FirestoreCache:
    """Firestoreを使用したキャッシュサービス"""
    
    def __init__(self):
        """初期化"""
        self.enabled = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
        self.collection_name = "detection_cache"
        
        if self.enabled:
            try:
                # Firestore クライアント初期化
                # エミュレータ使用時は FIRESTORE_EMULATOR_HOST が設定される
                if os.getenv("FIRESTORE_EMULATOR_HOST"):
                    logger.info(f"Using Firestore Emulator: {os.getenv('FIRESTORE_EMULATOR_HOST')}")
                    self.db = firestore.Client(project=os.getenv("FIRESTORE_PROJECT_ID", "furniture-detection-local"))
                else:
                    self.db = firestore.Client()
                
                logger.info("Firestore cache initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore: {e}")
                self.enabled = False
                self.db = None
        else:
            self.db = None
            logger.info("Cache disabled")
    
    def generate_key(self, image_data: bytes, confidence_threshold: float) -> str:
        """
        キャッシュキーを生成
        
        Args:
            image_data: 画像データ
            confidence_threshold: 信頼度閾値
            
        Returns:
            キャッシュキー
        """
        # 画像のハッシュ値を計算
        image_hash = hashlib.sha256(image_data).hexdigest()
        
        # 閾値を含めたキーを生成
        cache_key = f"{image_hash}_{confidence_threshold:.2f}"
        
        return cache_key
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        キャッシュから取得
        
        Args:
            key: キャッシュキー
            
        Returns:
            キャッシュデータまたはNone
        """
        if not self.enabled or not self.db:
            return None
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(key)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # 有効期限チェック
                expires_at = data.get("expires_at")
                if expires_at and expires_at > datetime.now():
                    logger.info(f"Cache hit: {key}")
                    return data.get("result")
                else:
                    # 期限切れの場合は削除
                    doc_ref.delete()
                    logger.info(f"Cache expired: {key}")
            
            logger.info(f"Cache miss: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Dict[str, Any]) -> bool:
        """
        キャッシュに保存
        
        Args:
            key: キャッシュキー
            value: 保存するデータ
            
        Returns:
            成功フラグ
        """
        if not self.enabled or not self.db:
            return False
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(key)
            
            # 有効期限を設定
            expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
            
            # データを保存
            doc_ref.set({
                "result": value,
                "expires_at": expires_at,
                "created_at": datetime.now(),
                "hit_count": 0
            })
            
            logger.info(f"Cache set: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def increment_hit_count(self, key: str):
        """
        キャッシュヒット数をインクリメント
        
        Args:
            key: キャッシュキー
        """
        if not self.enabled or not self.db:
            return
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(key)
            doc_ref.update({
                "hit_count": firestore.Increment(1),
                "last_accessed": datetime.now()
            })
        except Exception as e:
            logger.error(f"Failed to increment hit count: {e}")
    
    async def clear_expired(self):
        """期限切れキャッシュを削除"""
        if not self.enabled or not self.db:
            return
        
        try:
            # 期限切れドキュメントを検索
            expired_docs = self.db.collection(self.collection_name).where(
                "expires_at", "<", datetime.now()
            ).stream()
            
            # バッチ削除
            batch = self.db.batch()
            count = 0
            
            for doc in expired_docs:
                batch.delete(doc.reference)
                count += 1
                
                # バッチサイズ制限（500）
                if count >= 500:
                    batch.commit()
                    batch = self.db.batch()
                    count = 0
            
            if count > 0:
                batch.commit()
            
            logger.info(f"Cleared {count} expired cache entries")
            
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        キャッシュ統計を取得
        
        Returns:
            統計情報
        """
        if not self.enabled or not self.db:
            return {"enabled": False}
        
        try:
            collection = self.db.collection(self.collection_name)
            
            # ドキュメント数を取得
            total_docs = len(list(collection.stream()))
            
            # 期限切れドキュメント数
            expired_docs = len(list(collection.where(
                "expires_at", "<", datetime.now()
            ).stream()))
            
            return {
                "enabled": True,
                "total_entries": total_docs,
                "expired_entries": expired_docs,
                "active_entries": total_docs - expired_docs,
                "ttl_seconds": self.ttl_seconds
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"enabled": True, "error": str(e)}