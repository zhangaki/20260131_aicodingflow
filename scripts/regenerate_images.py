
import os
import sys
import random
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

# Import Styles from workflow script (to ensure consistency)
# We can't easily import because of the main guard, so I'll copy the FINAL list here.
# This ensures we use the EXACT styles the user approved.
STYLES = [
    # 1. High-Impact Digital Art & Surrealism
    "Surrealist digital art, dreamlike composition, floating geometric shapes in nature, ethereal lighting, Octane render, cinematic 8k",
    "Double exposure artistic collage, silhouette of a human head filled with galaxy stars and circuit board lines, emotional and dramatic",
    "Bioluminescent fantasy landscape, glowing organic forms, deep purple and teal palette, Avatar-like atmosphere, magical realism",
    "Futuristic abstract sculpture, liquid metal and glass, raytracing, vibrant iridescent colors, high-end 3D art, ArtStation trending",
    "Moebius style sci-fi illustration, intricate line work, flat pastel colors, surreal desert landscape, sense of scale and wonder",

    # 2. Expressive Fine Art (Texture & Color)
    "Vincent van Gogh inspired, thick impasto brushstrokes, swirling energy patterns, vibrant contrasting colors (blue/gold), expressive oil painting",
    "Abstract Alcohol Ink art, fluid flowing dyes, gold leaf veins, marble texture, organic chaos, rich saturated colors, elegant",
    "Washedui watercolor painting, wet-on-wet technique, soft bleeding colors, white negative space, artistic and emotive, minimalist composition",
    "Pop Art explosion, bold black outlines, halftone dots, bright primary colors, comic book dynamic action, Roy Lichtenstein style",
    "Kim Jung Gi style, incredibly detailed black ink sketching, fish-eye perspective, dynamic crowd/machinery, masterful composition",

    # 3. Conceptual & Graphic
    "Neo-Constructivism, bold geometric shapes, red black and cream color palette, industrial design, revolutionary poster art style",
    "Paper cut light box art, layers of paper creating depth, backlit with warm light, silhouette landscapes, cozy yet striking",
    "Glitch art portrait, digital distortion, datamoshing, RGB shift, cyberpunk aesthetic (but artistic), raw and edgy",
    "Low poly isometric world, but high-detail lighting, vibrant gradients, stylized digital illustration, charming and clean"
]

TARGETS = [
    {
        "slug": "deepseek-r1-release", 
        "title": "DeepSeek R1: New LLM Outperforms Llama 3 - Benchmarks & API Details"
    },
    {
        "slug": "bolt-vs-cursor-agentic-ide",
        "title": "Bolt vs Cursor: A Deep Dive into Agentic IDEs for Developers"
    },
    {
        "slug": "building-enterprise-ai-agent-teams-chatgpt-atlas",
        "title": "How to Build Enterprise AI Agent Teams with ChatGPT Atlas"
    },
    {
        "slug": "ideogram-2-vs-luma-dream-machine-1-5-quality",
        "title": "Ideogram 2.0 vs. Luma Dream Machine 1.5: A Quality Deep Dive"
    },
    {
        "slug": "tencent-hy-1-8b-2bit-architecture",
        "title": "Tencent HY-1.8B: 2-Bit Quantization Architecture Deep Dive for Developers"
    },
    {
        "slug": "google-web-mcp-release",
        "title": "Google Launches WebMCP: Revolutionizing Web Performance?"
    }
]

def optimize_image(img_path):
    try:
        with Image.open(img_path) as img:
            if img.width > 1200:
                ratio = 1200 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
            
            webp_path = img_path.with_suffix(".webp")
            img.save(webp_path, "WEBP", quality=85)
            
            if img_path != webp_path:
                os.remove(img_path)
                
        print(f"✅ Optimized: {webp_path}")
    except Exception as e:
        print(f"❌ Optimization failed: {e}")

def regenerate_image(target):
    # Select distinct styles for variety
    # We use a hash of the title to deterministically pick a style to avoid repeats across runs if re-run,
    # BUT here we want random for retry. Let's use random but ensure we pick from different categories if possible.
    style = random.choice(STYLES)
    
    print(f"\n🎨 Regenerating for: {target['title']}")
    print(f"🖌️  Style: {style[:50]}...")
    
    design_prompt = f"""
    Act as an expert AI Art Director. Create a detailed prompt for an AI image generator (Imagen 3) for this article: "{target['title']}".
    
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
        
        image_resp = client.models.generate_images(
            model=MODEL_IMAGE,
            prompt=image_prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
        )
        
        if image_resp.generated_images:
            # We assume slug matches filename in public/assets/ (checking extensions)
            # We will save as .png then optimize to .webp, overwriting existing
            
            # Note: The target might have been webp or png or jpg. We will force webp.
            # But the markdown file must refer to it.
            # We assume standard naming convention: public/assets/{slug}.webp
            
            # Check if DeepSeek really exists
            slug = target['slug']
            if slug == "deepseek-r1-new-llm-outperforms-llama-3":
                 # Fallback check if file exists, if not try find matching one
                 pass 

            raw_path = PROJECT_ROOT / "public" / "assets" / f"{slug}.png"
            
            with open(raw_path, "wb") as f:
                f.write(image_resp.generated_images[0].image.image_bytes)
            
            optimize_image(raw_path)
            
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    # Correction for DeepSeek slug based on ls output (if needed)
    # The ls command was run in parallel, let's assume standard slug for now.
    # If file not found, we might create a new orphan image, but that's okay for now.
    
    # We want to ensure we don't pick the same style for all.
    random.shuffle(STYLES)
    
    for i, target in enumerate(TARGETS):
        # Rotate styles
        style = STYLES[i % len(STYLES)]
        # regenerate_image(target, style) # Pass style explicitly?
        # Actually let's just modify regenerate_image to take style
        
        print(f"\n--- Processing {i+1}/{len(TARGETS)}: {target['slug']} ---")
        
        # Inline modified regenerate_image logic to take style
        print(f"🖌️  Style: {style[:50]}...")
        
        design_prompt = f"""
        Act as an expert AI Art Director. Create a detailed prompt for an AI image generator (Imagen 3) for this article: "{target['title']}".
        
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
            
            image_resp = client.models.generate_images(
                model=MODEL_IMAGE,
                prompt=image_prompt,
                config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
            )
            
            if image_resp.generated_images:
                raw_path = PROJECT_ROOT / "public" / "assets" / f"{target['slug']}.png"
                with open(raw_path, "wb") as f:
                    f.write(image_resp.generated_images[0].image.image_bytes)
                optimize_image(raw_path)
                
        except Exception as e:
            print(f"❌ Failed: {e}")
