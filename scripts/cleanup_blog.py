
import os
import re

blog_dir = "/Users/mac/code/super-individual/projects/seo-site/src/content/blog"
assets_dir = "/Users/mac/code/super-individual/projects/seo-site/public/assets"
fallback_image = "/assets/blog-fallback.png"

# Get list of existing assets
existing_assets = os.listdir(assets_dir)

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

def cleanup_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    filename = os.path.basename(filepath)
    slug = filename.replace(".md", "").replace(".mdx", "")
    best_image = get_best_image(slug)

    # 1. Remove all frontmatter blocks and extract data from them
    frontmatter_blocks = re.findall(r'^---(.*?)---', content, re.DOTALL | re.MULTILINE)
    
    title = slug.replace('-', ' ').title()
    description = "Autonomous intelligence trends and technical deep dives into the 2026-2030 landscape."
    pub_date = "Feb 01 2026"
    hero_image = best_image

    if frontmatter_blocks:
        # Use the first block as base but try to find more specific info in any block
        for block in frontmatter_blocks:
            t_match = re.search(r'title:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
            if t_match: title = t_match.group(1).strip()
            
            d_match = re.search(r'description:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
            if d_match: description = d_match.group(1).strip()
            
            date_match = re.search(r'pubDate:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
            if date_match: pub_date = date_match.group(1).strip()
            
            h_match = re.search(r'heroImage:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
            if h_match: 
                candidate_img = h_match.group(1).strip()
                # Check if candidate image exists
                if os.path.exists(os.path.join(assets_dir, os.path.basename(candidate_img))):
                    hero_image = candidate_img

    # 2. Strip all frontmatter blocks from content
    content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL | re.MULTILINE)
    
    # 3. Strip leading/trailing whitespace and weird markers like "md" or "markdown" at the top
    content = content.strip()
    while content.startswith(('md', 'markdown')):
         content = re.sub(r'^(md|markdown)\s*\n?', '', content, count=1).strip()

    # 4. Remove any remaining frontmatter blocks if they were nested or missed by regex (greedy)
    # Be careful not to remove horizontal rules (---) that are used for styling
    # But usually horizontal rules have space before/after. 
    # Let's just focus on the top blocks we already removed.

    # 5. Reconstruct the file with clean frontmatter
    new_frontmatter = f"""---
title: "{title}"
description: "{description}"
pubDate: "{pub_date}"
heroImage: "{hero_image}"
---

"""
    new_content = new_frontmatter + content

    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

files = [os.path.join(blog_dir, f) for f in os.listdir(blog_dir) if f.endswith(('.md', '.mdx'))]
fixed_count = 0
for f in files:
    try:
        if cleanup_file(f):
            fixed_count += 1
    except Exception as e:
        print(f"Error fixing {f}: {e}")

print(f"Cleaned up {fixed_count} files.")
