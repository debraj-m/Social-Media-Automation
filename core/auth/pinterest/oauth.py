import os
import requests
import json
from typing import Optional

class PinterestOAuthClient:
    AUTH_URL = "https://www.pinterest.com/oauth/"
    TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: str, token_path: str = "env/pinterest_token.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.token_path = token_path

    def get_auth_url(self) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
        }
        from urllib.parse import urlencode
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Optional[dict]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = requests.post(self.TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            return token_data
        except requests.RequestException as e:
            print(f"Error exchanging code for token: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def load_token(self) -> Optional[dict]:
        if not os.path.exists(self.token_path):
            return None
        try:
            with open(self.token_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load token: {e}")
            return None

    def save_token(self, token_data: dict) -> None:
        try:
            with open(self.token_path, "w") as f:
                json.dump(token_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save token: {e}")

    def prompt_authorization(self) -> str:
        auth_url = self.get_auth_url()
        print("Visit this URL to authorize the application:")
        print(auth_url)
        return input("Paste the authorization code here: ").strip()

    def get_access_token(self) -> str:
        token_data = self.load_token()
        if not token_data:
            print("No valid token found. Please re-authorize.")
            code = self.prompt_authorization()
            token_data = self.exchange_code_for_token(code)
            if not token_data:
                raise Exception("Failed to obtain access token.")
            self.save_token(token_data)
        return token_data["access_token"]
