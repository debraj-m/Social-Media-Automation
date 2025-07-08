import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from dotenv import load_dotenv
load_dotenv()
import sys
import webbrowser
import random
import re
import json
import pickle
from core.automation.linkedin import linkedin as linkedin_automation
from core.content_generation.generator import ContentGenerator
from core.auth.linkedin.oauth import LinkedInOAuthClient
from core.automation.twitter.twitter import TwitterBot
from core.automation.blogger.blogger import post_to_blogger
from core.automation.pinterest.pinterest import post_to_pinterest
import requests
from core.automation.disqus import disqus

def run_linkedin(generate_image=True):
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    
    # Auto-select scenario randomly
    scenarios = ["school", "college", "workplace", "garden", "cafe", "library", "park", "home", "gym", "beach"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="linkedin", scenario=scenario)
    print(f"Generated LinkedIn post (scenario: {scenario}):\n", post)
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8000/callback")
    SCOPE = os.environ.get("SCOPE")
    TOKEN_PATH = "env/linkedin_token.json"
    oauth_client = LinkedInOAuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        token_path=TOKEN_PATH
    )
    token = oauth_client.get_access_token()
    print("Posting to LinkedIn...", token)
    urn = 'urn:li:organization:107168982'  # You may want to make this dynamic
    image_data = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Generate image using Pollinations and get bytes directly
        image_data = img_gen.generate_image(post, preferred_method="pollinations")
        if not image_data:
            print("Image generation failed, posting text only.")
        else:
            print(f"Generated image using Pollinations (bytes length: {len(image_data)})")
    success = linkedin_automation.post_to_linkedin(token, urn, post, image_data=image_data)
    if success:
        print("Post successful!")
    return success

def run_twitter(generate_image=True):
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    
    # Auto-select scenario randomly
    scenarios = ["cafe", "workplace", "home", "park", "gym", "library"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="twitter", scenario=scenario)
    print(f"Generated Twitter post (scenario: {scenario}):\n", post)
    
    # Generate image if requested
    image_data = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Generate image using Pollinations and get bytes directly
        image_data = img_gen.generate_image(post, preferred_method="pollinations")
        if image_data:
            print(f"Generated image using Pollinations (bytes length: {len(image_data)})")
        else:
            print("Image generation failed, posting text only.")
    bot = TwitterBot()
    # Use appropriate method based on whether we have image data
    if image_data:
        success = bot.post_to_twitter_with_image(post, image_data=image_data)
    else:
        success = bot.post_to_twitter(post)
    if success:
        print("Post successful!")
    else:
        print("Post failed.")
    return success

def run_twitter_with_image_approval():
    """Run Twitter automation with image generation and user approval"""
    try:
        print("\n🐦 Starting Twitter automation with image generation...")
        bot = TwitterBot()
        
        # Ask user for scenario preference
        scenarios = {
            "1": "school",
            "2": "college",
            "3": "workplace",
            "4": "garden",
            "5": "cafe",
            "6": "library",
            "7": "park",
            "8": "home",
            "9": "gym",
            "10": "beach",
            "auto": "auto-detect"
        }
        
        print("\n📍 Choose a scenario for your story (or let AI auto-detect):")
        for key, scenario in scenarios.items():
            print(f"   {key}. {scenario.title()}")
        
        choice = input("\nEnter choice (1-10 or 'auto'): ").strip().lower()
        
        if choice in scenarios:
            scenario = scenarios[choice] if choice != "auto" else None
            print(f"Selected: {scenario or 'Auto-detect from content'}")
        else:
            scenario = None
            print("Using auto-detection")
        
        # Run the automation with approval
        success = bot.run_automation_with_approval(generate_image=True, scenario=scenario)
        
        if success:
            print("✅ Twitter automation completed successfully!")
        else:
            print("❌ Twitter automation failed or was cancelled")
            
    except Exception as e:
        print(f'❌ Error in Twitter automation with images: {e}')

