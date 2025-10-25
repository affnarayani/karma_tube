import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the API client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define input and output file paths
audio_file_path = 'temp/speech.wav'
transcript_file_path = 'temp/transcript.txt'

# Ensure the 'temp' directory exists
os.makedirs(os.path.dirname(transcript_file_path), exist_ok=True)

try:
    # Upload the audio file
    myfile = genai.upload_file(path=audio_file_path)
    print(f"Uploaded file: {myfile.name}")

    # Initialize the model
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Generate transcript
    prompt = 'Generate only the transcript of the speech with timestamps (no explanations, no intro text). Each line should be 4–7 words maximum. Format strictly like this: [start - end] sentence.'
    response = model.generate_content(
        contents=[prompt, myfile]
    )

    # Save the transcript to a file with UTF-8 encoding
    with open(transcript_file_path, 'w', encoding='utf-8') as f:
        f.write(response.text)

    print(f"Transcript saved to {transcript_file_path}")

except Exception as e:
    print(f"An error occurred: {e}")
