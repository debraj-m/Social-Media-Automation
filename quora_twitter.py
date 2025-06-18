import os
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BlogPost:
    """Data class for blog post content"""
    original_content: str
    title: str = ""
    medium_content: str = ""
    twitter_content: str = ""
    quora_question: str = ""
    quora_answer: str = ""
    tags: List[str] = None

class AIContentGenerator:
    """OpenAI integration for content generation and adaptation"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def generate_title(self, content: str) -> str:
        """Generate an engaging title from content"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content marketing expert. Generate engaging, SEO-friendly titles."},
                    {"role": "user", "content": f"Generate a compelling title for this content:\n\n{content[:500]}..."}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip().strip('"')
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return "Untitled Post"
    
    def adapt_for_medium(self, content: str, title: str) -> str:
        """Adapt content for Medium's format"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Medium writer. Adapt content for Medium's audience with engaging formatting, subheadings, and storytelling elements."},
                    {"role": "user", "content": f"Title: {title}\n\nContent: {content}\n\nRewrite this for Medium with proper formatting, engaging introduction, and conclusion."}
                ],
                max_tokens=2000,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error adapting for Medium: {e}")
            return content
    
    def create_twitter_thread(self, content: str, title: str) -> List[str]:
        """Create Twitter thread from content"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Twitter content creator. Create an engaging Twitter thread. Each tweet should be under 280 characters. Return as numbered list."},
                    {"role": "user", "content": f"Create a Twitter thread from this content:\n\nTitle: {title}\nContent: {content[:1000]}..."}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            thread_text = response.choices[0].message.content.strip()
            # Split into individual tweets
            tweets = []
            for line in thread_text.split('\n'):
                if line.strip() and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.startswith('•')):
                    tweet = line.split('.', 1)[1].strip() if '.' in line else line.strip('• ')
                    if len(tweet) <= 280:
                        tweets.append(tweet)
            
            return tweets[:5]  # Limit to 5 tweets
        except Exception as e:
            logger.error(f"Error creating Twitter thread: {e}")
            return [content[:250] + "..."]
    
    def generate_quora_qa(self, content: str, title: str) -> tuple:
        """Generate Quora question and answer"""
        try:
            # Generate question
            q_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate a natural, searchable Quora question based on the content topic."},
                    {"role": "user", "content": f"Based on this content about '{title}', generate a Quora-style question:\n\n{content[:300]}..."}
                ],
                max_tokens=100,
                temperature=0.7
            )
            question = q_response.choices[0].message.content.strip().strip('"')
            
            # Generate answer
            a_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Quora expert answering questions. Provide detailed, helpful answers with examples and formatting."},
                    {"role": "user", "content": f"Question: {question}\n\nAnswer this question based on: {content}"}
                ],
                max_tokens=1500,
                temperature=0.6
            )
            answer = a_response.choices[0].message.content.strip()
            
            return question, answer
        except Exception as e:
            logger.error(f"Error generating Quora Q&A: {e}")
            return "How can I learn more about this topic?", content[:500]
    
    def generate_tags(self, content: str, title: str) -> List[str]:
        """Generate relevant tags for the content"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate 5-7 relevant tags/keywords for blog content. Return as comma-separated list."},
                    {"role": "user", "content": f"Title: {title}\nContent: {content[:500]}...\n\nGenerate tags:"}
                ],
                max_tokens=100,
                temperature=0.5
            )
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip() for tag in tags_text.split(',')]
            return tags[:7]  # Limit to 7 tags
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return ["blog", "content", "writing"]

class BlogAutomator:
    def __init__(self, headless=False, use_existing_profile=True):
        self.use_existing_profile = use_existing_profile
        self.setup_driver(headless, use_existing_profile)
        self.wait = WebDriverWait(self.driver, 20)
        self.ai_generator = AIContentGenerator()
        
    def setup_driver(self, headless, use_existing_profile=True):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        
        if use_existing_profile:
            # Use existing Chrome profile (where you're already logged in)
            # You can find your profile path by going to chrome://version/ in your browser
            user_data_dir = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data"
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument("--profile-directory=Default")  # or "Profile 1", "Profile 2" etc.
            
            # Additional options for profile mode
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-default-apps")
        
        if headless:
            chrome_options.add_argument("--headless")
            
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def prepare_content(self, original_content: str) -> BlogPost:
        """Use AI to prepare content for all platforms"""
        logger.info("Generating AI-adapted content...")
        
        post = BlogPost(original_content=original_content)
        
        # Generate title
        post.title = self.ai_generator.generate_title(original_content)
        logger.info(f"Generated title: {post.title}")
        
        # Generate tags
        post.tags = self.ai_generator.generate_tags(original_content, post.title)
        logger.info(f"Generated tags: {', '.join(post.tags)}")
        
        # Adapt for Medium
        post.medium_content = self.ai_generator.adapt_for_medium(original_content, post.title)
        
        # Create Twitter content
        twitter_tweets = self.ai_generator.create_twitter_thread(original_content, post.title)
        post.twitter_content = twitter_tweets[0] if twitter_tweets else original_content[:250]
        
        # Generate Quora Q&A
        post.quora_question, post.quora_answer = self.ai_generator.generate_quora_qa(original_content, post.title)
        
        return post
        
    def login_medium(self):
        """Login to Medium"""
        try:
            logger.info("Logging into Medium...")
            self.driver.get("https://medium.com/m/signin")
            time.sleep(3)
            
            # Click on Sign in with email
            email_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign in with email')]"))
            )
            email_btn.click()
            
            # Enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys(os.getenv('MEDIUM_EMAIL'))
            
            # Click continue
            continue_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
            continue_btn.click()
            
            # Enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(os.getenv('MEDIUM_PASSWORD'))
            
            # Click sign in
            signin_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
            signin_btn.click()
            
            time.sleep(5)
            logger.info("Medium login successful")
            return True
            
        except Exception as e:
            logger.error(f"Medium login failed: {str(e)}")
            return False
    
    def post_to_medium(self, blog_post: BlogPost):
        """Post article to Medium (assumes already logged in if using profile)"""
        try:
            logger.info("Posting to Medium...")
            
            # Go to write page
            self.driver.get("https://medium.com/new-story")
            time.sleep(5)
            
            # Check if we're logged in by looking for the write interface
            try:
                title_input = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//h1[@data-default-value='Title']"))
                )
            except TimeoutException:
                logger.warning("Not logged into Medium or need to accept terms")
                if not self.use_existing_profile:
                    return self.login_medium() and self.post_to_medium(blog_post)
                else:
                    logger.error("Please manually log into Medium in your browser first")
                    return False
            
            # Enter title
            title_input.click()
            title_input.clear()
            title_input.send_keys(blog_post.title)
            
            # Enter content
            content_area = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-default-value='Tell your story...']"))
            )
            content_area.click()
            content_area.send_keys(blog_post.medium_content)
            
            time.sleep(3)
            
            # Publish
            publish_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publish')]"))
            )
            publish_btn.click()
            
            time.sleep(3)
            
            # Add tags if available
            try:
                tags_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Add a tag...']")
                for tag in blog_post.tags[:5]:  # Medium allows up to 5 tags
                    tags_input.send_keys(tag)
                    tags_input.send_keys('\n')
                    time.sleep(1)
            except:
                logger.warning("Could not add tags to Medium post")
            
            # Final publish
            final_publish = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publish now')]"))
            )
            final_publish.click()
            
            logger.info("Medium post published successfully")
            return True
            
        except Exception as e:
            logger.error(f"Medium posting failed: {str(e)}")
            return False
    
    def login_twitter(self):
        """Login to Twitter/X"""
        try:
            logger.info("Logging into Twitter/X...")
            self.driver.get("https://twitter.com/login")
            time.sleep(3)
            
            # Enter username
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_input.send_keys(os.getenv('TWITTER_USERNAME'))
            
            # Click next
            next_btn = self.driver.find_element(By.XPATH, "//span[text()='Next']")
            next_btn.click()
            
            # Enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(os.getenv('TWITTER_PASSWORD'))
            
            # Click login
            login_btn = self.driver.find_element(By.XPATH, "//span[text()='Log in']")
            login_btn.click()
            
            time.sleep(5)
            logger.info("Twitter login successful")
            return True
            
        except Exception as e:
            logger.error(f"Twitter login failed: {str(e)}")
            return False
    
    def post_to_twitter(self, blog_post: BlogPost):
        """Post tweet to Twitter (assumes already logged in if using profile)"""
        try:
            logger.info("Posting to Twitter...")
            
            # Navigate to home
            self.driver.get("https://twitter.com/home")
            time.sleep(5)
            
            # Check if logged in by looking for compose tweet button
            try:
                tweet_box = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
                )
            except TimeoutException:
                logger.warning("Not logged into Twitter")
                if not self.use_existing_profile:
                    return self.login_twitter() and self.post_to_twitter(blog_post)
                else:
                    logger.error("Please manually log into Twitter in your browser first")
                    return False
            
            # Enter tweet content
            tweet_box.click()
            tweet_box.send_keys(blog_post.twitter_content)
            
            # Click tweet button
            tweet_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetButton']"))
            )
            tweet_btn.click()
            
            time.sleep(3)
            logger.info("Twitter post published successfully")
            return True
            
        except Exception as e:
            logger.error(f"Twitter posting failed: {str(e)}")
            return False
    
    def login_quora(self):
        """Login to Quora"""
        try:
            logger.info("Logging into Quora...")
            self.driver.get("https://www.quora.com/")
            time.sleep(3)
            
            # Click login
            login_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']"))
            )
            login_link.click()
            
            # Enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys(os.getenv('QUORA_EMAIL'))
            
            # Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(os.getenv('QUORA_PASSWORD'))
            
            # Click login button
            login_btn = self.driver.find_element(By.XPATH, "//input[@value='Login']")
            login_btn.click()
            
            time.sleep(5)
            logger.info("Quora login successful")
            return True
            
        except Exception as e:
            logger.error(f"Quora login failed: {str(e)}")
            return False
    
    def post_to_quora(self, blog_post: BlogPost):
        """Post answer to Quora (assumes already logged in if using profile)"""
        try:
            logger.info("Posting to Quora...")
            
            # Go to Quora home
            self.driver.get("https://www.quora.com/")
            time.sleep(5)
            
            # Check if logged in
            try:
                # Look for "Add Question" button which appears when logged in
                add_question_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add question')]")
            except NoSuchElementException:
                logger.warning("Not logged into Quora")
                if not self.use_existing_profile:
                    return self.login_quora() and self.post_to_quora(blog_post)
                else:
                    logger.error("Please manually log into Quora in your browser first")
                    return False
            
            # Go to ask question page
            self.driver.get("https://www.quora.com/qedit/ask")
            time.sleep(3)
            
            # Enter question
            question_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Start your question with \"What\", \"How\", \"Why\", etc.']"))
            )
            question_input.send_keys(blog_post.quora_question)
            
            # Click "Add Question" button
            add_question_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add question')]"))
            )
            add_question_btn.click()
            
            time.sleep(5)
            
            # Now answer the question
            answer_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Answer')]"))
            )
            answer_btn.click()
            
            # Enter answer
            answer_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            answer_box.send_keys(blog_post.quora_answer)
            
            # Submit answer
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
            )
            submit_btn.click()
            
            logger.info("Quora Q&A posted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Quora posting failed: {str(e)}")
            return False
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def validate_env_variables():
    """Validate that all required environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'MEDIUM_EMAIL', 'MEDIUM_PASSWORD',
        'TWITTER_USERNAME', 'TWITTER_PASSWORD', 
        'QUORA_EMAIL', 'QUORA_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def automate_ai_blog_posting(content: str, platforms: List[str] = None, use_existing_profile: bool = True):
    """
    Main function to automate AI-powered blog posting
    
    Args:
        content: The original blog content
        platforms: List of platforms to post to ['medium', 'twitter', 'quora']
        use_existing_profile: Whether to use existing Chrome profile (recommended)
    """
    
    if not validate_env_variables():
        logger.error("Environment validation failed. Please check your .env file.")
        return
    
    if platforms is None:
        platforms = ['medium', 'twitter', 'quora']
    
    # Initialize automator with profile option
    automator = BlogAutomator(headless=False, use_existing_profile=use_existing_profile)
    
    try:
        # Generate AI-adapted content
        blog_post = automator.prepare_content(content)
        
        logger.info(f"Content prepared for platforms: {', '.join(platforms)}")
        
        if use_existing_profile:
            logger.info("🌐 Using existing Chrome profile - make sure you're logged into your accounts!")
            input("Press Enter after confirming you're logged into your accounts in Chrome...")
        
        # Post to Medium
        if 'medium' in platforms:
            if use_existing_profile or automator.login_medium():
                automator.post_to_medium(blog_post)
                time.sleep(5)  # Delay between platforms
        
        # Post to Twitter
        if 'twitter' in platforms:
            if use_existing_profile or automator.login_twitter():
                automator.post_to_twitter(blog_post)
                time.sleep(5)
        
        # Post to Quora
        if 'quora' in platforms:
            if use_existing_profile or automator.login_quora():
                automator.post_to_quora(blog_post)
        
        logger.info("Automation completed successfully!")
        
    except Exception as e:
        logger.error(f"Automation failed: {str(e)}")
    
    finally:
        automator.close()

