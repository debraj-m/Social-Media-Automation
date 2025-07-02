import os
import sys
from core.automation.linkedin import linkedin as linkedin_automation
# from core.automation import twitter as twitter_automation  # Uncomment if implemented
from core.content_generation.generator import ContentGenerator
from core.auth.linkedin.oauth import LinkedInOAuthClient
from core.automation.twitter.twitter import TwitterBot

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

def run_pinterest():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="pinterest")
    print("Generated Pinterest post:\n", post)
    # TODO: Add Pinterest API posting logic here
    print("[Pinterest posting not yet implemented]")

def run_reddit():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="reddit")
    print("Generated Reddit post:\n", post)
    # TODO: Add Reddit API posting logic here
    print("[Reddit posting not yet implemented]")

def run_mastodon():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="mastodon")
    print("Generated Mastodon post:\n", post)
    # TODO: Add Mastodon API posting logic here
    print("[Mastodon posting not yet implemented]")

def run_medium():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="medium")
    print("Generated Medium post:\n", post)
    # TODO: Add Medium API posting logic here
    print("[Medium posting not yet implemented]")

def run_devto():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="devto")
    print("Generated Dev.to post:\n", post)
    # TODO: Add Dev.to API posting logic here
    print("[Dev.to posting not yet implemented]")

def run_hashnode():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="hashnode")
    print("Generated Hashnode post:\n", post)
    # TODO: Add Hashnode API posting logic here
    print("[Hashnode posting not yet implemented]")

def run_ghost():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="ghost")
    print("Generated Ghost post:\n", post)
    # TODO: Add Ghost API posting logic here
    print("[Ghost posting not yet implemented]")

def run_wordpress():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="wordpress")
    print("Generated WordPress post:\n", post)
    # TODO: Add WordPress API posting logic here
    print("[WordPress posting not yet implemented]")

def main():
    print("Select automation platform:")
    print("1. LinkedIn")
    print("2. Twitter")
    print("3. Pinterest")
    print("4. Reddit")
    print("5. Mastodon")
    print("6. Medium")
    print("7. Dev.to")
    print("8. Hashnode")
    print("9. Ghost")
    print("10. WordPress")
    choice = input("Enter a number (1-10): ").strip()
    if choice == "1":
        run_linkedin()
    elif choice == "2":
        run_twitter()
    elif choice == "3":
        run_pinterest()
    elif choice == "4":
        run_reddit()
    elif choice == "5":
        run_mastodon()
    elif choice == "6":
        run_medium()
    elif choice == "7":
        run_devto()
    elif choice == "8":
        run_hashnode()
    elif choice == "9":
        run_ghost()
    elif choice == "10":
        run_wordpress()
    else:
        print("Invalid choice.")
        sys.exit(1)

if __name__ == "__main__":
    main()
