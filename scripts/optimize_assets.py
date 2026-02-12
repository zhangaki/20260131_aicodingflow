import os
import glob
from PIL import Image
import frontmatter
from pathlib import Path

ASSETS_DIR = "public/assets"
CONTENT_DIR = "src/content/blog"
MAX_WIDTH = 1280
QUALITY = 80

def optimize_image(img_path):
    """Converts image to WebP and resizes if necessary."""
    try:
        # Open the image to check actual format
        with Image.open(img_path) as img:
            format = img.format
            width, height = img.size
            
            # Decide if we need to process this file
            is_wrong_format = (os.path.splitext(img_path)[1].lower() == '.webp' and format != 'WEBP')
            is_too_large = width > MAX_WIDTH
            is_compressible = (os.path.splitext(img_path)[1].lower() in ['.jpg', '.jpeg', '.png'])
            
            if not (is_wrong_format or is_too_large or is_compressible):
                return None

            # Resize if too large
            if width > MAX_WIDTH:
                new_height = int(height * (MAX_WIDTH / width))
                img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)
                print(f"Resizing {os.path.basename(img_path)}: {width}x{height} -> {MAX_WIDTH}x{new_height}")

            # Generate output path
            output_path = os.path.splitext(img_path)[0] + ".webp"
            
            # Save as WebP
            img.save(output_path, "WEBP", quality=QUALITY)
            print(f"Optimized {os.path.basename(img_path)} (Actual format: {format})")
            
            # Delete original if it's not the same file
            # Or if it was a mismatched webp (Pillow saves to temporary then overwrites sometimes)
            if img_path != output_path:
                os.remove(img_path)
            
            return output_path
    except Exception as e:
        print(f"Error optimizing {img_path}: {e}")
        return None

def update_markdown_links():
    """Updates all markdown files to point to .webp images."""
    files = glob.glob(os.path.join(CONTENT_DIR, "*.md"))
    count = 0
    for f in files:
        try:
            post = frontmatter.load(f)
            hero = post.get('heroImage', '')
            # Now we only update if it still ends in .jpg or .png
            if hero and (hero.endswith('.jpg') or hero.endswith('.png')):
                new_hero = os.path.splitext(hero)[0] + ".webp"
                post['heroImage'] = new_hero
                with open(f, 'wb') as out:
                    frontmatter.dump(post, out)
                count += 1
        except Exception as e:
            print(f"Error updating markdown {f}: {e}")
    if count > 0:
        print(f"Updated {count} markdown files to WebP.")

def main():
    images = []
    # Include .webp in search list to check for format mismatches
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        images.extend(glob.glob(os.path.join(ASSETS_DIR, ext)))
    
    # Use set to avoid duplicates
    images = list(set(images))
    print(f"Checking {len(images)} images for optimization...")
    
    optimized_count = 0
    for img_path in images:
        result = optimize_image(img_path)
        if result:
            optimized_count += 1
            
    print(f"Successfully optimized {optimized_count} images.")
    
    update_markdown_links()

if __name__ == "__main__":
    main()
