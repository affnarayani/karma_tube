import os
import random
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() # Load environment variables from .env

# Arrays for dynamic advice generation
god_names = ["Lord Krishna", "Lord Shiva", "Lord Ram", "Goddess Durga", "Lord Ganesha", "Goddess Lakshmi", "Lord Hanuman"]
aspects_of_advice = [
    "karma", "shanti", "dharam", "tyaag", "jeevan", "pariwaar", "patni", "pati", "pita", "mata",
    "mitrata", "prem", "krodh", "daya", "satya", "dhairya", "sukh", "dukh", "moksha", "bhakti",
    "gyaan", "seva", "sanskriti", "swasthya", "dhan", "samay", "shiksha", "santosha", "sahanubhuti",
    "vinamrata", "parishram", "prayas", "utsah", "shraddha", "vishwas", "samarpan", "sanyam", "vivek",
    "nyay", "shaurya", "bal", "shakti", "pragati", "safalta", "asafalta", "nirasha", "aasha", "prerna"
]

# Configure the Gemini API client
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('gemini-2.5-flash')

# Randomly choose a god and an aspect for dynamic advice generation
selected_god = random.choice(god_names)
selected_aspect = random.choice(aspects_of_advice)

# Save selected god and aspect to config.json
# Read existing config data
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
except FileNotFoundError:
    config_data = {} # Initialize if file doesn't exist

# Update selected god and aspect
config_data["selected_god"] = selected_god
config_data["selected_aspect"] = selected_aspect

# Write updated config data back to file
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config_data, f, ensure_ascii=False, indent=4)
print(f"Selected god '{selected_god}' and aspect '{selected_aspect}' saved to config.json")

# Instruct Gemini to imagine being the selected god and preach advice in Hindi on the selected aspect
response = model.generate_content(
    contents=(
        f"Imagine you are {selected_god}. Give one short life advice in Hindi language focusing on '{selected_aspect}'. "
        "The advice should be suitable for a 30-second spoken video. "
        f"Speak directly in first person as {selected_god} but do not mention {selected_god}'s name or identity. "
        "Do not use any special characters, names, or forms of address like 'priye' or 'bhakt'. "
        "Keep the message concise, poetic, powerful, and strictly ensure it is between 200 and 250 characters long."
    )
)

# Print the advice to the console
os.makedirs('temp', exist_ok=True)
with open('temp/advice.txt', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Advice saved to temp/advice.txt")
