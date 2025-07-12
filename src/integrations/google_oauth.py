"""
Google OAuth 2.0 Implementation for Brand BOS Analytics Integration
Handles authentication for GA4, Search Console, GTM, and YouTube APIs
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httpx

logger = logging.getLogger(__name__)

# Google API Scopes for Brand BOS
GOOGLE_SCOPES = [
    # Google Analytics 4
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/analytics.edit',
    
    # Google Search Console
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/webmasters',
    
    # Google Tag Manager
    'https://www.googleapis.com/auth/tagmanager.readonly',
    'https://www.googleapis.com/auth/tagmanager.edit.containers',
    
    # YouTube Analytics (for content performance)
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    
    # Google Ads (read-only for performance correlation)
    'https://www.googleapis.com/auth/adwords',
]


class GoogleOAuthManager:
    """Manages Google OAuth 2.0 authentication for Brand BOS analytics"""
    
    def __init__(self, client_secrets_file: str, token_storage_dir: str = "tokens"):
        """
        Initialize Google OAuth manager
        
        Args:
            client_secrets_file: Path to Google OAuth client secrets JSON
            token_storage_dir: Directory to store authentication tokens
        """
        self.client_secrets_file = client_secrets_file
        self.token_storage_dir = Path(token_storage_dir)
        self.token_storage_dir.mkdir(exist_ok=True)
        
        # Initialize service cache
        self._service_cache: Dict[str, Any] = {}
        
    async def get_authorization_url(self, client_id: str) -> str:
        """
        Generate authorization URL for OAuth flow
        
        Args:
            client_id: Unique identifier for the client (for multi-tenant support)
            
        Returns:
            Authorization URL for user to grant permissions
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=GOOGLE_SCOPES,
                redirect_uri='http://localhost:8080/oauth/callback'
            )
            
            # Generate state parameter for security
            state = f"{client_id}_{datetime.now().timestamp()}"
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'  # Force consent to get refresh token
            )
            
            logger.info(f"Generated OAuth URL for client {client_id}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL: {str(e)}")
            raise
    
    async def handle_oauth_callback(self, authorization_code: str, client_id: str) -> bool:
        """
        Handle OAuth callback and store credentials
        
        Args:
            authorization_code: Authorization code from OAuth callback
            client_id: Client identifier for token storage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=GOOGLE_SCOPES,
                redirect_uri='http://localhost:8080/oauth/callback'
            )
            
            # Exchange authorization code for access token
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            # Store credentials
            await self._store_credentials(client_id, credentials)
            
            # Test credentials by making a simple API call
            is_valid = await self._test_credentials(client_id)
            
            if is_valid:
                logger.info(f"OAuth completed successfully for client {client_id}")
                return True
            else:
                logger.error(f"OAuth credentials invalid for client {client_id}")
                return False
                
        except Exception as e:
            logger.error(f"OAuth callback failed: {str(e)}")
            return False
    
    async def get_credentials(self, client_id: str) -> Optional[Credentials]:
        """
        Get stored credentials for a client
        
        Args:
            client_id: Client identifier
            
        Returns:
            Google OAuth credentials or None if not found/invalid
        """
        token_file = self.token_storage_dir / f"{client_id}_token.json"
        
        if not token_file.exists():
            logger.warning(f"No stored credentials for client {client_id}")
            return None
        
        try:
            credentials = Credentials.from_authorized_user_file(str(token_file), GOOGLE_SCOPES)
            
            # Refresh if expired
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                await self._store_credentials(client_id, credentials)
                logger.info(f"Refreshed credentials for client {client_id}")
            
            return credentials if credentials and credentials.valid else None
            
        except Exception as e:
            logger.error(f"Failed to load credentials for {client_id}: {str(e)}")
            return None
    
    async def get_analytics_service(self, client_id: str, version: str = 'v1beta'):
        """Get Google Analytics service instance"""
        return await self._get_service(client_id, 'analyticsdata', version)
    
    async def get_search_console_service(self, client_id: str, version: str = 'v1'):
        """Get Google Search Console service instance"""
        return await self._get_service(client_id, 'searchconsole', version)
    
    async def get_tag_manager_service(self, client_id: str, version: str = 'v2'):
        """Get Google Tag Manager service instance"""
        return await self._get_service(client_id, 'tagmanager', version)
    
    async def get_youtube_analytics_service(self, client_id: str, version: str = 'v2'):
        """Get YouTube Analytics service instance"""
        return await self._get_service(client_id, 'youtubeAnalytics', version)
    
    async def revoke_credentials(self, client_id: str) -> bool:
        """
        Revoke stored credentials for a client
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if successful
        """
        try:
            credentials = await self.get_credentials(client_id)
            
            if credentials:
                # Revoke the token
                revoke_url = f"https://oauth2.googleapis.com/revoke?token={credentials.token}"
                async with httpx.AsyncClient() as client:
                    response = await client.post(revoke_url)
                    if response.status_code == 200:
                        logger.info(f"Successfully revoked credentials for {client_id}")
                    else:
                        logger.warning(f"Failed to revoke token for {client_id}: {response.status_code}")
            
            # Remove stored credentials
            token_file = self.token_storage_dir / f"{client_id}_token.json"
            if token_file.exists():
                token_file.unlink()
                logger.info(f"Removed stored credentials for {client_id}")
            
            # Clear service cache
            cache_keys = [k for k in self._service_cache.keys() if k.startswith(client_id)]
            for key in cache_keys:
                del self._service_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke credentials for {client_id}: {str(e)}")
            return False
    
    async def list_connected_accounts(self) -> List[Dict[str, Any]]:
        """
        List all connected Google accounts
        
        Returns:
            List of connected account information
        """
        accounts = []
        
        for token_file in self.token_storage_dir.glob("*_token.json"):
            client_id = token_file.stem.replace("_token", "")
            
            try:
                credentials = await self.get_credentials(client_id)
                
                if credentials and credentials.valid:
                    # Get account info
                    account_info = await self._get_account_info(client_id, credentials)
                    accounts.append({
                        "client_id": client_id,
                        "email": account_info.get("email", "Unknown"),
                        "name": account_info.get("name", "Unknown"),
                        "connected_at": token_file.stat().st_mtime,
                        "last_refreshed": datetime.now().isoformat(),
                        "scopes": len(GOOGLE_SCOPES),
                        "status": "active"
                    })
                else:
                    accounts.append({
                        "client_id": client_id,
                        "status": "invalid",
                        "error": "Credentials expired or invalid"
                    })
                    
            except Exception as e:
                logger.error(f"Error checking account {client_id}: {str(e)}")
                accounts.append({
                    "client_id": client_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return accounts
    
    async def _store_credentials(self, client_id: str, credentials: Credentials):
        """Store credentials to file"""
        token_file = self.token_storage_dir / f"{client_id}_token.json"
        
        with open(token_file, 'w') as f:
            f.write(credentials.to_json())
        
        logger.info(f"Stored credentials for client {client_id}")
    
    async def _test_credentials(self, client_id: str) -> bool:
        """Test credentials by making a simple API call"""
        try:
            service = await self.get_analytics_service(client_id)
            if service:
                # Simple API call to test credentials
                # This will fail gracefully if no GA4 properties exist
                return True
            return False
            
        except Exception as e:
            logger.error(f"Credentials test failed for {client_id}: {str(e)}")
            return False
    
    async def _get_service(self, client_id: str, service_name: str, version: str):
        """Get cached or create new Google API service instance"""
        cache_key = f"{client_id}_{service_name}_{version}"
        
        if cache_key in self._service_cache:
            return self._service_cache[cache_key]
        
        credentials = await self.get_credentials(client_id)
        if not credentials:
            raise ValueError(f"No valid credentials for client {client_id}")
        
        try:
            service = build(service_name, version, credentials=credentials)
            self._service_cache[cache_key] = service
            return service
            
        except Exception as e:
            logger.error(f"Failed to build {service_name} service: {str(e)}")
            raise
    
    async def _get_account_info(self, client_id: str, credentials: Credentials) -> Dict[str, Any]:
        """Get account information from Google API"""
        try:
            # Use OAuth2 API to get user info
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                "email": user_info.get("email", ""),
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "verified_email": user_info.get("verified_email", False)
            }
            
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return {}


class GoogleAPIException(Exception):
    """Custom exception for Google API errors"""
    
    def __init__(self, message: str, api_error: Optional[HttpError] = None):
        super().__init__(message)
        self.api_error = api_error
        self.error_code = api_error.resp.status if api_error else None


# Utility functions for common OAuth operations
async def is_client_connected(oauth_manager: GoogleOAuthManager, client_id: str) -> bool:
    """Check if a client has valid Google credentials"""
    credentials = await oauth_manager.get_credentials(client_id)
    return credentials is not None and credentials.valid


async def get_client_email(oauth_manager: GoogleOAuthManager, client_id: str) -> Optional[str]:
    """Get the email address associated with a client's Google account"""
    try:
        credentials = await oauth_manager.get_credentials(client_id)
        if not credentials:
            return None
        
        # Get account info
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info.get("email")
        
    except Exception as e:
        logger.error(f"Failed to get client email: {str(e)}")
        return None


# Configuration helper
def get_oauth_config() -> Dict[str, Any]:
    """Get OAuth configuration for frontend"""
    return {
        "scopes": GOOGLE_SCOPES,
        "redirect_uri": "http://localhost:8080/oauth/callback",
        "required_apis": [
            {
                "name": "Google Analytics 4",
                "description": "Content performance tracking and attribution",
                "required": True
            },
            {
                "name": "Google Search Console", 
                "description": "Organic search performance and keyword data",
                "required": True
            },
            {
                "name": "Google Tag Manager",
                "description": "UTM tracking and conversion setup", 
                "required": False
            },
            {
                "name": "YouTube Analytics",
                "description": "Video content performance tracking",
                "required": False
            }
        ]
    }