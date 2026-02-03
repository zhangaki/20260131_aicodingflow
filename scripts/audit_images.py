
import os
import re
import glob

BLOG_DIR = "/Users/mac/code/super-individual/projects/seo-site/src/content/blog"
ASSETS_DIR = "/Users/mac/code/super-individual/projects/seo-site/public/assets"

def analyze_assets():
    # 1. Scan all blog posts for image usage
    used_images = set()
    posts_needing_images = []
    
    print("--- Scanning Blog Posts ---")
    for filepath in glob.glob(os.path.join(BLOG_DIR, "*.md")):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        filename = os.path.basename(filepath)
        match = re.search(r'heroImage:\s*"?([^"\n]+)"?', content)
        
        if match:
            image_path = match.group(1).strip()
            # Normalize path (remove leading /)
            clean_path = image_path.lstrip('/')
            
            # Check if using fallback/placeholder or dead link
            if "fallback" in image_path or "placeholder" in image_path:
                posts_needing_images.append((filename, image_path))
            else:
                # Add to used set if it's in our assets folder
                if clean_path.startswith('assets/'):
                    # Store filename only for comparison
                    used_images.add(os.path.basename(clean_path))
        else:
            posts_needing_images.append((filename, "MISSING"))

    # 2. Scan assets directory for zombie files
    print("\n--- Scanning Asset Directory ---")
    all_assets = set()
    for filepath in glob.glob(os.path.join(ASSETS_DIR, "*")):
        if os.path.isfile(filepath) and not filepath.endswith('.DS_Store'):
            all_assets.add(os.path.basename(filepath))
            
    zombie_images = all_assets - used_images
    
    # Exclude system files or manual keeps if any
    zombie_images = {img for img in zombie_images if img not in ['favicon.svg', 'robots.txt']}

    return posts_needing_images, zombie_images

if __name__ == "__main__":
    needs_img, zombies = analyze_assets()
    
    print(f"\n[REPORT] Posts needing custom images: {len(needs_img)}")
    for post, current in needs_img:
        print(f"  - {post} (Current: {current})")
        
    print(f"\n[REPORT] Zombie images found: {len(zombies)}")
    for img in zombies:
        print(f"  - {img}")
