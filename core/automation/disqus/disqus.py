import os
import json
import requests

def post_to_disqus(access_token, title, content, tags, image_url=None):
    """
    Post to Disqus using the API.
    Args:
        access_token (str): OAuth 2.0 access token
        title (str): Title of the post
        content (str): Content of the post
        tags (list): List of tag strings
        image_url (str, optional): URL of an image to embed in the content
    Returns:
        bool: True if successful, False otherwise
    """
    api_key = os.environ.get("DISQUS_API_KEY")
    if not api_key:
        print("DISQUS_API_KEY not set in environment.")
        return False
        
    forum = os.environ.get("DISQUS_FORUM")
    if not forum:
        print("DISQUS_FORUM not set in environment.")
        return False

    # If an image URL is provided, embed it in the content using HTML
    if image_url:
        content = f'<p><img src="{image_url}" alt="Generated Image"></p>\n{content}'

    try:
        # First create a thread
        thread_url = "https://disqus.com/api/3.0/threads/create.json"
        thread_data = {
            "api_key": api_key,
            "access_token": access_token,
            "forum": forum,
            "title": title,
            "message": content
        }
        
        print("\nCreating thread...")
        print(f"Thread data: {json.dumps(thread_data, indent=2)}")
        
        thread_response = requests.post(thread_url, data=thread_data)
        print(f"Response status: {thread_response.status_code}")
        print(f"Response body: {thread_response.text}")
        
        if thread_response.status_code != 200:
            print(f"Error creating thread: HTTP {thread_response.status_code}")
            try:
                error_data = thread_response.json()
                error_msg = error_data.get('response', 'Unknown error')
                print(f"Error details: {error_msg}")
            except json.JSONDecodeError:
                print(f"Raw error response: {thread_response.text}")
            return False
            
        try:
            thread_result = thread_response.json()
            
            if thread_result.get('code') != 0:
                error = thread_result.get('response', 'Unknown error')
                print(f"API error: {error}")
                return False
                
            thread_id = thread_result['response']['id']
            thread_url = thread_result['response'].get('link', '')
            
            if thread_url:
                print(f"\nThread created: {thread_url}")
                
            # Now create a post in the thread
            post_url = "https://disqus.com/api/3.0/posts/create.json"
            post_data = {
                "api_key": api_key,
                "access_token": access_token,
                "thread": thread_id,
                "message": content
            }
            
            print("\nCreating post...")
            print(f"Post data: {json.dumps(post_data, indent=2)}")
            
            post_response = requests.post(post_url, data=post_data)
            print(f"Response status: {post_response.status_code}")
            print(f"Response body: {post_response.text}")
            
            if post_response.status_code != 200:
                print(f"Error creating post: HTTP {post_response.status_code}")
                try:
                    error_data = post_response.json()
                    error_msg = error_data.get('response', 'Unknown error')
                    print(f"Error details: {error_msg}")
                except json.JSONDecodeError:
                    print(f"Raw error response: {post_response.text}")
                return False
                
            post_result = post_response.json()
            if post_result.get('code') != 0:
                error = post_result.get('response', 'Unknown error')
                print(f"API error: {error}")
                return False
                
            post_url = post_result['response'].get('url', '')
            if post_url:
                print(f"\nPost created: {post_url}")
                
            print("\nSuccessfully posted to Disqus!")
            return True
            
        except json.JSONDecodeError:
            print(f"Invalid JSON response: {thread_response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False
