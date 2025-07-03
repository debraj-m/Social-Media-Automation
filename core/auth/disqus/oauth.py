import os
import requests
from requests_oauthlib import OAuth2Session

class DisqusOAuthClient:
    def __init__(self, client_id, client_secret, redirect_uri, token_path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_path = token_path
        self.authorization_base_url = "https://disqus.com/api/oauth/2.0/authorize/"
        self.token_url = "https://disqus.com/api/oauth/2.0/access_token/"

    def get_access_token(self):
        token = None
        if os.path.exists(self.token_path):
            with open(self.token_path, 'r') as f:
                token = f.read().strip()
        if not token:
            oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)
            authorization_url, state = oauth.authorization_url(self.authorization_base_url)
            print(f"Go to the following URL and authorize access: {authorization_url}")
            redirect_response = input("Paste the full redirect URL here: ")
            token_data = oauth.fetch_token(
                self.token_url,
                authorization_response=redirect_response,
                client_id=self.client_id,
                client_secret=self.client_secret,
                include_client_id=True
            )
            token = token_data["access_token"]
            with open(self.token_path, 'w') as f:
                f.write(token)
        return token
