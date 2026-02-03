
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

def is_delimiter(line):
    # Detects | --- | --- |
    return '|' in line and set(line.strip().replace('|', '').replace(' ', '')) == {'-'}

def generate_header(delimiter_line):
    # Count columns based on pipes
    # Example: |---|---| has 3 pipes, creating 2 columns? Or | --- | --- | has 4 pipes -> 3 cols?
    # Let's count the '---' blocks
    cols = delimiter_line.count('-|-') + 1 # Rough heuristic
    # Better: split by pipe
    parts = [p for p in delimiter_line.split('|') if p.strip()]
    col_count = len(parts)
    
    headers = []
    for i in range(col_count):
        if i == 0: headers.append("Category/Metric")
        elif i == 1: headers.append("Description/Value")
        else: headers.append(f"Notes {i}")
        
    return "| **" + "** | **".join(headers) + "** |\n"

modified_count = 0

for filepath in files:
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    file_modified = False
    
    for i, line in enumerate(lines):
        # We process line by line.
        # If we see a delimiter line, check the END of new_lines
        if is_delimiter(line):
            # Check if appropriate header exists
            # We look at new_lines[-1]
            if new_lines and not new_lines[-1].strip():
                # Previous line is empty! Insert header.
                print(f"Fixing table in {os.path.basename(filepath)} at line {i+1}")
                header = generate_header(line)
                new_lines.append(header)
                new_lines.append(line)
                file_modified = True
            elif new_lines and '|' not in new_lines[-1]:
                 # Previous line exists but isn't a pipe row. Insert header.
                 # ACTUALLY: Sometimes users write text right before table. Markdown requires empty line usually.
                 # BUT for table to render, Header is mandatory.
                 print(f"Fixing table in {os.path.basename(filepath)} at line {i+1} (No header row found)")
                 header = generate_header(line)
                 new_lines.append(header)
                 new_lines.append(line)
                 file_modified = True
            else:
                # Looks like it has a header
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    if file_modified:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        modified_count += 1

print(f"Fixed tables in {modified_count} files.")