def ask_scenario(platform_name):
    scenarios = {
        "1": "school",
        "2": "college",
        "3": "workplace",
        "4": "garden",
        "5": "cafe",
        "6": "library",
        "7": "park",
        "8": "home",
        "9": "gym",
        "10": "beach",
        "auto": "auto-detect"
    }
    print(f"\n📍 Choose a scenario for your {platform_name} story (or let AI auto-detect):")
    for key, scenario in scenarios.items():
        print(f"   {key}. {scenario.title()}")
    choice = input("\nEnter choice (1-10 or 'auto'): ").strip().lower()
    if choice in scenarios:
        scenario = scenarios[choice] if choice != "auto" else None
        print(f"Selected: {scenario or 'Auto-detect from content'}")
    else:
        scenario = None
        print("Using auto-detection")
    return scenario

def run_devto(generate_image=True):
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    devto_api_key = os.environ.get("DEVTO_API_KEY")
    from core.automation.devto.devto import post_to_devto
    generator = ContentGenerator(openai_api_key)
    
    # Auto-select scenario randomly
    scenarios = ["school", "college", "workplace", "garden", "cafe", "library", "park", "home", "gym", "beach"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="devto", scenario=scenario)
    print(f"Generated Dev.to post (scenario: {scenario}):\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Dev.to Post"
    words = re.findall(r"\b\w{5,}\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "python"]
    
    image_url = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Only use Pollinations for image generation; do not fall back
        image_data = img_gen.generate_image(post, preferred_method="pollinations")
        if image_data:
            print("Image generated successfully (bytes) [Pollinations]")
            image_url = upload_image_data_to_cloudinary(image_data)
            if image_url:
                print(f"Image uploaded: {image_url}")
            else:
                print("Image upload failed, posting without image.")
        else:
            print("Pollinations image generation failed, posting text only.")
    
    # Embed image at the top if available
    if image_url:
        post = f"![AI Generated Image]({image_url})\n\n" + post
    
    success = post_to_devto(devto_api_key, title, post, tags)
    if success:
        print("✅ Dev.to post successful!")
    else:
        print("❌ Dev.to post failed!")
    return success

def run_hashnode(generate_image=True):
    """Post only textual content to Hashnode. The generate_image argument is ignored."""
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    hashnode_api_key = os.environ.get("HASHNODE_API_KEY")
    publication_id = os.environ.get("HASHNODE_PUBLICATION_ID")
    print(f"Using HASHNODE_PUBLICATION_ID: {publication_id}")
    from core.automation.hashnode.hashnode import post_to_hashnode
    generator = ContentGenerator(openai_api_key)
    
    # Auto-select scenario randomly
    scenarios = ["school", "college", "workplace", "garden", "cafe", "library", "park", "home", "gym", "beach"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="hashnode", scenario=scenario)
    print(f"Generated Hashnode post (scenario: {scenario}):\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Hashnode Post"
    import re
    words = re.findall(r"\b\w{5,}\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "python"]
    
    # Post to Hashnode without image
    success = post_to_hashnode(hashnode_api_key, title, post, tags)
    if success:
        print("Post successful!")
    else:
        print("Post failed.")
    return success

def run_blogger(generate_image=True):
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    CLIENT_ID = os.environ.get("BLOGGER_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("BLOGGER_CLIENT_SECRET")
    REDIRECT_URI = os.environ.get("BLOGGER_REDIRECT_URI", "http://localhost:8000/")
    TOKEN_PATH = "env/blogger_token.pickle"
    from core.auth.blogger.oauth import BloggerOAuthClient
    from core.automation.blogger.blogger import post_to_blogger
    generator = ContentGenerator(openai_api_key)
    post = generator.generate_content(platform="blogger")
    print("Generated Blogger post:\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Blogger Post"
    import re
    words = re.findall(r"\b\w{5,}\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "python"]

    # Add paragraph breaks for better readability
    def add_paragraph_breaks(text):
        import re
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        # Group sentences into paragraphs of 2-3 sentences each
        paragraphs = []
        para = []
        for i, sentence in enumerate(sentences):
            para.append(sentence)
            if (i + 1) % 3 == 0:
                paragraphs.append(' '.join(para))
                para = []
        if para:
            paragraphs.append(' '.join(para))
        return '\n\n'.join(paragraphs)

    post = add_paragraph_breaks(post)

    image_data = None
    image_url = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Only use Pollinations for image generation
        image_data = img_gen.generate_image(post, preferred_method="pollinations")
        if image_data:
            print("Image generated successfully [Pollinations]")
            image_url = upload_image_data_to_cloudinary(image_data)
            if image_url:
                print(f"Image uploaded: {image_url}")
            else:
                print("Image upload failed, posting without image.")
        else:
            print("Pollinations image generation failed, posting text only.")

    # If we have an image URL, add it to the post content as HTML
    if image_url:
        post = f'<p><img src="{image_url}" alt="AI Generated Image" style="max-width:100%"></p>\n\n' + post

    oauth_client = BloggerOAuthClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        token_path=TOKEN_PATH
    )
    access_token = oauth_client.get_access_token()
    success = post_to_blogger(access_token, title, post, tags)
    if success:
        print("Post successful!")
        return True
    else:
        print("Post failed!")
        return False

def run_disqus(generate_image=True):
    """Run Disqus automation with the dedicated Disqus content generation"""
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    
    # Auto-select scenario randomly
    scenarios = ["school", "college", "workplace", "garden", "cafe", "library", "park", "home", "gym", "beach"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="disqus", scenario=scenario)
    print(f"Generated Disqus post (scenario: {scenario}):\n", post)
    title = post.split("\n")[0][:80] if post else "Automated Disqus Post"
    words = re.findall(r"\b\w{5,}\b", post.lower())
    tags = list(dict.fromkeys(words))[:3] if words else ["automation", "ai", "discussion"]

    # Load Disqus token
    try:
        with open("env/disqus_token.txt", "r") as f:
            access_token = f.read().strip()
    except Exception as e:
        print(f"Error reading Disqus token: {e}")
        return

    image_data = None
    image_url = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Only use Pollinations for image generation
        image_data = img_gen.generate_image(post, preferred_method="pollinations")
        if image_data:
            print("Image generated successfully [Pollinations]")
            image_url = upload_image_data_to_cloudinary(image_data)
            if image_url:
                print(f"Image uploaded: {image_url}")
            else:
                print("Image upload failed, posting without image.")
        else:
            print("Pollinations image generation failed, posting text only.")
    
    success = disqus.post_to_disqus(access_token, title, post, tags, image_url=image_url)
    if success:
        print("Post successful!")
    else:
        print("Post failed!")
    return success

def run_mastodon(generate_image=True):
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    access_token = os.environ.get("MASTODON_ACCESS_TOKEN")
    api_base_url = os.environ.get("MASTODON_API_BASE_URL", "https://mastodon.social")
    generator = ContentGenerator(openai_api_key)
    import requests
    
    # Auto-select scenario randomly
    scenarios = ["school", "college", "workplace", "garden", "cafe", "library", "park", "home", "gym", "beach"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="mastodon", scenario=scenario)
    print(f"Generated Mastodon post (scenario: {scenario}):\n", post)
    
    # Truncate post to 500 chars at word boundary
    max_length = 500
    if len(post) > max_length:
        truncated = post[:max_length].rsplit(' ', 1)[0]
        post = truncated + '...'
        print(f"Post truncated to {max_length} characters for Mastodon.")
    
    image_data = None
    media_id = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Generate image using Pollinations and get bytes directly
        image_data = img_gen.generate_image(post, preferred_method="pollinations")
        if image_data:
            print("Image generated successfully [Pollinations]")
            # Upload image buffer directly to Mastodon
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                files = {"file": ("image.jpg", image_data, "image/jpeg")}
                media_url = f"{api_base_url}/api/v2/media"
                resp = requests.post(media_url, headers=headers, files=files)
                if resp.status_code == 200:
                    media_id = resp.json().get("id")
                    print(f"Mastodon image uploaded, media_id: {media_id}")
                else:
                    print(f"Mastodon image upload failed: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"Error uploading image to Mastodon: {e}")
        else:
            print("Image generation failed, posting text only.")
    
    # Post status with or without media_id
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        status_url = f"{api_base_url}/api/v1/statuses"
        data = {"status": post}
        if media_id:
            data["media_ids[]"] = media_id
        resp = requests.post(status_url, headers=headers, data=data)
        if resp.status_code == 200:
            print(f"✅ Mastodon post successful! {resp.json().get('url')}")
            return True
        else:
            print(f"❌ Mastodon post failed: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error posting to Mastodon: {e}")
        return False

def run_pinterest(generate_image=True):
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    
    # Auto-select scenario randomly
    scenarios = ["lifestyle", "food", "travel", "home", "fashion", "craft"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="pinterest", scenario=scenario)
    print(f"Generated Pinterest post (scenario: {scenario}):\n", post)
    
    image_data = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Generate image and get bytes or file path
        print(f"[DEBUG] Calling generate_human_image_for_story with post length: {len(post)}, scenario: {scenario}")
        result = img_gen.generate_human_image_for_story(post, scenario)
        print(f"[DEBUG] generate_human_image_for_story returned: {result} (type: {type(result)})")
        if isinstance(result, bytes):
            image_data = result  # Send buffer directly
        elif isinstance(result, str) and os.path.isfile(result):
            try:
                with open(result, "rb") as f:
                    image_data = f.read()
                print(f"[DEBUG] Read image data from file: {result} (bytes: {len(image_data)})")
            except Exception as e:
                print(f"[ERROR] Failed to read image file for Pinterest: {e}")
                return False
        else:
            print(f"Image generation failed or file not found: {result}. Pinterest requires an image, skipping post.")
            return False
    else:
        print("Pinterest requires an image. Please enable image generation.")
        return False
    # Use the first line as title, rest as content
    title = post.split("\n")[0][:100] if post else "Automated Pinterest Post"
    content = post
    success = post_to_pinterest(title, content, image_data=image_data)
    if success:
        print("Post successful!")
        return True
    else:
        print("Post failed!")
        return False


def run_pixelfed(generate_image=True):
    """Run Pixelfed automation with the dedicated Pixelfed content generation"""
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    
    # Auto-select scenario randomly
    scenarios = ["art", "photography", "nature", "urban", "abstract", "portrait"]
    scenario = random.choice(scenarios)
    
    post = generator.generate_story_based_content(platform="pixelfed", scenario=scenario)
    print(f"Generated Pixelfed post (scenario: {scenario}):\n", post)
    
    # Load Pixelfed token
    try:
        with open("env/pixelfed_token.json", "r") as f:
            pixelfed_token = json.load(f)
    except Exception as e:
        print(f"Error reading Pixelfed token: {e}")
        return False
    
    image_data = None
    if generate_image:
        from core.image_generation.generator import ImageGenerator
        img_gen = ImageGenerator()
        # Generate image and get bytes directly
        image_data = img_gen.generate_human_image_for_story(post, "artistic")
        if not image_data:
            print("Image generation failed. Pixelfed requires an image, skipping post.")
            return False
        else:
            print(f"Generated image buffer (bytes length: {len(image_data)})")
    else:
        print("Pixelfed requires an image. Please enable image generation.")
        return False

    from core.automation.pixelfed.pixelfed import post_to_pixelfed
    success = post_to_pixelfed(pixelfed_token, post, image_data=image_data)
    if success:
        print("Post successful!")
        return True
    else:
        print("Post failed.")
        return False

def run_reddit(generate_image=True, subreddits=None):
    """Post to multiple subreddits, handling subreddit-specific rules and flair errors."""
    import requests
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    generator = ContentGenerator(openai_api_key)
    scenarios = [
        "work stress", "finding motivation", "dealing with deadlines", "balancing work and life", "making new friends online", "coping with change", "learning new skills", "funny work stories", "random acts of kindness", "unexpected advice"
    ]
    scenario = random.choice(scenarios)
    names = ["Alex", "Jamie", "Taylor", "Jordan", "Morgan", "Casey", "Riley", "Sam", "Drew", "Cameron"]
    name = random.choice(names)
    openers = [
        f"Has anyone else ever felt completely overwhelmed at work? Today, {name} was just trying to get through the day when...",
        f"What do you all do when you hit a wall with motivation? {name} found themselves staring at the screen, totally stuck.",
        f"Do you ever feel like your to-do list just keeps growing? {name} sure did today!",
        f"How do you all handle days when everything seems to go wrong? {name} had one of those days recently.",
        f"Is it just me, or does everyone have those moments where you question your career choices? {name} had a big one today."
    ]
    opener = random.choice(openers)
    body = (
        f"{opener}\n\nIt got me thinking: how do other people deal with these kinds of days? Do you have any little routines, habits, or tricks that help you reset? I feel like everyone has their own way of coping, but it's not something we talk about much.\n\nWould love to hear your thoughts or stories!"
    )
    title_options = [
        "How do you handle tough days at work?",
        "What's your go-to way to reset after a stressful day?",
        "Anyone else struggle with motivation sometimes?",
        "How do you keep going when you're overwhelmed?",
        "What's your best tip for dealing with stress?"
    ]
    title = random.choice(title_options)
    try:
        with open("env/reddit_token.json", "r") as f:
            reddit_token = json.load(f)
    except Exception as e:
        print(f"Error reading Reddit token: {e}")
        return False
    from core.automation.reddit.reddit import post_to_reddit
    if not subreddits:
        subreddits = ["technology", "Entrepreneur", "startups", "InternetIsBeautiful"]
    results = {}
    for subreddit in subreddits:
        flair_id = None
        flair_text = None
        allow_flair = True
        # Check subreddit rules (text posts allowed?)
        try:
            headers = {"Authorization": f"bearer {reddit_token['access_token']}", "User-Agent": "ai-marketing-suite/0.1"}
            about_url = f"https://oauth.reddit.com/r/{subreddit}/about.json"
            about_resp = requests.get(about_url, headers=headers)
            if about_resp.status_code == 200:
                data = about_resp.json()
                if not data.get("data", {}).get("submission_type", "any") in ["any", "self"]:
                    print(f"Skipping r/{subreddit}: does not allow text posts.")
                    results[subreddit] = False
                    continue
        except Exception as e:
            print(f"Warning: Could not check rules for r/{subreddit}: {e}")
        post_title = title
        if subreddit.lower() == "startups":
            if "i will not promote" not in post_title.lower():
                post_title = f"[I will not promote] {post_title}"
        # Try to fetch flairs and pick a relevant one, but only set if allowed
        try:
            headers = {"Authorization": f"bearer {reddit_token['access_token']}", "User-Agent": "ai-marketing-suite/0.1"}
            url = f"https://oauth.reddit.com/r/{subreddit}/api/link_flair_v2"
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                flairs = resp.json()
                found = False
                # Prioritize special flairs for r/Entrepreneur
                if subreddit.lower() == "entrepreneur":
                    keywords = ["sidehustle", "side hustler", "entrepreneur"]
                    for flair in flairs:
                        flair_text_candidate = flair.get("text", "").lower()
                        if any(kw in flair_text_candidate for kw in keywords):
                            flair_id = flair.get("id")
                            flair_text = flair.get("text")
                            found = True
                            break
                # Fallback: match scenario/title
                if not found:
                    for flair in flairs:
                        flair_text_candidate = flair.get("text", "").lower()
                        if flair_text_candidate and (flair_text_candidate in scenario.lower() or flair_text_candidate in post_title.lower()):
                            flair_id = flair.get("id")
                            flair_text = flair.get("text")
                            found = True
                            break
                if not found and flairs:
                    flair_id = flairs[0].get("id")
                    flair_text = flairs[0].get("text")
            elif resp.status_code == 403:
                print(f"Could not fetch flairs for r/{subreddit}: 403 (not allowed)")
                allow_flair = False
            else:
                print(f"Could not fetch flairs for r/{subreddit}: {resp.status_code}")
                allow_flair = False
        except Exception as e:
            print(f"Error fetching flairs for r/{subreddit}: {e}")
            allow_flair = False
        # Post to subreddit, retry without flair if flair fails
        try:
            success = False
            flair_attempted = False
            if allow_flair and flair_id:
                try:
                    success = post_to_reddit(
                        reddit_token,
                        title=post_title,
                        selftext=body,
                        subreddit=subreddit,
                        image_data=None,
                        flair_id=flair_id,
                        flair_text=flair_text
                    )
                    flair_attempted = True
                except Exception as e:
                    print(f"Error posting with flair to r/{subreddit}: {e}. Retrying without flair...")
            if not success:
                try:
                    success = post_to_reddit(
                        reddit_token,
                        title=post_title,
                        selftext=body,
                        subreddit=subreddit,
                        image_data=None
                    )
                except Exception as e:
                    print(f"Error posting to r/{subreddit} without flair: {e}")
            if success:
                print(f"Post successful in r/{subreddit}! (flair: {flair_text if allow_flair and flair_id and flair_attempted else 'None'})")
                results[subreddit] = True
            else:
                print(f"Post failed in r/{subreddit}!")
                results[subreddit] = False
        except Exception as e:
            print(f"Error posting to r/{subreddit}: {e}")
            results[subreddit] = False
    return results

def upload_image_to_imgur(image_path: str) -> str:
    """Upload an image to Imgur anonymously and return the public URL."""
    IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID")
    if not IMGUR_CLIENT_ID:
        print("IMGUR_CLIENT_ID not set in environment. Cannot upload image.")
        return None
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    with open(image_path, "rb") as img_file:
        files = {"image": img_file}
        response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        print(f"Imgur upload failed: {response.status_code} {response.text}")
        return None

def upload_image_to_cloudinary(image_path: str) -> str:
    """Upload an image to Cloudinary and return the public URL."""
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")
    print(f"Cloudinary cloud name: {CLOUDINARY_CLOUD_NAME}")
    print(f"Cloudinary API key: {CLOUDINARY_API_KEY}")
    print(f"Cloudinary API secret (first 4 chars): {CLOUDINARY_API_SECRET[:4] if CLOUDINARY_API_SECRET else None}")
    if not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
        print("Cloudinary credentials not set in environment. Cannot upload image.")
        return None
    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload"
    import hashlib
    import time
    timestamp = int(time.time())
    # Cloudinary requires a signature: sha1('timestamp=TIMESTAMP' + API_SECRET)
    params_to_sign = f"timestamp={timestamp}"
    string_to_sign = f"{params_to_sign}{CLOUDINARY_API_SECRET}"
    signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()
    print(f"Cloudinary string to sign: '{params_to_sign + CLOUDINARY_API_SECRET}'")
    print(f"Cloudinary signature: {signature}")
    data = {
        'api_key': CLOUDINARY_API_KEY,
        'timestamp': timestamp,
        'signature': signature
    }
    with open(image_path, "rb") as img_file:
        files = {"file": img_file}
        response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        return response.json()["secure_url"]
    else:
        print(f"Cloudinary upload failed: {response.status_code} {response.text}")
        return None

def upload_image_data_to_cloudinary(image_data: bytes) -> str:
    """Upload image data (bytes) to Cloudinary and return the public URL."""
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")
    print(f"Cloudinary cloud name: {CLOUDINARY_CLOUD_NAME}")
    print(f"Cloudinary API key: {CLOUDINARY_API_KEY}")
    print(f"Cloudinary API secret (first 4 chars): {CLOUDINARY_API_SECRET[:4] if CLOUDINARY_API_SECRET else None}")
    if not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
        print("Cloudinary credentials not set in environment. Cannot upload image.")
        return None
    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload"
    import hashlib
    import time
    timestamp = int(time.time())
    # Cloudinary requires a signature: sha1('timestamp=TIMESTAMP' + API_SECRET)
    params_to_sign = f"timestamp={timestamp}"
    string_to_sign = f"{params_to_sign}{CLOUDINARY_API_SECRET}"
    signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()
    print(f"Cloudinary string to sign: '{params_to_sign + CLOUDINARY_API_SECRET}'")
    print(f"Cloudinary signature: {signature}")
    data = {
        'api_key': CLOUDINARY_API_KEY,
        'timestamp': timestamp,
        'signature': signature
    }
    # Send the image buffer directly as the file
    files = {"file": ("image.jpg", image_data, "image/jpeg")}
    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        return response.json()["secure_url"]
    else:
        print(f"Cloudinary upload failed: {response.status_code} {response.text}")
        return None

def main():
    """Run all platforms in sequence and print a summary of successes."""
    platforms = [
        ("LinkedIn", run_linkedin),
        ("Twitter", run_twitter),
        ("Dev.to", run_devto),
        ("Hashnode", run_hashnode),
        ("Blogger", run_blogger),
        ("Disqus", run_disqus),
        ("Mastodon", run_mastodon),
        ("Pinterest", run_pinterest),
        ("Pixelfed", run_pixelfed),
        ("Reddit", run_reddit),
    ]
    successes = 0
    total = len(platforms)
    print("\n Running all platforms in sequence...\n")
    for name, func in platforms:
        try:
            print(f"--- {name} ---")
            result = func()
            if result is True:
                print(f"✅ {name} succeeded\n")
                successes += 1
            else:
                print(f"❌ {name} failed\n")
        except Exception as e:
            print(f"❌ Error in {name} -> {e}\n")
    print(f"\n📊 Summary: {successes} succeeded, {total - successes} failed out of {total} platforms\n")

if __name__ == "__main__":
    main()
