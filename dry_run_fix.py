
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

print("Dry run fixing code blocks...")

for file_path in files:
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    fence_indices = [i for i, line in enumerate(lines) if line.strip().startswith('```')]
    
    if len(fence_indices) % 2 != 0:
        last_fence_idx = fence_indices[-1]
        
        # Look for the insertion point
        insert_idx = -1
        for i in range(last_fence_idx + 1, len(lines)):
            if lines[i].strip().startswith('#'):
                insert_idx = i
                break
        
        if insert_idx == -1:
            insert_idx = len(lines) # Append to end
            
        print(f"File: {os.path.basename(file_path)}")
        print(f"  Last fence at line {last_fence_idx + 1}")
        print(f"  Proposing close at line {insert_idx + 1}")
        print(f"  Context: {lines[insert_idx-1].strip() if insert_idx > 0 else 'START'}  --> [CLOSE] --> {lines[insert_idx].strip() if insert_idx < len(lines) else 'EOF'}")
