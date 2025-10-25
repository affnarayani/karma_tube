import time
import os
import re
import random # Import the random module
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from login import login_with_cookies

HEADLESS = True

def get_next_video_index(videos_dir="videos"):
    """
    Determines the next available integer index for a video file in the specified directory.
    E.g., if video_1.mp4 and video_3.mp4 exist, returns 4.
    """
    os.makedirs(videos_dir, exist_ok=True) # Ensure the directory exists
    existing_indices = []
    for filename in os.listdir(videos_dir):
        match = re.match(r"video_(\d+)\.mp4", filename)
        if match:
            existing_indices.append(int(match.group(1)))
    
    if not existing_indices:
        return 1 # Start from 1 if no videos exist

    existing_indices.sort()
    
    # Find the first missing positive integer
    for i, index in enumerate(existing_indices):
        if index != i + 1:
            return i + 1
            
    return existing_indices[-1] + 1 # If no gaps, return the next highest

def generate_video():
    print("Starting video generation process...")
    target_url = "https://www.meta.ai"
    cookies_filename = "cookies.json.encypted"

    print(f"Attempting to log in to {target_url} with headless mode set to {HEADLESS}...")
    # Use a consistent window size for headless mode to ensure element visibility
    driver = login_with_cookies(target_url, cookies_filename, headless=HEADLESS, window_size="1920,1080")

    if driver:
        try:
            print("Login successful. Proceeding to generate video.")
            
            print("Login successful. Proceeding to generate video.")
            
            # Removed 'New chat' button interaction as it's not required when a new chat is already open.

            print("Attempting to find the prompt input field.")
            # Define potential selectors for the prompt input field
            prompt_selectors = [
                (By.XPATH, "//div[@contenteditable='true' and @role='textbox']"),
                (By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']"),
                (By.CSS_SELECTOR, "textarea[aria-label*='Prompt']"),
                (By.CSS_SELECTOR, "div[aria-label*='Prompt']"),
                (By.XPATH, "//p[contains(@class, 'x') and @data-lexical-editor='true']"), # Common pattern for Lexical editor
                (By.XPATH, "//div[contains(@class, 'x') and @data-lexical-editor='true']"),
                # Original XPath as a fallback, though less robust
                (By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div[1]/p")
            ]
            
            prompt_field = None
            wait = WebDriverWait(driver, 20)

            for by_type, selector in prompt_selectors:
                try:
                    print(f"Trying selector: {selector} (By: {by_type})")
                    prompt_field = wait.until(EC.presence_of_element_located((by_type, selector)))
                    print(f"Prompt input field found with selector: {selector}.")
                    break
                except TimeoutException:
                    print(f"Timeout: Prompt input field not found with selector: {selector}.")
            
            if not prompt_field:
                raise TimeoutException("Critical Timeout: Prompt input field not found with any tested selectors. Cannot proceed.")

            # Fill the field with text
            prompt_text = "Generate a short animated video in vibrant cartoon style showing Lord Shiva portrayed symbolically — a serene blue-skinned divine figure with a calm expression, sitting on Mount Kailash, holding a trident, with gentle glowing light around him and a flowing river nearby. The animation should feel peaceful, spiritual, and mythic, with smooth camera movement and soft ambient music."
            print(f"Typing prompt: '{prompt_text}' into the prompt field.")
            prompt_field.send_keys(prompt_text)
            print(f"Prompt typed. Waiting for 3 seconds.")

            # Wait for 3 seconds
            time.sleep(3)

            # Locate and click the 'Send' button using CSS selector
            send_button_css_selector = "div[aria-label='Send']"
            print(f"Attempting to click the 'Send' button using CSS selector: {send_button_css_selector}.")
            send_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, send_button_css_selector)))
            send_button.click()
            print("Clicked 'Send' button.")

            print("Waiting for 60 seconds after sending the prompt.")
            time.sleep(60)

            print("Refreshing the page.")
            driver.refresh()

            print("Waiting for 15 seconds after refresh.")
            time.sleep(15)

            # Define the XPaths for the videos
            first_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
            second_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
            third_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[3]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
            fourth_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[4]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
            
            # Define XPaths for download and close buttons
            download_button_xpath = "/html/body/div[1]/div/div/div/div[2]/div[3]/div/div/div[2]/div/div/div[2]/div[1]/div/div/div/div/div/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div[1]/div"
            close_button_xpath = "/html/body/div[1]/div/div/div/div[2]/div[3]/div/div/div[2]/div/div/div[2]/div[1]/div/div/div/div/div/div/div[2]/div[1]/div[1]/div"

            all_video_xpaths = [
                ("first video", first_video_xpath),
                ("second video", second_video_xpath),
                ("third video", third_video_xpath),
                ("fourth video", fourth_video_xpath),
            ]

            found_videos = []
            for video_name, video_xpath in all_video_xpaths:
                try:
                    # Check if the video element is present without waiting for clickability
                    video_element = wait.until(EC.presence_of_element_located((By.XPATH, video_xpath)))
                    found_videos.append((video_name, video_xpath))
                    print(f"Found {video_name} at XPath: {video_xpath}")
                except TimeoutException:
                    print(f"Timeout: {video_name} not found at XPath: {video_xpath}. Skipping.")
                except Exception as e:
                    print(f"An error occurred while trying to find {video_name}: {e}. Skipping.")

            if not found_videos:
                raise Exception("No videos found to download. Failing the program as per requirement.")

            # Randomly select one video from the found videos
            selected_video_name, selected_video_xpath = random.choice(found_videos)
            print(f"Randomly selected {selected_video_name} for download.")

            try:
                # Click on the selected video
                video_element = wait.until(EC.element_to_be_clickable((By.XPATH, selected_video_xpath)))
                video_element.click()
                print(f"Clicked on {selected_video_name}. Waiting for 15 seconds.")
                time.sleep(15)

                # Click the download button
                download_button = wait.until(EC.element_to_be_clickable((By.XPATH, download_button_xpath)))
                download_button.click()
                print("Clicked download button. Waiting for 15 seconds for download to initiate.")
                time.sleep(15)

                # Click the close button
                close_button = wait.until(EC.element_to_be_clickable((By.XPATH, close_button_xpath)))
                close_button.click()
                print("Clicked close button. Waiting for 15 seconds to return to main screen.")
                time.sleep(15)
                print(f"Successfully processed and downloaded {selected_video_name}.")

            except TimeoutException:
                print(f"Timeout: Could not find or click elements for {selected_video_name}. Download failed.")
                raise Exception(f"Failed to download the selected video: {selected_video_name}.")
            except Exception as e:
                print(f"An error occurred while processing {selected_video_name}: {e}. Download failed.")
                raise Exception(f"Failed to download the selected video: {selected_video_name}.")

            print("Finished processing the selected video. Waiting for 10 seconds before closing the browser.")
            time.sleep(10)
        finally:
            if driver:
                driver.quit()
                print("Browser closed.")
    else:
        print("Failed to get a driver instance. Login might have failed. Exiting video generation.")

if __name__ == "__main__":
    generate_video()
