
import os
import sys
import random
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Load Environment
env_paths = [PROJECT_ROOT / ".env", Path("/Users/mac/code/super-individual/.env")]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

GEMINI_API_KEY = os.getenv("Gemini_api_key") or os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_TEXT = "gemini-2.0-flash"
MODEL_IMAGE = "imagen-4.0-fast-generate-001"

# The Updated Styles List
STYLES = [
    # 1. Tech / Modern / Clean
    "Minimalist modern tech, clean white background, soft blue gradients, isometric 3D elements, high-end presentation",
    "Glassmorphism, frosted glass layers, soft pastel colors, modern UI elements, clean composition, bright lighting",
    "Futuristic laboratory, clean white surfaces, glowing blue interfaces, high-end photography style, depth of field",
    "Abstract digital waves, flowing lines, vibrant orange and purple gradients, dark background, motion blur",
    "Technical schematic blueprint, white lines on deep blue background, detailed engineering diagram, glowing nodes, precise",

    # 2. Cinematic / Photographic
    "Cinematic studio lighting, dramatic shadows, sharp focus, professional product photography style, neutral background",
    "Macro photography of circuit board, shallow depth of field, golden contacts, detailed texture, warm lighting",
    "Cyberpunk city street at night, neon lights reflection, rain-slicked wet pavement, cinematic lighting, detailed atmosphere",
    "Architectural photography, modern building details, glass and steel, blue sky reflection, geometric patterns",
    "Double exposure photography, blending nature and technology, artistic silhouette, dreamlike atmosphere",

    # 3. Artistic / Creative / Illustration
    "Digital collage art, mixed media, paper textures, bold typography elements, vibrant colors, contemporary style",
    "Watercolor illustration, soft washes, ink outlines, artistic and expressive, white paper texture background",
    "Surrealist composition, dreamlike elements, floating objects, soft clouds, pastel sky, magritte style",
    "Pop art style, bold outlines, halftone patterns, bright primary colors, retro comic aesthetic",
    "Bauhaus geometric style, simple shapes, balanced composition, retro color palette, abstract design",
    "Low poly 3D landscape, geometric mountains, soft gradient sky, digital art style, clean facets",
    "Paper cut art, layered depth, soft shadows, monochromatic color scheme, intricate details",
    "Fluid art, swirling paint colors, oil on water effect, vibrant and organic, abstract expressionism",
    "Neon wireframe mesh, 3D terrain, retro 80s grid, dark background, synthwave aesthetic",
    "Isometric 3D illustration, cute stylized characters, soft lighting, pastel colors, clean rendering"
]

def generate_sample(title, filename_suffix, specific_style=None):
    style = specific_style if specific_style else random.choice(STYLES)
    print(f"\n🎨 Generating sample for style: {style[:50]}...")
    
    # 1. Design Prompt
    design_prompt = f"""
    Act as an expert AI Art Director. Create a detailed prompt for an AI image generator (Imagen 3) for this article: "{title}".
    
    Selected Art Style: "{style}"

    Instructions:
    1. Analyze the title and pick a concrete, visual metaphor or subject (e.g., objects, landscapes, abstract forms) that represents the topic.
    2. Describe the lighting, color palette, and composition based on the selected style.
    3. Ensure the scene is visually striking and suitable for a blog hero image (16:9 aspect ratio).
    4. CRITICAL: DO NOT include any text, letters, or words in the image.
    5. Output ONLY the prompt string to be sent to the image generator.
    """
    
    try:
        prompt_resp = client.models.generate_content(model=MODEL_TEXT, contents=design_prompt)
        image_prompt = prompt_resp.text.strip()
        print(f"📝 Prompt: {image_prompt}")
        
        # 2. Generate Image
        image_resp = client.models.generate_images(
            model=MODEL_IMAGE,
            prompt=image_prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
        )
        
        if image_resp.generated_images:
            output_path = PROJECT_ROOT / "public" / "assets" / f"test_gen_{filename_suffix}.webp"
            
            # Save and optimize
            with open(output_path, "wb") as f:
                f.write(image_resp.generated_images[0].image.image_bytes)
            
            print(f"✅ Image saved to {output_path}")
            return str(output_path)
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

if __name__ == "__main__":
    title = "Google Launches WebMCP: Revolutionizing Web Performance?"
    
    print(f"Testing generation for: {title}")
    
    # Test new artistic styles
    styles_to_test = [
        "Vincent van Gogh style, thick impasto brushstrokes, swirling starry night sky patterns, vibrant yellow and blue palette, expressive oil painting",
        "Kim Jung Gi style, intricate black ink sketch, fish-eye perspective, dynamic composition, detailed character crowds, cross-hatching shade",
        "Digital CG Art, ArtStation trending, Octane render, hyper-detailed, dramatic lighting, volumetric fog, cinematic composition"
    ]
    
    for i, style in enumerate(styles_to_test):
        generate_sample(title, f"artistic_{i+1}", style)
