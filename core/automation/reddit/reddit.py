import os
import praw
import requests
from core.auth.reddit.oauth import RedditOAuthClient
import logging
import time

class RedditAutomation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize OAuth client
        self.oauth_client = RedditOAuthClient(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            redirect_uri=os.getenv('REDDIT_REDIRECT_URI', 'http://localhost:8000/')
        )
        
        # Get token data
        token_data = self.oauth_client.get_valid_token()
        if not token_data:
            raise ValueError("No Reddit access token available. Please run the OAuth flow first.")
            
        # Initialize PRAW with OAuth credentials
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            refresh_token=token_data.get('refresh_token'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'ai-marketing-suite/1.0')
        )
        self.logger.info("Reddit automation initialized")

    def get_available_flairs(self, subreddit):
        """Get available post flairs for a subreddit"""
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            # Try to get flairs through the submission API
            choices = list(subreddit_obj.flair.link_templates)
            if choices:
                return [{"id": f["id"], "text": f["text"]} for f in choices if f.get("id")]
                
            # Fallback: try to get available flairs from subreddit rules
            about = subreddit_obj.mod.settings()
            if "post_flair_required" in about and about["post_flair_required"]:
                # Get flairs through submission requirements
                requirements = subreddit_obj._submit_requirements()
                if "flairIds" in requirements:
                    flairs = []
                    for fid in requirements["flairIds"]:
                        try:
                            flair = subreddit_obj.flair.link_templates.get_template_by_id(fid)
                            flairs.append({"id": flair["id"], "text": flair["text"]})
                        except:
                            continue
                    return flairs
            return []
        except Exception as e:
            self.logger.warning(f"Could not fetch flairs for r/{subreddit}: {str(e)}")
            # Since we couldn't get flairs but know they're required, provide some common ones
            return [
                {"id": "OC", "text": "OC"},
                {"id": "Non-OC", "text": "Non-OC"},
                {"id": "Image", "text": "Image"},
                {"id": "Discussion", "text": "Discussion"}
            ]
            
    def get_subreddit_flairs(self, subreddit_name):
        """Get available post flairs for a subreddit using direct API call"""
        try:
            headers = {
                'Authorization': f'Bearer {self.oauth_client.get_access_token()}',
                'User-Agent': os.getenv('REDDIT_USER_AGENT', 'ai-marketing-suite/1.0')
            }
            response = requests.get(
                f'https://oauth.reddit.com/r/{subreddit_name}/api/link_flair_v2',
                headers=headers
            )
            response.raise_for_status()
            flairs = response.json()
            self.logger.info(f"Retrieved {len(flairs)} flairs from API")
            return flairs
        except Exception as e:
            self.logger.error(f"Error fetching flairs via API: {str(e)}")
            return []

    def post(self, subreddit, title, body=None, image_data: bytes = None, flair_text=None, flair_id=None):
        """Post to Reddit with optional image and flair"""
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            
            # Get flairs using direct API call
            flairs = self.get_subreddit_flairs(subreddit)
            
            if not flairs:
                self.logger.warning("No flairs found via API, using default list")
                # Default mapping for IndiaSocial (text to ID)
                flairs = [
                    {"text": "Story-Time", "type": "richtext", "id": "7d215400-97a4-11eb-89a5-0e3bfc27f650"},
                    {"text": "Photography", "type": "richtext", "id": "7d215401-97a4-11eb-89a5-0e3bfc27f651"},
                    {"text": "Art", "type": "richtext", "id": "7d215402-97a4-11eb-89a5-0e3bfc27f652"},
                    {"text": "Discussion", "type": "richtext", "id": "7d215403-97a4-11eb-89a5-0e3bfc27f653"}
                ]
            
            if flair_text and not flair_id:
                # Automatically select flair ID based on provided flair text
                flair_id = next((flair["id"] for flair in flairs if flair["text"] == flair_text), None)
                if not flair_id:
                    self.logger.warning(f"Flair text '{flair_text}' not found in available flairs")
            
            if not flair_id:
                # Automatically select the first available flair if none provided
                if flairs:
                    flair_data = flairs[0]
                    flair_id = flair_data["id"]
                    flair_text = flair_data["text"]
                    self.logger.info(f"Auto-selected flair: {flair_data}")
                else:
                    flair_id = None
                    flair_text = None
            
            # Submit post with selected flair
            if image_data:
                self.logger.info(f"Submitting image post to r/{subreddit}")
                # Create a temporary file from the image data
                import io
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                try:
                    temp_file.write(image_data)
                    temp_file.close()
                    submission_args = {
                        "title": title,
                        "image_path": temp_file.name,
                        "flair_id": flair_id,
                    }
                    self.logger.info(f"Submission args: {submission_args}")
                    post = subreddit_obj.submit_image(**submission_args)
                    self.logger.info(f"Post successful! ID: {post.id}")
                    return post
                finally:
                    # Clean up the temporary file
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
            else:
                self.logger.info(f"Submitting text post to r/{subreddit}")
                submission_args = {
                    "title": title,
                    "selftext": body or '',
                    "flair_id": flair_id,
                }
                self.logger.info(f"Submission args: {submission_args}")
                post = subreddit_obj.submit(**submission_args)
                self.logger.info(f"Post successful! ID: {post.id}")
                return post
                
        except Exception as e:
            self.logger.error(f"Error posting to Reddit: {str(e)}")
            raise

def post_to_reddit(reddit_token, title, selftext, subreddit, image_path=None, image_data=None, flair_text=None, flair_id=None):
    """
    Post to Reddit using the RedditAutomation class.
    - If image_data (bytes) is provided, it will be used for the image post.
    - If image_path is provided (legacy), it will read the file as bytes.
    - If neither, will post as text.
    - flair_text or flair_id can be provided to select a flair automatically.
    """
    automation = RedditAutomation()
    img_bytes = None
    if image_data:
        img_bytes = image_data
    elif image_path:
        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
        except Exception as e:
            automation.logger.warning(f"Could not read image file: {e}")
            img_bytes = None
    try:
        post = automation.post(
            subreddit=subreddit,
            title=title,
            body=selftext,
            image_data=img_bytes,
            flair_text=flair_text,
            flair_id=flair_id
        )
        return True if post else False
    except Exception as e:
        automation.logger.error(f"Failed to post to Reddit: {e}")
        return False
