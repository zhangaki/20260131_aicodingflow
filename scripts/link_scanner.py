import os
import re

BLOG_DIR = "/Users/mac/code/super-individual/projects/seo-site/src/content/blog"

def scan_links():
    # 1. Get list of all valid slugs (filenames without .md)
    files = os.listdir(BLOG_DIR)
    valid_slugs = {f.replace(".md", "") for f in files if f.endswith(".md")}
    valid_slugs.add("") # For the root /blog/ or /blog link
    
    print(f"🔍 Found {len(valid_slugs)} valid blog posts.")
    
    broken_links = []
    
    # 2. Regex for internal links: (/blog/slug)
    # This matches (/blog/some-slug) or (/blog/some-slug/) or (/blog)
    link_pattern = re.compile(r'\(/(blog/[a-zA-Z0-9\-\\\/]*)\)')

    # 3. Iterate through files
    for filename in files:
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(BLOG_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        links = link_pattern.findall(content)
        
        for link in links:
            # Normalize the link: remove 'blog/' prefix and trailing slash
            slug = link.replace("blog/", "").strip("/")
            
            if slug not in valid_slugs:
                broken_links.append({
                    "file": filename,
                    "raw_link": f"/{link}",
                    "detected_slug": slug
                })

    # 4. Report
    if not broken_links:
        print("✅ No broken internal links found!")
    else:
        print(f"❌ Found {len(broken_links)} broken links:")
        for bl in broken_links:
            print(f"   - File: {bl['file']}")
            print(f"     Link: {bl['raw_link']}")
            print(f"     Slug: {bl['detected_slug']}")
            print("-" * 20)

if __name__ == "__main__":
    scan_links()
