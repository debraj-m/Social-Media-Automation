import os
import requests
import logging
from typing import Optional
import base64
from PIL import Image
import io
import hashlib
from datetime import datetime

class ImageGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_image_huggingface(self, prompt: str, model: str = "stabilityai/stable-diffusion-xl-base-1.0") -> Optional[bytes]:
        """Generate image using Hugging Face's free inference API and return the image buffer"""
        try:
            # Hugging Face Inference API (free tier)
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            # Clean and optimize prompt for image generation
            image_prompt = self.optimize_prompt_for_image(prompt)
            
            headers = {
                "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"
            }
            
            payload = {
                "inputs": image_prompt,
                "parameters": {
                    "negative_prompt": "blurry, low quality, text, watermark, logo, signature",
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5,
                    "width": 512,
                    "height": 512
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.content
            else:
                self.logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating image with Hugging Face: {str(e)}")
            return None
    
    def generate_image_pollinations(self, prompt: str) -> Optional[bytes]:
        """Generate image using Pollinations AI and return the image buffer"""
        try:
            # Clean and optimize prompt for image generation
            image_prompt = self.optimize_prompt_for_image(prompt)
            
            # Pollinations AI API (free, no API key required)
            api_url = "https://image.pollinations.ai/prompt/"
            
            # URL encode the prompt
            import urllib.parse
            encoded_prompt = urllib.parse.quote(image_prompt)
            
            # Add parameters for better image quality
            params = "?width=800&height=800&nologo=true&enhance=true"
            full_url = f"{api_url}{encoded_prompt}{params}"
            
            response = requests.get(full_url, timeout=60)
            
            if response.status_code == 200:
                return response.content
            else:
                self.logger.error(f"Pollinations API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating image with Pollinations: {str(e)}")
            return None
    
    def generate_image_replicate(self, prompt: str) -> Optional[bytes]:
        """Generate image using Replicate API and return the image buffer"""
        try:
            replicate_api_key = os.getenv('REPLICATE_API_TOKEN')
            if not replicate_api_key:
                self.logger.warning("Replicate API key not found, skipping Replicate generation")
                return None
                
            import replicate
            
            # Clean and optimize prompt for image generation
            image_prompt = self.optimize_prompt_for_image(prompt)
            
            output = replicate.run(
                "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
                input={
                    "prompt": image_prompt,
                    "negative_prompt": "blurry, low quality, text, watermark, logo, signature",
                    "width": 768,
                    "height": 768,
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5
                }
            )
            
            if output:
                # Download the generated image
                image_url = output[0] if isinstance(output, list) else output
                response = requests.get(image_url)
                
                if response.status_code == 200:
                    return response.content
                    
        except Exception as e:
            self.logger.error(f"Error generating image with Replicate: {str(e)}")
            return None

    def optimize_prompt_for_image(self, text_content: str) -> str:
        """Convert text content to optimized image generation prompt based on actual story"""
        try:
            # Use AI to analyze the content and extract visual elements
            return self.extract_visual_elements_with_ai(text_content)
        except:
            # Fallback to manual analysis
            return self.analyze_content_manually(text_content)
    
    def extract_visual_elements_with_ai(self, content: str) -> str:
        """Use AI to extract visual elements from story content"""
        from openai import OpenAI
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return self.analyze_content_manually(content)
        
        try:
            client = OpenAI(api_key=openai_api_key)
            
            prompt = f"""Analyze this social media content and create a detailed image generation prompt that would create a relevant, engaging image for it.

Content: {content}

Extract the key visual elements, setting, mood, and objects mentioned. Create an image prompt that would generate a picture that directly relates to and supports this content.

Focus on:
1. The actual setting/location mentioned
2. Objects, tools, or products referenced
3. The mood and atmosphere
4. People and their activities
5. Colors and visual style that would match

Return only the image generation prompt, no explanation. Make it detailed and specific to this content.
Example format: "realistic photo of [specific scene], [specific objects], [setting details], [mood/lighting], professional photography, high quality"
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at creating image generation prompts that perfectly match written content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            ai_prompt = response.choices[0].message.content.strip()
            
            # Clean and enhance the AI-generated prompt
            enhanced_prompt = f"{ai_prompt}, high quality, professional, detailed, beautiful lighting, no text, no watermark, 4k resolution"
            
            print(f"🤖 AI-generated image prompt: {enhanced_prompt[:100]}...")
            return enhanced_prompt
            
        except Exception as e:
            print(f"⚠️ AI prompt generation failed: {e}, using manual analysis")
            return self.analyze_content_manually(content)
    
    def analyze_content_manually(self, text_content: str) -> str:
        """Manually analyze content and create relevant image prompt"""
        clean_content = text_content.replace('#', '').replace('@', '').replace('https://', '').replace('http://', '').strip()
        content_lower = clean_content.lower()
        
        # Extract specific mentions and context
        visual_elements = []
        setting = "modern professional setting"
        objects = []
        activities = []
        
        # Detect settings/locations
        location_keywords = {
            'cafe': 'cozy coffee shop with laptop and coffee cup',
            'coffee shop': 'cozy coffee shop with laptop and coffee cup',
            'office': 'modern office workspace with computer',
            'workplace': 'professional office environment',
            'home': 'comfortable home workspace',
            'library': 'quiet library with books and study materials',
            'park': 'outdoor park setting with nature',
            'gym': 'modern fitness center with equipment',
            'school': 'educational classroom environment',
            'college': 'university campus setting',
            'garden': 'beautiful garden with plants and flowers',
            'beach': 'peaceful beach scene with ocean waves',
            'kitchen': 'modern kitchen workspace',
            'studio': 'creative studio workspace',
            'restaurant': 'elegant restaurant setting'
        }
        
        detected_location = None
        for location, description in location_keywords.items():
            if location in content_lower:
                detected_location = description
                break
        
        # Detect activities and objects
        activity_keywords = {
            'working': 'person working with laptop and documents',
            'studying': 'person studying with books and notes',
            'coding': 'person coding on computer with multiple screens',
            'writing': 'person writing with pen and notebook',
            'designing': 'person designing with creative tools',
            'meeting': 'professional meeting with people discussing',
            'presenting': 'person presenting to audience',
            'learning': 'person engaged in learning activities',
            'creating': 'person creating and building something',
            'planning': 'person planning with charts and diagrams'
        }
        
        detected_activity = None
        for activity, description in activity_keywords.items():
            if activity in content_lower:
                detected_activity = description
                break
        
        # Detect technology/tools mentioned
        tech_keywords = {
            'app': 'mobile phone with app interface',
            'website': 'computer screen showing website',
            'tool': 'digital tools and software interface',
            'software': 'computer with software application',
            'platform': 'digital platform interface',
            'system': 'organized digital system display',
            'solution': 'problem-solving visualization'
        }
        
        detected_tech = None
        for tech, description in tech_keywords.items():
            if tech in content_lower:
                detected_tech = description
                break
        
        # Build the image prompt
        if detected_location:
            base_scene = detected_location
        elif detected_activity:
            base_scene = detected_activity
        else:
            base_scene = "modern professional workspace"
        
        # Add technology elements if mentioned
        if detected_tech:
            base_scene += f", {detected_tech}"
        
        # Detect mood and style
        if any(word in content_lower for word in ['breakthrough', 'success', 'achievement', 'excited', 'amazing']):
            mood = "bright, optimistic lighting, success atmosphere"
        elif any(word in content_lower for word in ['challenge', 'problem', 'difficult', 'struggle']):
            mood = "focused, determined atmosphere, problem-solving environment"
        elif any(word in content_lower for word in ['peaceful', 'calm', 'relaxing', 'quiet']):
            mood = "calm, peaceful lighting, serene atmosphere"
        else:
            mood = "natural lighting, professional atmosphere"
        
        # Create final prompt
        final_prompt = f"realistic photo of {base_scene}, {mood}, professional photography, high quality, detailed, no text, no watermark"
        
        print(f"📝 Manual image prompt: {final_prompt[:100]}...")
        return final_prompt
    
    def generate_image(self, prompt: str, preferred_method: str = "pollinations") -> Optional[bytes]:
        """Generate image using the specified method with fallbacks"""
        methods = {
            "pollinations": self.generate_image_pollinations,
            "huggingface": self.generate_image_huggingface,
            "replicate": self.generate_image_replicate
        }
        
        # Try the preferred method first
        if preferred_method in methods:
            result = methods[preferred_method](prompt)
            if result:
                return result
        
        # Fallback to other methods
        for method_name, method_func in methods.items():
            if method_name != preferred_method:
                self.logger.info(f"Trying fallback method: {method_name}")
                result = method_func(prompt)
                if result:
                    return result
        
        # If all methods fail, return None
        self.logger.error("All image generation methods failed")
        return None
    
    def create_text_image(self, title: str, content: str) -> Optional[str]:
        """Create a simple text-based image as a last resort"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image
            width, height = 800, 800
            background_color = (255, 107, 107)  # Pinterest red
            text_color = (255, 255, 255)
            
            image = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(image)
            
            # Try to use a nice font, fall back to default
            try:
                font_title = ImageFont.truetype("arial.ttf", 48)
                font_content = ImageFont.truetype("arial.ttf", 24)
            except:
                font_title = ImageFont.load_default()
                font_content = ImageFont.load_default()
            
            # Add title
            title_lines = self.wrap_text(title, 15)
            y_offset = 100
            for line in title_lines:
                bbox = draw.textbbox((0, 0), line, font=font_title)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y_offset), line, font=font_title, fill=text_color)
                y_offset += 60
            
            # Add content
            content_lines = self.wrap_text(content[:200] + "...", 25)
            y_offset += 50
            for line in content_lines[:8]:  # Max 8 lines
                bbox = draw.textbbox((0, 0), line, font=font_content)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y_offset), line, font=font_content, fill=text_color)
                y_offset += 35
            
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"text_image_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            image.save(filepath)
            self.logger.info(f"Text image created: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating text image: {str(e)}")
            return None
    
    def wrap_text(self, text: str, max_chars: int) -> list:
        """Wrap text to fit within specified character limit per line"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def generate_human_image_for_story(self, story_content: str, scenario: str = None) -> Optional[bytes]:
        """Generate human images for specific story scenarios"""
        try:
            # First, try to create content-specific image without human scenarios
            content_based_image = self.generate_content_based_image(story_content)
            if content_based_image:
                return content_based_image
            
            # Fallback to scenario-based human images
            if not scenario:
                scenario = self.detect_scenario_from_content(story_content)
            
            # Create human-focused prompts based on scenario
            human_prompts = {
                "school": "realistic photo of a young student studying at school, sitting at desk with books, natural lighting, educational environment, happy expression, professional photography",
                "college": "realistic photo of college student in university campus, carrying backpack and books, walking between buildings, natural outdoor lighting, casual clothing, smiling",
                "workplace": "realistic photo of professional person in modern office, sitting at desk with computer, business casual attire, confident expression, clean office environment",
                "garden": "realistic photo of person in beautiful garden, tending to flowers and plants, natural outdoor lighting, peaceful expression, gardening tools nearby",
                "cafe": "realistic photo of person in cozy coffee shop, sitting at table with laptop and coffee, warm lighting, relaxed atmosphere, casual clothing",
                "library": "realistic photo of person reading in quiet library, surrounded by bookshelves, soft natural lighting, focused expression, scholarly atmosphere",
                "park": "realistic photo of person enjoying time in public park, sitting on bench or walking path, green trees and nature, sunny day, relaxed expression",
                "home": "realistic photo of person in comfortable home setting, natural indoor lighting, casual clothing, warm and inviting atmosphere",
                "gym": "realistic photo of person exercising in modern gym, workout clothes, determined expression, fitness equipment in background",
                "beach": "realistic photo of person walking on beach, ocean waves in background, natural sunlight, relaxed vacation mood, casual beach attire"
            }
            
            # Get the appropriate prompt
            base_prompt = human_prompts.get(scenario, human_prompts["workplace"])
            
            # Add quality enhancers
            quality_enhancers = "high quality, 4k, natural lighting, realistic, professional photography, detailed, no text, no watermark"
            
            # Create final prompt
            final_prompt = f"{base_prompt}, {quality_enhancers}"
            
            # Generate image using preferred method
            image_path = self.generate_image(final_prompt, preferred_method="pollinations")
            
            if image_path:
                self.logger.info(f"Generated human image for scenario: {scenario}")
                return image_path
            else:
                # Fallback to text-based image
                return self.create_scenario_text_image(scenario, story_content)
                
        except Exception as e:
            self.logger.error(f"Error generating human image: {str(e)}")
            return None
    
    def generate_content_based_image(self, content: str) -> Optional[bytes]:
        """Generate image directly based on content without human scenarios"""
        try:
            # Create a more specific prompt based on the actual content
            optimized_prompt = self.optimize_prompt_for_image(content)
            
            print(f"🎨 Generating image with prompt: {optimized_prompt[:100]}...")
            
            # Generate image using preferred method
            image_path = self.generate_image(optimized_prompt, preferred_method="pollinations")
            
            if image_path:
                self.logger.info(f"Generated content-based image successfully")
                return image_path
            else:
                self.logger.warning("Content-based image generation failed")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating content-based image: {str(e)}")
            return None

    def detect_scenario_from_content(self, content: str) -> str:
        """Detect scenario from story content"""
        content_lower = content.lower()
        
        scenario_keywords = {
            "school": ["school", "classroom", "student", "teacher", "homework", "study", "learning", "education"],
            "college": ["university", "college", "campus", "degree", "graduation", "dorm", "lecture", "professor"],
            "workplace": ["office", "work", "job", "career", "business", "meeting", "colleague", "professional"],
            "garden": ["garden", "flowers", "plants", "nature", "outdoor", "green", "growing", "bloom"],
            "cafe": ["coffee", "cafe", "latte", "barista", "espresso", "cappuccino", "coffee shop"],
            "library": ["library", "books", "reading", "quiet", "study", "research", "knowledge"],
            "park": ["park", "outdoor", "walking", "nature", "trees", "fresh air", "exercise"],
            "home": ["home", "house", "family", "comfortable", "cozy", "living room", "kitchen"],
            "gym": ["gym", "workout", "exercise", "fitness", "training", "health", "sports"],
            "beach": ["beach", "ocean", "waves", "sand", "vacation", "summer", "swimming"]
        }
        
        # Count matches for each scenario
        scenario_scores = {}
        for scenario, keywords in scenario_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            scenario_scores[scenario] = score
        
        # Return the scenario with highest score, default to workplace
        best_scenario = max(scenario_scores, key=scenario_scores.get)
        return best_scenario if scenario_scores[best_scenario] > 0 else "workplace"
    
    def create_scenario_text_image(self, scenario: str, content: str) -> Optional[str]:
        """Create text-based image for specific scenario"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Scenario-specific colors
            scenario_colors = {
                "school": (52, 152, 219),    # Blue
                "college": (155, 89, 182),   # Purple
                "workplace": (52, 73, 94),   # Dark blue
                "garden": (46, 125, 50),     # Green
                "cafe": (121, 85, 72),       # Brown
                "library": (69, 90, 100),    # Blue gray
                "park": (76, 175, 80),       # Light green
                "home": (255, 152, 0),       # Orange
                "gym": (244, 67, 54),        # Red
                "beach": (3, 169, 244)       # Light blue
            }
            
            # Create image
            width, height = 800, 800
            background_color = scenario_colors.get(scenario, (52, 73, 94))
            text_color = (255, 255, 255)
            
            image = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(image)
            
            # Add scenario title
            scenario_title = scenario.title() + " Story"
            
            # Try to use a nice font
            try:
                font_title = ImageFont.truetype("arial.ttf", 54)
                font_content = ImageFont.truetype("arial.ttf", 28)
            except:
                font_title = ImageFont.load_default()
                font_content = ImageFont.load_default()
            
            # Add title
            bbox = draw.textbbox((0, 0), scenario_title, font=font_title)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, 100), scenario_title, font=font_title, fill=text_color)
            
            # Add content preview
            content_preview = content[:300] + "..." if len(content) > 300 else content
            content_lines = self.wrap_text(content_preview, 30)
            
            y_offset = 200
            for line in content_lines[:10]:  # Max 10 lines
                bbox = draw.textbbox((0, 0), line, font=font_content)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y_offset), line, font=font_content, fill=text_color)
                y_offset += 40
            
            # Add scenario emoji/icon
            scenario_icons = {
                "school": "📚",
                "college": "🎓",
                "workplace": "💼",
                "garden": "🌺",
                "cafe": "☕",
                "library": "📖",
                "park": "🌳",
                "home": "🏠",
                "gym": "💪",
                "beach": "🏖️"
            }
            
            icon = scenario_icons.get(scenario, "📝")
            try:
                icon_font = ImageFont.truetype("seguiemj.ttf", 100)
                bbox = draw.textbbox((0, 0), icon, font=icon_font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, 600), icon, font=icon_font, fill=text_color)
            except:
                pass  # Skip emoji if font not available
            
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scenario_{scenario}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            image.save(filepath)
            self.logger.info(f"Scenario text image created: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating scenario text image: {str(e)}")
            return None
    
    def generate_platform_optimized_image(self, content: str, platform: str, scenario: str = None) -> Optional[str]:
        """Generate an image that is optimized for both the content and the target platform"""
        try:
            from core.content_generation.generator import ContentGenerator
            
            # First try content-based image generation
            content_based_path = self.generate_content_based_image(content)
            if content_based_path:
                return content_based_path
            
            # Get platform-specific style guidelines
            temp_generator = ContentGenerator(os.getenv("OPENAI_API_KEY", ""))
            platform_style = temp_generator.get_platform_visual_style(platform)
            
            # If no scenario provided, detect it from content
            if not scenario:
                scenario = self.detect_scenario_from_content(content)
            
            # Create platform-optimized prompt
            prompt_elements = [
                # Base scenario prompt
                self.get_scenario_prompt(scenario),
                
                # Platform-specific style elements
                f"Style: {platform_style['style']}",
                f"Color palette: {platform_style['color_scheme']}",
                f"Composition: {platform_style['composition']}",
                f"Mood: {platform_style['mood']}",
                
                # Quality enhancements
                "high quality, professional photography",
                "4k resolution, detailed",
                "no text, no watermark",
                "perfect lighting and composition"
            ]
            
            final_prompt = ", ".join(prompt_elements)
            
            # Generate image with the optimized prompt
            return self.generate_image(final_prompt)
            
        except Exception as e:
            self.logger.error(f"Error generating platform-optimized image: {str(e)}")
            return None

    def get_scenario_prompt(self, scenario: str) -> str:
        """Get base prompt for a specific scenario"""
        scenario_prompts = {
            "school": "realistic photo in educational setting, classroom or study environment, academic atmosphere",
            "college": "realistic photo on university campus, modern educational facilities, academic environment",
            "workplace": "realistic photo in professional office setting, modern workspace, business environment",
            "garden": "realistic photo in beautiful garden setting, natural environment, outdoor scenery",
            "cafe": "realistic photo in cozy cafe setting, warm lighting, coffee shop atmosphere",
            "library": "realistic photo in quiet library setting, books and study areas, peaceful environment",
            "park": "realistic photo in public park, natural outdoor setting, recreational environment",
            "home": "realistic photo in modern home setting, comfortable living space, residential environment",
            "gym": "realistic photo in modern fitness center, exercise equipment, active environment",
            "beach": "realistic photo at scenic beach location, ocean views, coastal environment",
            "restaurant": "realistic photo in upscale restaurant setting, dining atmosphere, culinary environment",
            "travel": "realistic photo in travel setting, tourism location, adventurous environment",
            "shopping": "realistic photo in retail environment, shopping center, commercial setting",
            "hospital": "realistic photo in healthcare setting, medical facility, professional environment",
            "airport": "realistic photo in modern airport terminal, travel hub, transportation setting",
            "hotel": "realistic photo in luxury hotel setting, hospitality environment, accommodation space",
            "museum": "realistic photo in cultural museum setting, exhibition space, artistic environment",
            "concert": "realistic photo at live event venue, performance space, entertainment setting",
            "wedding": "realistic photo at elegant wedding venue, ceremonial setting, celebration environment",
            "party": "realistic photo at social gathering, event space, celebratory environment"
        }
        
        return scenario_prompts.get(scenario, "realistic photo in professional modern setting, clean environment")
