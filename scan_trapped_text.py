
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

def analyze_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    in_code_block = False
    block_start_line = 0
    suspicious_blocks = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        if line_stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                block_start_line = i
            else:
                in_code_block = False
                # Block ended. Let's analyze the content of this block.
                block_content = lines[block_start_line+1 : i]
                
                # Check for "Text Trap" pattern:
                # Code...
                # (Blank Line)
                # Prose text...
                # ```
                
                # Heuristic: Look for the last N lines. If they look like pure prose.
                # Prose criteria: No indentation, long lines, sentences.
                
                consecutive_text_lines = 0
                text_start_index = -1
                
                for j in range(len(block_content) - 1, -1, -1):
                    l = block_content[j].rstrip()
                    if not l: # Blank line
                        if consecutive_text_lines > 0:
                            # We found a block of text at the end, separated by blank line.
                            # Assume this is the trapped text.
                            text_start_index = j + 1
                            break # Found the separation
                        else:
                            continue # Just trailing blank lines
                    
                    # Analyze line 'l'
                    # If it looks like code, break.
                    is_code_like = (
                        l.startswith('    ') or l.startswith('\t') or # Indented
                        l.startswith('def ') or l.startswith('import ') or l.startswith('class ') or # Keywords
                        ' = ' in l or 'return ' in l or # Syntax
                        l.endswith(';') or l.endswith('{') or l.endswith('}') or # Syntax
                        len(l) < 20 # Short lines might be code
                    )
                    
                    if is_code_like:
                        # Hit code. Stop.
                        break
                    
                    consecutive_text_lines += 1
                
                if text_start_index != -1 and consecutive_text_lines > 0:
                    # We found trapped text!
                    trapped_text = "".join(block_content[text_start_index:])
                    if len(trapped_text) > 50: # Threshold to ignore small comments
                        suspicious_blocks.append({
                            'start': block_start_line + 1,
                            'end': i + 1,
                            'trapped_start_rel': text_start_index,
                            'trapped_preview': trapped_text[:100].replace('\n', ' ')
                        })

    if suspicious_blocks:
        print(f"File: {os.path.basename(filepath)}")
        for b in suspicious_blocks:
            print(f"  - Block {b['start']}-{b['end']} seems to trap text starting at line {b['start'] + b['trapped_start_rel'] + 1}")
            print(f"    Preview: {b['trapped_preview']}...")

print("Scanning for 'Trapped Text' inside code blocks...")
for f in files:
    analyze_file(f)
print("Scan complete.")
