import requests
from typing import Optional

def post_to_wordpress(site_url: str, token: str, title: str, content: str, status: str = "publish") -> bool:
    """Post an article to WordPress via REST API."""
    url = f"{site_url}/wp-json/wp/v2/posts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "content": content,
        "status": status
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code in (200, 201):
        print("✅ WordPress post successful!")
        return True
    else:
        print("❌ WordPress post failed:", res.status_code, res.text)
        return False
