import os
import requests
import json
import time
from typing import Optional

class MediumOAuthClient:
    # Medium uses integration tokens, not OAuth for most API access
    def __init__(self, integration_token: str, token_path: str = "env/medium_token.json"):
        self.integration_token = integration_token
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
        # For Medium, the integration token is the access token
        return self.integration_token
