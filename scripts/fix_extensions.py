
import os
import re
import subprocess

assets_dir = "/Users/mac/code/super-individual/projects/20260131_seo-site/public/assets"
blog_dir = "/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog"

def fix_extensions():
    renamed_files = {}
    
    # 1. Identify and rename files
    for filename in os.listdir(assets_dir):
        if not filename.endswith(".png"): continue
        
        filepath = os.path.join(assets_dir, filename)
        try:
            output = subprocess.check_output(["file", filepath]).decode('utf-8')
            if "JPEG image data" in output:
                new_filename = filename.replace(".png", ".jpg")
                new_filepath = os.path.join(assets_dir, new_filename)
                
                # If .jpg already exists, we might have a duplicate name but different extension
                # for now let's just rename
                if not os.path.exists(new_filepath):
                    os.rename(filepath, new_filepath)
                    renamed_files[f"/assets/{filename}"] = f"/assets/{new_filename}"
                    print(f"Renamed {filename} -> {new_filename}")
                else:
                    # If it already exists, just record the mapping and delete the .png one
                    # to avoid confusion
                    os.remove(filepath)
                    renamed_files[f"/assets/{filename}"] = f"/assets/{new_filename}"
                    print(f"Found existing {new_filename}, deleted {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # 2. Update blog posts
    updated_posts = 0
    for filename in os.listdir(blog_dir):
        if not filename.endswith((".md", ".mdx")): continue
        
        filepath = os.path.join(blog_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        for old_ref, new_ref in renamed_files.items():
            content = content.replace(f'heroImage: "{old_ref}"', f'heroImage: "{new_ref}"')
            content = content.replace(f"heroImage: '{old_ref}'", f"heroImage: '{new_ref}'")
            
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            updated_posts += 1
            
    print(f"Updated {updated_posts} blog posts with new image extensions.")

if __name__ == "__main__":
    fix_extensions()
