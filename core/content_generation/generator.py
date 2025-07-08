from typing import Optional, Dict, List
import re
import logging
import random
from openai import OpenAI
import os

class ContentGenerator:
    def __init__(self, openai_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)

        self.products = [
            {
                "name": "Helpothon",
                "link": "https://helpothon.com/",
                "description": "A platform dedicated to helping everyone, businesses, and communities by leveraging technology for good",
                "key_features": ["Technology for social good", "Community building", "Global impact"],
                "target_audience": "Businesses and communities seeking positive technological impact",
                "story_angle": "Mission-driven technology company spreading smiles worldwide"
            },
            {
                "name": "ScanMeee",
                "link": "https://scanmeee.com/",
                "description": "A fun QR code generator that creates and shares entertaining QR codes with various categories and themes",
                "key_features": ["Fun QR code creation", "Category-based themes", "Social sharing", "Entertainment focus"],
                "target_audience": "Social media users, content creators, and anyone looking to add fun to QR codes",
                "story_angle": "Making QR codes entertaining and shareable for social engagement"
            },
            {
                "name": "FormatWeaver",
                "link": "https://formatweaver.com/",
                "description": "A universal file format converter that transforms any file format to any other format with browser-based processing",
                "key_features": ["Universal file conversion", "Browser-based processing", "No data storage", "Privacy-focused"],
                "target_audience": "Professionals, students, and anyone needing file format conversion",
                "story_angle": "Seamless file format transformation with complete privacy protection"
            },
            {
                "name": "SnapCompress",
                "link": "https://snapcompress.com/",
                "description": "Free online image compression tool that reduces file sizes while maintaining quality, supporting JPEG and PNG formats",
                "key_features": ["Image compression", "Adjustable compression levels", "No data storage", "JPEG and PNG support"],
                "target_audience": "Web developers, bloggers, photographers, and content creators",
                "story_angle": "Effortless image optimization for faster web performance"
            },
            {
                "name": "PixelArtz",
                "link": "https://pixelartz.com/",
                "description": "Free online pixel art creator that allows users to draw, convert images to pixel art, and share their creations",
                "key_features": ["Pixel art creation", "Image to pixel art conversion", "Drawing tools", "Community sharing"],
                "target_audience": "Game developers, digital artists, hobbyists, and retro gaming enthusiasts",
                "story_angle": "Unleashing pixel creativity for the digital art community"
            },
            {
                "name": "AllRandomTools",
                "link": "https://allrandomtools.com/",
                "description": "A collection of random selection and decision-making tools including wheels, generators, and choice makers",
                "key_features": ["Decision-making wheel", "Random number generator", "Coin flip", "Dice roller", "Yes/No decisions"],
                "target_audience": "Anyone needing help with decisions, gamers, teachers, and event organizers",
                "story_angle": "Simplifying life's choices with fun random decision tools"
            },
            {
                "name": "CasualGameZone",
                "link": "https://casualgamezone.com/",
                "description": "A collection of fun, free online casual games including brain teasers, action games, and skill challenges",
                "key_features": ["Multiple game categories", "Browser-based games", "Free to play", "Skill and brain challenges"],
                "target_audience": "Casual gamers, office workers on breaks, students, and entertainment seekers",
                "story_angle": "Quick entertainment hub for casual gaming enthusiasts"
            },
            {
                "name": "CalculateDaily",
                "link": "https://calculatedaily.com/",
                "description": "Comprehensive calculator hub offering various everyday calculators for health, finance, conversions, and more",
                "key_features": ["BMI calculator", "Financial calculators", "Unit converters", "Grade calculators", "Utility calculations"],
                "target_audience": "Students, professionals, homeowners, and anyone needing quick calculations",
                "story_angle": "Your everyday mathematical companion for life's calculations"
            },
            {
                "name": "PicxCraft",
                "link": "https://picxcraft.com/",
                "description": "Free online image editing tool with photo filters, drawing capabilities, and ASCII art creation features",
                "key_features": ["Photo filters", "Drawing tools", "ASCII art creation", "Multiple export formats", "Free image editing"],
                "target_audience": "Content creators, social media users, hobbyists, and digital artists",
                "story_angle": "Transforming ordinary photos into extraordinary creative expressions"
            },
            {
                "name": "AImagEasy",
                "link": "https://aimageasy.com/",
                "description": "AI-powered art generation platform that transforms ideas into stunning digital artwork using artificial intelligence",
                "key_features": ["AI art generation", "Text-to-image creation", "Stunning visual output", "Creative AI tools"],
                "target_audience": "Digital artists, content creators, marketers, and AI enthusiasts",
                "story_angle": "Democratizing art creation through accessible AI technology"
            },
            {
                "name": "PichaVerse",
                "link": "https://pichaverse.com/",
                "description": "AI-powered image transformation tool that applies creative filters and styles to pictures with various artistic themes",
                "key_features": ["AI filters", "Multiple artistic styles", "Ghibli and anime styles", "Cyberpunk and vintage effects", "Easy sharing"],
                "target_audience": "Social media users, content creators, photographers, and digital art enthusiasts",
                "story_angle": "Unleashing endless creative possibilities with AI-powered image transformation"
            },
            {
                "name": "PrettyParser",
                "link": "https://prettyparser.com/",
                "description": "Code beautifier and minifier for JSON, HTML, and XML that formats code for better readability and optimization",
                "key_features": ["Code beautification", "Code minification", "JSON/HTML/XML support", "No data storage", "Developer-focused"],
                "target_audience": "Web developers, programmers, API developers, and software engineers",
                "story_angle": "Making code beautiful and readable for the developer community"
            },
            {
                "name": "MoodyBuddy",
                "link": "https://moodybuddy.com/",
                "description": "AI companion chatbot named Emma that provides emotional support through voice, video, and text conversations",
                "key_features": ["AI companion", "Voice and video chat", "Multilingual support", "Emotional support", "Always available"],
                "target_audience": "People seeking emotional support, companionship, or someone to talk to",
                "story_angle": "Your AI companion for every mood and moment, bringing comfort and connection"
            }
        ]
        

      

    @staticmethod
    def clean_text_for_selenium(text: str) -> str:
        """Clean text to remove problematic characters, preserving paragraphs."""
        emoji_pattern = re.compile("["  # same pattern as before
                                   u"\U0001F600-\U0001F64F"
                                   u"\U0001F300-\U0001F5FF"
                                   u"\U0001F680-\U0001F6FF"
                                   u"\U0001F1E0-\U0001F1FF"
                                   u"\U00002500-\U00002BEF"
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u"\U00010000-\U0010ffff"
                                   u"\u2640-\u2642"
                                   u"\u2600-\u2B55"
                                   u"\u200d"
                                   u"\u23cf"
                                   u"\u23e9"
                                   u"\u231a"
                                   u"\ufe0f"
                                   u"\u3030"
                                   "]+", flags=re.UNICODE)

        # Remove emojis
        cleaned_text = emoji_pattern.sub('', text)

        # Keep line breaks (used for paragraphs)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        cleaned_text = re.sub(r'[ \t]+\n', '\n', cleaned_text)
        cleaned_text = ''.join(char for char in cleaned_text if ord(char) < 65536)

        return cleaned_text.strip()

    def generate_linkedin_story_post(self, product: Dict) -> str:
        """Generate a story-driven LinkedIn post prompt"""
        story_prompts = [
            f"Write a LinkedIn post about {product['name']} that starts with a relatable workplace challenge or personal struggle that the tool solves. Include a brief story about discovery or transformation.",
            f"Create a LinkedIn post about {product['name']} that begins with 'Last week, I discovered...' and tells a story about how this tool changed someone's workflow or life.",
            f"Write a LinkedIn post about {product['name']} that starts with a question to the audience about a common problem, then reveals how this tool provides the solution.",
            f"Create a compelling LinkedIn post about {product['name']} that tells a story about innovation, problem-solving, or helping others, connecting it to the bigger mission of Helpothon.",
            f"Write a LinkedIn post about {product['name']} that starts with 'You know that feeling when...' and builds a narrative around the relief or joy this tool brings.",
            f"Include the product link when you are posting"
        ]
        selected_prompt = random.choice(story_prompts)

        context_info = f"""
Product: {product['name']}
Description: {product['description']}
Key Features: {', '.join(product['key_features'])}
Target Audience: {product['target_audience']}
Story Angle: {product['story_angle']}
Link: {product['link']}
        """

        return f"""{selected_prompt}

Context: {context_info}

Requirements:
- Keep it between 750–900 characters
- MANDATORY: Include the product link {product['link']} naturally in the narrative
- Focus on storytelling that resonates with professionals
- Highlight how the product solves a real-world problem or enhances productivity
- Use paragraph breaks (\\n\\n)
- Add relevant hashtags (not more than 10)
- CRITICAL: Must include the product link {product['link']} in the post
- No emojis or unicode
- End with CTA that includes the link
"""

    def generate_twitter_post(self, product: Dict) -> str:
        """Generate a tweet prompt"""
        selected_prompt = random.choice([
            f"Create a single punchy Twitter post about {product['name']} that highlights its main benefit in under 250 characters.",
            f"Write a single Twitter post about {product['name']} that uses a before/after structure in under 250 characters.",
            f"Create a single tweet: Pro tip - use {product['name']} to {product['key_features'][0].lower()}!",
        ])

        return f"""{selected_prompt}

Product: {product['name']}
Description: {product['description']}
Key Features: {', '.join(product['key_features'])}
Link: {product['link']}

Requirements:
- SINGLE TWEET ONLY (under 250 characters total)
- 1-2 hashtags maximum
- MANDATORY: Include link {product['link']} in the post
- CRITICAL: Must include the product link in every tweet
- CRITICAL: Must be ONE tweet, not multiple tweets or threads
"""

    def generate_devto_post(self, product: Dict) -> str:
        """Generate a Dev.to article introducing the product to developers"""
        return f"""Write a Dev.to article introducing {product['name']} to developers.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Developer-focused\n- MANDATORY: Include product link {product['link']} in the article\n- No emojis or unicode\n- End with a call to action that includes the link\n- CRITICAL: Must include the product link in the content\n"""

    def generate_hashnode_post(self, product: Dict) -> str:
        """Generate a Hashnode blog post about the product for the tech community"""
        return f"""Write a Hashnode blog post about {product['name']} for the tech community.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Tech blog style\n- MANDATORY: Include product link {product['link']} in the post\n- No emojis or unicode\n- End with a call to action that includes the link\n- CRITICAL: Must include the product link in the content\n"""

    def generate_blogger_post(self, product: Dict) -> str:
        """Generate a Blogger post about the product"""
        return f"""Write a Blogger blog post about {product['name']}.
\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Blogging style\n- MANDATORY: Include product link {product['link']} in the post\n- No emojis or unicode\n- End with a call to action that includes the link\n- CRITICAL: Must include the product link in the content\n"""

    def generate_disqus_post(self, product: Dict) -> str:
        """Generate a Disqus post about the product"""
        return f"""Write a Disqus comment introducing {product['name']}.
\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 1000 characters\n- MANDATORY: Include product link {product['link']} in the comment\n- No emojis or unicode\n- End with a call to action that includes the link\n- CRITICAL: Must include the product link in the content\n"""

    def generate_mastodon_post(self, product: Dict) -> str:
        """Generate a Mastodon post prompt"""
        selected_prompt = random.choice([
            f"Create an engaging Mastodon post about {product['name']} that tells a story about how it solves a real problem.",
            f"Write a detailed Mastodon post about {product['name']} focusing on its impact and benefits for users.",
            f"Share an in-depth story about how {product['name']} is making a difference in people's workflows!",
        ])
        return f"""{selected_prompt}

Product: {product['name']}
Description: {product['description']}
Key Features: {', '.join(product['key_features'])}
Link: {product['link']}

Requirements:
- Write an engaging post (up to 3000 characters)
- Include 2-3 relevant hashtags
- MANDATORY: Include link {product['link']} in the post
- No emojis or unicode
- Use paragraph breaks for readability
- The hashtags should be posted in separate lines
- CRITICAL: Must include the product link in the post
- End with a clear call-to-action
"""

    def generate_pinterest_post(self, product: Dict) -> str:
        """Generate a Pinterest pin description with title and content"""
        story_prompts = [
            f"Create an inspiring Pinterest pin about {product['name']} that showcases its visual impact",
            f"Design a Pinterest-worthy description for {product['name']} focusing on transformation",
            f"Write a creative Pinterest pin for {product['name']} that drives engagement"
        ]
        selected_prompt = random.choice(story_prompts)
        
        context = f"""
Product: {product['name']}
Description: {product['description']}
Key Features: {', '.join(product['key_features'])}
Target Audience: {product['target_audience']}
Link: {product['link']}

Requirements:
- Create a catchy title (max 100 characters)
- Write an engaging description (max 500 characters)
- Focus on visual and aesthetic appeal
- Include relevant keywords for Pinterest SEO
- MANDATORY: Include the product link {product['link']} naturally in the description
- End with a clear call-to-action that includes the link
- CRITICAL: Must include the product link in the pin description
"""
        return f"{selected_prompt}\n\n{context}"

    def generate_reddit_post(self, product: Dict) -> str:
        """Generate a Reddit post with title and content for a neutral subreddit, human-like, no image."""
        # Use a neutral, general-interest subreddit (can be overridden elsewhere)
        neutral_subreddit = "CasualConversation"  # Change as needed
        subreddit_style = (
            "Write a personal, discussion-oriented post as a real Reddit user. "
            "Share your genuine thoughts, experiences, or questions about the product. "
            "Avoid sounding like an advertisement or AI. Use a natural, conversational tone. "
            "Encourage comments and discussion. Do NOT mention AI, bots, or automation. "
            "Do NOT include or reference any images."
        )
        context = f"""
{subreddit_style}\n\nProduct Details:\n- Name: {product['name']}\n- Description: {product['description']}\n- Key Features: {', '.join(product['key_features'])}\n- Target Audience: {product['target_audience']}\n- Link: {product['link']}\n\nRequirements:\n- Create an engaging, human-sounding title (max 300 characters)\n- Write a detailed, story-driven body\n- Use proper formatting\n- Include the product link {product['link']} naturally in the post\n- End with a question or discussion point\n- CRITICAL: Do NOT generate or mention any images\n- CRITICAL: Write as a real Reddit user, not as an AI\n"""
        return context

    def get_platform_visual_style(self, platform: str) -> Dict:
        """Get platform-specific visual style guidelines"""
        return {
            "linkedin": {
                "style": "professional, corporate, business-like",
                "color_scheme": "professional blues and grays",
                "composition": "clean, organized, minimalist",
                "mood": "professional, trustworthy, authoritative"
            },
            "twitter": {
                "style": "dynamic, engaging, informal",
                "color_scheme": "vibrant, high contrast",
                "composition": "eye-catching, bold",
                "mood": "energetic, conversational, immediate"
            },
            "pinterest": {
                "style": "artistic, visually rich, aesthetic",
                "color_scheme": "rich, warm tones, pinterest-style color palette",
                "composition": "beautifully composed, pinterest-worthy",
                "mood": "inspiring, creative, aspirational"
            },
            "devto": {
                "style": "technical, developer-focused",
                "color_scheme": "dark mode friendly, code editor colors",
                "composition": "clean, technical, structured",
                "mood": "educational, technical, practical"
            },
            "hashnode": {
                "style": "modern tech, developer-centric",
                "color_scheme": "modern, tech-focused",
                "composition": "clean, structured, modern",
                "mood": "educational, professional, community-focused"
            },
            "blogger": {
                "style": "editorial, blog-style",
                "color_scheme": "warm, inviting",
                "composition": "editorial, story-focused",
                "mood": "informative, personal, engaging"
            },
            "disqus": {
                "style": "conversational, comment-style",
                "color_scheme": "neutral, balanced",
                "composition": "simple, focused",
                "mood": "engaging, discussion-oriented"
            },
            "mastodon": {
                "style": "community-focused, federated",
                "color_scheme": "mastodon brand colors",
                "composition": "balanced, community-oriented",
                "mood": "inclusive, privacy-focused, empowering"
            },
            "pixelfed": {
                "style": "artistic, instagram-like",
                "color_scheme": "vibrant, photo-centric",
                "composition": "visually striking, photo-focused",
                "mood": "creative, artistic, visual"
            },
            "reddit": {
                "style": "community-focused, discussion-oriented",
                "color_scheme": "reddit brand colors",
                "composition": "clear, informative",
                "mood": "discussion-focused, community-driven"
            }
        }.get(platform.lower(), {
            "style": "professional, modern",
            "color_scheme": "balanced, neutral",
            "composition": "clean, organized",
            "mood": "professional, engaging"
        })

    def generate_content(self, style: str = "casual", platform: str = "linkedin") -> Optional[str]:
        try:
            product = random.choice(self.products)
            platform = platform.lower()

            if platform == "linkedin":
                prompt = self.generate_linkedin_story_post(product)
            elif platform == "twitter":
                prompt = self.generate_twitter_post(product)
            elif platform == "devto":
                prompt = self.generate_devto_post(product)
            elif platform == "hashnode":
                prompt = self.generate_hashnode_post(product)
            elif platform == "blogger":
                prompt = self.generate_blogger_post(product)
            elif platform == "disqus":
                prompt = self.generate_disqus_post(product)
            elif platform == "mastodon":
                prompt = self.generate_mastodon_post(product)
            elif platform == "pinterest":
                prompt = self.generate_pinterest_post(product)
            elif platform == "reddit":
                prompt = self.generate_reddit_post(product)
            elif platform == "pixelfed":
                prompt = self.generate_pixelfed_post(product)
            else:
                prompt = f"Write a {style} post about {product['name']} from Helpothon.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n"

            # Get platform-specific visual style to influence both content and image generation
            visual_style = self.get_platform_visual_style(platform)
            
            # Add visual style context to system message
            system_message = f"You are a professional copywriter creating {platform} content. " \
                           f"Create content that aligns with the platform's visual style: {visual_style['style']}, " \
                           f"mood: {visual_style['mood']}, and composition: {visual_style['composition']}. " \
                           f"Preserve paragraph breaks. Use natural human tone. " \
                           f"IMPORTANT: Do not use any emojis, emoticons, or Unicode symbols in your content. " \
                           f"CRITICAL: Always include the product link in your content - this is mandatory."

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )

            content = response.choices[0].message.content.strip()

            # For Blogger, convert double newlines to <p> tags for better formatting
            if platform == "blogger":
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                html_content = ''.join(f'<p>{p}</p>' for p in paragraphs)
                return html_content
            
            # Clean text only for Twitter or platforms that don't support paragraphs
            return self.clean_text_for_selenium(content) if platform == "twitter" else content

        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            return None

    def list_products(self) -> List[str]:
        return [p["name"] for p in self.products]

    def get_product_info(self, product_name: str) -> Optional[Dict]:
        for product in self.products:
            if product["name"].lower() == product_name.lower():
                return product
        return None

    def get_story_scenarios(self) -> List[str]:
        """Get list of story scenarios for content generation"""
        return [
            "school", "college", "workplace", "garden", "cafe", "library", 
            "park", "home", "gym", "beach", "restaurant", "travel", "shopping",
            "hospital", "airport", "hotel", "museum", "concert", "wedding", "party"
        ]

    def generate_story_based_content(self, platform: str, scenario: str = None) -> str:
        """Generate story-based content for any platform with specific scenarios"""
        if not scenario:
            scenario = random.choice(self.get_story_scenarios())
        
        product = random.choice(self.products)
        
        # Create scenario-specific story prompts
        scenario_stories = {
            "school": f"Tell a story about a student who discovered {product['name']} while working on a school project",
            "college": f"Share a story about a college student who used {product['name']} to solve a university challenge",
            "workplace": f"Tell a story about a professional who found {product['name']} during a busy workday",
            "garden": f"Share a story about someone who used {product['name']} while relaxing in their garden",
            "cafe": f"Tell a story about discovering {product['name']} while working from a cozy cafe",
            "library": f"Share a story about a student who found {product['name']} while studying at the library",
            "park": f"Tell a story about someone who used {product['name']} while enjoying time at the park",
            "home": f"Share a story about discovering {product['name']} while working from home",
            "gym": f"Tell a story about someone who used {product['name']} to track their fitness progress",
            "beach": f"Share a story about using {product['name']} while on a beach vacation",
            "restaurant": f"Tell a story about discovering {product['name']} while dining at a restaurant",
            "travel": f"Share a story about how {product['name']} helped during a travel experience",
            "shopping": f"Tell a story about using {product['name']} while shopping or running errands",
            "hospital": f"Share a story about how {product['name']} helped in a healthcare setting",
            "airport": f"Tell a story about discovering {product['name']} while waiting at an airport",
            "hotel": f"Share a story about using {product['name']} while staying at a hotel",
            "museum": f"Tell a story about someone who used {product['name']} during a museum visit",
            "concert": f"Share a story about using {product['name']} at a concert or event",
            "wedding": f"Tell a story about how {product['name']} helped with wedding planning",
            "party": f"Share a story about using {product['name']} to organize a party or event"
        }
        
        story_prompt = scenario_stories.get(scenario, scenario_stories["workplace"])
        
        # Platform-specific formatting
        if platform == "twitter":
            return self.generate_twitter_story_content(product, story_prompt, scenario)
        elif platform == "linkedin":
            return self.generate_linkedin_story_content(product, story_prompt, scenario)
        elif platform == "pinterest":
            return self.generate_pinterest_story_content(product, story_prompt, scenario)
        elif platform == "devto":
            return self.generate_devto_story_content(product, story_prompt, scenario)
        elif platform == "hashnode":
            return self.generate_hashnode_story_content(product, story_prompt, scenario)
        elif platform == "blogger":
            return self.generate_blogger_story_content(product, story_prompt, scenario)
        elif platform == "mastodon":
            return self.generate_mastodon_story_content(product, story_prompt, scenario)
        else:
            return self.generate_generic_story_content(product, story_prompt, scenario)

    def generate_twitter_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate Twitter story content with scenario context"""
        prompt = f"""{story_prompt}

