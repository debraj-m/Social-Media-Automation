import os
from requests_oauthlib import OAuth1

class TwitterOAuthClient:
    def __init__(self):
        self.consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        self.consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        if not all([
            self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret
        ]):
            raise ValueError("Missing Twitter API credentials in environment variables.")

    def get_oauth1(self):
        return OAuth1(
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret
        )
