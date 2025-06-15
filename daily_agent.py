import openai
import schedule
import time
import json
from linkedin_utils import load_token, authenticate, get_user_urn, post_to_linkedin

# Load config
from openai import OpenAI

# Load config
config = json.load(open("config.json"))

# Initialize OpenAI client with your API key
client = OpenAI(api_key=config["openai_api_key"])

def generate_post():
    prompt = (
         """You are an AI content generator helping me write LinkedIn posts for each blog article based on tools listed on Helpothon.com. For each tool, generate a short LinkedIn post using the following format:

        1. Tone: Conversational, humorous, and storytelling.
        2. Audience: Young professionals, developers, students, and creators.
3. Style:
   - Start with a quirky or funny story, personal experience, or observation that loosely relates to the tool’s function.
   - Smoothly transition to what the tool does.
   - Mention that a full blog is available.
   - End with a light CTA (e.g., "Check it out", "Link in comments", "Ever tried something like this?").

4. Output: 1 short LinkedIn post (~100–150 words) per tool.

5. Tools (from Helpothon.com) to generate posts for:
   - Scanmeee
   - Formatweaver
   - Snapcompress
   - Pixelartz
   - Allrandomtools
   - CasualGameZone
   - Calculatedaily
   - Picxcraft
   - Aimageasy
   - Pichaverse
   - PrettyParser
   - MoodyBuddy

Ensure each post is unique and lightly witty, suitable for LinkedIn. Keep hashtags optional and minimal."""
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def job():
    print("⚙️ Generating daily post...")
    post = generate_post()
    print("📝 Generated:\n", post)

    token = load_token()
    if not token:
        print("🔐 No token found. Please authenticate once.")
        authenticate()
        token = load_token()

    urn = get_user_urn(token)
    print("📤 Posting to LinkedIn...")
    post_to_linkedin(token, urn, post)

# Run immediately for testing
if __name__ == "__main__":
    schedule.every().day.at("10:00").do(job)
    print("✅ Scheduler started. Will post daily at 10:00 AM.")
    job()  # First post now
    while True:
        schedule.run_pending()
        time.sleep(60)
