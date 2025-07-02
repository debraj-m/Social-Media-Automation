import requests
from typing import Optional

def post_to_mastodon(token: str, instance_url: str, status: str) -> bool:
    """Post a status to Mastodon."""
    url = f"{instance_url}/api/v1/statuses"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "status": status
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        print("✅ Mastodon post successful!")
        print(res.headers)
        return True
    else:
        print("❌ Mastodon post failed:", res.status_code, res.text)
        return False
