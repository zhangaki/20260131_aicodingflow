
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

def is_fence(line):
    return line.strip().startswith('```')

def is_header(line):
    # Only detect top-level headers, identifying them specifically at start of line
    return line.startswith('#')

def scan_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    in_block = False
    start_line_idx = -1
    
    fixes_needed = []

    for i, line in enumerate(lines):
        if is_fence(line):
            if in_block:
                # Normal closing
                in_block = False
                start_line_idx = -1
            else:
                # Opening
                in_block = True
                start_line_idx = i
        
        elif in_block:
            # We are inside a block. Check for illegal content that suggests we missed a close.
            
            # 1. Hit a Header
            if is_header(line):
                print(f"[VIOLATION] File: {os.path.basename(filepath)}")
                print(f"    Code block started at line {start_line_idx + 1}")
                print(f"    Hit HEADER at line {i + 1}: {line.strip()}")
                print(f"    -> Suggestion: Close block at line {i}")
                fixes_needed.append((i, "header"))
                in_block = False # Reset state to avoid cascading errors
                
            # 2. Hit another Fence (Wait, logic above handles this as "Normal closing"? No.)
            # If we see ```python inside a block, that's ambiguous. 
            # Standard markdown parser treats the next ``` as close.
            # So ` ```python ... ```javascript ` -> The second one CLOSES the first.
            # But visually it looks wrong if the user intended two blocks.
            # However, detecting "Start of new block" vs "End of old block" is hard if they use the same ```
            
            # Let's rely on Indentation? No.
            
            # Let's check for "Text that looks like analysis" followed by a new block? Hard.
            pass

    if in_block:
        print(f"[VIOLATION] File: {os.path.basename(filepath)}")
        print(f"    Code block started at line {start_line_idx + 1}")
        print(f"    Hit End of File without closing")
        print(f"    -> Suggestion: Close block at end of file")
        fixes_needed.append((len(lines), "eof"))

    return fixes_needed

print("Deep scanning for unclosed code blocks...")
for f in files:
    scan_file(f)
