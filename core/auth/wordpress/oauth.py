import os
import requests
import json
import time
from typing import Optional

class WordPressOAuthClient:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, site_url: str, token_path: str = "env/wordpress_token.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.site_url = site_url
        self.token_path = token_path

    def get_token(self) -> Optional[str]:
        url = f"{self.site_url}/oauth/token"
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_data = response.json()
            self.save_token(token_data)
            return token_data.get("access_token")
        except Exception as e:
            print(f"Failed to get WordPress token: {e}")
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

    def get_access_token(self) -> str:
        token_data = self.load_token()
        if not token_data:
            print("No valid token found. Please re-authorize.")
            token = self.get_token()
            if not token:
                raise Exception("Failed to obtain access token.")
            return token
        return token_data["access_token"]
