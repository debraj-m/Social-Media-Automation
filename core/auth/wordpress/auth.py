import os
import requests
import json
from typing import Optional

class WordPressAuthClient:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, site_url: str, token_path: str = "env/wordpress_token.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.site_url = site_url
        self.token_path = token_path

    def get_token(self) -> Optional[str]:
        # For WordPress.com, use OAuth2; for self-hosted, use Application Passwords
        # This is a placeholder for OAuth2
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
            return token_data.get("access_token")
        except Exception as e:
            print(f"Failed to get WordPress token: {e}")
            return None
