#!/usr/bin/env python3
"""
image_manager.py

Unified tool for managing blog assets.
Merges functionality from:
- optimize_assets.py (WebP conversion, resizing)
- apply_generated_images.py (Updating markdown with new images)
- update_covers.py (Manual cover updates)
- audit_images.py (Finding missing/unused images)

Usage:
    python scripts/image_manager.py --action optimize
    python scripts/image_manager.py --action apply
    python scripts/image_manager.py --action audit
    python scripts/image_manager.py --action clean
"""

import os
import glob
import json
import re
import argparse
import sys
from pathlib import Path
from PIL import Image
try:
    from google import genai
    from dotenv import load_dotenv
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = PROJECT_ROOT / "src" / "content" / "blog"
ASSETS_DIR = PROJECT_ROOT / "public" / "assets"
PLAN_FILE = PROJECT_ROOT / "scripts" / "image_generation_tasks.json"

MAX_WIDTH = 1280
QUALITY = 80

# ---------------------------------------------------------------------------
# 1. OPTIMIZE LOGIC (from optimize_assets.py)
# ---------------------------------------------------------------------------

def optimize_image(img_path):
    """Converts image to WebP and resizes if necessary."""
    try:
        with Image.open(img_path) as img:
            format = img.format
            width, height = img.size
            
            is_wrong_format = (os.path.splitext(img_path)[1].lower() == '.webp' and format != 'WEBP')
            is_too_large = width > MAX_WIDTH
            is_compressible = (os.path.splitext(img_path)[1].lower() in ['.jpg', '.jpeg', '.png'])
            
            if not (is_wrong_format or is_too_large or is_compressible):
                return None

            if width > MAX_WIDTH:
                new_height = int(height * (MAX_WIDTH / width))
                img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)
                print(f"  Resizing: {width}x{height} -> {MAX_WIDTH}x{new_height}")

            output_path = os.path.splitext(img_path)[0] + ".webp"
            img.save(output_path, "WEBP", quality=QUALITY)
            print(f"  Optimized: {os.path.basename(img_path)}")
            
            if str(img_path) != str(output_path):
                os.remove(img_path)
            
            return output_path
    except Exception as e:
        print(f"  Error optimizing {img_path}: {e}")
        return None

def update_markdown_links():
    """Updates all markdown files to point to .webp images."""
    files = list(BLOG_DIR.glob("*.md"))
    count = 0
    hero_pattern = re.compile(r"^(heroImage:\s*[\"']?)(.*?)([\"']?)$", re.MULTILINE)
    
    for f_path in files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = hero_pattern.search(content)
            if match:
                prefix, path, suffix = match.groups()
                if path and (path.endswith('.jpg') or path.endswith('.png')):
                    new_path = os.path.splitext(path)[0] + ".webp"
                    new_content = content[:match.start(2)] + new_path + content[match.end(2):]
                    with open(f_path, 'w', encoding='utf-8') as f_out:
                        f_out.write(new_content)
                    count += 1
        except Exception as e:
            print(f"  Error updating markdown {f_path.name}: {e}")
    
    if count > 0:
        print(f"Updated {count} markdown files to point to .webp images.")

def run_optimize():
    print("=== Optimizing Assets ===")
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        images.extend(glob.glob(str(ASSETS_DIR / ext)))
    
    images = list(set(images))
    print(f"Checking {len(images)} images...")
    
    optimized_count = 0
    for img_path in images:
        if optimize_image(img_path):
            optimized_count += 1
            
    print(f"Optimized {optimized_count} images.")
    update_markdown_links()

# ---------------------------------------------------------------------------
# 2. APPLY LOGIC (from apply_generated_images.py & update_covers.py)
# ---------------------------------------------------------------------------

def update_hero_image_in_file(filepath, new_image):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'heroImage:' in content:
        updated = re.sub(
            r'heroImage:\s*["\'][^"\']*["\']',
            f'heroImage: "{new_image}"',
            content
        )
        if updated != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated)
            return True
    return False

def run_apply():
    print("=== Applying Generated Images ===")
    if not os.path.exists(PLAN_FILE):
        print(f"Plan file {PLAN_FILE} not found.")
        return

    with open(PLAN_FILE, 'r') as f:
        tasks = json.load(f)

    updated_count = 0
    for task in tasks:
        rel_image_path = task['output_image_path']
        # Check if corresponding WebP exists (since optimization might have run)
        webp_path = os.path.splitext(rel_image_path)[0] + ".webp"
        
        final_rel_path = rel_image_path
        if (PROJECT_ROOT / "public" / webp_path.lstrip('/')).exists():
            final_rel_path = webp_path
        
        md_path = PROJECT_ROOT / task['file_path']
        if md_path.exists():
            if update_hero_image_in_file(md_path, final_rel_path):
                print(f"  Updated: {md_path.name} -> {final_rel_path}")
                updated_count += 1
    
    print(f"Applied images to {updated_count} posts.")

