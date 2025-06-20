import time
import os
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

# Load environment variables
load_dotenv()

class QuoraAutomation:
    def __init__(self, headless=False):
        """Initialize the Quora automation bot"""
        self.driver = None
        self.wait = None
        self.setup_driver(headless)
    
    def setup_driver(self, headless=False):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Add common options for better stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Set user agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.maximize_window()
            print("✓ Chrome driver initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing driver: {e}")
            raise
    
    def login_to_quora(self, email, password):
        """Login to Quora using email and password"""
        try:
            print("Navigating to Quora...")
            self.driver.get("https://www.quora.com/")
            time.sleep(5)
            
            print(f"Current URL: {self.driver.current_url}")
            
            # Handle potential cookie banner
            try:
                cookie_selectors = [
                    "//button[contains(text(), 'Accept')]",
                    "//button[contains(text(), 'Got it')]",
                    "//button[contains(text(), 'Allow')]",
                    "//div[contains(@class, 'cookie')]//button"
                ]
                
                for selector in cookie_selectors:
                    try:
                        cookie_btn = self.driver.find_element(By.XPATH, selector)
                        cookie_btn.click()
                        print("✓ Clicked cookie banner")
                        time.sleep(2)
                        break
                    except NoSuchElementException:
                        continue
            except Exception as e:
                print(f"No cookie banner found: {e}")
            
            # Try multiple approaches for login
            login_attempts = [
                self._try_login_method_1,
                self._try_login_method_2,
                self._try_login_method_3
            ]
            
            for i, login_method in enumerate(login_attempts, 1):
                print(f"\n--- Trying login method {i} ---")
                try:
                    if login_method(email, password):
                        return True
                except Exception as e:
                    print(f"Login method {i} failed: {e}")
                    continue
            
            print("✗ All login methods failed")
            return False
                
        except Exception as e:
            print(f"✗ Error during login: {e}")
            return False
    
    def _try_login_method_1(self, email, password):
        """Login method 1: Direct navigation to login page"""
        print("Method 1: Direct login page navigation")
        
        self.driver.get("https://www.quora.com/login")
        time.sleep(5)
        
        # Look for email field
        email_field = self._find_email_field()
        if not email_field:
            return False
        
        # Look for password field
        password_field = self._find_password_field()
        if not password_field:
            return False
        
        # Fill credentials
        email_field.clear()
        email_field.send_keys(email)
        print("✓ Entered email")
        
        password_field.clear()
        password_field.send_keys(password)
        print("✓ Entered password")
        
        # Submit form
        return self._submit_login_form(password_field)
    
    def _try_login_method_2(self, email, password):
        """Login method 2: Click login button from homepage"""
        print("Method 2: Homepage login button")
        
        self.driver.get("https://www.quora.com/")
        time.sleep(3)
        
        # Look for login button on homepage
        login_selectors = [
            "//button[contains(text(), 'Login') or contains(text(), 'Log in')]",
            "//a[contains(text(), 'Login') or contains(text(), 'Log in')]",
            "//div[contains(text(), 'Login') or contains(text(), 'Log in')]",
            "//span[contains(text(), 'Login') or contains(text(), 'Log in')]",
            "//button[contains(@class, 'login')]",
            "//a[contains(@href, 'login')]"
        ]
        
        login_btn = None
        for selector in login_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        login_btn = element
                        break
                if login_btn:
                    break
            except Exception:
                continue
        
        if not login_btn:
            print("✗ Could not find login button on homepage")
            return False
        
        # Click login button
        self.driver.execute_script("arguments[0].click();", login_btn)
        print("✓ Clicked login button")
        time.sleep(3)
        
        # Now try to fill login form
        email_field = self._find_email_field()
        password_field = self._find_password_field()
        
        if not email_field or not password_field:
            print("✗ Could not find login fields after clicking login button")
            return False
        
        # Fill credentials
        email_field.clear()
        email_field.send_keys(email)
        print("✓ Entered email")
        
        password_field.clear()
        password_field.send_keys(password)
        print("✓ Entered password")
        
        return self._submit_login_form(password_field)
    
    def _try_login_method_3(self, email, password):
        """Login method 3: Try Google login approach"""
        print("Method 3: Alternative selectors")
        
        self.driver.get("https://www.quora.com/")
        time.sleep(3)
        
        # Try clicking on sign in areas
        signin_areas = [
            "//div[contains(@class, 'signin')]",
            "//div[contains(@class, 'auth')]",
            "//nav//button",
            "//header//button"
        ]
        
        for selector in signin_areas:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    text = element.get_attribute('textContent') or element.text
                    if any(word in text.lower() for word in ['login', 'sign in', 'log in']):
                        element.click()
                        print(f"✓ Clicked signin area: {text[:50]}...")
                        time.sleep(3)
                        break
            except Exception:
                continue
        
        # Try to find and fill login form
        email_field = self._find_email_field()
        password_field = self._find_password_field()
        
        if email_field and password_field:
            email_field.clear()
            email_field.send_keys(email)
            print("✓ Entered email")
            
            password_field.clear()
            password_field.send_keys(password)
            print("✓ Entered password")
            
            return self._submit_login_form(password_field)
        
        return False
    
    def _find_email_field(self):
        """Find email input field with multiple selectors"""
        email_selectors = [
            "//input[@type='email']",
            "//input[@name='email']",
            "//input[@id='email']",
            "//input[@placeholder*='email' or @placeholder*='Email']",
            "//input[contains(@class, 'email')]",
            "//input[contains(@autocomplete, 'email')]",
            "//form//input[1]"  # Often first input in login form
        ]
        
        for selector in email_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found email field with selector: {selector}")
                        return element
            except Exception:
                continue
        
        print("✗ Could not find email field")
        return None
    
    def _find_password_field(self):
        """Find password input field with multiple selectors"""
        password_selectors = [
            "//input[@type='password']",
            "//input[@name='password']",
            "//input[@id='password']",
            "//input[@placeholder*='password' or @placeholder*='Password']",
            "//input[contains(@class, 'password')]",
            "//input[contains(@autocomplete, 'password')]"
        ]
        
        for selector in password_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"✓ Found password field with selector: {selector}")
                        return element
            except Exception:
                continue
        
        print("✗ Could not find password field")
        return None
    
    def _submit_login_form(self, password_field):
        """Submit the login form using multiple methods"""
        # Try multiple submit methods
        submit_methods = [
            self._click_submit_button,
            lambda: password_field.send_keys(Keys.RETURN),
            lambda: password_field.send_keys(Keys.ENTER),
            self._submit_form_directly
        ]
        
        for i, method in enumerate(submit_methods, 1):
            try:
                print(f"Trying submit method {i}...")
                method()
                time.sleep(5)
                
                # Check if login was successful
                if self.check_login_success():
                    print("✓ Successfully logged in to Quora")
                    return True
                else:
                    print(f"Submit method {i} didn't work, trying next...")
                    
            except Exception as e:
                print(f"Submit method {i} failed: {e}")
                continue
        
        return False
    
    def _click_submit_button(self):
        """Try to find and click submit button"""
        submit_selectors = [
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(), 'Login') or contains(text(), 'Log in')]",
            "//button[contains(text(), 'Sign in')]",
            "//form//button[last()]",  # Last button in form
            "//button[contains(@class, 'submit')]"
        ]
        
        for selector in submit_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        self.driver.execute_script("arguments[0].click();", element)
                        print(f"✓ Clicked submit button with selector: {selector}")
                        return
            except Exception:
                continue
        
        raise Exception("Could not find submit button")
    
    def _submit_form_directly(self):
        """Submit form using JavaScript"""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if forms:
                self.driver.execute_script("arguments[0].submit();", forms[0])
                print("✓ Submitted form directly")
            else:
                raise Exception("No forms found")
        except Exception as e:
            raise Exception(f"Direct form submission failed: {e}")
    
    def check_login_success(self):
        """Check if login was successful with comprehensive checks"""
        try:
            print("Checking login status...")
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")
            
            # Check URL patterns that indicate successful login
            success_url_patterns = [
                'quora.com/',
                'quora.com/following',
                'quora.com/answer',
                'quora.com/home'
            ]
            
            # Check if we're NOT on login page
            if not any(pattern in current_url for pattern in ['login', 'signin', 'auth']):
                print("✓ Not on login page anymore")
                
                # Look for elements that indicate successful login
                success_indicators = [
                    # Profile/user elements
                    "//div[contains(@class, 'profile')]",
                    "//img[contains(@class, 'profile_photo')]",
                    "//a[contains(@href, '/profile/')]",
                    
                    # Navigation elements
                    "//div[contains(@class, 'nav_item_text') and (contains(text(), 'Home') or contains(text(), 'Answer'))]",
                    "//a[contains(text(), 'Home')]",
                    "//a[contains(text(), 'Following')]",
                    "//a[contains(text(), 'Answer')]",
                    
                    # Action elements
                    "//button[contains(text(), 'Add question')]",
                    "//div[contains(text(), 'Add question')]",
                    "//a[contains(text(), 'Write')]",
                    
                    # User-specific elements
                    "//div[contains(@class, 'user')]",
                    "//div[contains(@class, 'logged')]",
                    
                    # Search and main content
                    "//input[contains(@placeholder, 'Search')]",
                    "//div[contains(@class, 'feed')]"
                ]
                
                found_indicators = []
                for indicator in success_indicators:
                    try:
                        elements = self.driver.find_elements(By.XPATH, indicator)
                        if elements:
                            for element in elements:
                                if element.is_displayed():
                                    found_indicators.append(indicator)
                                    break
                    except Exception:
                        continue
                
                print(f"Found {len(found_indicators)} login success indicators")
                
                if found_indicators:
                    print("✓ Login appears successful based on page elements")
                    return True
                else:
                    # Additional check: look for any sign of being logged in
                    page_source = self.driver.page_source.lower()
                    login_keywords = ['profile', 'following', 'logout', 'settings', 'notifications']
                    
                    found_keywords = [keyword for keyword in login_keywords if keyword in page_source]
                    if found_keywords:
                        print(f"✓ Login success confirmed by keywords: {found_keywords}")
                        return True
            
            # Check for error messages
            error_selectors = [
                "//div[contains(@class, 'error')]",
                "//div[contains(text(), 'incorrect') or contains(text(), 'wrong') or contains(text(), 'invalid')]",
                "//div[contains(@class, 'alert')]"
            ]
            
            for selector in error_selectors:
                try:
                    error_elements = self.driver.find_elements(By.XPATH, selector)
                    for element in error_elements:
                        if element.is_displayed():
                            error_text = element.text
                            print(f"✗ Found error message: {error_text}")
                            return False
                except Exception:
                    continue
            
            print("⚠ Login status unclear - may need manual verification")
            return False
                
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    def search_questions(self, search_term, max_results=5):
        """Search for questions on Quora"""
        try:
            print(f"Searching for questions about: {search_term}")
            
            # Navigate to search
            search_url = f"https://www.quora.com/search?q={search_term.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Find question links
            question_links = []
            question_selectors = [
                "//a[contains(@class, 'question_link')]",
                "//a[contains(@href, '/What-') or contains(@href, '/How-') or contains(@href, '/Why-')]",
                "//div[contains(@class, 'Question')]//a"
            ]
            
            for selector in question_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements[:max_results]:
                        href = element.get_attribute('href')
                        text = element.text.strip()
                        if href and text and len(text) > 10:
                            question_links.append({
                                'url': href,
                                'title': text
                            })
                    
                    if question_links:
                        break
                        
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            print(f"✓ Found {len(question_links)} questions")
            return question_links[:max_results]
            
        except Exception as e:
            print(f"✗ Error searching questions: {e}")
            return []
    
    def answer_question(self, question_url, answer_text):
        """Answer a specific question"""
        try:
            print(f"Navigating to question: {question_url}")
            self.driver.get(question_url)
            time.sleep(3)
            
            # Look for answer button/area
            answer_selectors = [
                "//button[contains(text(), 'Answer')]",
                "//div[contains(text(), 'Answer')]",
                "//span[contains(text(), 'Answer')]",
                "//div[contains(@class, 'answer_editor')]",
                "//div[@contenteditable='true']"
            ]
            
            answer_element = None
            for selector in answer_selectors:
                try:
                    answer_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not answer_element:
                print("✗ Could not find answer button/area")
                return False
            
            # Click to start answering
            self.driver.execute_script("arguments[0].scrollIntoView(true);", answer_element)
            time.sleep(1)
            answer_element.click()
            print("✓ Clicked answer area")
            
            time.sleep(2)
            
            # Find the text editor
            editor_selectors = [
                "//div[@contenteditable='true']",
                "//div[contains(@class, 'editor')]//div[@contenteditable='true']",
                "//div[contains(@class, 'answer')]//div[@contenteditable='true']",
                "//textarea"
            ]
            
            editor = None
            for selector in editor_selectors:
                try:
                    editor = self.driver.find_element(By.XPATH, selector)
                    if editor.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not editor:
                print("✗ Could not find answer editor")
                return False
            
            # Clear and enter answer
            editor.click()
            time.sleep(1)
            
            # Clear existing content
            editor.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            editor.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Type answer with realistic delays
            self.type_with_delay(editor, answer_text)
            print("✓ Entered answer text")
            
            time.sleep(2)
            
            # Look for submit/publish button
            submit_selectors = [
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Publish')]",
                "//button[contains(text(), 'Post')]",
                "//button[contains(text(), 'Add Answer')]"
            ]
            
            submit_btn = None
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.XPATH, selector)
                    if submit_btn.is_displayed() and submit_btn.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if submit_btn:
                submit_btn.click()
                print("✓ Submitted answer")
                time.sleep(3)
                return True
            else:
                print("⚠ Could not find submit button - answer may be saved as draft")
                return False
                
        except Exception as e:
            print(f"✗ Error answering question: {e}")
            return False
    
    def type_with_delay(self, element, text, min_delay=0.05, max_delay=0.15):
        """Type text with human-like delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))
    
    def post_question(self, question_title, question_details=""):
        """Post a new question on Quora"""
        try:
            print("Creating new question...")
            
            # Navigate to add question
            self.driver.get("https://www.quora.com/")
            time.sleep(3)
            
            # Look for "Add question" button
            add_question_selectors = [
                "//button[contains(text(), 'Add question')]",
                "//div[contains(text(), 'Add question')]",
                "//a[contains(text(), 'Add question')]",
                "//span[contains(text(), 'Add question')]"
            ]
            
            add_btn = None
            for selector in add_question_selectors:
                try:
                    add_btn = self.driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if add_btn:
                add_btn.click()
                print("✓ Clicked Add question button")
            else:
                # Try direct navigation
                self.driver.get("https://www.quora.com/qedit/add_question")
                print("✓ Navigated directly to add question page")
            
            time.sleep(3)
            
            # Find question title field
            title_selectors = [
                "//input[@placeholder*='question' or @placeholder*='Question']",
                "//textarea[@placeholder*='question' or @placeholder*='Question']",
                "//div[@contenteditable='true']"
            ]
            
            title_field = None
            for selector in title_selectors:
                try:
                    title_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except TimeoutException:
                    continue
            
            if title_field:
                title_field.click()
                title_field.clear()
                self.type_with_delay(title_field, question_title)
                print(f"✓ Entered question title: {question_title}")
            else:
                print("✗ Could not find question title field")
                return False
            
            # Add details if provided
            if question_details:
                time.sleep(1)
                title_field.send_keys(Keys.TAB)
                time.sleep(1)
                
                # Find details field
                details_field = self.driver.switch_to.active_element
                self.type_with_delay(details_field, question_details)
                print("✓ Added question details")
            
            # Submit question
            submit_selectors = [
                "//button[contains(text(), 'Add question')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Post')]"
            ]
            
            submit_btn = None
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.XPATH, selector)
                    if submit_btn.is_displayed() and submit_btn.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if submit_btn:
                submit_btn.click()
                print("✓ Question posted successfully!")
                time.sleep(3)
                return True
            else:
                print("⚠ Could not find submit button")
                return False
                
        except Exception as e:
            print(f"✗ Error posting question: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("✓ Browser closed")

def main():
    """Main function to demonstrate usage"""
    # Load credentials from .env file
    EMAIL = os.getenv('QUORA_EMAIL')
    PASSWORD = os.getenv('QUORA_PASSWORD')
    
    # Validate credentials
    if not EMAIL or not PASSWORD:
        print("❌ Error: QUORA_EMAIL and QUORA_PASSWORD must be set in .env file")
        print("Create a .env file with:")
        print("QUORA_EMAIL=your_email@example.com")
        print("QUORA_PASSWORD=your_password")
        return
    
    # Search and answer configuration
    SEARCH_TERMS = ["python programming", "machine learning", "web development"]
    
    SAMPLE_ANSWER = """Great question! Based on my experience, here are some key points to consider:

