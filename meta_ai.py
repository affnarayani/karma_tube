import sys # Import sys for exiting the program
import time
import os
import re
import json
import shutil
import random
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
    prompts_filename = "prompts.json"
    videos_dir = "videos"
    
    # XPath for login verification
    login_verification_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[1]/div/div/div[3]/div/div[1]/span/span"
    expected_username = "kumar.ujjawal247"

    # Load prompts from prompts.json
    try:
        with open(prompts_filename, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        print(f"Loaded {len(prompts_data)} prompts from {prompts_filename}.")
    except FileNotFoundError:
        print(f"Error: {prompts_filename} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {prompts_filename}.")
        return

    os.makedirs(videos_dir, exist_ok=True) # Ensure the videos directory exists

    error_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div"
    
    for prompt_entry in prompts_data:
        for prompt_key, prompt_text in prompt_entry.items():
            print(f"\n--- Processing {prompt_key}: '{prompt_text[:50]}...' ---")

            max_retries_per_prompt = 2 # 1 main attempt + 2 retries
            current_retry = 0
            
            while current_retry <= max_retries_per_prompt:
                driver = None # Initialize driver for each retry attempt
                file_to_rename_after_browser_close = None # Initialize variable for each retry

                try:
                    print(f"Attempt {current_retry + 1}/{max_retries_per_prompt + 1}: Logging in to {target_url} with headless mode set to {HEADLESS}...")
                    driver = login_with_cookies(target_url, cookies_filename, headless=HEADLESS, window_size="1920,1080")

                    if not driver:
                        print("Failed to get a driver instance. Login might have failed. Retrying...")
                        current_retry += 1
                        if current_retry > max_retries_per_prompt:
                            raise Exception(f"Failed to log in after {max_retries_per_prompt + 1} attempts for prompt '{prompt_key}'. Failing program.")
                        continue # Continue to the next retry attempt

                    # --- Login Verification Logic ---
                    print("Waiting for page to load completely after applying cookies...")
                    wait = WebDriverWait(driver, 30) # Increased wait time for initial page load

                    try:
                        # Wait for the specific XPath to be present and check its text
                        username_element = wait.until(EC.presence_of_element_located((By.XPATH, login_verification_xpath)))
                        if expected_username in username_element.text:
                            print(f"Login successful. Verified username: '{username_element.text}'. Proceeding to generate video.")
                        else:
                            print(f"Login verification failed. Expected '{expected_username}' but found '{username_element.text}'.")
                            print("Cookie has expired, please renew the cookie.")
                            driver.quit()
                            sys.exit(1) # Exit the program
                    except TimeoutException:
                        print("Login verification failed: Timeout while waiting for username element.")
                        print("Cookie has expired, please renew the cookie.")
                        driver.quit()
                        sys.exit(1) # Exit the program
                    except Exception as e:
                        print(f"An error occurred during login verification: {e}")
                        print("Cookie has expired, please renew the cookie.")
                        driver.quit()
                        sys.exit(1) # Exit the program
                    # --- End Login Verification Logic ---
                    
                    print("Attempting to find the prompt input field.")
                    prompt_selectors = [
                        (By.XPATH, "//div[@contenteditable='true' and @role='textbox']"),
                        (By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']"),
                        (By.CSS_SELECTOR, "textarea[aria-label*='Prompt']"),
                        (By.CSS_SELECTOR, "div[aria-label*='Prompt']"),
                        (By.XPATH, "//p[contains(@class, 'x') and @data-lexical-editor='true']"),
                        (By.XPATH, "//div[contains(@class, 'x') and @data-lexical-editor='true']"),
                        (By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div[1]/p")
                    ]
                    
                    prompt_field = None
                    # Re-using the wait object from login verification, or creating a new one if needed
                    # wait = WebDriverWait(driver, 20) # This line is now redundant if wait is already defined above

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

                    print(f"Typing prompt: '{prompt_text}' into the prompt field.")
                    prompt_field.send_keys(prompt_text)
                    print(f"Prompt typed. Waiting for 3 seconds.")

                    time.sleep(3)

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

                    first_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
                    second_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
                    third_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[3]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
                    fourth_video_xpath = "/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[2]/div/div/div/div[4]/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div"
                    
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
                            video_element = wait.until(EC.presence_of_element_located((By.XPATH, video_xpath)))
                            found_videos.append((video_name, video_xpath))
                            print(f"Found {video_name} at XPath: {video_xpath}")
                        except TimeoutException:
                            print(f"Timeout: {video_name} not found at XPath: {video_xpath}. Skipping.")
                        except Exception as e:
                            print(f"An error occurred while trying to find {video_name}: {e}. Skipping.")

                    # Check for error message if no videos are found
                    if not found_videos:
                        try:
                            error_element = wait.until(EC.presence_of_element_located((By.XPATH, error_xpath)))
                            error_text = error_element.text
                            if "Oops! Something went wrong!" in error_text:
                                print(f"Error detected at XPath: {error_xpath} with text: '{error_text}'. Retrying...")
                                current_retry += 1
                                if current_retry > max_retries_per_prompt:
                                    raise Exception(f"Video generation failed after {max_retries_per_prompt + 1} attempts for prompt '{prompt_key}'. Failing program.")
                                continue # Retry the current prompt
                        except TimeoutException:
                            print("No videos found and no specific error message detected. Proceeding with existing retry logic for video elements.")
                        except Exception as e:
                            print(f"An unexpected error occurred while checking for error XPath: {e}. Proceeding with existing retry logic for video elements.")

                    # Existing retry logic for finding videos (if no specific error was detected)
                    retries_video_find = 0
                    max_retries_video_find = 2 # This is separate from the prompt-level retries
                    while not found_videos and retries_video_find < max_retries_video_find:
                        retries_video_find += 1
                        print(f"No videos found. Refreshing page (Video find retry {retries_video_find}/{max_retries_video_find}).")
                        driver.refresh()
                        time.sleep(15) # Wait after refresh
                        
                        for video_name, video_xpath in all_video_xpaths:
                            try:
                                video_element = wait.until(EC.presence_of_element_located((By.XPATH, video_xpath)))
                                found_videos.append((video_name, video_xpath))
                                print(f"Found {video_name} at XPath: {video_xpath}")
                            except TimeoutException:
                                print(f"Timeout: {video_name} not found at XPath: {video_xpath}. Skipping.")
                            except Exception as e:
                                print(f"An error occurred while trying to find {video_name}: {e}. Skipping.")

                    if not found_videos:
                        raise Exception("No videos found to download after multiple retries (including video find retries). Failing the program as per requirement.")

                    selected_video_name, selected_video_xpath = random.choice(found_videos)
                    print(f"Randomly selected {selected_video_name} for download.")

                    try:
                        video_element = wait.until(EC.element_to_be_clickable((By.XPATH, selected_video_xpath)))
                        video_element.click()
                        print(f"Clicked on {selected_video_name}. Waiting for 15 seconds.")
                        time.sleep(15)

                        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, download_button_xpath)))
                        download_button.click()
                        print("Clicked download button. Waiting for 15 seconds for download to initiate.")
                        time.sleep(15)

                        # The file is directly downloaded to the videos directory in the program directory.
                        download_dir = videos_dir
                        list_of_downloaded_items = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
                        
                        # Filter for actual files, not directories
                        downloaded_files = [f for f in list_of_downloaded_items if os.path.isfile(f)]
                        
                        if not downloaded_files:
                            print("Error: No files found in the downloads directory to move.")
                            # This is a critical error for the current prompt, so we should retry if possible
                            current_retry += 1
                            if current_retry > max_retries_per_prompt:
                                raise Exception(f"No files downloaded after {max_retries_per_prompt + 1} attempts for prompt '{prompt_key}'. Failing program.")
                            continue # Retry the current prompt

                        latest_file_in_downloads = max(downloaded_files, key=os.path.getctime)
                        original_filename = os.path.basename(latest_file_in_downloads)
                        
                        # Move the file to the videos directory with its original name
                        temp_video_path = os.path.join(videos_dir, original_filename)
                        shutil.move(latest_file_in_downloads, temp_video_path)
                        print(f"Moved downloaded video to {temp_video_path} (original name).")
                        print(f"Successfully processed and downloaded {selected_video_name} for {prompt_key}.")

                        # Store information for renaming after browser close
                        file_to_rename_after_browser_close = (temp_video_path, prompt_key)

                        try:
                            close_button = wait.until(EC.element_to_be_clickable((By.XPATH, close_button_xpath)))
                            close_button.click()
                            print("Clicked close button. Waiting for 15 seconds to return to main screen.")
                            time.sleep(15)
                        except TimeoutException:
                            print(f"Warning: Timeout while trying to click the close button for {selected_video_name}. Proceeding without closing modal.")
                        except Exception as e:
                            print(f"Warning: An error occurred while trying to click the close button for {selected_video_name}: {e}. Proceeding without closing modal.")

                    except TimeoutException:
                        print(f"Timeout: Could not find or click elements for {selected_video_name}. Download failed. Retrying...")
                        current_retry += 1
                        if current_retry > max_retries_per_prompt:
                            raise Exception(f"Video download failed after {max_retries_per_prompt + 1} attempts for prompt '{prompt_key}'. Failing program.")
                        continue # Retry the current prompt
                    except Exception as e:
                        print(f"An error occurred while processing {selected_video_name}: {e}. Download failed. Retrying...")
                        current_retry += 1
                        if current_retry > max_retries_per_prompt:
                            raise Exception(f"Video processing failed after {max_retries_per_prompt + 1} attempts for prompt '{prompt_key}'. Failing program.")
                        continue # Retry the current prompt

                    print("Finished processing the selected video. Waiting for 10 seconds before closing the browser.")
                    time.sleep(10)
                    break # Break out of the retry loop if successful

                except Exception as e:
                    print(f"An unexpected error occurred during video generation for prompt '{prompt_key}': {e}. Retrying...")
                    current_retry += 1
                    if current_retry > max_retries_per_prompt:
                        raise Exception(f"Video generation failed after {max_retries_per_prompt + 1} attempts for prompt '{prompt_key}'. Failing program.")
                    # If an exception occurs, the finally block will close the driver, and the loop will continue for a retry.
                finally:
                    if driver:
                        driver.quit()
                        print("Browser closed.")
                    
                    # Perform renaming after the browser is closed
                    if file_to_rename_after_browser_close:
                        original_path_in_videos, current_prompt_key = file_to_rename_after_browser_close
                        final_video_name = os.path.join(videos_dir, f"{current_prompt_key}.mp4")
                        try:
                            if os.path.exists(original_path_in_videos):
                                os.rename(original_path_in_videos, final_video_name)
                                print(f"Renamed '{os.path.basename(original_path_in_videos)}' to '{os.path.basename(final_video_name)}' in '{videos_dir}'.")
                            else:
                                print(f"Warning: File '{original_path_in_videos}' not found for renaming.")
                        except Exception as e:
                            print(f"Error renaming file '{original_path_in_videos}' to '{final_video_name}': {e}")
            else:
                print(f"All {max_retries_per_prompt + 1} attempts failed for prompt '{prompt_key}'. Moving to the next prompt.")

if __name__ == "__main__":
    generate_video()
