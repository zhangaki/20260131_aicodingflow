
import os
import glob
import frontmatter

blog_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog'
assets_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/public' # Assets are in public/assets, path in yaml starts with /

files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

print("Checking for missing images...")
helpers_cnt = 0
for file_path in files:
    try:
        with open(file_path, 'r') as f:
            post = frontmatter.load(f)
            hero_image = post.metadata.get('heroImage')
            
            if hero_image:
                # heroImage is like /assets/image.jpg
                # absolute path should be invalid on local, but relative to public it is valid
                full_path = os.path.join(assets_dir, hero_image.lstrip('/'))
                if not os.path.exists(full_path):
                     print(f"MISSING IMAGE: {os.path.basename(file_path)} references {hero_image}")
                     helpers_cnt += 1
            else:
                 print(f"NO HERO IMAGE: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if helpers_cnt == 0:
    print("All referenced images exist.")
