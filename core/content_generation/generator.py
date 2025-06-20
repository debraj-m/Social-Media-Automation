from openai import OpenAI
from typing import Optional
import re
import logging

class ContentGenerator:
    def __init__(self, openai_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def clean_text_for_selenium(text: str) -> str:
        """Clean text to remove characters that ChromeDriver can't handle"""
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002500-\U00002BEF"  # chinese char
                                   u"\U00002702-\U000027B0"
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
                                   u"\ufe0f"  # dingbats
                                   u"\u3030"
                                   "]+", flags=re.UNICODE)
        cleaned_text = emoji_pattern.sub(r'', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        cleaned_text = ''.join(char for char in cleaned_text if ord(char) < 65536)
        return cleaned_text

    def generate_content(self, topic: Optional[str] = None, style: str = "casual", max_length: int = 250) -> Optional[str]:
        """Generate content using OpenAI"""
        try:
            if topic:
                prompt = f"Write a {style} tweet about {topic}. Limit to {max_length} characters. No emojis or special unicode."
            else:
                prompt = f"Write a {style} tweet. Limit to {max_length} characters. No emojis or special unicode."
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media content creator who writes engaging, authentic tweets that sound natural and human. Do not use emojis or special unicode characters in your responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            content = response.choices[0].message.content.strip()
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            content = self.clean_text_for_selenium(content)
            self.logger.info(f"Generated content: {content}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to generate content: {e}")
            return None

    def generate_post(self, prompt: str) -> Optional[str]:
        """Generate a post using OpenAI's API."""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            max_completion_tokens=2800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content if response.choices else None
