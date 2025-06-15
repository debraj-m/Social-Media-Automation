import json
import requests

def load_token():
    try:
        with open("config.json") as f:
            config = json.load(f)
            return config["linkedin_access_token"]
    except:
        return None

def authenticate():
    print("🔐 Please implement OAuth if token not found.")

def get_user_urn(token):
    url = "https://api.linkedin.com/v2/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_id = response.json()["id"]
        return f"urn:li:person:{user_id}"
    else:
        print("❌ Failed to get URN:", response.text)
        return None

def post_to_linkedin(token, urn, content):
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
    else:
        print("❌ Post failed:", res.status_code, res.text)
