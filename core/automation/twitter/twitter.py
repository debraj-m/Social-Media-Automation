import os
import requests
from core.content_generation.generator import ContentGenerator
from core.auth.twitter.oauth import TwitterOAuthClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterBot:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.oauth_client = TwitterOAuthClient()

    def post_to_twitter(self, tweet_text):
        url = "https://api.twitter.com/2/tweets"
        auth = self.oauth_client.get_oauth1()
        payload = {"text": tweet_text}
        response = requests.post(url, json=payload, auth=auth)
        if response.status_code in (200, 201):
            logger.info("Tweet posted successfully via API.")
            return True
        else:
            logger.error(f"Failed to post tweet via API: {response.status_code} {response.text}")
            return False

    def run_automation(self):
        generator = ContentGenerator(self.openai_api_key)
        tweet = generator.generate_content(platform="twitter")
        logger.info(f"Generated tweet: {tweet}")
        return self.post_to_twitter(tweet)