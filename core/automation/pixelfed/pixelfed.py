import os
import logging
import requests
from core.auth.pixelfed.oauth import PixelfedOAuthClient

class PixelfedAutomation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = os.getenv('PIXELFED_BASE_URL', 'https://pixelfed.social')
        
        # Initialize OAuth client
        self.oauth_client = PixelfedOAuthClient(
            client_id=os.getenv('PIXELFED_CLIENT_ID'),
            client_secret=os.getenv('PIXELFED_CLIENT_SECRET'),
            redirect_uri=os.getenv('PIXELFED_REDIRECT_URI', 'http://localhost:8000/'),
            base_url=self.base_url
        )

    def _make_request(self, method, endpoint, data=None, files=None, **kwargs):
        """Make an authenticated request to Pixelfed API"""
        token = self.oauth_client.get_valid_token()
        if not token:
            raise ValueError("No valid token available. Please run the OAuth flow first.")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "ai-marketing-suite/1.0"
        }
        
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, data=data, files=files, **kwargs)
        
        if response.status_code == 401:  # Token might be invalid
            token = self.oauth_client.get_valid_token()  # This will refresh if needed
            if token:
                headers["Authorization"] = f"Bearer {token}"
                response = requests.request(method, url, headers=headers, data=data, files=files, **kwargs)
                
        response.raise_for_status()
        return response.json() if response.text else None

    def post_image(self, image_data: bytes = None, caption=None, alt_text=None):
        """Post an image to Pixelfed"""
        try:
            import io
            if image_data:
                # Debug: Check first few bytes of image_data
                print(f"[DEBUG] image_data[:10]: {image_data[:10]}")
                files = {'file': ('image.png', io.BytesIO(image_data), 'image/png')}
                media_response = self._make_request('POST', '/media', files=files)
            else:
                print("[DEBUG] No image_data provided to post_image.")
                media_response = None
            if not media_response or 'id' not in media_response:
                raise ValueError("Failed to upload media")
            media_id = media_response['id']
            self.logger.info(f"Media uploaded successfully with ID: {media_id}")
            post_data = {
                'media_ids[]': [media_id],
                'status': caption or '',
                'visibility': 'public'
            }
            if alt_text:
                post_data['media_descriptions[]'] = [alt_text]
            response = self._make_request('POST', '/statuses', data=post_data)
            if response and 'id' in response:
                self.logger.info(f"Post created successfully with ID: {response['id']}")
                return response
            else:
                raise ValueError("Failed to create post")
        except Exception as e:
            print(f"[DEBUG] Exception in post_image: {e}")
            self.logger.error(f"Error posting to Pixelfed: {str(e)}")
            raise

    def get_profile(self):
        """Get the authenticated user's profile"""
        return self._make_request('GET', '/accounts/verify_credentials')

def post_to_pixelfed(pixelfed_token, post, image_data=None, image_path=None):
    """Wrapper function to post to Pixelfed using PixelfedAutomation class."""
    import io
    automation = PixelfedAutomation()
    # If image_data is not provided, read from image_path
    if image_data is None and image_path:
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
    if image_data is None:
        print("No image data provided for Pixelfed post.")
        return False
    try:
        response = automation.post_image(image_data=image_data, caption=post)
        return True if response else False
    except Exception as e:
        logging.error(f"Pixelfed post failed: {e}")
        return False
