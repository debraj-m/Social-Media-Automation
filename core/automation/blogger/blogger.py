import os
import requests
from core.auth.blogger.oauth import BloggerOAuthClient

def post_to_blogger(access_token, title, content, tags, photo_url=None):
    """
    Post an article to Blogger using OAuth 2.0 access token.
    Args:
        access_token (str): OAuth 2.0 access token
        title (str): Title of the post
        content (str): HTML or plain text content
        tags (list): List of tag strings
        photo_url (str, optional): URL of the image to include at the top
    Returns:
        bool: True if successful, False otherwise
    """
    blog_id = os.environ.get("BLOGGER_BLOG_ID")
    if not blog_id:
        print("BLOGGER_BLOG_ID not set in environment.")
        return False
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    # Insert image at the top if photo_url is provided
    if photo_url:
        image_html = f'<img src="{photo_url}" alt="Post image" style="max-width:100%;height:auto;"><br>'
        content = image_html + content
    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": tags
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in (200, 201):
            print("Blogger post published!", response.json().get("url"))
            return True
        else:
            print("Blogger API error:", response.text)
            return False
    except Exception as e:
        print(f"Exception posting to Blogger: {e}")
        return False
