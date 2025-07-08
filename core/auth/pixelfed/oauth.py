import os
import json
import time
import requests
import logging
from urllib.parse import urlencode
import webbrowser

class PixelfedOAuthClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, base_url: str = None, token_path: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = base_url or os.getenv('PIXELFED_BASE_URL', 'https://pixelfed.social')
        self.token_path = token_path or "env/pixelfed_token.json"
        self.logger = logging.getLogger(__name__)
        
        # OAuth endpoints
        self.auth_url = f"{self.base_url}/oauth/authorize"
        self.token_url = f"{self.base_url}/oauth/token"
        
        # Required scopes for posting
        self.scope = "read write follow"

    def get_authorization_url(self) -> str:
        """Generate the authorization URL for Pixelfed OAuth"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        self.logger.info(f"Authorization URL generated: {auth_url}")
        return auth_url

    def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri
            }
            
            headers = {
                "Accept": "application/json",
                "User-Agent": "ai-marketing-suite/1.0"
            }
            
            self.logger.info("Exchanging code for token...")
            response = requests.post(self.token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                # Add timestamp for expiry checking
                token_data["created_at"] = int(time.time())
                self.save_token(token_data)
                return token_data
                
            error_msg = f"Failed to exchange code for token: {response.status_code} {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            self.logger.error(f"Error exchanging code for token: {str(e)}")
            raise

    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token"""
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            headers = {
                "Accept": "application/json",
                "User-Agent": "ai-marketing-suite/1.0"
            }
            
            response = requests.post(self.token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                token_data["created_at"] = int(time.time())
                self.save_token(token_data)
                return token_data
                
            error_msg = f"Failed to refresh token: {response.status_code} {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            self.logger.error(f"Error refreshing token: {str(e)}")
            raise

    def save_token(self, token_data: dict):
        """Save token data to file"""
        try:
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f)
            self.logger.info(f"Token saved to {self.token_path}")
        except Exception as e:
            self.logger.error(f"Failed to save token: {str(e)}")
            raise

    def load_token(self) -> dict:
        """Load token data from file"""
        try:
            if not os.path.exists(self.token_path):
                return None
            with open(self.token_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load token: {str(e)}")
            return None

    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        token_data = self.load_token()
        if not token_data:
            return None
            
        # Check if token is expired (with 5 min buffer)
        now = int(time.time())
        expires_at = token_data.get("created_at", 0) + token_data.get("expires_in", 3600)
        
        if now >= (expires_at - 300):  # 5 minute buffer
            if "refresh_token" in token_data:
                token_data = self.refresh_token(token_data["refresh_token"])
            else:
                return None
                
        return token_data.get("access_token")
