import requests
from typing import Optional
import os


def get_user_urn(token: str) -> Optional[str]:
    """Get the LinkedIn user URN using the access token."""
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get("sub")
    return None


def upload_linkedin_image(token: str, image_path: str) -> Optional[str]:
    """Upload an image to LinkedIn and return the asset URN."""
    # Register upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": None,  # To be filled in by caller
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    # The owner must be the user or organization URN
    # The caller must set register_body['registerUploadRequest']['owner']

    return None


def post_to_linkedin(token: str, urn: str, content: str, image_data: Optional[bytes] = None) -> bool:
    """Post to LinkedIn with optional image data (bytes)."""
    return _post_to_linkedin_internal(token, urn, content, image_data)


def _post_to_linkedin_internal(token: str, urn: str, content: str, image_data: Optional[bytes] = None) -> bool:
    """Post to LinkedIn with optional image data."""
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    if image_data:
        # 1. Register upload
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        register_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        reg_res = requests.post(register_url, headers=headers, json=register_body)
        if reg_res.status_code != 200:
            print("❌ Failed to register image upload:", reg_res.text)
            return False
        reg_data = reg_res.json()
        upload_url = reg_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = reg_data['value']['asset']
        # 2. Upload image
        upload_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}
        up_res = requests.put(upload_url, headers=upload_headers, data=image_data)
        if up_res.status_code not in (200, 201):
            print("❌ Failed to upload image:", up_res.text)
            return False
        # 3. Post with image
        data = {
            "author": urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": content[:200]},
                            "media": asset,
                            "title": {"text": "AI Generated Image"}
                        }
                    ]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
    else:
        data = {
            "author": urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 201:
        print("✅ Post successful!")
        print(res.headers)
        return True
    else:
        print("❌ Post failed:", res.status_code, res.text)
        return False