1. **First important point**: This is where you provide valuable insight based on your knowledge and experience.

2. **Second key aspect**: Make sure to give practical, actionable advice that readers can actually use.

3. **Additional considerations**: Always back up your points with examples or evidence when possible.

Remember, the best answers on Quora are those that provide genuine value to the person asking the question. Focus on being helpful rather than just promoting yourself.

Hope this helps!"""
    
    # Question posting configuration
    NEW_QUESTION = "What are the best practices for learning Python programming in 2024?"
    QUESTION_DETAILS = "I'm a beginner looking to start learning Python. What resources, projects, and learning path would you recommend for someone starting from scratch?"
    
    # Initialize automation
    bot = None
    try:
        print("🚀 Starting Quora automation...")
        bot = QuoraAutomation(headless=False)  # Set to True for headless mode
        
        # Login
        if not bot.login_to_quora(EMAIL, PASSWORD):
            print("❌ Login failed. Please check your credentials.")
            return
        
        print("\n" + "="*50)
        print("Choose an action:")
        print("1. Search and answer questions")
        print("2. Post a new question")
        print("3. Both")
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            # Search and answer questions
            print(f"\n🔍 Searching for questions...")
            for search_term in SEARCH_TERMS:
                questions = bot.search_questions(search_term, max_results=2)
                
                for i, question in enumerate(questions):
                    print(f"\n📝 Answering question {i+1}: {question['title'][:100]}...")
                    
                    success = bot.answer_question(question['url'], SAMPLE_ANSWER)
                    if success:
                        print("✅ Answer posted successfully!")
                    else:
                        print("❌ Failed to post answer")
                    
                    # Add delay between answers to avoid rate limiting
                    if i < len(questions) - 1:
                        time.sleep(random.randint(30, 60))
                
                # Delay between different search terms
                time.sleep(random.randint(60, 120))
        
        if choice in ['2', '3']:
            # Post a new question
            print(f"\n❓ Posting new question...")
            if bot.post_question(NEW_QUESTION, QUESTION_DETAILS):
                print("✅ Question posted successfully!")
            else:
                print("❌ Failed to post question")
        
        print("\n🎉 Quora automation completed!")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
    
    finally:
        if bot:
            input("Press Enter to close the browser...")
            bot.close()

if __name__ == "__main__":
    main()