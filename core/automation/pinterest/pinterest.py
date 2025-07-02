import requests
from typing import Optional

def post_to_pinterest(token: str, board_id: str, title: str, description: str, link: str, image_url: str) -> bool:
    """Post a Pin to Pinterest using the v5 API."""
    url = "https://api.pinterest.com/v5/pins"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 201:
        print("✅ Pin posted successfully!")
        print(res.headers)
        return True
    else:
        print("❌ Pin post failed:", res.status_code, res.text)
        return False
