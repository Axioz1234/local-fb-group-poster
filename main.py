import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from threading import Thread

class FacebookPoster:
    def __init__(self, test_mode=False):
        if not test_mode:
            self.window = ctk.CTk()
            self.window.title("Facebook Group Poster")
            self.window.geometry("600x800")
            self.setup_gui()
            self.window.mainloop()
        else:
            # Initialize without GUI for testing
            self.email = ""
            self.password = ""
            self.groups = []
            self.message = ""

    def setup_gui(self):
        # Login Frame
        login_frame = ctk.CTkFrame(self.window)
        login_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(login_frame, text="Login Details").pack()
        self.email_entry = ctk.CTkEntry(login_frame, placeholder_text="Email")
        self.email_entry.pack(pady=5)
        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=5)

        # Groups Frame
        groups_frame = ctk.CTkFrame(self.window)
        groups_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(groups_frame, text="Group URLs (one per line)").pack()
        self.groups_text = ctk.CTkTextbox(groups_frame, height=200)
        self.groups_text.pack(pady=5, fill="both", expand=True)

        # Message Frame
        message_frame = ctk.CTkFrame(self.window)
        message_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(message_frame, text="Message").pack()
        self.message_text = ctk.CTkTextbox(message_frame, height=200)
        self.message_text.pack(pady=5, fill="both", expand=True)

        # Control Frame
        control_frame = ctk.CTkFrame(self.window)
        control_frame.pack(pady=10, padx=10, fill="both")
        
        self.status_text = ctk.CTkTextbox(control_frame, height=100)
        self.status_text.pack(pady=5, fill="both")
        
        ctk.CTkButton(control_frame, text="Start Posting", command=self.start_posting).pack(pady=5)

    def log(self, message):
        if hasattr(self, 'status_text'):
            self.status_text.insert("end", f"{message}\n")
            self.status_text.see("end")
        print(message)

    def start_posting(self):
        Thread(target=self.post_to_groups, daemon=True).start()

    def post_to_groups(self, test_credentials=None):
        self.log("Starting Facebook posting process...")
        
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
        if not all([email, password, groups, message]):
            self.log("Please fill in all fields!")
            return

         # Setup Chrome
        self.log("Setting up Chrome...")
        try:
            username = os.getlogin()
            user_data_dir = f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data'
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            prefs = {"profile.default_content_setting_values.notifications": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            
            driver = webdriver.Chrome(options=chrome_options)


            # Login to Facebook
            self.log("Logging into Facebook...")
            driver.get("https://www.facebook.com")
            
            email_element = driver.find_element(By.ID, "email")
            email_element.send_keys(email)
            
            pass_element = driver.find_element(By.ID, "pass")
            pass_element.send_keys(password)
            
            login_button = driver.find_element(By.NAME, "login")
            login_button.click()
            
            time.sleep(5)  # Wait for login to complete

            # Post to each group
            for group_url in groups:
                try:
                    self.log(f"Posting to: {group_url}")
                    driver.get(group_url)
                    time.sleep(3)

                    # Find and click post box
                    post_box = driver.find_element(By.CSS_SELECTOR, "[role='textbox']")
                    post_box.click()
                    time.sleep(1)

                    # Enter message
                    post_box.send_keys(message)
                    time.sleep(1)

                    # Click post button
                    post_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Post']")
                    post_button.click()
                    time.sleep(10)  # Move this inside the try block properly
                    time.sleep(3)

                    self.log(f"Successfully posted to {group_url}")

                except Exception as e:
                    self.log(f"Error posting to {group_url}: {str(e)}")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            
        finally:
            if 'driver' in locals():
                driver.quit()

if __name__ == "__main__":
    FacebookPoster()
