import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import random
from pathlib import Path

class FacebookPoster:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Facebook Group Poster")
        self.window.geometry("800x600")
        
        # Default delay settings
        self.min_delay = 30  # minimum delay in seconds
        self.max_delay = 60  # maximum delay in seconds
        
        self.setup_gui()

    def setup_gui(self):
        # Create main container
        container = ctk.CTkFrame(self.window)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left side - Input fields
        input_frame = ctk.CTkFrame(container)
        input_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Email
        ctk.CTkLabel(input_frame, text="Email:").pack(pady=5)
        self.email_entry = ctk.CTkEntry(input_frame, width=200)
        self.email_entry.pack(pady=5)

        # Password
        ctk.CTkLabel(input_frame, text="Password:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(input_frame, width=200, show="*")
        self.password_entry.pack(pady=5)

        # Groups
        ctk.CTkLabel(input_frame, text="Group URLs (one per line):").pack(pady=5)
        self.groups_text = ctk.CTkTextbox(input_frame, width=200, height=100)
        self.groups_text.pack(pady=5)

        # Message
        ctk.CTkLabel(input_frame, text="Message:").pack(pady=5)
        self.message_text = ctk.CTkTextbox(input_frame, width=200, height=100)
        self.message_text.pack(pady=5)

        # Delay Settings Frame
        delay_frame = ctk.CTkFrame(input_frame)
        delay_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(delay_frame, text="Delay Settings (seconds)").pack(pady=5)
        
        min_delay_frame = ctk.CTkFrame(delay_frame)
        min_delay_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(min_delay_frame, text="Min:").pack(side="left", padx=5)
        self.min_delay_entry = ctk.CTkEntry(min_delay_frame, width=60)
        self.min_delay_entry.insert(0, str(self.min_delay))
        self.min_delay_entry.pack(side="left", padx=5)

        max_delay_frame = ctk.CTkFrame(delay_frame)
        max_delay_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(max_delay_frame, text="Max:").pack(side="left", padx=5)
        self.max_delay_entry = ctk.CTkEntry(max_delay_frame, width=60)
        self.max_delay_entry.insert(0, str(self.max_delay))
        self.max_delay_entry.pack(side="left", padx=5)

        # Random delay checkbox
        self.random_delay_var = ctk.BooleanVar(value=True)
        self.random_delay_check = ctk.CTkCheckBox(delay_frame, text="Use random delay", 
                                                 variable=self.random_delay_var)
        self.random_delay_check.pack(pady=5)

        # Control Frame
        control_frame = ctk.CTkFrame(input_frame)
        control_frame.pack(fill="x", pady=10)

        # Start Button
        self.start_button = ctk.CTkButton(control_frame, text="Start Posting", command=self.post_to_groups)
        self.start_button.pack(pady=5)

        # Continue Button (hidden initially)
        self.continue_button = ctk.CTkButton(control_frame, text="Continue After Verification", 
                                           command=lambda: setattr(self, 'can_continue', True))
        self.continue_button.pack(pady=5)
        self.continue_button.pack_forget()

        # Right side - Log
        log_frame = ctk.CTkFrame(container)
        log_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(log_frame, text="Log:").pack(pady=5)
        self.log_text = ctk.CTkTextbox(log_frame, width=300, height=400)
        self.log_text.pack(pady=5)

    def get_random_delay(self):
        """Get random delay between min and max values"""
        try:
            min_delay = float(self.min_delay_entry.get())
            max_delay = float(self.max_delay_entry.get())
            
            if self.random_delay_var.get():
                delay = random.uniform(min_delay, max_delay)
                self.log(f"Waiting for {delay:.1f} seconds...")
                return delay
            else:
                self.log(f"Waiting for {min_delay} seconds...")
                return min_delay
        except ValueError:
            self.log("Invalid delay values, using defaults")
            return 30

    def get_app_data_path(self):
        """Get the appropriate path for storing app data"""
        if os.name == 'nt':  # Windows
            app_data = os.getenv('APPDATA')
            base_path = Path(app_data) / "FacebookPoster"
        else:  # Linux/Mac
            home = os.path.expanduser("~")
            base_path = Path(home) / ".facebook_poster"
            
        base_path.mkdir(parents=True, exist_ok=True)
        return base_path

    def load_cookies(self):
        try:
            cookies_path = self.get_app_data_path() / 'facebook_cookies.json'
            if cookies_path.exists():
                with open(cookies_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.log(f"Error loading cookies: {e}")
        return None

    def save_cookies(self, driver):
        try:
            cookies_path = self.get_app_data_path() / 'facebook_cookies.json'
            cookies = driver.get_cookies()
            with open(cookies_path, 'w') as f:
                json.dump(cookies, f)
        except Exception as e:
            self.log(f"Error saving cookies: {e}")

    def log(self, message):
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.window.update()

    def post_to_groups(self, test_credentials=None):
        self.log("Starting Facebook posting process...")
        self.can_continue = False
        
        # Get input values
        if test_credentials:
            email = test_credentials['email']
            password = test_credentials['password']
            groups = test_credentials['groups']
            message = test_credentials['message']
        else:
            email = self.email_entry.get()
            password = self.password_entry.get()
            groups = [url.strip() for url in self.groups_text.get("1.0", "end-1c").split('\n') if url.strip()]
            message = self.message_text.get("1.0", "end-1c")

        # Validate inputs
        if not all([groups, message]):
            self.log("Please fill in all fields!")
            return

        # Setup Chrome
        self.log("Setting up Chrome...")
        try:
            username = os.getlogin()
            user_data_dir = f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1'
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-extensions')
            prefs = {"profile.default_content_setting_values.notifications": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            os.system("taskkill /f /im chrome.exe")
            time.sleep(2)
            
            driver = webdriver.Chrome(options=chrome_options)

            # Try cookies first
            cookies = self.load_cookies()
            if cookies:
                self.log("Attempting to login with saved cookies...")
                driver.get("https://www.facebook.com")
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                driver.refresh()
                time.sleep(5)

            # If no cookies or cookie login failed, try normal login
            if not cookies or "login" in driver.current_url.lower():
                self.log("Logging in with credentials...")
                driver.get("https://www.facebook.com")
                
                email_element = driver.find_element(By.ID, "email")
                email_element.send_keys(email)
                
                pass_element = driver.find_element(By.ID, "pass")
                pass_element.send_keys(password)
                
                login_button = driver.find_element(By.NAME, "login")
                login_button.click()
                
                time.sleep(5)

            # Check if verification is needed
            if "checkpoint" in driver.current_url or "login" in driver.current_url:
                self.log("Verification needed. Please complete verification in the browser.")
                self.continue_button.pack()  # Show continue button
                
                while not self.can_continue:
                    time.sleep(1)
                    if hasattr(self, 'window'):
                        self.window.update()
                
                self.continue_button.pack_forget()  # Hide continue button
                self.save_cookies(driver)  # Save cookies after successful login

            # Post to each group
            for group_url in groups:
                try:
                    self.log(f"Posting to: {group_url}")
                    driver.get(group_url)
                    time.sleep(5)  # Wait for group page to load

                    # First try to find and click "Write something" or "Create Post"
                    try:
                        create_post = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Write something')]")) or
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Create Post')]")) or
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Start Discussion')]"))
                        )
                        create_post.click()
                        time.sleep(3)
                        
                        # Wait for and switch to popup dialog
                        dialog = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                        )
                        
                        # Find and click the post box in the popup using exact matching
                        post_box = WebDriverWait(dialog, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Write something...'][@role='textbox']"))
                        )
                        
                        # Try to scroll the post box into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", post_box)
                        time.sleep(1)
                        
                        # Click and enter text using JavaScript
                        driver.execute_script("arguments[0].click();", post_box)
                        time.sleep(1)
                        
                        # Try different methods to enter text
                        try:
                            post_box.send_keys(message)
                        except:
                            driver.execute_script(f"arguments[0].innerHTML = '{message}'", post_box)
                        
                        time.sleep(2)

                        # Try to find the post button with specific selectors
                        try:
                            post_button = WebDriverWait(dialog, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Post'][@role='button']"))
                            )
                            # Try to scroll the button into view
                            driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
                            time.sleep(1)
                            
                            # Try JavaScript click first
                            try:
                                driver.execute_script("arguments[0].click();", post_button)
                            except:
                                # If JavaScript click fails, try regular click
                                post_button.click()
                            
                            self.log("Clicked post button")
                            time.sleep(5)  # Wait for post to complete
                            
                        except Exception as e:
                            self.log(f"Error clicking post button: {str(e)}")
                            # Try alternative selector
                            try:
                                post_button = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Post'][role='button']")
                                driver.execute_script("arguments[0].click();", post_button)
                                self.log("Clicked post button using alternative method")
                                time.sleep(5)
                            except Exception as e:
                                self.log(f"Failed to click post button with alternative method: {str(e)}")
                                raise
 
                        time.sleep(self.get_random_delay())  # Add this line
                        self.log(f"Successfully posted to {group_url}")
                        time.sleep(3)  # Wait before moving to next group

                    except Exception as e:
                        self.log(f"Error with post box or posting: {str(e)}")
                        # Take screenshot for debugging
                        driver.save_screenshot(f"error_screenshot_{time.time()}.png")
                        continue

                except Exception as e:
                    self.log(f"Error posting to {group_url}: {str(e)}")
                    # Take screenshot for debugging
                    driver.save_screenshot(f"error_screenshot_{time.time()}.png")
                    continue

        except Exception as e:
            self.log(f"Error: {str(e)}")
            
        finally:
            if 'driver' in locals():
                driver.quit()

    def run(self):
        """Start the GUI application"""
        self.window.mainloop()


def main():
    """Entry point for the application"""
    app = FacebookPoster()
    app.run()


if __name__ == "__main__":
    main()
