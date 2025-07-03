import os
import requests

def post_to_disqus(access_token, title, content, tags):
    """
    Post a thread to Disqus using the API.
    Args:
        access_token (str): OAuth 2.0 access token
        title (str): Title of the thread
        content (str): Content of the thread
        tags (list): List of tag strings (not directly supported by Disqus, can be added to message)
    Returns:
        bool: True if successful, False otherwise
    """
    forum = os.environ.get("DISQUS_FORUM")  # Your Disqus forum shortname
    if not forum:
        print("DISQUS_FORUM not set in environment.")
        return False
    api_key = os.environ.get("DISQUS_CLIENT_ID")
    if not api_key:
        print("DISQUS_CLIENT_ID not set in environment.")
        return False
    url = "https://disqus.com/api/3.0/threads/create.json"
    payload = {
        "access_token": access_token,
        "api_key": api_key,
        "forum": forum,
        "title": title,
        "message": content,
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            thread_data = response.json()
            print("Disqus thread created!", thread_data)
            # Print the thread link if available
            thread_link = thread_data.get('response', {}).get('link')
            if thread_link:
                print(f"Thread link: {thread_link}")
            # Post the content as a comment to the thread
            thread_id = thread_data.get('response', {}).get('id')
            if thread_id:
                post_url = "https://disqus.com/api/3.0/posts/create.json"
                post_payload = {
                    "access_token": access_token,
                    "api_key": api_key,
                    "thread": thread_id,
                    "message": content,
                }
                post_response = requests.post(post_url, data=post_payload)
                if post_response.status_code == 200:
                    print("Disqus comment posted!", post_response.json())
                    return True
                else:
                    print("Disqus comment error:", post_response.text)
                    return False
            return True
        else:
            print("Disqus API error:", response.text)
            return False
    except Exception as e:
        print(f"Exception posting to Disqus: {e}")
        return False