# ---------------------------------------------------------------------------
# 3. AUDIT LOGIC (from audit_images.py)
# ---------------------------------------------------------------------------

def run_audit(clean=False):
    print("=== Auditing Images ===")
    used_images = set()
    posts_needing_images = []
    
    # Scan Posts
    for filepath in BLOG_DIR.glob("*.md"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if match:
            image_path = match.group(1).strip()
            clean_path = image_path.lstrip('/')
            
            if "fallback" in image_path or "placeholder" in image_path:
                posts_needing_images.append((filepath.name, image_path))
            else:
                # Check for "Suspect" images (known placeholder sizes)
                full_path = ASSETS_DIR / os.path.basename(clean_path)
                if full_path.exists():
                    size = full_path.stat().st_size
                    # Common placeholder sizes from find_suspects.py
                    if size in [34890, 33136, 32040, 28687, 38690]:
                         posts_needing_images.append((filepath.name, f"{image_path} (SUSPECT SIZE: {size})"))
                    
                    used_images.add(os.path.basename(clean_path))
                else:
                    posts_needing_images.append((filepath.name, f"{image_path} (MISSING)"))
        else:
            posts_needing_images.append((filepath.name, "MISSING"))

    # Scan Assets
    all_assets = set()
    for filepath in ASSETS_DIR.glob("*"):
        if filepath.is_file() and filepath.name != '.DS_Store':
            all_assets.add(filepath.name)
            
    zombie_images = all_assets - used_images
    zombie_images = {img for img in zombie_images if img not in ['favicon.svg', 'robots.txt', 'blog-placeholder-about.webp']}
    
    print(f"\n[REPORT] Posts needing images: {len(posts_needing_images)}")
    for post, current in posts_needing_images:
        print(f"  - {post} (Current: {current})")
        
    print(f"\n[REPORT] Zombie images found: {len(zombie_images)}")
    for img in zombie_images:
        print(f"  - {img}")
        
    if clean and zombie_images:
        print("\nDeleting zombie images...")
        count = 0
        for img in zombie_images:
            try:
                os.remove(ASSETS_DIR / img)
                print(f"  Deleted: {img}")
                count += 1
            except Exception as e:
                print(f"  Error deleting {img}: {e}")
        print(f"Deleted {count} unused images.")

# ---------------------------------------------------------------------------
# 4. GENERATE LOGIC (from generate_images_gemini.py)
# ---------------------------------------------------------------------------

class GeminiImageGenerator:
    def __init__(self):
        if not HAS_GENAI:
            raise ImportError("google-genai or python-dotenv not installed.")
        
        load_dotenv()
        api_key = os.getenv("Gemini_api_key")
        if not api_key:
             # Try fallback path
            env_path = Path("/Users/mac/code/super-individual/.env")
            if env_path.exists():
                load_dotenv(env_path)
                api_key = os.getenv("Gemini_api_key")
        
        if not api_key:
            raise ValueError("Gemini API key not found.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = "imagen-4.0-fast-generate-001"

    def generate(self, prompt, output_path):
        try:
            print(f"Generating: {prompt[:50]}...")
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=prompt,
                config=genai.types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9", 
                )
            )
            if response.generated_images:
                image_bytes = response.generated_images[0].image.image_bytes
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Saved to {output_path}")
                return True
            return False
        except Exception as e:
            print(f"Generation Error: {e}")
            return False

def run_generate(prompt, output):
    if not prompt or not output:
        print("Error: --prompt and --output are required for 'generate' action.")
        return
    
    try:
        gen = GeminiImageGenerator()
        gen.generate(prompt, output)
        # Auto-optimize after generation
        result = optimize_image(output)
        if result:
            print(f"Auto-optimized to: {result}")
    except Exception as e:
        print(f"Failed to initialize generator: {e}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Unified Image Manager")
    parser.add_argument("--action", choices=["optimize", "apply", "audit", "clean", "generate"], required=True, help="Action to perform")
    parser.add_argument("--prompt", help="Prompt for image generation")
    parser.add_argument("--output", help="Output path for generated image")
    args = parser.parse_args()
    
    if args.action == "optimize":
        run_optimize()
    elif args.action == "apply":
        run_apply()
    elif args.action == "audit":
        run_audit(clean=False)
    elif args.action == "clean":
        run_audit(clean=True)
    elif args.action == "generate":
        run_generate(args.prompt, args.output)

if __name__ == "__main__":
    main()
