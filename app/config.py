"""
アプリケーション設定
"""
import os
from typing import List
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

class Settings:
    """アプリケーション設定"""
    
    # 環境設定
    ENV: str = os.getenv("ENV", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # サーバー設定
    PORT: int = int(os.getenv("PORT", "8080"))
    
    # Google Cloud設定
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Firestore設定
    FIRESTORE_EMULATOR_HOST: str = os.getenv("FIRESTORE_EMULATOR_HOST", "")
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "furniture-detection-local")
    
    # モデル設定
    MODEL_SIZE: str = os.getenv("MODEL_SIZE", "n")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    
    # API設定
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_FILE_SIZE: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    API_KEY: str = os.getenv("API_KEY", "")
    
    # キャッシュ設定
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # 許可される画像形式
    ALLOWED_FORMATS: set = {'image/jpeg', 'image/png', 'image/webp'}
    
    @classmethod
    def is_development(cls) -> bool:
        """開発環境かどうか"""
        return cls.ENV == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """本番環境かどうか"""
        return cls.ENV == "production"
    
    @classmethod
    def is_test(cls) -> bool:
        """テスト環境かどうか"""
        return cls.ENV == "test"

# シングルトンインスタンス
settings = Settings()