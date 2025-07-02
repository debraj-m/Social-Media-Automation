import requests
from typing import Optional

def post_to_hashnode(api_key: str, publication_id: str, title: str, content_markdown: str, tags: list = None) -> bool:
    """Post an article to Hashnode using the v2 GraphQL API."""
    url = "https://api.hashnode.com/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    mutation = """
    mutation CreateStory($input: CreateStoryInput!) {
      createStory(input: $input) {
        code
        success
        message
        post {
          _id
          title
        }
      }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": content_markdown,
            "publicationId": publication_id,
            "tags": tags or []
        }
    }
    data = {"query": mutation, "variables": variables}
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200 and 'errors' not in res.json():
        print("✅ Hashnode post successful!")
        print(res.headers)
        return True
    else:
        print("❌ Hashnode post failed:", res.status_code, res.text)
        return False