# Example usage
if __name__ == "__main__":
    # Sample blog content
    sample_content = """
    The rise of artificial intelligence in content creation is transforming how businesses approach digital marketing. 
    With AI tools becoming more sophisticated, content creators can now automate repetitive tasks while focusing on 
    strategy and creativity.
    
    Key benefits include faster content generation, better SEO optimization, and personalized content at scale. 
    However, the human touch remains crucial for emotional resonance and brand authenticity.
    
    As we look toward the future, the most successful content strategies will combine AI efficiency with human creativity, 
    creating content that is both scalable and meaningful.
    """
    
    print("AI-Powered Blog Automation")
    print("=" * 30)
    print("\nMake sure your .env file contains:")
    print("OPENAI_API_KEY=your_openai_key")
    print("MEDIUM_EMAIL=your_email")
    print("MEDIUM_PASSWORD=your_password")
    print("TWITTER_USERNAME=your_username")
    print("TWITTER_PASSWORD=your_password")
    print("QUORA_EMAIL=your_email")
    print("QUORA_PASSWORD=your_password")
    
    # Check if .env file exists and has credentials
    if os.path.exists('.env'):
        print("\n✅ .env file found!")
        
        # Ask user what they want to do
        print("\nOptions:")
        print("1. Test with sample content")
        print("2. Enter custom content")
        print("3. Show setup instructions only")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting automation with sample content...")
            print("Platforms: Twitter and Medium")
            print("Mode: Using existing Chrome profile (recommended)")
            automate_ai_blog_posting(sample_content, ['twitter', 'medium'], use_existing_profile=True)
            
        elif choice == "2":
            print("\nEnter your blog content (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "" and len(lines) > 0 and lines[-1] == "":
                    break
                lines.append(line)
            
            custom_content = '\n'.join(lines[:-1])  # Remove last empty line
            
            if custom_content.strip():
                platforms = input("\nEnter platforms (comma-separated) [medium,twitter,quora]: ").strip()
                if not platforms:
                    platforms = "medium,twitter,quora"
                platform_list = [p.strip() for p in platforms.split(',')]
                
                profile_choice = input("\nUse existing Chrome profile? (Y/n): ").strip().lower()
                use_profile = profile_choice != 'n'
                
                print(f"\n🚀 Starting automation with custom content...")
                print(f"Platforms: {', '.join(platform_list)}")
                print(f"Mode: {'Existing Chrome profile' if use_profile else 'Fresh login'}")
                automate_ai_blog_posting(custom_content, platform_list, use_existing_profile=use_profile)
            else:
                print("❌ No content provided!")
                
        else:
            print("\n📋 Setup Instructions:")
            print("1. Create .env file with your credentials")
            print("2. Run the script again")
            print("3. Choose option 1 or 2 to start automation")
    else:
        print("\n❌ .env file not found!")
        print("Please create a .env file in the same directory with your credentials.")
        print("\nExample .env file content:")
        print("OPENAI_API_KEY=sk-your_key_here")
        print("MEDIUM_EMAIL=your_email@example.com")
        print("MEDIUM_PASSWORD=your_password")
        print("TWITTER_USERNAME=your_username")
        print("TWITTER_PASSWORD=your_password")  
        print("QUORA_EMAIL=your_email@example.com")
        print("QUORA_PASSWORD=your_password")