
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

def is_table_delimiter(line):
    # Matches | --- | --- | patterns roughly
    # Must contain at least one | and one ---
    return '|' in line and '---' in line and len(line.strip()) > 5

def audit_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    filename = os.path.basename(filepath)
    issues = []
    
    # 1. Check for mismatched code fences
    fence_count = 0
    for line in lines:
        if line.strip().startswith('```'):
            fence_count += 1
            
    if fence_count % 2 != 0:
        issues.append(f"Odd number of code fences ({fence_count})")
        
    # 2. Check for missing table headers
    for i, line in enumerate(lines):
        if is_table_delimiter(line):
            # Check previous line
            if i == 0:
                issues.append(f"Table delimiter at line {i+1} creates table without header (at start of file)")
                continue
                
            prev_line = lines[i-1].strip()
            # Heuristic: Header line usually contains pipes |, but not dashes --- (unless escaped)
            # And it shouldn't be empty
            if not prev_line:
                issues.append(f"Table delimiter at line {i+1} preceded by empty line (Missing Header?)")
            elif '|' not in prev_line:
                 issues.append(f"Table delimiter at line {i+1} preceded by non-pipe line: '{prev_line[:20]}...' (Missing Header?)")

    if issues:
        print(f"File: {filename}")
        for issue in issues:
            print(f"  - {issue}")

print("Scanning for remaining layout issues...")
for f in files:
    audit_file(f)
print("Scan complete.")
