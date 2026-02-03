
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

def is_fence(line):
    return line.strip().startswith('```')

def is_safe_header(line):
    # Only treat ##, ###, #### as definitive headers to break code blocks
    # Single # is too risky (often comments in Python/Bash)
    return line.startswith('##')

modified_files = 0

for filepath in files:
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    in_block = False
    file_modified = False
    
    for i, line in enumerate(lines):
        if is_fence(line):
            in_block = not in_block
            new_lines.append(line)
        elif in_block and is_safe_header(line):
            # FOUND A DEFINITIVE HEADER INSIDE A CODE BLOCK
            # Insert a closing fence before this line
            print(f"Fixing {os.path.basename(filepath)}: Closing block before '{line.strip()}'")
            new_lines.append("```\n")
            new_lines.append("\n") # Add a blank line for breathing room
            new_lines.append(line)
            in_block = False
            file_modified = True
        else:
            new_lines.append(line)
            
    # Check for EOF violation
    if in_block:
        print(f"Fixing {os.path.basename(filepath)}: Closing block at EOF")
        if not new_lines[-1].endswith('\n'):
            new_lines.append('\n')
        new_lines.append("```\n")
        file_modified = True
        
    if file_modified:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        modified_files += 1

print(f"Script finished. Modified {modified_files} files.")
