"""
Supabase Storage Service Implementation
"""

import os
from typing import Optional, Dict, List, Union, Any
from supabase import create_client, Client
from ..interfaces import (
    IStorageService,
    StorageResult,
    StorageError,
    StorageFile,
    UploadOptions,
    SignedUrlOptions,
    ListOptions
)


class SupabaseStorageService(IStorageService):
    """Supabase Storage implementation"""
    
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        url = supabase_url or os.getenv('SUPABASE_URL')
        key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not url or not key:
            raise ValueError('Supabase URL and Key are required')
        
        self.supabase: Client = create_client(url, key)
    
    async def upload(
        self,
        bucket: str,
        path: str,
        file: Union[bytes, Any],
        options: Optional[UploadOptions] = None
    ) -> StorageResult:
        """Upload a file to Supabase Storage"""
        try:
            upload_options = {}
            if options:
                if options.content_type:
                    upload_options['content-type'] = options.content_type
                if options.cache_control:
                    upload_options['cache-control'] = options.cache_control
                if options.upsert:
                    upload_options['upsert'] = options.upsert
            
            response = self.supabase.storage.from_(bucket).upload(
                path=path,
                file=file,
                file_options=upload_options
            )
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            url = self.get_public_url(bucket, path)
            
            return StorageResult(
                data={
                    'path': path,
                    'url': url
                }
            )
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def download(
        self,
        bucket: str,
        path: str
    ) -> StorageResult:
        """Download a file from Supabase Storage"""
        try:
            response = self.supabase.storage.from_(bucket).download(path)
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            return StorageResult(data=response)
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def delete(
        self,
        bucket: str,
        paths: Union[str, List[str]]
    ) -> StorageResult:
        """Delete file(s) from Supabase Storage"""
        try:
            path_list = [paths] if isinstance(paths, str) else paths
            
            response = self.supabase.storage.from_(bucket).remove(path_list)
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            return StorageResult(data=None)
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def move(
        self,
        bucket: str,
        from_path: str,
        to_path: str
    ) -> StorageResult:
        """Move/rename a file in Supabase Storage"""
        try:
            response = self.supabase.storage.from_(bucket).move(from_path, to_path)
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            return StorageResult(data=None)
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def copy(
        self,
        bucket: str,
        from_path: str,
        to_path: str
    ) -> StorageResult:
        """Copy a file in Supabase Storage"""
        try:
            # Download the file first
            download_response = await self.download(bucket, from_path)
            if download_response.error:
                return download_response
            
            # Upload to new location
            upload_response = await self.upload(bucket, to_path, download_response.data)
            return upload_response
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def create_signed_url(
        self,
        bucket: str,
        path: str,
        options: SignedUrlOptions
    ) -> StorageResult:
        """Create a signed URL for a file"""
        try:
            sign_options = {
                'expires_in': options.expires_in
            }
            
            if options.download:
                sign_options['download'] = options.download
            
            if options.transform:
                transform_dict = {}
                if options.transform.width:
                    transform_dict['width'] = options.transform.width
                if options.transform.height:
                    transform_dict['height'] = options.transform.height
                if options.transform.quality:
                    transform_dict['quality'] = options.transform.quality
                if options.transform.format:
                    transform_dict['format'] = options.transform.format
                sign_options['transform'] = transform_dict
            
            response = self.supabase.storage.from_(bucket).create_signed_url(
                path=path,
                expires_in=options.expires_in,
                options=sign_options
            )
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            return StorageResult(
                data={'signed_url': response['signedURL']}
            )
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    def get_public_url(
        self,
        bucket: str,
        path: str
    ) -> str:
        """Get public URL for a file"""
        response = self.supabase.storage.from_(bucket).get_public_url(path)
        return response
    
    async def list(
        self,
        bucket: str,
        path: Optional[str] = None,
        options: Optional[ListOptions] = None
    ) -> StorageResult:
        """List files in a bucket/path"""
        try:
            list_options = {}
            if options:
                list_options['limit'] = options.limit
                list_options['offset'] = options.offset
                if options.sort_by_column and options.sort_order:
                    list_options['sortBy'] = {
                        'column': options.sort_by_column,
                        'order': options.sort_order
                    }
            
            response = self.supabase.storage.from_(bucket).list(
                path=path or '',
                options=list_options
            )
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            files = []
            for file_data in response:
                files.append(StorageFile(
                    name=file_data['name'],
                    id=file_data.get('id'),
                    size=file_data.get('metadata', {}).get('size', 0),
                    mimetype=file_data.get('metadata', {}).get('mimetype', 'application/octet-stream'),
                    created_at=file_data['created_at'],
                    updated_at=file_data['updated_at'],
                    metadata=file_data.get('metadata')
                ))
            
            return StorageResult(data=files)
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def exists(
        self,
        bucket: str,
        path: str
    ) -> bool:
        """Check if a file exists"""
        try:
            # Try to list the specific file
            parent_path = '/'.join(path.split('/')[:-1])
            filename = path.split('/')[-1]
            
            response = self.supabase.storage.from_(bucket).list(
                path=parent_path,
                options={'limit': 1, 'search': filename}
            )
            
            return len(response) > 0 if response else False
        except:
            return False
    
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        file_size_limit: Optional[int] = None,
        allowed_mime_types: Optional[List[str]] = None
    ) -> StorageResult:
        """Create a new bucket"""
        try:
            options = {'public': public}
            if file_size_limit:
                options['file_size_limit'] = file_size_limit
            if allowed_mime_types:
                options['allowed_mime_types'] = allowed_mime_types
            
            response = self.supabase.storage.create_bucket(
                id=name,
                options=options
            )
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            return StorageResult(data=None)
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def delete_bucket(
        self,
        name: str
    ) -> StorageResult:
        """Delete a bucket"""
        try:
            response = self.supabase.storage.delete_bucket(name)
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            return StorageResult(data=None)
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    async def list_buckets(self) -> StorageResult:
        """List all buckets"""
        try:
            response = self.supabase.storage.list_buckets()
            
            if hasattr(response, 'error') and response.error:
                return StorageResult(
                    error=self._map_error(response.error)
                )
            
            bucket_names = [bucket['name'] for bucket in response]
            
            return StorageResult(data=bucket_names)
        except Exception as e:
            return StorageResult(
                error=self._map_error(e)
            )
    
    def _map_error(self, error: Any) -> StorageError:
        """Map error to StorageError"""
        if isinstance(error, Exception):
            return StorageError(
                message=str(error),
                code='UNKNOWN_ERROR'
            )
        
        return StorageError(
            message=error.get('message', 'Unknown error occurred'),
            code=error.get('code', error.get('error', 'UNKNOWN_ERROR')),
            status_code=error.get('statusCode', error.get('status', 500))
        )