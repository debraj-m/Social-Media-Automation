import os
import requests
import json
from typing import Optional

class RedditOAuthClient:
    AUTH_URL = "https://www.reddit.com/api/v1/authorize"
    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: str, token_path: str = "env/reddit_token.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.token_path = token_path

    def get_auth_url(self, state: str = "random_state") -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",
            "scope": self.scope,
        }
        from urllib.parse import urlencode
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Optional[dict]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        auth = (self.client_id, self.client_secret)
        headers = {"User-Agent": "YourApp/0.1 by YourRedditUsername"}
        try:
            response = requests.post(self.TOKEN_URL, data=data, headers=headers, auth=auth)
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
