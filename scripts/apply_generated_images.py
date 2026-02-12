
import os
import json
import re
from pathlib import Path

PLAN_FILE = "image_generation_tasks.json"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def update_hero_image(filepath, new_image):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has heroImage
    if 'heroImage:' in content:
        # Replace heroImage value. Supports both single and double quotes.
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

def main():
    if not os.path.exists(PLAN_FILE):
        print(f"Plan file {PLAN_FILE} not found.")
        return

    with open(PLAN_FILE, 'r') as f:
        tasks = json.load(f)

    print(f"Applying generated images from {PLAN_FILE}...")
    
    updated_count = 0
    for task in tasks:
        # Get path to image in public folder
        rel_image_path = task['output_image_path'] # e.g. /assets/xyz.jpg
        local_image_path = PROJECT_ROOT / "public" / rel_image_path.lstrip('/')
        
        # Check if image has been generated
        if local_image_path.exists():
            # Update the markdown file
            md_path = PROJECT_ROOT / task['file_path']
            if md_path.exists():
                if update_hero_image(md_path, rel_image_path):
                    print(f"Updated: {md_path.name} -> {rel_image_path}")
                    updated_count += 1
            else:
                print(f"Markdown file not found: {md_path}")
        else:
            # Skip if image not yet generated
            pass

    print(f"Finished. Updated {updated_count} blog posts.")

if __name__ == "__main__":
    main()
