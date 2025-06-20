import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import openai
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI()

class MediumAutomation:
    def __init__(self):
        self.load_environment_variables()
        self.setup_driver()
        
    def load_environment_variables(self):
        """Load and validate required environment variables"""
        load_dotenv()
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.x_username = os.getenv('TWITTER_USERNAME')
        self.x_password = os.getenv('TWITTER_PASSWORD')
        self.x_email = os.getenv('TWITTER_EMAIL')
        
        missing_vars = []
        if not self.openai_api_key:
            missing_vars.append("OPENAI_API_KEY")
        if not self.x_username:
            missing_vars.append("TWITTER_USERNAME")
        if not self.x_password:
            missing_vars.append("TWITTER_PASSWORD")
        if not self.x_email:
            missing_vars.append("TWITTER_EMAIL")
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        openai.api_key = self.openai_api_key
    
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        
        # Common options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable notifications and images
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 20)
            self.actions = ActionChains(self.driver)
            logger.info("✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Chrome WebDriver: {e}")
            raise
    
    def dismiss_cookie_banner(self):
        """Try to dismiss cookie banners if present"""
        try:
            cookie_buttons = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Got it')]",
                "//button[@id='onetrust-accept-btn-handler']"
            ]
            self.click_element_with_retry(cookie_buttons, "Cookie banner", timeout=5)
        except:
            pass
    
    def click_element_with_retry(self, xpaths, element_name, timeout=10):
        """Try multiple selectors to click an element"""
        for xpath in xpaths:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"✅ Clicked {element_name}")
                time.sleep(2)
                return True
            except:
                continue
        raise Exception(f"Could not find {element_name}")
    
    def login_to_twitter(self):
        """Login to Twitter/X with improved reliability"""
        try:
            logger.info("Navigating to Twitter login page")
            self.driver.get("https://twitter.com/i/flow/login")
            
            # Wait and enter email/username
            email_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            email_input.clear()
            email_input.send_keys(self.x_email)
            
            # Click Next button
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]'))
            )
            next_button.click()
            
            time.sleep(2)
            
            # Handle potential username step
            try:
                username_input = self.driver.find_element(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
                if username_input.is_displayed():
                    username = self.x_username if '@' not in self.x_username else self.x_username.split('@')[0]
                    username_input.send_keys(username)
                    
                    next_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]'))
                    )
                    next_button.click()
                    time.sleep(2)
            except NoSuchElementException:
                pass
            
            # Enter password
            password_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_input.clear()
            password_input.send_keys(self.x_password)
            
            # Click Login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]'))
            )
            login_button.click()
            
            # Wait for login to complete
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))
            )
            
            logger.info("✅ Successfully logged into Twitter/X")
            return True
            
        except TimeoutException:
            logger.error("❌ Login failed - timeout waiting for elements")
            self.take_screenshot("twitter_login_error")
            return False
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            self.take_screenshot("twitter_login_error")
            return False
    
    def login_to_medium_via_x(self):
        """Login to Medium using X (Twitter) credentials"""
        try:
            logger.info("🌐 Navigating to Medium...")
            self.driver.get("https://medium.com")
            time.sleep(3)
            
            # Dismiss cookie banner
            self.dismiss_cookie_banner()
            
            # Click Sign In button
            logger.info("🔍 Looking for Sign In button...")
            self.click_element_with_retry([
                "//a[contains(@href, '/signin')]",
                "//button[contains(text(), 'Sign in')]",
                "//a[contains(text(), 'Sign in')]",
                "//*[contains(text(), 'Get started')]"
            ], "Sign In button")
            
            time.sleep(3)
            
            # Click Sign in with X button
            logger.info("🔍 Looking for X login button...")
            self.click_element_with_retry([
                "//button[.//span[contains(text(), 'Sign in with X')]]",
                "//button[contains(., 'Sign in with X')]",
                "//button[@data-action='sign-in-with-x']",
                "//button[contains(@aria-label, 'Sign in with X')]",
                "//*[contains(text(), 'Sign in with X')]"
            ], "X login button")
            
            time.sleep(3)
            
            # Switch to Twitter login
            logger.info("🔐 Attempting Twitter/X login...")
            if not self.login_to_twitter():
                raise Exception("Twitter login failed")
            
            # Handle authorization if needed
            try:
                authorize_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@value='Authorize app']"))
                )
                authorize_btn.click()
                time.sleep(3)
            except:
                logger.info("ℹ️ No authorization needed")
            
            # Verify we're back on Medium
            if "medium.com" in self.driver.current_url.lower():
                logger.info("✅ Successfully logged into Medium via X!")
                return True
            
            logger.error(f"❌ Login may have failed. Current URL: {self.driver.current_url}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error during Medium login: {e}")
            self.take_screenshot("medium_login_error")
            return False
    
    def generate_content(self, topic, keywords=None, model="gpt-3.5-turbo"):
        """Generate blog content using OpenAI"""
        try:
            prompt = f"""
            Write a comprehensive, engaging blog post about: {topic}
            
            Requirements:
            - Write in a conversational, professional tone
            - Include an engaging introduction and compelling conclusion
            - Use markdown formatting with headings (##), subheadings (###)
            - Include bullet points or numbered lists where appropriate
            - Add a call-to-action in the conclusion
            - Target length: 800-1200 words
            """
            
            if keywords:
                prompt += f"\nInclude these keywords naturally (2-3 times each): {', '.join(keywords)}"
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional blog writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Generate title
            title_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Generate catchy, SEO-friendly blog titles."},
                    {"role": "user", "content": f"Create 3 title options for a blog post about: {topic}"}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            titles = title_response.choices[0].message.content.split('\n')
            title = titles[0].strip('"').replace('Title: ', '').replace('Option 1: ', '')
            
            return {
                'title': title,
                'content': content,
                'topic': topic,
                'word_count': len(content.split())
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating content: {e}")
            return None
    
    def post_to_medium(self, title, content):
        """Publish content to Medium"""
        try:
            logger.info("📝 Starting publishing process...")
            self.driver.get("https://medium.com/new-story")
            time.sleep(5)
            
            # Add title
            logger.info("✏️ Adding title...")
            title_field = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//h1[@data-testid='storyTitle']"))
            )
            title_field.click()
            self.actions.send_keys(title).perform()
            time.sleep(1)
            
            # Add content
            logger.info("📖 Adding content...")
            content_field = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='storyContent']"))
            )
            content_field.click()
            
            # Split and add content with proper formatting
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for i, paragraph in enumerate(paragraphs):
                if paragraph.startswith('##'):
                    # Handle headings
                    self.actions.send_keys(Keys.ENTER + paragraph + Keys.ENTER).perform()
                else:
                    self.actions.send_keys(paragraph).perform()
                
                if i < len(paragraphs) - 1:
                    self.actions.send_keys(Keys.ENTER + Keys.ENTER).perform()
                time.sleep(0.3)
            
            # Publish the post
            logger.info("🚀 Publishing post...")
            self.click_element_with_retry([
                "//button[contains(text(), 'Publish')]",
                "//button[@data-testid='publishButton']"
            ], "Publish button")
            
            # Handle publish modal
            time.sleep(2)
            self.click_element_with_retry([
                "//button[contains(text(), 'Publish now')]",
                "//button[contains(text(), 'Publish story')]"
            ], "Final publish button")
            
            logger.info("✅ Post published successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publishing post: {e}")
            self.take_screenshot("publish_error")
            return False
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved as {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Could not take screenshot: {e}")
    
    def run_automation(self, topic, keywords=None, model="gpt-3.5-turbo"):
        """Run complete automation workflow"""
        try:
            logger.info(f"\n🚀 Starting automation for topic: {topic}")
            
            # Generate content
            logger.info("\n🖊️ Generating content...")
            content = self.generate_content(topic, keywords, model)
            if not content:
                raise Exception("Failed to generate content")
                
            logger.info(f"📝 Generated: {content['title']} ({content['word_count']} words)")
            
            # Login and post
            logger.info("\n🔐 Logging into Medium via X...")
            if not self.login_to_medium_via_x():
                raise Exception("Login failed")
                
            logger.info("\n📤 Publishing post...")
            if not self.post_to_medium(content['title'], content['content']):
                raise Exception("Publishing failed")
                
            logger.info("\n🎉 Automation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"\n❌ Automation failed: {e}")
            return False
            
        finally:
            logger.info("\n🧹 Cleaning up...")
            time.sleep(5)
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    try:
        automation = MediumAutomation()
        
        blog_topic = "The Future of AI in Web Development"
        keywords = ["AI", "web development", "automation", "JavaScript"]
        
        success = automation.run_automation(
            topic=blog_topic,
            keywords=keywords,
            model="gpt-3.5-turbo"
        )
        
        if success:
            logger.info("✅ Blog post published successfully!")
        else:
            logger.error("❌ Failed to publish blog post")
            
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")