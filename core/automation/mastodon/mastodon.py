import os
import logging
from mastodon import Mastodon, MastodonError

class MastodonAutomation:
    def __init__(self, access_token: str, api_base_url: str = "https://mastodon.social"):
        self.logger = logging.getLogger(__name__)
        self.api_base_url = api_base_url
        self.mastodon = Mastodon(
            access_token=access_token,
            api_base_url=api_base_url
        )

    def post_status(self, content: str, image_data: bytes = None):
        try:
            # Don't truncate content since Mastodon actually allows up to 500 words
            media_ids = None
            if image_data:
                # Upload image buffer directly
                media = self.mastodon.media_post(image_data, mime_type='image/png')
                media_ids = [media['id']]
                self.logger.info(f"Uploaded image to Mastodon: {media['id']}")
            status = self.mastodon.status_post(content, media_ids=media_ids)
            self.logger.info(f"Posted to Mastodon: {status['url']}")
            return True
        except MastodonError as e:
            self.logger.error(f"Failed to post to Mastodon: {e}")
            return False

if __name__ == "__main__":
    # You can set these as environment variables or replace with your credentials
    ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN", "yPt7rZlYyXmJQ-XSSLa2OFQuL15PHzlPa1CcQgDFCT0")
    API_BASE_URL = os.getenv("MASTODON_API_BASE_URL", "https://mastodon.social")

    from core.content_generation.generator import ContentGenerator

    # Use your OpenAI API key here
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
    generator = ContentGenerator(OPENAI_API_KEY)
    content = generator.generate_content(platform="mastodon")
    image_path = None  # Set this to your image path if you want to test image posting
    if content:
        mastodon_bot = MastodonAutomation(ACCESS_TOKEN, API_BASE_URL)
        mastodon_bot.post_status(content, image_data=image_path)
    else:
        print("Failed to generate content.")
