import time
import csv
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FacebookAdChecker:
    def __init__(self, headless=False):
        """Initialize the automation with Chrome driver"""
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        
        # Chrome options for better automation
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = None
        self.wait = None
        
        # Set up OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
    def start_driver(self):
        """Start the Chrome driver"""
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def get_companies_from_openai(self, industry="FMCG", count=10):
        """Get list of companies from OpenAI for a specific industry"""
        try:
            prompt = f"""
            List {count} well-known {industry} companies from India. 
            Provide only the company names, one per line, without any additional text or numbering.
            Focus on companies that are likely to run digital advertising campaigns.
            """
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            companies = response.choices[0].message.content.strip().split('\n')
            companies = [company.strip() for company in companies if company.strip()]
            
            print(f"✅ Generated {len(companies)} {industry} companies from OpenAI")
            return companies[:count]  # Ensure we don't exceed the requested count
            
        except Exception as e:
            print(f"❌ Error getting companies from OpenAI: {e}")
            # Fallback list of FMCG companies
            return [
                "Hindustan Unilever",
                "ITC Limited",
                "Nestle India",
                "Britannia Industries",
                "Dabur India",
                "Marico Limited",
                "Godrej Consumer Products",
                "Parle Products",
                "Amul",
                "Patanjali Ayurved"
            ]
    
    def search_company_ads(self, company_name):
        """Search for a company's ads on Facebook Ad Library"""
        try:
            # Navigate to Facebook Ad Library
            fb_ad_url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=IN&is_targeted_country=false&media_type=all"
            self.driver.get(fb_ad_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Find and click on the search box
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search by keyword or advertiser']"))
            )
            
            # Clear and enter company name
            search_box.clear()
            search_box.send_keys(company_name)
            time.sleep(2)
            
            # Press Enter to search
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Look for search results
            try:
                # Check if there are any ads displayed
                ads_container = self.driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Search results')]")
                
                # Look for "No results" message
                no_results = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'No results')]")
                
                # Look for ad cards or advertiser info
                ad_cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ad-card') or contains(@role, 'article')]")
                
                # Check for advertiser sections
                advertiser_sections = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Advertiser')]")
                
                if no_results:
                    return False, 0, "No ads found"
                elif ad_cards or advertiser_sections:
                    ad_count = len(ad_cards) if ad_cards else len(advertiser_sections)
                    return True, ad_count, f"Found {ad_count} ad elements"
                else:
                    # Try to find any content that suggests ads exist
                    page_content = self.driver.page_source.lower()
                    if company_name.lower() in page_content and ('ad' in page_content or 'advertiser' in page_content):
                        return True, 1, "Ads detected in page content"
                    else:
                        return False, 0, "No ads detected"
                        
            except Exception as e:
                print(f"⚠️  Error analyzing search results for {company_name}: {e}")
                return False, 0, f"Error: {str(e)}"
                
        except Exception as e:
            print(f"❌ Error searching for {company_name}: {e}")
            return False, 0, f"Search error: {str(e)}"
    
    def run_automation(self, industry="FMCG", company_count=10):
        """Main automation function"""
        print(f"🚀 Starting Facebook Ad Library checker for {industry} companies...")
        
        # Get companies from OpenAI
        companies = self.get_companies_from_openai(industry, company_count)
        
        if not companies:
            print("❌ No companies found. Exiting.")
            return
        
        print(f"📋 Companies to check: {', '.join(companies)}")
        
        # Start browser
        self.start_driver()
        
        results = []
        
        try:
            for i, company in enumerate(companies, 1):
                print(f"\n🔍 [{i}/{len(companies)}] Checking ads for: {company}")
                
                has_ads, ad_count, message = self.search_company_ads(company)
                
                result = {
                    'company': company,
                    'has_ads': has_ads,
                    'ad_count': ad_count,
                    'message': message,
                    'status': '✅ Running Ads' if has_ads else '❌ No Ads'
                }
                
                results.append(result)
                print(f"   {result['status']} - {message}")
                
                # Add delay between searches to avoid rate limiting
                if i < len(companies):
                    time.sleep(random.uniform(2, 4))
        
        except KeyboardInterrupt:
            print("\n⏹️  Automation stopped by user")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        # Print summary
        self.print_summary(results, industry)
        
        # Save to CSV
        self.save_to_csv(results, industry)
        
        return results
    
    def print_summary(self, results, industry):
        """Print summary of results"""
        print(f"\n📊 SUMMARY - {industry} Companies Ad Check")
        print("=" * 50)
        
        companies_with_ads = [r for r in results if r['has_ads']]
        companies_without_ads = [r for r in results if not r['has_ads']]
        
        print(f"Total companies checked: {len(results)}")
        print(f"Companies running ads: {len(companies_with_ads)}")
        print(f"Companies not running ads: {len(companies_without_ads)}")
        
        if companies_with_ads:
            print(f"\n✅ Companies running ads:")
            for result in companies_with_ads:
                print(f"   • {result['company']} ({result['message']})")
        
        if companies_without_ads:
            print(f"\n❌ Companies not running ads:")
            for result in companies_without_ads:
                print(f"   • {result['company']}")
    
    def save_to_csv(self, results, industry):
        """Save results to CSV file"""
        filename = f"{industry.lower()}_ad_check_results.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['company', 'has_ads', 'ad_count', 'message', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in results:
                    writer.writerow(result)
            
            print(f"\n💾 Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")

def main():
    """Main function to run the automation"""
    # You can change these parameters
    INDUSTRY = "FMCG"  # You can change to other industries like "Technology", "Banking", "Automotive", etc.
    COMPANY_COUNT = 10
    HEADLESS = False  # Set to True to run without opening browser window
    
    # Create and run automation
    checker = FacebookAdChecker(headless=HEADLESS)
    results = checker.run_automation(industry=INDUSTRY, company_count=COMPANY_COUNT)
    
    return results

if __name__ == "__main__":
    # Make sure you have your .env file with OPENAI_API_KEY
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
    else:
        main()