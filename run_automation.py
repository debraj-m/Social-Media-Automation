import os
import sys
from core.automation import linkedin as linkedin_automation
# from core.automation import twitter as twitter_automation  # Uncomment if implemented
from core.content_generation.generator import ContentGenerator
from core.auth.linkedin.oauth import LinkedInOAuthClient
from core.automation.twitter import TwitterBot

def run_linkedin():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    # prompt = input("Enter the prompt for your LinkedIn post: ")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content()
    print("Generated post:\n", post)
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8000/callback")
    SCOPE = os.environ.get("SCOPE")
    TOKEN_PATH = "env/linkedin_token.json"
    oauth_client = LinkedInOAuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        token_path=TOKEN_PATH
    )
    token = oauth_client.get_access_token()
    print("Posting to LinkedIn...",token)
    success = linkedin_automation.post_to_linkedin(token, 'urn:li:organization:107168982', post)
    if success:
        print("Post successful!")

def run_twitter():
    bot = TwitterBot()
    # topic = input("Enter topic for the tweet.")
    bot.run_automation()

def main():
    print("Select automation platform:")
    print("1. LinkedIn")
    print("2. Twitter")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        run_linkedin()
    elif choice == "2":
        run_twitter()
    else:
        print("Invalid choice.")
        sys.exit(1)

if __name__ == "__main__":
    main()
