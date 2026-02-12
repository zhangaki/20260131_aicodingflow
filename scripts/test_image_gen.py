
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("Gemini_api_key")
if not api_key:
    # Try finding .env manually if load_dotenv fails
    print("Trying to find api key manually...")
    # Assuming .env in root
    try:
        with open('../../.env') as f:
            for line in f:
                if 'Gemini_api_key' in line:
                    api_key = line.split('=')[1].strip().strip('"')
                    break
    except:
        pass

if not api_key:
    print("No API key found")
    exit(1)

genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'image' in m.name:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")

# Try to generate an image
try:
    # Using the latest imagen model name known for Gemini API
    model = genai.GenerativeModel('imagen-3.0-generate-001')
    response = model.generate_content("A futuristic city skyline, cyberpunk style", generation_config={"response_mime_type": "image/jpeg"})
    print("Generation successful (using generate_content technique)?")
    # Response handling depends on SDK version, usually it returns bytes or a link
    if response.parts:
        print("Response has parts")
except Exception as e:
    print(f"Failed to generate with generate_content: {e}")

