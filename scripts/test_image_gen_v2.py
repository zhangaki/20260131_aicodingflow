
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("Gemini_api_key")
if not api_key:
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

client = genai.Client(api_key=api_key)

print("Attempting to generate image with google-genai library...")
try:
    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='A futuristic city skyline, cyberpunk style',
        config=genai.types.GenerateImagesConfig(
            number_of_images=1,
        )
    )
    if response.generated_images:
        print("Success! Generated images.")
        img_bytes = response.generated_images[0].image.image_bytes
        with open("test_image.png", "wb") as f:
            f.write(img_bytes)
        print("Saved test_image.png")
    else:
        print("Response OK but no images?")
except Exception as e:
    print(f"Error generating image: {e}")
