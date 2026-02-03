
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

print("Scanning for unclosed code blocks...")
issues_found = False

for file_path in files:
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Count occurrences of triple backticks
    # Note: This is a heuristic. It might fail on nested code blocks or escaped backticks, 
    # but it's good for catching simple missing closing tags.
    matches = re.findall(r'^```', content, re.MULTILINE)
    count = len(matches)
    
    if count % 2 != 0:
        issues_found = True
        print(f"SUSPECT: {os.path.basename(file_path)} has odd number of code fences ({count})")
        
        # Try to identify which block is unclosed
        lines = content.splitlines()
        fence_cnt = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                fence_cnt += 1
        
        if fence_cnt % 2 != 0:
             print(f"  -> Confirmed by line scan: {fence_cnt} fences found.")

if not issues_found:
    print("ALL CLEAR: No unclosed code blocks detected in other files.")
