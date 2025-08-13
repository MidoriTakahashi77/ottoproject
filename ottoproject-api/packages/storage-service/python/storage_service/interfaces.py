"""
Storage Service Interfaces
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List, Union, Literal, Any
from datetime import datetime


class StorageProvider(Enum):
    """Storage provider types"""
    SUPABASE = "supabase"
    S3 = "s3"
    MINIO = "minio"


@dataclass
class UploadOptions:
    """Options for file upload"""
    content_type: Optional[str] = None
    cache_control: Optional[str] = None
    upsert: bool = False
    metadata: Optional[Dict[str, str]] = None


@dataclass
class TransformOptions:
    """Image transformation options"""
    width: Optional[int] = None
    height: Optional[int] = None
    quality: Optional[int] = None
    format: Optional[Literal['webp', 'avif', 'auto']] = None


@dataclass
class SignedUrlOptions:
    """Options for signed URL generation"""
    expires_in: int  # seconds
    download: Optional[Union[bool, str]] = None
    transform: Optional[TransformOptions] = None


@dataclass
class StorageFile:
    """Storage file metadata"""
    name: str
    size: int
    mimetype: str
    created_at: str
    updated_at: str
    id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class ListOptions:
    """Options for listing files"""
    limit: int = 100
    offset: int = 0
    sort_by_column: Optional[Literal['name', 'created_at', 'updated_at']] = None
    sort_order: Optional[Literal['asc', 'desc']] = None


@dataclass
class StorageError:
    """Storage error information"""
    message: str
    code: Optional[str] = None
    status_code: Optional[int] = None


@dataclass
class StorageResult:
    """Storage operation result"""
    data: Optional[Any] = None
    error: Optional[StorageError] = None


class IStorageService(ABC):
    """Storage service interface"""
    
    @abstractmethod
    async def upload(
        self,
        bucket: str,
        path: str,
        file: Union[bytes, Any],
        options: Optional[UploadOptions] = None
    ) -> StorageResult:
        """Upload a file"""
        pass
    
    @abstractmethod
    async def download(
        self,
        bucket: str,
        path: str
    ) -> StorageResult:
        """Download a file"""
        pass
    
    @abstractmethod
    async def delete(
        self,
        bucket: str,
        paths: Union[str, List[str]]
    ) -> StorageResult:
        """Delete file(s)"""
        pass
    
    @abstractmethod
    async def move(
        self,
        bucket: str,
        from_path: str,
        to_path: str
    ) -> StorageResult:
        """Move/rename a file"""
        pass
    
    @abstractmethod
    async def copy(
        self,
        bucket: str,
        from_path: str,
        to_path: str
    ) -> StorageResult:
        """Copy a file"""
        pass
    
    @abstractmethod
    async def create_signed_url(
        self,
        bucket: str,
        path: str,
        options: SignedUrlOptions
    ) -> StorageResult:
        """Create a signed URL"""
        pass
    
    @abstractmethod
    def get_public_url(
        self,
        bucket: str,
        path: str
    ) -> str:
        """Get public URL"""
        pass
    
    @abstractmethod
    async def list(
        self,
        bucket: str,
        path: Optional[str] = None,
        options: Optional[ListOptions] = None
    ) -> StorageResult:
        """List files"""
        pass
    
    @abstractmethod
    async def exists(
        self,
        bucket: str,
        path: str
    ) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        file_size_limit: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None
    ) -> StorageResult:
        """Create a bucket"""
        pass
    
    @abstractmethod
    async def delete_bucket(
        self,
        name: str
    ) -> StorageResult:
        """Delete a bucket"""
        pass
    
    @abstractmethod
    async def list_buckets(self) -> StorageResult:
        """List all buckets"""
        pass