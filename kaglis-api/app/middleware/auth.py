"""
API key authentication middleware
"""
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader, APIKeyQuery
from starlette.status import HTTP_403_FORBIDDEN
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# APIキーの取得方法を定義
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    api_key_from_header: Optional[str] = Security(api_key_header),
    api_key_from_query: Optional[str] = Security(api_key_query),
) -> str:
    """
    Validate API key
    
    Get and validate API key from header or query parameter
    """
    # Skip if API key authentication is disabled
    if not settings.API_KEY:
        return "no-auth-required"
    
    # Get API key from header or query
    api_key = api_key_from_header or api_key_from_query
    
    if not api_key:
        logger.warning("API key not provided")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="API key required。Please provide via X-API-Key header or api_key parameter。"
        )
    
    # API key validation
    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key: {api_key[:8]}...")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API keyです"
        )
    
    return api_key


class APIKeyMiddleware:
    """
    API key authentication middleware（オプション）
    
    Use to enforce API key authentication for specific paths
    """
    
    def __init__(self, app, protected_paths: list = None):
        self.app = app
        self.protected_paths = protected_paths or ["/api/"]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            
            # Check if path is protected
            is_protected = any(
                path.startswith(protected_path) 
                for protected_path in self.protected_paths
            )
            
            # Exclude health checks etc
            if path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
                is_protected = False
            
            if is_protected and settings.API_KEY:
                # Get API key from header
                headers = dict(scope["headers"])
                api_key = None
                
                # Look for X-API-Key header
                for header_name, header_value in headers.items():
                    if header_name == b"x-api-key":
                        api_key = header_value.decode("utf-8")
                        break
                
                # Also look in query parameters
                if not api_key:
                    query_string = scope.get("query_string", b"").decode("utf-8")
                    if "api_key=" in query_string:
                        for param in query_string.split("&"):
                            if param.startswith("api_key="):
                                api_key = param.split("=")[1]
                                break
                
                # API key validation
                if not api_key or api_key != settings.API_KEY:
                    # Authentication error response
                    await send({
                        "type": "http.response.start",
                        "status": 403,
                        "headers": [
                            [b"content-type", b"application/json"],
                        ],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b'{"detail":"Invalid or missing API key"}',
                    })
                    return
        
        await self.app(scope, receive, send)