import requests
from typing import Optional

def post_to_ghost(api_url: str, admin_api_key: str, title: str, html: str, tags: list = None) -> bool:
    """Post an article to Ghost via Admin API (Content API is read-only)."""
    url = f"{api_url}/ghost/api/v3/admin/posts/"
    headers = {
        "Authorization": f"Ghost {admin_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "posts": [{
            "title": title,
            "html": html,
            "status": "published"
        }]
    }
    if tags:
        data["posts"][0]["tags"] = tags
    res = requests.post(url, headers=headers, json=data)
    if res.status_code in (200, 201):
        print("✅ Ghost post successful!")
        print(res.headers)
        return True
    else:
        print("❌ Ghost post failed:", res.status_code, res.text)
        return False
