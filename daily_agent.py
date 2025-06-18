import openai
import os
import schedule
import time
import json
from oauth import LinkedInOAuthClient
from linkedin_utils import load_token, authenticate, get_user_urn, post_to_linkedin

# Load config
from openai import OpenAI

# Load config
config = json.load(open("config.json"))

# Initialize OpenAI client with your API key
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8000/callback")
SCOPE = os.environ.get("SCOPE")
TOKEN_PATH = "linkedin_token.json"
oauth_client = LinkedInOAuthClient(
    client_id=CLIENT_ID,   
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    token_path=TOKEN_PATH
)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_post():
    prompt = (
         """My name is Debraj, just add one line after this"""
    )

    response = client.chat.completions.create(
        model="gpt-4",
        max_completion_tokens=2800,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def job():
    print("Generating daily post...")
    post = generate_post()
    print("Generated:\n", post)

    token =oauth_client.get_access_token()
    if not token:
        print("No token found. Please authenticate once.")
        authenticate()
        token =oauth_client.get_access_token()

    urn = get_user_urn(token)
    print("📤 Posting to LinkedIn...")
    post_to_linkedin(token, urn, post)

# Run immediately for testing
if __name__ == "__main__":
    schedule.every().day.at("10:00").do(job)
    print("✅ Scheduler started. Will post daily at 10:00 AM.")
    job()  # First post now
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
