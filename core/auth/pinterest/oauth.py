import os
import requests
import webbrowser
from urllib.parse import urlparse, parse_qs
import json
import logging

class PinterestOAuthClient:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str, token_path: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.token_path = token_path or "env/pinterest_token.json"
        self.logger = logging.getLogger(__name__)
        
        # Authorization URL is always pinterest.com
        self.auth_url = "https://www.pinterest.com/oauth/"
        
        # Token URL depends on environment
        self.is_sandbox = os.getenv('PINTEREST_ENV', '').lower() == 'sandbox'
        if self.is_sandbox:
            self.token_url = "https://api-sandbox.pinterest.com/v5/oauth/token"
            self.api_url = "https://api-sandbox.pinterest.com/v5"
        else:
            self.token_url = "https://api.pinterest.com/v5/oauth/token"
            self.api_url = "https://api.pinterest.com/v5"
        
        self.scope = "boards:write,boards:read,pins:read,pins:write"

    def get_authorization_url(self) -> str:
        """Generate the authorization URL for Pinterest OAuth"""
        params = {
            "response_type": "code",
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": "pinterest_oauth",
            "prompt": "consent"  # Always show consent screen
        }
        
        # Use requests to properly encode parameters
        auth_url = f"{self.auth_url}?" + "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
        print(f"[DEBUG] Authorization URL: {auth_url}")
        return auth_url

    def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        # Ensure all values are stripped of quotes and whitespace
        def clean(val):
            if val is None:
                return None
            return str(val).strip().strip('"').strip("'")

        # Pinterest requires these exact parameters in this exact format
        data = {
            "grant_type": "authorization_code",
            "code": clean(code),
            "redirect_uri": clean(self.redirect_uri)
        }
        
        # Use Basic Auth instead of client credentials in the body
        auth = (clean(self.app_id), clean(self.app_secret))
        
        print(f"[DEBUG] Token exchange URL: {self.token_url}")
        print(f"[DEBUG] Token exchange data: {data}")
        print(f"[DEBUG] Using Basic Auth with client_id: {self.app_id}")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                auth=auth
            )
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response headers: {dict(response.headers)}")
            print(f"[DEBUG] Response body: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                self.save_token(token_data)
                return token_data
            else:
                error_msg = f"Failed to exchange code for token: {response.status_code} {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Exception during token exchange: {str(e)}")
            raise

    def save_token(self, token_data: dict):
        """Save token to file"""
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
        with open(self.token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        self.logger.info(f"Token saved to {self.token_path}")

    def load_token(self) -> dict:
        """Load token from file"""
        if not os.path.exists(self.token_path):
            return None
        
        with open(self.token_path, 'r') as f:
            token_data = json.load(f)
        
        return token_data

    def get_access_token(self) -> str:
        """Get access token, handling OAuth flow if needed"""
        # Try to load existing token
        token_data = self.load_token()
        
        if token_data and 'access_token' in token_data:
            return token_data['access_token']
        
        # If no token exists, start OAuth flow
        print("No valid Pinterest token found. Starting OAuth flow...")
        auth_url = self.get_authorization_url()
        print(f"Please visit this URL to authorize the application: {auth_url}")
        
        # Open the authorization URL in the default browser
        webbrowser.open(auth_url)
        
        # Get the authorization code from user
        callback_url = input("Please enter the full callback URL after authorization: ")
        
        # Parse the callback URL to get the code
        parsed_url = urlparse(callback_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' not in query_params:
            raise Exception("No authorization code found in callback URL")
        
        code = query_params['code'][0]
        
        # Exchange code for token
        token_data = self.exchange_code_for_token(code)
        
        return token_data['access_token']

    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.app_id,
            "client_secret": self.app_secret
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(self.token_url, json=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            self.save_token(token_data)
            return token_data
        else:
            self.logger.error(f"Failed to refresh token: {response.status_code} {response.text}")
            raise Exception(f"Token refresh failed: {response.text}")
