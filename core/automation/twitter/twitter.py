import os
import requests
from core.content_generation.generator import ContentGenerator
from core.auth.twitter.oauth import TwitterOAuthClient
from core.image_generation.generator import ImageGenerator
import logging
from typing import Optional
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterBot:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.oauth_client = TwitterOAuthClient()
        self.image_generator = ImageGenerator()

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

    def post_to_twitter_with_image(self, tweet_text: str, image_data: bytes = None) -> bool:
        """Post tweet with image"""
        try:
            # First, upload the image
            media_id = self.upload_image(image_data) if image_data else None
            if not media_id:
                logger.warning("Image upload failed or no image data, falling back to text-only tweet")
                return self.post_to_twitter(tweet_text)
            
            # Then post the tweet with the image
            url = "https://api.twitter.com/2/tweets"
            auth = self.oauth_client.get_oauth1()
            payload = {
                "text": tweet_text,
                "media": {"media_ids": [media_id]}
            }
            
            response = requests.post(url, json=payload, auth=auth)
            if response.status_code in (200, 201):
                logger.info("Tweet with image posted successfully via API.")
                return True
            else:
                logger.error(f"Failed to post tweet with image via API: {response.status_code} {response.text}")
                
                # If posting with image fails due to permissions, try without image
                if response.status_code == 403:
                    logger.warning("Image posting not permitted, falling back to text-only tweet")
                    return self.post_to_twitter(tweet_text)
                
                return False
                
        except Exception as e:
            logger.error(f"Error posting tweet with image: {str(e)}")
            logger.warning("Falling back to text-only tweet")
            return self.post_to_twitter(tweet_text)

    def upload_image(self, image_data: bytes) -> Optional[str]:
        """Upload image to Twitter and return media_id"""
        try:
            url = "https://upload.twitter.com/1.1/media/upload.json"
            auth = self.oauth_client.get_oauth1()
            
            import io
            files = {'media': ('image.png', io.BytesIO(image_data), 'image/png')}
            response = requests.post(url, files=files, auth=auth)
            
            if response.status_code == 200:
                media_id = response.json()['media_id_string']
                logger.info(f"Image uploaded successfully. Media ID: {media_id}")
                return media_id
            else:
                logger.error(f"Failed to upload image: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return None

    def show_image_preview(self, image_path: str) -> None:
        """Show image preview to user"""
        try:
            full_path = os.path.abspath(image_path)
            print(f"\n📸 Generated Image Preview:")
            print(f"📁 Image saved at: {full_path}")
            
            # Try to open the image with default viewer
            try:
                if sys.platform == "win32":
                    os.startfile(image_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", image_path])
                else:
                    subprocess.run(["xdg-open", image_path])
                print("🖼️  Image opened in default viewer")
            except Exception as e:
                print(f"⚠️  Could not open image automatically: {str(e)}")
                print(f"💡 Please manually open: {full_path}")
                
        except Exception as e:
            logger.error(f"Error showing image preview: {str(e)}")

    def get_user_approval(self, tweet_text: str, image_path: str) -> bool:
        """Get user approval for tweet and image"""
        print("\n" + "="*60)
        print("🐦 TWITTER POST PREVIEW")
        print("="*60)
        print(f"📝 Tweet Text:")
        print(f"   {tweet_text}")
        print(f"📊 Character count: {len(tweet_text)}/280")
        
        if image_path:
            print(f"\n🖼️  Image: {os.path.basename(image_path)}")
            self.show_image_preview(image_path)
        
        print("\n" + "="*60)
        
        while True:
            choice = input("✅ Do you approve this tweet? (y/n/e): ").lower().strip()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            elif choice in ['e', 'edit']:
                new_text = input("📝 Enter new tweet text: ").strip()
                if new_text:
                    tweet_text = new_text
                    print(f"\n📝 Updated tweet: {tweet_text}")
                    print(f"📊 Character count: {len(tweet_text)}/280")
                    continue
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'e' to edit")

    def run_automation_with_approval(self, generate_image: bool = True, scenario: str = None) -> bool:
        """Run Twitter automation with user approval"""
        try:
            # Generate story-based content
            generator = ContentGenerator(self.openai_api_key)
            
            # Use story-based content generation if scenario is provided
            if scenario and scenario != "auto-detect":
                tweet = generator.generate_story_based_content(platform="twitter", scenario=scenario)
            else:
                # Use regular content generation and let image generator detect scenario
                tweet = generator.generate_content(platform="twitter")
            
            if not tweet:
                print("❌ Failed to generate tweet content")
                return False
            
            logger.info(f"Generated tweet: {tweet}")
            
            # Generate image if requested
            image_path = None
            if generate_image:
                print("🎨 Generating image for your tweet...")
                
                # Detect scenario from tweet content if not provided
                detected_scenario = self.image_generator.detect_scenario_from_content(tweet)
                final_scenario = scenario if scenario and scenario != "auto-detect" else detected_scenario
                
                print(f"📍 Using scenario: {final_scenario}")
                
                image_path = self.image_generator.generate_human_image_for_story(tweet, final_scenario)
                
                if image_path:
                    print(f"✅ Image generated successfully!")
                else:
                    print("⚠️  Image generation failed, proceeding without image")
            
            # Get user approval
            if self.get_user_approval(tweet, image_path):
                print("\n🚀 Posting to Twitter...")
                
                # Post with or without image
                if image_path:
                    success = self.post_to_twitter_with_image(tweet, image_path)
                else:
                    success = self.post_to_twitter(tweet)
                
                if success:
                    print("🎉 Tweet posted successfully!")
                    return True
                else:
                    print("❌ Failed to post tweet")
                    return False
            else:
                print("❌ Tweet cancelled by user")
                return False
                
        except Exception as e:
            logger.error(f"Error in Twitter automation: {str(e)}")
            return False

    def run_automation(self):
        """Original automation method (kept for backwards compatibility)"""
        generator = ContentGenerator(self.openai_api_key)
        tweet = generator.generate_content(platform="twitter")
        logger.info(f"Generated tweet: {tweet}")
        return self.post_to_twitter(tweet)