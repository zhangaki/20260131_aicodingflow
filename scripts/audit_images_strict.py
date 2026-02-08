
import os
import re
import glob

BLOG_DIR = "/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog"
ASSETS_DIR = "/Users/mac/code/super-individual/projects/20260131_seo-site/public" # Base dir for assets

def analyze_assets_strict():
    broken_links = []
    placeholder_users = []
    
    print("--- Strict Image Audit ---")
    for filepath in glob.glob(os.path.join(BLOG_DIR, "*.md")):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        filename = os.path.basename(filepath)
        match = re.search(r'heroImage:\s*"?([^"\n]+)"?', content)
        
        if match:
            image_path = match.group(1).strip()
            
            # Check for generic placeholders explicitly
            if "placeholder" in image_path or "fallback" in image_path:
                placeholder_users.append((filename, image_path))
                continue

            # Verify file actually exists
            # image_path usually starts with /assets/... so we join with public dir
            full_path = os.path.join(ASSETS_DIR, image_path.lstrip('/'))
            
            if not os.path.exists(full_path):
                broken_links.append((filename, image_path))
        else:
            broken_links.append((filename, "MISSING"))

    return broken_links, placeholder_users

if __name__ == "__main__":
    broken, placeholders = analyze_assets_strict()
    
    print(f"\n[CRITICAL] Broken Links / Missing Files: {len(broken)}")
    for post, path in broken:
        print(f"  - {post} -> {path} (File not found)")

    print(f"\n[WARNING] Using Placeholder/Fallback: {len(placeholders)}")
    for post, path in placeholders:
        print(f"  - {post} -> {path}")
