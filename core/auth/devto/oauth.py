import os
import requests
import json
import time
from typing import Optional

class DevtoOAuthClient:
    def __init__(self, api_key: str, token_path: str = "env/devto_token.json"):
        self.api_key = api_key
        self.token_path = token_path

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
        # For Dev.to, the API key is the access token
        return self.api_key
