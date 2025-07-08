import os
import requests
from typing import Optional

def post_to_hashnode(api_key: str, title: str, content: str, tags: list, cover_image_url: Optional[str] = None) -> bool:
    """
    Create and publish an article on Hashnode using the v2 API (GraphQL).

    Args:
        api_key (str): Hashnode API key
        title (str): Title of the post
        content (str): Markdown or HTML content
        tags (list): List of tag strings
        cover_image_url (str, optional): URL of the cover image (ignored)

    Returns:
        bool: True if successful, False otherwise
    """
    publication_id = os.environ.get("HASHNODE_PUBLICATION_ID")
    if not publication_id:
        print("HASHNODE_PUBLICATION_ID not set in environment.")
        return False
    url = "https://gql.hashnode.com/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    # Step 1: Create draft (no cover image)
    create_draft_query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) {
        draft {
          id
          title
          slug
        }
      }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": content,
            "publicationId": publication_id,
        }
    }
    payload = {"query": create_draft_query, "variables": variables}
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if response.status_code == 200 and 'errors' not in data:
            draft_id = data['data']['createDraft']['draft']['id']
            # Step 2: Publish draft
            publish_query = """
            mutation PublishDraft($input: PublishDraftInput!) {
              publishDraft(input: $input) {
                post {
                  id
                  title
                  slug
                  url
                }
              }
            }
            """
            publish_input = {"draftId": draft_id}
            publish_variables = {"input": publish_input}
            publish_payload = {"query": publish_query, "variables": publish_variables}
            publish_response = requests.post(url, json=publish_payload, headers=headers)
            publish_data = publish_response.json()
            if publish_response.status_code == 200 and 'errors' not in publish_data:
                post_id = publish_data['data']['publishDraft']['post']['id']
                post_url = publish_data['data']['publishDraft']['post']['url']
                print("Post published successfully!", post_url)
                return True
            else:
                print("Hashnode publish error:", publish_response.text)
                return False
        else:
            print("Hashnode API error:", response.text)
            return False
    except Exception as e:
        print(f"Exception posting to Hashnode: {e}")
        return False
