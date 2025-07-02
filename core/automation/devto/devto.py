import requests
from typing import Optional

def post_to_devto(api_key: str, title: str, body_markdown: str, tags: list = None) -> bool:
    """Post an article to Dev.to."""
    url = "https://dev.to/api/articles"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": True
        }
    }
    if tags:
        data["article"]["tags"] = tags
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 201:
        print("✅ Dev.to post successful!")
        return True
    else:
        print("❌ Dev.to post failed:", res.status_code, res.text)
        return False
