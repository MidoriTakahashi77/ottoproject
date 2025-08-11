"""
Storage Service Factory
"""

import os
from typing import Optional, Dict, Any
from .interfaces import IStorageService, StorageProvider
from .providers.supabase_storage import SupabaseStorageService


class StorageFactory:
    """Factory class for creating storage service instances"""
    
    _instance: Optional[IStorageService] = None
    
    @classmethod
    def get_storage_service(
        cls,
        provider: Optional[StorageProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> IStorageService:
        """
        Get storage service instance
        
        Args:
            provider: Storage provider type
            config: Configuration dictionary
        
        Returns:
            Storage service instance
        """
        # Return existing instance if no provider change
        if cls._instance and not provider:
            return cls._instance
        
        # Determine provider
        if provider:
            selected_provider = provider
        else:
            provider_str = os.getenv('STORAGE_PROVIDER', 'supabase')
            selected_provider = StorageProvider(provider_str)
        
        # Create instance based on provider
        if selected_provider == StorageProvider.SUPABASE:
            cls._instance = SupabaseStorageService(
                supabase_url=config.get('supabase_url') if config else None,
                supabase_key=config.get('supabase_key') if config else None
            )
        elif selected_provider == StorageProvider.S3:
            raise NotImplementedError('S3 storage provider not implemented yet')
        elif selected_provider == StorageProvider.MINIO:
            raise NotImplementedError('MinIO storage provider not implemented yet')
        else:
            raise ValueError(f'Unknown storage provider: {selected_provider}')
        
        print(f'Storage service initialized with provider: {selected_provider.value}')
        return cls._instance
    
    @classmethod
    def get_current_provider(cls) -> StorageProvider:
        """Get current storage provider"""
        provider_str = os.getenv('STORAGE_PROVIDER', 'supabase')
        return StorageProvider(provider_str)
    
    @classmethod
    def reset(cls) -> None:
        """Reset instance (mainly for testing)"""
        cls._instance = None