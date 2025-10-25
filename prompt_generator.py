import json
import google.generativeai as genai
import os
import re
import time
import random # Moved import random to the top
from dotenv import load_dotenv
import google.api_core.exceptions

load_dotenv() # Load environment variables from .env

# Load API key from environment variables
# Ensure you have your Google API key set as an environment variable named 'GEMINI_API_KEY'
# For example: export GEMINI_API_KEY='your_api_key_here'
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_gemini_model():
    """Initializes and returns the Gemini text generation model."""
    # Using the same model as advice_generator.py
    return genai.GenerativeModel('gemini-2.5-flash')

def read_config(file_path="config.json"):
    """Reads the selected_god from config.json."""
    with open(file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get("selected_god")

def read_transcript(file_path="temp/transcript.txt"):
    """Reads the transcript lines and extracts the text."""
    transcript_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Extract text after the timestamp
            match = re.match(r'\[\d{2}:\d{2} - \d{2}:\d{2}\] (.*)', line)
            if match:
                transcript_lines.append(match.group(1).strip())
    return transcript_lines

def generate_video_prompt(model, selected_god, transcript_line):
    """Generates a video prompt using the Gemini text generation model."""
    prompt_engineer_instruction = (
        "You are a prompt engineer. Your task is to generate a concise and effective "
        "video generation prompt for a Gemini video model. "
        "The video should be in a mature cartoon style, suitable for adults, not children. "
        "Do not include any text overlays in the video. "
        "The final prompt must not contain any Hindi or Unicode characters. "
        "Provide only the final prompt, without any introductory sentences like 'Here's the prompt:'."
    )

    selected_god_phrase = ""
    if random.random() < 0.5:
        selected_god_phrase = f"'{selected_god}' "
        print(f"Using selected_god: {selected_god} in the prompt.")
    else:
        print("Not using selected_god in the prompt for this iteration.")
    user_request = (
        f"Generate a video prompt for a scene featuring {selected_god_phrase}"
        f"conveying the message: '{transcript_line}'. "
        f"Ensure the prompt adheres to the following: mature cartoon style for adults, no text overlays, "
        f"and no Hindi or Unicode characters in the final output. "
        f"Translate the message '{transcript_line}' to English before incorporating it into the prompt."
    )

    full_prompt = f"{prompt_engineer_instruction}\n\n{user_request}"

    max_retries = 2  # 2 retries + 1 initial attempt = 3 total attempts
    retry_delay = 30 # seconds

    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(full_prompt)
            if response.candidates:
                return response.candidates[0].content.parts[0].text
            return "Error: Could not generate prompt."
        except google.api_core.exceptions.InternalServerError as e:
            if attempt < max_retries:
                print(f"InternalServerError encountered. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(retry_delay)
            else:
                print(f"InternalServerError encountered after {max_retries + 1} attempts. Failing. Error: {e}")
                return "Error: Internal Server Error after multiple retries."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "Error: An unexpected error occurred."

def main():
    selected_god = read_config()
    if not selected_god:
        print("Error: 'selected_god' not found in config.json.")
        return

    transcript_lines = read_transcript()
    if not transcript_lines:
        print("Error: No transcript lines found in temp/transcript.txt.")
        return

    model = get_gemini_model()
    output_file = "prompts.json"
    generated_prompts = []

    # Clear prompts.json at the beginning of execution
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([], f) # Write an empty JSON array to clear the file

    # Load existing prompts if the file exists, otherwise start with an empty list
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            try:
                generated_prompts = json.load(f)
            except json.JSONDecodeError:
                generated_prompts = [] # Handle empty or malformed JSON

    for i, line in enumerate(transcript_lines):
        print(f"Generating prompt for line {i+1}: '{line}'")
        prompt_text = "Generate a video: " + generate_video_prompt(model, selected_god, line)
        
        # Append the new prompt to the list
        generated_prompts.append({f"prompt_{len(generated_prompts) + 1}": prompt_text})
        print(f"Generated: {prompt_text}\n")

        # Save the updated list to the JSON file after each generation
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(generated_prompts, f, indent=2, ensure_ascii=False)
        print(f"Prompt for line {i+1} saved to {output_file}")

        if i < len(transcript_lines) - 1: # Don't sleep after the last prompt
            print("Waiting for 30 seconds before the next API call...")
            time.sleep(30)

    print(f"All prompts processed and saved to {output_file}")

if __name__ == "__main__":
    main()
