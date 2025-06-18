import os
import requests
import json
import time
import webbrowser
from urllib.parse import urlencode


class LinkedInOAuthClient:
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    PROFILE_URL = "https://api.linkedin.com/v2/people/(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
    EMAIL_URL = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"

    def __init__(self, client_id, client_secret, redirect_uri, scope, token_path="linkedin_token.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.token_path = token_path

    def get_auth_url(self):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
          
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            response = requests.post(self.TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            token_data["created_at"] = int(time.time())
            return token_data
        except requests.RequestException as e:
            print(f"Error exchanging code for token: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def is_token_expired(self, token_data):
        created_at = token_data.get("created_at", 0)
        expires_in = token_data.get("expires_in", 0)
        return time.time() >= (created_at + expires_in)

    def load_token(self):
        if not os.path.exists(self.token_path):
            return None
        try:
            with open(self.token_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load token: {e}")
            return None

    def save_token(self, token_data):
        try:
            with open(self.token_path, "w") as f:
                json.dump(token_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save token: {e}")

    def prompt_authorization(self):
        auth_url = self.get_auth_url()
        print("Visit this URL to authorize the application:")
        print(auth_url)
        return input("Paste the authorization code here: ").strip()

    def get_access_token(self)->str:
        token_data = self.load_token()

        if not token_data or self.is_token_expired(token_data):
            print("No valid token found. Please re-authorize.")
            code = self.prompt_authorization()
            token_data = self.exchange_code_for_token(code)
            if not token_data:
                raise Exception("Failed to obtain access token.")
            self.save_token(token_data)

        return token_data["access_token"]


if __name__ == '__main__':
    CLIENT_ID = "86o1ujmj5p1fhy"
    CLIENT_SECRET = "WPL_AP1.GfQkChH88pKywSVP.GUVRNg=="
    REDIRECT_URI = "http://localhost:8000/linkedin/callback"
    SCOPE = "w_member_social profile openid email r_organization_social w_organization_social rw_organization_admin"

    TOKEN_PATH = "linkedin_token.json"
    oauth_client = LinkedInOAuthClient(
        client_id=CLIENT_ID,   
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        token_path=TOKEN_PATH
    )
    print(oauth_client.get_access_token())