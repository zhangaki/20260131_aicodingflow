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
        ext = os.path.splitext(img_path)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            return None

        with Image.open(img_path) as img:
            # Original dimensions
            width, height = img.size
            
            # Resize if too large
            if width > MAX_WIDTH:
                new_height = int(height * (MAX_WIDTH / width))
                img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)
                print(f"Resized {os.path.basename(img_path)}: {width}x{height} -> {MAX_WIDTH}x{new_height}")

            # Generate output path
            output_path = os.path.splitext(img_path)[0] + ".webp"
            
            # Save as WebP
            img.save(output_path, "WEBP", quality=QUALITY)
            
            # Delete original if it's not the same file (e.g. if we converted jpg -> webp)
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
            if hero and (hero.endswith('.jpg') or hero.endswith('.png')):
                new_hero = os.path.splitext(hero)[0] + ".webp"
                post['heroImage'] = new_hero
                with open(f, 'wb') as out:
                    frontmatter.dump(post, out)
                count += 1
        except Exception as e:
            print(f"Error updating markdown {f}: {e}")
    print(f"Updated {count} markdown files to WebP.")

def main():
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        images.extend(glob.glob(os.path.join(ASSETS_DIR, ext)))
    
    print(f"Found {len(images)} images to optimize.")
    
    optimized_count = 0
    for img_path in images:
        result = optimize_image(img_path)
        if result:
            optimized_count += 1
            
    print(f"Successfully optimized {optimized_count} images.")
    
    update_markdown_links()

if __name__ == "__main__":
    main()
