import requests
from typing import Optional

def post_to_reddit(token: str, subreddit: str, title: str, text: str) -> bool:
    """Post a text submission to a subreddit using Reddit API."""
    url = "https://oauth.reddit.com/api/submit"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "YourApp/0.1 by YourRedditUsername"
    }
    data = {
        "sr": subreddit,
        "title": title,
        "kind": "self",
        "text": text
    }
    res = requests.post(url, headers=headers, data=data)
    if res.status_code == 200:
        print("✅ Reddit post successful!")
        return True
    else:
        print("❌ Reddit post failed:", res.status_code, res.text)
        return False