Product Context:
- Name: {product['name']}
- Description: {product['description']}
- Key Features: {', '.join(product['key_features'])}
- Link: {product['link']}

Scenario: {scenario}

Create a single Twitter post (NOT a thread) that:
- Tells a brief, engaging story set in the {scenario} setting
- Mentions discovering or using {product['name']}
- Shows the benefit in a concise way
- MANDATORY: Includes the product link {product['link']} naturally
- Uses 1-2 relevant hashtags
- Stays under 280 characters total
- Makes the story relatable and engaging
- CRITICAL: Must be ONE single tweet, not multiple tweets
- CRITICAL: Must include the product link in the tweet
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a skilled storyteller who creates engaging, relatable social media content. IMPORTANT: Do not use any emojis, emoticons, or Unicode symbols in your content. CRITICAL: Create only ONE single tweet, never multiple tweets or threads. CRITICAL: Keep tweets under 280 characters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            
            # Ensure tweet is under 280 characters
            if len(content) > 280:
                self.logger.warning(f"Tweet too long ({len(content)} chars), truncating...")
                link = product['link']
                hashtags = re.findall(r"#\w+", content)
                hashtags_str = " ".join(hashtags[:2]) if hashtags else ""
                # Remove hashtags and link from main content
                main_content = re.sub(r"#\w+", "", content)
                main_content = main_content.replace(link, "").strip()
                # Reserve space for link and hashtags (with spaces)
                reserved = len(link) + (1 if hashtags_str else 0) + len(hashtags_str)
                available = 280 - reserved - 1
                # Truncate main content at word boundary, no ellipsis
                safe_main = main_content[:available]
                if ' ' in safe_main:
                    safe_main = safe_main[:safe_main.rfind(' ')]
                safe_main = safe_main.rstrip()
                # Compose final tweet
                tweet_parts = [safe_main, link]
                if hashtags_str:
                    tweet_parts.append(hashtags_str)
                content = ' '.join(part for part in tweet_parts if part).strip()
                # If still too long (rare), trim hashtags
                while len(content) > 280 and hashtags_str:
                    hashtags = hashtags[:-1]
                    hashtags_str = " ".join(hashtags)
                    tweet_parts = [safe_main, link]
                    if hashtags_str:
                        tweet_parts.append(hashtags_str)
                    content = ' '.join(part for part in tweet_parts if part).strip()
                # If still too long, trim main content further
                while len(content) > 280 and len(safe_main) > 0:
                    safe_main = safe_main[:-1].rstrip()
                    tweet_parts = [safe_main, link]
                    if hashtags_str:
                        tweet_parts.append(hashtags_str)
                    content = ' '.join(part for part in tweet_parts if part).strip()

            return content
        except Exception as e:
            self.logger.error(f"Error generating Twitter story content: {e}")
            return f"Discover how {product['name']} can transform your {scenario} experience! {product['link']}"
    def generate_linkedin_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate LinkedIn story content with scenario context"""
        prompt = f"""{story_prompt}

