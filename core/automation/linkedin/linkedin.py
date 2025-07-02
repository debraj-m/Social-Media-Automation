import requests
from typing import Optional


def get_user_urn(token: str) -> Optional[str]:
    """Get the LinkedIn user URN using the access token."""
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get("sub")
    return None


def post_to_linkedin(token: str, urn: str, content: str) -> bool:
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    data = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 201:
        print("✅ Post successful!")
        print(res.headers)
        
    else:
        print("❌ Post failed:", res.status_code, res.text)
