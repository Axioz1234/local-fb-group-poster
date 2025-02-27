import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json

class FacebookPoster:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Facebook Group Poster")
        self.window.geometry("800x600")
        self.setup_gui()

    def load_cookies(self):
        try:
            with open('facebook_cookies.json', 'r') as f:
                cookies = json.load(f)
                return cookies
        except:
            return None

    def save_cookies(self, driver):
        cookies = driver.get_cookies()
        with open('facebook_cookies.json', 'w') as f:
            json.dump(cookies, f)

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
        self.continue_button.pack_forget()  # Hide initially

        # Right side - Log
        log_frame = ctk.CTkFrame(container)
        log_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(log_frame, text="Log:").pack(pady=5)
        self.log_text = ctk.CTkTextbox(log_frame, width=300, height=400)
        self.log_text.pack(pady=5)

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
                    except Exception as e:
                        self.log(f"Initial button not found, trying alternative approach: {str(e)}")

                    # Find and click the post box
                    try:
                        # Try multiple possible selectors for the text input
                        post_box = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']")) or
                            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")) or
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Write')]"))
                        )
                        post_box.click()
                        time.sleep(2)
                        
                        # Enter message
                        post_box.send_keys(message)
                        time.sleep(2)

                        # Try to find the post button
                        try:
                            post_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Post']")) or
                                EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']")) or
                                EC.element_to_be_clickable((By.XPATH, "//div[text()='Post']"))
                            )
                        except:
                            # If the above fails, try finding any button containing "Post"
                            post_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Post')]")
                        
                        post_button.click()
                        self.log("Clicked post button")
                        time.sleep(5)  # Wait for post to complete

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
        self.window.mainloop()

if __name__ == "__main__":
    app = FacebookPoster()
    app.run()
