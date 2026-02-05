
import os
import glob

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

count = 0
for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---title:'):
        new_content = content.replace('---title:', '---\ntitle:', 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Repaired: {os.path.basename(filepath)}")
        count += 1

print(f"Repair complete. Fixed {count} files.")