Product Context:
- Name: {product['name']}
- Description: {product['description']}
- Key Features: {', '.join(product['key_features'])}
- Link: {product['link']}

Scenario: {scenario}

Create a LinkedIn post that:
- Starts with a professional story set in the {scenario} environment
- Shares a personal insight or lesson learned
- Connects to broader professional themes
- MANDATORY: Includes the product {product['link']} naturally in the narrative
- Uses professional tone but remains engaging
- Includes relevant hashtags
- Ends with a call to action that includes the link
- 800-1000 characters
- CRITICAL: Must include the product link in the LinkedIn post
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional content creator who writes engaging LinkedIn posts with storytelling. IMPORTANT: Do not use any emojis, emoticons, or Unicode symbols in your content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating LinkedIn story content: {e}")
            return f"Here's how {product['name']} transformed my {scenario} experience: {product['link']}"
    def generate_pinterest_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate Pinterest story content with scenario context"""
        prompt = f"""{story_prompt}

Product Context:
- Name: {product['name']}
- Description: {product['description']}
- Key Features: {', '.join(product['key_features'])}
- Link: {product['link']}

Scenario: {scenario}

Create a Pinterest pin description that:
- Tells a visual story set in the {scenario} environment
- Focuses on the transformation or benefit
- Uses descriptive, visual language
- Includes relevant keywords for Pinterest SEO
- MANDATORY: Mentions the product and includes link {product['link']} naturally
- Includes the link in the description
- 200-300 characters
- Uses Pinterest-friendly hashtags
- CRITICAL: Must include the product link in the pin description
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Pinterest content creator who writes engaging, visual descriptions. IMPORTANT: Do not use any emojis, emoticons, or Unicode symbols in your content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating Pinterest story content: {e}")
            return f"Transform your {scenario} experience with {product['name']}! {product['link']}"
    def generate_devto_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate Dev.to story content with scenario context"""
        prompt = f"""{story_prompt}

