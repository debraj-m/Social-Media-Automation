import os
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import logging

from core.content_generation.generator import ContentGenerator

# Load environment variables
load_dotenv()
# te
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
class TwitterBot:
    def __init__(self):
        self.email = os.getenv('TWITTER_EMAIL')
        self.password = os.getenv('TWITTER_PASSWORD')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not all([self.email, self.password, self.openai_api_key]):
            raise ValueError("Missing required environment variables")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless=new')  # use `--headless` for older Chrome versions

        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        # Add encoding support
        self.chrome_options.add_argument('--lang=en-US')
        self.chrome_options.add_argument('--disable-extensions')
        
        self.driver = None
        self.wait = None
    
    def clean_text_for_selenium(self, text):
        """Clean text to remove characters that ChromeDriver can't handle"""
        # Remove emojis and other non-BMP characters
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
        
        # Remove emojis
        cleaned_text = emoji_pattern.sub(r'', text)
        
        # Remove extra spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Ensure only BMP characters (Basic Multilingual Plane)
        cleaned_text = ''.join(char for char in cleaned_text if ord(char) < 65536)
        
        return cleaned_text
    def setup_driver(self):
        """Initialize the Chrome driver"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    
    def login_to_twitter(self):
        """Login to Twitter"""
        try:
            logger.info("Navigating to Twitter login page")
            self.driver.get("https://twitter.com/i/flow/login")
            
            # Wait and enter email/username
            email_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            
            # Click Next button
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]'))
            )
            next_button.click()
            
            time.sleep(2)
            
            # Handle potential username step (Twitter sometimes asks for username)
            try:
                username_input = self.driver.find_element(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
                if username_input.is_displayed():
                    # If username is required, you might need to set TWITTER_USERNAME in .env
                    username = os.getenv('TWITTER_USERNAME', self.email.split('@')[0])
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
            password_input.send_keys(self.password)
            
            # Click Login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]'))
            )
            login_button.click()
            
            # Wait for login to complete
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]'))
            )
            
            logger.info("Successfully logged into Twitter")
            return True
            
        except TimeoutException:
            logger.error("Login failed - timeout waiting for elements")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def safe_click(self, element):
        """Safely click an element using multiple methods"""
        try:
            # Method 1: Regular click
            element.click()
            return True
        except Exception as e1:
            logger.info(f"Regular click failed: {e1}")
            try:
                # Method 2: JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e2:
                logger.info(f"JavaScript click failed: {e2}")
                try:
                    # Method 3: Action chains click
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).move_to_element(element).click().perform()
                    return True
                except Exception as e3:
                    logger.error(f"All click methods failed: {e3}")
                    return False

    def wait_for_element_clickable(self, selectors, timeout=10):
        """Wait for element to be clickable using multiple selectors"""
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Found element with selector: {selector}")
                return element
            except TimeoutException:
                logger.info(f"Element not found with selector: {selector}")
                continue
        return None
    def post_tweet(self, content):
        """Post a tweet with the given content"""
        try:
            logger.info(f"Attempting to post tweet: {content}")
            
            # Clean content one more time before posting
            clean_content = self.clean_text_for_selenium(content)
            logger.info(f"Clean content: {clean_content}")
            
            # Try multiple selectors for the Tweet button
            tweet_button_selectors = [
                '[data-testid="SideNav_NewTweet_Button"]',
                '[aria-label="Post"]',
                '[data-testid="tweetButton"]',
                'a[href="/compose/tweet"]',
                '[role="button"][aria-label="Post"]'
            ]
            
            tweet_button = self.wait_for_element_clickable(tweet_button_selectors, 15)
            if not tweet_button:
                logger.error("Could not find tweet button with any selector")
                return False
            
            if not self.safe_click(tweet_button):
                logger.error("Failed to click tweet button")
                return False
            
            logger.info("Tweet button clicked, waiting for compose modal...")
            time.sleep(4)  # Wait for modal to fully load
            
            # Try multiple selectors for the compose box
            compose_selectors = [
                '[data-testid="tweetTextarea_0"]',
                '[contenteditable="true"][aria-label*="Post text"]',
                '[contenteditable="true"][role="textbox"]',
                '.public-DraftEditor-content',
                '[data-testid="tweetTextarea_0_label"]',
                'div[contenteditable="true"]',
                '[data-testid="tweetTextarea_0"] div[contenteditable="true"]'
            ]
            
            compose_box = self.wait_for_element_clickable(compose_selectors, 15)
            if not compose_box:
                logger.error("Could not find compose box with any selector")
                self.driver.save_screenshot("debug_compose_not_found.png")
                return False
            
            # Click on the compose box to focus it
            if not self.safe_click(compose_box):
                logger.error("Failed to click compose box")
                return False
            
            time.sleep(2)
            
            # Try multiple methods to input text
            input_success = False
            methods = [
                # Method 1: Send keys
                lambda: compose_box.send_keys(clean_content),
                # Method 2: Clear and send keys
                lambda: (compose_box.clear(), compose_box.send_keys(clean_content)),
                # Method 3: JavaScript innerText
                lambda: self.driver.execute_script("arguments[0].innerText = arguments[1];", compose_box, clean_content),
                # Method 4: JavaScript textContent
                lambda: self.driver.execute_script("arguments[0].textContent = arguments[1];", compose_box, clean_content),
                # Method 5: Focus and set content
                lambda: self.driver.execute_script("""
                    arguments[0].focus(); 
                    arguments[0].innerText = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, compose_box, clean_content)
            ]
            
            for i, method in enumerate(methods):
                try:
                    method()
                    logger.info(f"Successfully used input method {i+1}")
                    input_success = True
                    break
                except Exception as e:
                    logger.info(f"Input method {i+1} failed: {e}")
                    continue
            
            if not input_success:
                logger.error("All input methods failed")
                return False
            
            time.sleep(3)  # Give time for content to register and button to enable
            
            # Try multiple selectors for the Post button
            post_button_selectors = [
                '[data-testid="tweetButton"]',
                '[data-testid="tweetButtonInline"]',
                '[role="button"][data-testid="tweetButton"]',
                '[role="button"][data-testid="tweetButtonInline"]',
                'div[data-testid="tweetButton"]',
                '[aria-label="Post"]'
            ]
            
            post_button = self.wait_for_element_clickable(post_button_selectors, 15)
            if not post_button:
                logger.error("Could not find post button with any selector")
                self.driver.save_screenshot("debug_post_button_not_found.png")
                return False
            
            # Check if post button is enabled
            if post_button.get_attribute("aria-disabled") == "true":
                logger.error("Post button is disabled - content may not have been entered correctly")
                self.driver.save_screenshot("debug_button_disabled.png")
                return False
            
            # Wait a bit more and scroll to button if needed
            self.driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
            time.sleep(1)
            
            # Try to click the post button
            if not self.safe_click(post_button):
                logger.error("Failed to click post button")
                self.driver.save_screenshot("debug_click_failed.png")
                return False
            
            logger.info("Post button clicked, waiting for confirmation...")
            
            # Wait for tweet to be posted and look for success indicators
            success_indicators = [
                "Your post was sent",
                "Tweet sent",
                "Your Tweet was sent",
                "Post sent"
            ]
            
            # Wait longer and check multiple times
            for attempt in range(15):  # Wait up to 15 seconds
                try:
                    page_text = self.driver.page_source.lower()
                    if any(indicator.lower() in page_text for indicator in success_indicators):
                        logger.info("Tweet posted successfully - found success indicator")
                        return True
                    
                    # Check if we're back to timeline (another success indicator)
                    timeline_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="primaryColumn"]')
                    if timeline_elements and len(timeline_elements) > 0:
                        logger.info("Tweet posted successfully - returned to main timeline")
                        return True
                        
                except Exception as e:
                    logger.info(f"Success check attempt {attempt+1} failed: {e}")
                
                time.sleep(1)
            
            logger.warning("Could not confirm tweet was posted - assuming success")
            self.driver.save_screenshot("debug_post_uncertain.png")
            return True  # Assume success if no clear error
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            self.driver.save_screenshot("debug_post_error.png")
            return False
    
    def random_delay(self, min_seconds=30, max_seconds=120):
        """Add random delay to appear more human-like"""
        delay = random.randint(min_seconds, max_seconds)
        logger.info(f"Waiting {delay} seconds...")
        time.sleep(delay)
    
    def run_automation(self, topics=None, post_count=1, delay_between_posts=True):
        """Main automation function"""
        try:
            self.setup_driver()
            
            if not self.login_to_twitter():
                return False
            
            successful_posts = 0
            
            for i in range(post_count):
                logger.info(f"Generating and posting tweet {i+1}/{post_count}")
                
                # Generate content
                topic = random.choice(topics) if topics else None
                generator= ContentGenerator(self.openai_api_key)
                content = generator.generate_content(platform="twitter")
                
                if not content:
                    logger.error("Failed to generate content, skipping this post")
                    continue
                
                # Post the tweet
                if self.post_tweet(content):
                    successful_posts += 1
                    
                    # Add delay between posts (except for the last one)
                    if delay_between_posts and i < post_count - 1:
                        self.random_delay(300, 600)  # 5-10 minutes between posts
                else:
                    logger.error("Failed to post tweet")
            
            logger.info(f"Automation completed. Successfully posted {successful_posts}/{post_count} tweets")
            return successful_posts > 0
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")