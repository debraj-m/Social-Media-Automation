import os
import requests
import webbrowser
from urllib.parse import urlencode
import json
import logging
import uuid
import base64
from pathlib import Path
import time

class RedditOAuthClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, token_path: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_path = token_path or "env/reddit_token.json"
        self.logger = logging.getLogger(__name__)
        
        # Reddit OAuth URLs
        self.auth_url = "https://www.reddit.com/api/v1/authorize"
        self.token_url = "https://www.reddit.com/api/v1/access_token"
        
        # Reddit requires these scopes for posting and flair management
        self.scope = "identity submit flair"

    def get_authorization_url(self) -> str:
        """Generate the authorization URL for Reddit OAuth"""
        state = str(uuid.uuid4())  # Generate random state for security
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",  # Get a refresh token
            "scope": self.scope
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        print(f"[DEBUG] Authorization URL: {auth_url}")
        return auth_url, state

    def exchange_code_for_token(self, code: str, state: str) -> dict:
        """Exchange authorization code for access token"""
        try:
            # Clean the code (remove any trailing fragments)
            code = code.split('#')[0].strip()
            
            # Reddit requires Basic Auth with client_id:client_secret
            auth = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ai-marketing-suite/1.0"  # Added User-Agent
            }
            
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri
            }
            
            print(f"[DEBUG] Token exchange URL: {self.token_url}")
            print(f"[DEBUG] Token exchange data: {data}")
            
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                response = requests.post(
                    self.token_url,
                    headers=headers,
                    data=data
                )
                
                print(f"[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response headers: {dict(response.headers)}")
                print(f"[DEBUG] Response body: {response.text}")
                
                if response.status_code == 200:
                    token_data = response.json()
                    # Add timestamp for expiry checking
                    token_data["created_at"] = int(time.time())
                    self.save_token(token_data)
                    return token_data
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        print(f"Rate limited. Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    
                error_msg = f"Failed to exchange code for token: {response.status_code} {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Exception during token exchange: {str(e)}")
            raise

    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token"""
        try:
            # Reddit requires Basic Auth with client_id:client_secret
            auth = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ai-marketing-suite/1.0"  # Added User-Agent
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                response = requests.post(
                    self.token_url,
                    headers=headers,
                    data=data
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    # Add refresh token back as Reddit doesn't include it in refresh response
                    token_data["refresh_token"] = refresh_token
                    # Add timestamp for expiry checking
                    token_data["created_at"] = int(time.time())
                    self.save_token(token_data)
                    return token_data
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        print(f"Rate limited. Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    
                error_msg = f"Failed to refresh token: {response.status_code} {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Exception during token refresh: {str(e)}")
            raise

    def save_token(self, token_data: dict):
        """Save token data to file"""
        try:
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f)
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

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token"""
        try:
            auth = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ai-marketing-suite/1.0"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            response = requests.post(
                self.token_url,
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                # Add refresh_token back as Reddit doesn't include it in refresh response
                token_data["refresh_token"] = refresh_token
                token_data["created_at"] = int(time.time())
                self.save_token(token_data)
                return token_data
                
            error_msg = f"Failed to refresh token: {response.status_code} {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            self.logger.error(f"Error refreshing token: {str(e)}")
            raise

    def get_valid_token(self) -> dict:
        """Get a valid access token, refreshing if necessary"""
        token_data = self.load_token()
        if not token_data:
            return None
            
        # Check if token is expired (with 5 min buffer)
        now = int(time.time())
        expires_at = token_data.get("created_at", 0) + token_data.get("expires_in", 0)
        
        if now >= (expires_at - 300):  # 5 minute buffer
            if "refresh_token" in token_data:
                return self.refresh_access_token(token_data["refresh_token"])
            return None
            
        return token_data

    def get_access_token(self) -> str:
        """Get the current access token string"""
        token_data = self.get_valid_token()
        return token_data.get("access_token") if token_data else None