Product Context:
- Name: {product['name']}
- Description: {product['description']}
- Key Features: {', '.join(product['key_features'])}
- Link: {product['link']}

Scenario: {scenario}

Create a well-formatted Dev.to article that:
- Starts with a technical story set in the {scenario} environment
- Explains the problem and solution technically
- Includes code examples or technical details if relevant
- Shows practical applications
- MANDATORY: Include the product link {product['link']} naturally in the content
- Uses developer-friendly language
- 1000-1500 characters
- CRITICAL: Use proper paragraph formatting with double line breaks (\\n\\n) between paragraphs
- Use proper punctuation and sentence structure
- Include relevant hashtags at the end
- Structure content with clear paragraph breaks for readability
- CRITICAL: Must include the product link in the post content
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a technical writer who creates engaging, well-formatted content for developers. IMPORTANT: Do not use any emojis, emoticons, or Unicode symbols in your content. Always use proper paragraph breaks with double line breaks (\\n\\n) between paragraphs for better readability. Use proper punctuation and sentence structure throughout."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            
            # Ensure proper paragraph formatting
            content = self.format_content_for_blog(content)
            
            return content
        except Exception as e:
            self.logger.error(f"Error generating Dev.to story content: {e}")
            return f"How {product['name']} solved my {scenario} development challenge: {product['link']}"
    def generate_hashnode_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate Hashnode story content with scenario context"""
        return self.generate_devto_story_content(product, story_prompt, scenario)  # Similar to Dev.to
    def generate_blogger_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate Blogger story content with scenario context"""
        prompt = f"""{story_prompt}

Product Context:
- Name: {product['name']}
- Description: {product['description']}
- Key Features: {', '.join(product['key_features'])}
- Link: {product['link']}

Scenario: {scenario}

Create a well-formatted blog post that:
- Starts with a personal story set in the {scenario} environment
- Provides detailed experience and insights
- Includes practical tips and benefits
- Uses conversational, blog-friendly tone
- MANDATORY: Include the product link {product['link']} naturally in the content
- 1500-2000 characters
- CRITICAL: Use proper paragraph formatting with double line breaks (\\n\\n) between paragraphs
- Use proper punctuation and sentence structure
- Include relevant hashtags at the end
- Structure content with clear paragraph breaks for readability
- CRITICAL: Must include the product link in the post content
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional blogger who writes engaging, well-formatted personal stories. IMPORTANT: Do not use any emojis, emoticons, or Unicode symbols in your content. Always use proper paragraph breaks with double line breaks (\\n\\n) between paragraphs for better readability. Use proper punctuation and sentence structure throughout."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            
            # Ensure proper paragraph formatting
            content = self.format_content_for_blog(content)
            
            return content
        except Exception as e:
            self.logger.error(f"Error generating Blogger story content: {e}")
            return f"My {scenario} experience with {product['name']}: {product['link']}"
    def generate_mastodon_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate Mastodon story content with scenario context"""
        # Similar to Twitter but can be slightly longer
        return self.generate_twitter_story_content(product, story_prompt, scenario)
    def generate_generic_story_content(self, product: Dict, story_prompt: str, scenario: str) -> str:
        """Generate generic story content with scenario context"""
        prompt = f"""{story_prompt}

Product Context:
- Name: {product['name']}
- Description: {product['description']}
- Key Features: {', '.join(product['key_features'])}
- Link: {product['link']}

Scenario: {scenario}

Create engaging, well-formatted content that:
- Tells a relatable story set in the {scenario} environment
- Shows the value and benefits of the product
- MANDATORY: Include the product link {product['link']} naturally in the content
- Uses engaging, conversational tone
- 500-800 characters
- CRITICAL: Use proper paragraph formatting with double line breaks (\\n\\n) between paragraphs
- Use proper punctuation and sentence structure
- Structure content with clear paragraph breaks for readability
- CRITICAL: Must include the product link in the post content
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a content creator who writes engaging, well-formatted stories. IMPORTANT: Do not use any emojis, emoticons, or Unicode symbols in your content. Always use proper paragraph breaks with double line breaks (\\n\\n) between paragraphs for better readability. Use proper punctuation and sentence structure throughout."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            
            # Ensure proper paragraph formatting
            content = self.format_content_for_blog(content)
            
            return content
        except Exception as e:
            self.logger.error(f"Error generating generic story content: {e}")
            return f"Discover how {product['name']} can enhance your {scenario} experience! {product['link']}"

    def generate_pixelfed_post(self, product: Dict) -> str:
        """Generate a Pixelfed post with caption and image prompt"""
        caption_prompts = [
            f"Create a visually appealing Pixelfed post about {product['name']} highlighting its design elements",
            f"Design a creative Pixelfed caption for {product['name']} focusing on visual storytelling",
            f"Write an artistic Pixelfed post for {product['name']} that inspires creativity"
        ]
        selected_prompt = random.choice(caption_prompts)
        
        context = f"""
