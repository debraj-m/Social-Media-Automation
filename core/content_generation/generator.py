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
                "name": "Scanmeee",
                "link": "https://scanmeee.com/",
                "description": "Create and share fun, creative QR codes effortlessly",
                "key_features": ["QR code generation", "Creative designs", "Easy sharing"],
                "target_audience": "Marketers, event organizers, creative professionals",
                "story_angle": "Bridging physical and digital worlds through creative QR codes"
            },
            {
                "name": "FormatWeaver",
                "link": "https://formatweaver.com/",
                "description": "Any-to-any file format converter that processes files in your browser",
                "key_features": ["Universal file conversion", "Browser-based processing", "Privacy-focused"],
                "target_audience": "Professionals, students, content creators",
                "story_angle": "Seamless file transformation without compromising privacy"
            },
            {
                "name": "SnapCompress",
                "link": "https://snapcompress.com/",
                "description": "Compress files quickly and efficiently to save space and boost productivity",
                "key_features": ["File compression", "Space optimization", "Productivity boost"],
                "target_audience": "Professionals, developers, content creators",
                "story_angle": "Maximizing productivity through smart file management"
            },
            {
                "name": "PixelArtz",
                "link": "https://pixelartz.com/",
                "description": "Create stunning pixel art for home decor, gaming, or digital projects",
                "key_features": ["Pixel art creation", "Gaming assets", "Digital art"],
                "target_audience": "Game developers, digital artists, hobbyists",
                "story_angle": "Reviving retro aesthetics in modern digital creativity"
            },
            {
                "name": "All Random Tools",
                "link": "https://allrandomtools.com/",
                "description": "Access a comprehensive suite of utility tools for everyday tasks and creative solutions",
                "key_features": ["Multiple utilities", "Everyday tools", "Creative solutions"],
                "target_audience": "General users, professionals, students",
                "story_angle": "One-stop solution for all your digital tool needs"
            },
            {
                "name": "Casual Game Zone",
                "link": "https://casualgamezone.com/",
                "description": "Enjoy fun and engaging games for all ages to spark joy and entertainment",
                "key_features": ["Casual gaming", "All ages", "Entertainment"],
                "target_audience": "Families, casual gamers, entertainment seekers",
                "story_angle": "Bringing families together through fun, accessible gaming"
            },
            {
                "name": "Calculate Daily",
                "link": "https://calculatedaily.com/",
                "description": "Simplify daily calculations and boost productivity with intuitive tools",
                "key_features": ["Daily calculations", "Productivity tools", "Intuitive interface"],
                "target_audience": "Professionals, students, everyday users",
                "story_angle": "Making complex calculations simple for everyone"
            },
            {
                "name": "PicxCraft",
                "link": "https://picxcraft.com/",
                "description": "Craft vibrant images and pixel art for creative and gaming projects",
                "key_features": ["Image crafting", "Pixel art", "Creative tools"],
                "target_audience": "Digital artists, game developers, creatives",
                "story_angle": "Empowering digital creativity through innovative image tools"
            },
            {
                "name": "AImageasy",
                "link": "https://aimageasy.com/",
                "description": "Transform your ideas into stunning AI-generated art with ease",
                "key_features": ["AI art generation", "Idea transformation", "Easy creation"],
                "target_audience": "Artists, marketers, content creators",
                "story_angle": "Democratizing art creation through AI innovation"
            },
            {
                "name": "Pichaverse",
                "link": "https://pichaverse.com/",
                "description": "Unleash endless possibilities with crazy AI filters for your pictures",
                "key_features": ["AI filters", "Photo transformation", "Creative effects"],
                "target_audience": "Social media users, photographers, content creators",
                "story_angle": "Transforming ordinary photos into extraordinary art"
            },
            {
                "name": "MoodyBuddy",
                "link": "https://moodybuddy.com/",
                "description": "Track your mood and boost emotional well-being with AI friend Emma",
                "key_features": ["Mood tracking", "AI companion", "Mental health support"],
                "target_audience": "Individuals seeking mental health support, wellness enthusiasts",
                "story_angle": "Supporting mental health through compassionate AI companionship"
            },
            {
                "name": "PrettyParser",
                "link": "https://prettyparser.com/",
                "description": "Format and minify JSON, HTML, and XML with ease for clean, professional code",
                "key_features": ["Code formatting", "Minification", "Developer tools"],
                "target_audience": "Developers, programmers, technical professionals",
                "story_angle": "Making code beautiful and professional for developers worldwide"
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
- Include the product link naturally in the narrative
- Focus on storytelling that resonates with professionals
- Highlight how the product solves a real-world problem or enhances productivity
- Use paragraph breaks (\\n\\n)
- Add relevant hashtags (not more than 10)
- Add product link naturally
- No emojis or unicode
- End with CTA
"""

    def generate_twitter_post(self, product: Dict) -> str:
        """Generate a tweet prompt"""
        selected_prompt = random.choice([
            f"Create a punchy Twitter post about {product['name']} that highlights its main benefit.",
            f"Write a Twitter post about {product['name']} that uses a before/after structure.",
            f"Pro tip: use {product['name']} to {product['key_features'][0].lower()}!",
        ])

        return f"""{selected_prompt}

Product: {product['name']}
Description: {product['description']}
Key Features: {', '.join(product['key_features'])}
Link: {product['link']}

Requirements:
- Max 250 characters
- 1-2 hashtags
- Include link
- The hashtags should be posted in separate lines
"""

    def generate_pinterest_post(self, product: Dict) -> str:
        """Generate a visually inspiring Pinterest post prompt"""
        return f"""Create a visually inspiring Pinterest description for {product['name']}.
\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 500 characters\n- Focus on visual appeal and inspiration\n- Add 2-3 relevant hashtags\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_reddit_post(self, product: Dict) -> str:
        """Generate a Reddit post introducing the product to a relevant subreddit"""
        return f"""Write a Reddit post introducing {product['name']} to a relevant subreddit.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 10,000 characters\n- Start with a question or relatable problem\n- Encourage discussion\n- No emojis or unicode\n- Add product link naturally\n"""

    def generate_mastodon_post(self, product: Dict) -> str:
        """Generate a Mastodon post for the fediverse"""
        return f"""Write a Mastodon post about {product['name']} for the fediverse.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 500 characters\n- Add 1-2 hashtags\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_medium_post(self, product: Dict) -> str:
        """Generate a Medium story about the product"""
        return f"""Write a Medium story about {product['name']} and how it solves a real-world problem.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Storytelling style\n- Add product link naturally\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_devto_post(self, product: Dict) -> str:
        """Generate a Dev.to article introducing the product to developers"""
        return f"""Write a Dev.to article introducing {product['name']} to developers.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Developer-focused\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_hashnode_post(self, product: Dict) -> str:
        """Generate a Hashnode blog post about the product for the tech community"""
        return f"""Write a Hashnode blog post about {product['name']} for the tech community.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Tech blog style\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_ghost_post(self, product: Dict) -> str:
        """Generate a Ghost blog post about the product"""
        return f"""Write a Ghost blog post about {product['name']}.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Blogging style\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_wordpress_post(self, product: Dict) -> str:
        """Generate a WordPress blog post about the product"""
        return f"""Write a WordPress blog post about {product['name']}.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Blogging style\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_tumblr_post(self, product: Dict) -> str:
        """Generate a Tumblr post about the product"""
        return f"""Write a Tumblr blog post about {product['name']}.
\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Blogging style\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_blogger_post(self, product: Dict) -> str:
        """Generate a Blogger post about the product"""
        return f"""Write a Blogger blog post about {product['name']}.
\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Blogging style\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_substack_post(self, product: Dict) -> str:
        """Generate a Substack newsletter post about the product"""
        return f"""Write a Substack newsletter post about {product['name']}.
\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Newsletter style\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_wordpressorg_post(self, product: Dict) -> str:
        """Generate a WordPress.org blog post about the product"""
        return f"""Write a WordPress.org blog post about {product['name']}.
\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n\nRequirements:\n- Max 5000 characters\n- Blogging style\n- Add product link\n- No emojis or unicode\n- End with a call to action\n"""

    def generate_content(self, style: str = "casual", platform: str = "linkedin") -> Optional[str]:
        try:
            product = random.choice(self.products)
            platform = platform.lower()

            if platform == "linkedin":
                prompt = self.generate_linkedin_story_post(product)
            elif platform == "twitter":
                prompt = self.generate_twitter_post(product)
            elif platform == "pinterest":
                prompt = self.generate_pinterest_post(product)
            elif platform == "reddit":
                prompt = self.generate_reddit_post(product)
            elif platform == "mastodon":
                prompt = self.generate_mastodon_post(product)
            elif platform == "medium":
                prompt = self.generate_medium_post(product)
            elif platform == "devto":
                prompt = self.generate_devto_post(product)
            elif platform == "hashnode":
                prompt = self.generate_hashnode_post(product)
            elif platform == "ghost":
                prompt = self.generate_ghost_post(product)
            elif platform == "wordpress":
                prompt = self.generate_wordpress_post(product)
            elif platform == "tumblr":
                prompt = self.generate_tumblr_post(product)
            elif platform == "blogger":
                prompt = self.generate_blogger_post(product)
            elif platform == "substack":
                prompt = self.generate_substack_post(product)
            elif platform == "wordpressorg":
                prompt = self.generate_wordpressorg_post(product)
            else:
                prompt = f"""Write a {style} post about {product['name']} from Helpothon.\n\nDescription: {product['description']}\nKey Features: {', '.join(product['key_features'])}\nLink: {product['link']}\n"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional copywriter creating {platform} content. Preserve paragraph breaks. Use natural human tone."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )

            content = response.choices[0].message.content.strip()

            # Clean text only for Twitter or platforms that don’t support paragraphs
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
