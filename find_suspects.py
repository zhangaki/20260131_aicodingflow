
import os
import glob
import frontmatter

blog_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog'
assets_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/public'

files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

# Maps size -> list of (file_name, assets_path)
suspects = {}

# Known placeholder sizes from `ls -l` output
# 34890, 33136, 32040, 28687, 38690
target_sizes = [34890, 33136, 32040, 28687, 38690]

print("Checking for placeholder images based on file size...")
for file_path in files:
    try:
        with open(file_path, 'r') as f:
            post = frontmatter.load(f)
            hero_image = post.metadata.get('heroImage')
            
            if hero_image:
                full_path = os.path.join(assets_dir, hero_image.lstrip('/'))
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                    if size in target_sizes:
                         print(f"SUSPECT: {os.path.basename(file_path)} -> {hero_image} ({size} bytes)")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