Product: {product['name']}
Description: {product['description']}
Key Features: {', '.join(product['key_features'])}
Target Audience: {product['target_audience']}
Link: {product['link']}

Requirements:
- Create a concise, engaging caption (max 500 characters)
- Focus on visual appeal and aesthetics
- Include relevant hashtags (3-5 max)
- MANDATORY: Include the product link {product['link']} naturally in the caption
- Maintain artistic and creative tone
- Suggest visual elements that would work well with the caption
- CRITICAL: Must include the product link in the post
"""
        return f"{selected_prompt}\n\n{context}"

    @staticmethod
    def format_content_for_blog(content: str) -> str:
        """Format content with proper paragraph breaks and punctuation for blog posts"""
        # First clean the text
        content = ContentGenerator.clean_text_for_selenium(content)
        
        # Ensure proper sentence endings
        content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
        
        # Fix multiple spaces
        content = re.sub(r' +', ' ', content)
        
        # Ensure proper paragraph breaks (double line breaks)
        # First normalize all line breaks
        content = re.sub(r'\n+', '\n', content)
        
        # Split into sentences and group into paragraphs
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        # Group sentences into paragraphs (roughly 2-3 sentences per paragraph)
        paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                current_paragraph.append(sentence)
                # Create paragraph break after 2-3 sentences or if sentence is long
                if len(current_paragraph) >= 3 or len(sentence) > 100:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
        
        # Add any remaining sentences
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        # Join paragraphs with double line breaks
        formatted_content = '\n\n'.join(paragraphs)
        
        # Ensure hashtags are separated properly
        formatted_content = re.sub(r'(#\w+)', r' \1', formatted_content)
        formatted_content = re.sub(r' +', ' ', formatted_content)
        
        return formatted_content.strip()
