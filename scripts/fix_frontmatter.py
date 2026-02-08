
import os
import re

blog_dir = "/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog"
assets_dir = "/Users/mac/code/super-individual/projects/20260131_seo-site/public/assets"
fallback_image = "/assets/blog-fallback.png"

# Get list of existing assets
existing_assets = os.listdir(assets_dir)

def title_case(s):
    return s.replace('-', ' ').title()

def get_best_image(slug):
    # Try exact match with .png
    if f"{slug}.png" in existing_assets:
        return f"/assets/{slug}.png"
    
    # Try slug without year
    slug_no_year = re.sub(r'-\d{4}$', '', slug)
    if f"{slug_no_year}.png" in existing_assets:
        return f"/assets/{slug_no_year}.png"
    
    # Try partial match (slug contains or is contained in asset name)
    for asset in existing_assets:
        if asset.endswith(('.png', '.jpg', '.webp')):
            asset_name = os.path.splitext(asset)[0]
            if slug_no_year in asset_name or asset_name in slug_no_year:
                 return f"/assets/{asset}"
                 
    return fallback_image

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    filename = os.path.basename(filepath)
    slug = filename.replace(".md", "").replace(".mdx", "")
    best_image = get_best_image(slug)

    # Check for frontmatter
    if content.startswith("---"):
        # Update heroImage if it exists and is potentially broken
        # This is a bit risky but we want to fix the 404s
        if "heroImage:" in content:
            current_image_match = re.search(r'heroImage:\s*[\'"]?([^\'"\n]+)[\'"]?', content)
            if current_image_match:
                current_image = current_image_match.group(1)
                # If current image doesn't exist in assets, replace it
                asset_path = os.path.join(assets_dir, os.path.basename(current_image))
                if not os.path.exists(asset_path):
                     content = re.sub(r'heroImage:\s*[\'"]?[^\'"\n]+[\'"]?', f'heroImage: "{best_image}"', content)
    else:
        # Should have been caught by previous run, but just in case
        title = title_case(slug)
        date_str = "Feb 01 2026"
        year_match = re.search(r'-(\d{4})$', slug)
        if year_match:
            date_str = f"Feb 01 {year_match.group(1)}"
            
        frontmatter = f"---\ntitle: '{title}'\ndescription: 'Autonomous intelligence trends and technical deep dives into the 2026-2030 landscape.'\npubDate: '{date_str}'\nheroImage: '{best_image}'\n---\n\n"
        content = frontmatter + content

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

files = [os.path.join(blog_dir, f) for f in os.listdir(blog_dir) if f.endswith(('.md', '.mdx'))]
fixed_count = 0
for f in files:
    if fix_file(f):
        fixed_count += 1

print(f"Updated {fixed_count} files with better images.")
