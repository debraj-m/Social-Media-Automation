import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from dotenv import load_dotenv
load_dotenv()
import sys
from core.automation.linkedin import linkedin as linkedin_automation
from core.content_generation.generator import ContentGenerator
from core.auth.linkedin.oauth import LinkedInOAuthClient
from core.automation.twitter.twitter import TwitterBot

def run_linkedin():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="linkedin")
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
    print("Posting to LinkedIn...", token)
    success = linkedin_automation.post_to_linkedin(token, 'urn:li:organization:107168982', post)
    if success:
        print("Post successful!")

def run_twitter():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="twitter")
    print("Generated Twitter post:\n", post)
    bot = TwitterBot()
    success = bot.post_to_twitter(post)
    if success:
        print("Post successful!")
    else:
        print("Post failed.")

def run_devto():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    devto_api_key = os.environ.get("DEVTO_API_KEY")
    from core.automation.devto.devto import post_to_devto
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="devto")
    print("Generated Dev.to post:\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Dev.to Post"
    import re
    words = re.findall(r"\\b\\w{5,}\\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "python"]
    success = post_to_devto(devto_api_key, title, post, tags)
    if success:
        print("Post successful!")
    else:
        print("Post failed.")

def run_hashnode():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    hashnode_api_key = os.environ.get("HASHNODE_API_KEY")
    publication_id = os.environ.get("HASHNODE_PUBLICATION_ID")
    print(f"Using HASHNODE_PUBLICATION_ID: {publication_id}")  # Debug print
    from core.automation.hashnode.hashnode import post_to_hashnode
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="hashnode")
    print("Generated Hashnode post:\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Hashnode Post"
    import re
    words = re.findall(r"\\b\\w{5,}\\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "python"]
    success = post_to_hashnode(hashnode_api_key, title, post, tags)
    if success:
        print("Post successful!")
    else:
        print("Post failed.")

def run_blogger():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    CLIENT_ID = os.environ.get("BLOGGER_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("BLOGGER_CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("BLOGGER_REDIRECT_URI", "http://localhost:8000/")
    TOKEN_PATH = "env/blogger_token.pickle"
    from core.auth.blogger.oauth import BloggerOAuthClient
    from core.automation.blogger.blogger import post_to_blogger
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="blogger")
    print("Generated Blogger post:\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Blogger Post"
    import re
    words = re.findall(r"\\b\\w{5,}\\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "python"]
    oauth_client = BloggerOAuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        token_path=TOKEN_PATH
    )
    access_token = oauth_client.get_access_token()
    success = post_to_blogger(access_token, title, post, tags)
    if success:
        print("Post successful!")
    else:
        print("Post failed.")

def run_disqus():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    CLIENT_ID = os.environ.get("DISQUS_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("DISQUS_CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("DISQUS_REDIRECT_URI", "http://localhost:8000/")
    TOKEN_PATH = "env/disqus_token.txt"
    from core.auth.disqus.oauth import DisqusOAuthClient
    from core.automation.disqus.disqus import post_to_disqus
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="disqus")
    print("Generated Disqus post:\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Disqus Post"
    import re
    words = re.findall(r"\\b\\w{5,}\\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "python"]
    oauth_client = DisqusOAuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        token_path=TOKEN_PATH
    )
    access_token = os.environ.get("DISQUS_ACCESS_TOKEN") or oauth_client.get_access_token()
    success = post_to_disqus(access_token, title, post, tags)
    if success:
        print("Post successful!")
    else:
        print("Post failed.")

def main():
    print("Select automation platform:")
    print("1. LinkedIn")
    print("2. Twitter")
    print("3. Dev.to")
    print("4. Hashnode")
    print("5. Blogger")
    print("6. Disqus")
    choice = input("Enter a number (1-6): ").strip()
    if choice == "1":
        run_linkedin()
    elif choice == "2":
        run_twitter()
    elif choice == "3":
        run_devto()
    elif choice == "4":
        run_hashnode()
    elif choice == "5":
        run_blogger()
    elif choice == "6":
        run_disqus()
    else:
        print("Invalid choice.")
        sys.exit(1)

if __name__ == "__main__":
    main()
