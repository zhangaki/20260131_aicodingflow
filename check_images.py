
import os
import glob
import frontmatter

blog_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

print("All files and their hero images:")
for file_path in files:
    try:
        with open(file_path, 'r') as f:
            post = frontmatter.load(f)
            hero_image = post.metadata.get('heroImage', 'MISSING')
            print(f"- {os.path.basename(file_path)}: {hero_image}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
