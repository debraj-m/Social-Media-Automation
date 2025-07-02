import requests
from typing import Optional

def post_to_medium(token: str, user_id: str, title: str, content: str, tags: list = None) -> bool:
    """Post a story to Medium."""
    url = f"https://api.medium.com/v1/users/{user_id}/posts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "title": title,
        "contentFormat": "markdown",
        "content": content,
        "publishStatus": "public"
    }
    if tags:
        data["tags"] = tags
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 201:
        print("✅ Medium post successful!")
        return True
    else:
        print("❌ Medium post failed:", res.status_code, res.text)
        return False
