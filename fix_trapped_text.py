
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

def fix_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    in_code_block = False
    block_start_line = 0
    # Store pending changes to apply after iteration, or apply on the fly
    # Applying on the fly is tricky if we insert lines. 
    # Let's rebuild the lines array.
    
    i = 0
    modified = False
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
            else:
                in_code_block = False
            new_lines.append(line)
            i += 1
            continue
            
        if in_code_block:
            # We are inside a block. Check if this line looks like the start of "Trapped Prose".
            # Heuristic: 
            # 1. Previous line was blank (or we are at start of trapped block)
            # 2. This line is NOT indented
            # 3. This line does NOT look like code (no special chars like = { } ; )
            # 4. It starts with a capital letter or bold **
            
            is_blank = not stripped
            if is_blank:
                new_lines.append(line)
                i += 1
                continue
                
            # Check previous line in NEW_LINES to see if it was blank
            prev_was_blank = len(new_lines) > 0 and not new_lines[-1].strip()
            
            is_indented = line.startswith('    ') or line.startswith('\t')
            is_comment = stripped.startswith('#') or stripped.startswith('//')
            
            # Strong signal: "The Logic Explained", "**Savings**", "This pseudo-code"
            strong_start = (
                "**" in stripped or 
                stripped.startswith("The ") or 
                stripped.startswith("This ") or
                stripped.startswith("For ") or
                stripped.startswith("By ") or
                stripped.startswith("Note ") or
                stripped.startswith("It ")
            )
            
            # If previous line was blank AND this line looks like prose -> Insert closing fence
            if prev_was_blank and not is_indented and not is_comment and strong_start:
                 print(f"Fixing trapped text in {os.path.basename(filepath)} at line {i+1}: '{stripped[:30]}...'")
                 # Check if we need to remove a trailing fence later?
                 # Usually the block closes later. If we close it HERE, the later closing fence becomes an opening fence for subsequent text?
                 # No, simply inserting ``` here closes the Code Block.
                 # The EXISTING closing fence later will then OPEN a new code block?
                 # YES, that is a risk.
                 # If we close it here, the text becomes prose.
                 # Then the original closing ``` will toggle mode again.
                 # So we basically need to ensure that the original closing ``` is removed OR we open a new block if code follows.
                 
                 # Simpler strategy: Just close the block here. 
                 # If the original closing fence exists, we should probably comment it out or remove it?
                 # Or: Insert ``` here. The text follows. Then the original ``` is encountered.
                 # Text...
                 # ``` 
                 # This would mean the text is followed by an EMPTY code block? 
                 # No, ``` toggles. So:
                 # ```python
                 # code
                 # ``` (Inserted)
                 # Prose...
                 # ``` (Original)
                 # 
                 # Result: Prose is outside. The original ``` starts a NEW block?
                 # If the file ends there, we have an unclosed block at end of file.
                 # If there is more text, it becomes code.
                 
                 # Better Strategy:
                 # 1. Insert ``` before the prose.
                 # 2. Find the NEXT ``` line and remove it? Or replace it with nothing.
                 
                 # Let's peek ahead to find the closing fence
                 fence_index = -1
                 for k in range(i + 1, len(lines)):
                     if lines[k].strip().startswith('```'):
                         fence_index = k
                         break
                 
                 if fence_index != -1:
                     # We found the closing fence at k.
                     # Actions:
                     # 1. Insert ``` before current line i
                     # 2. SKIP the line at fence_index (remove it)
                     
                     new_lines.append("```\n")
                     new_lines.append("\n") # Add spacer
                     new_lines.append(line)
                     
                     # Process lines until fence_index
                     j = i + 1
                     while j < fence_index:
                         new_lines.append(lines[j])
                         j += 1
                     
                     # Now we are at fence_index. Skip it.
                     # And we are no longer in code block.
                     in_code_block = False
                     i = fence_index + 1
                     modified = True
                     continue
                 else:
                     # No closing fence found? That's weird (or file is broken).
                     # Just insert close here.
                     new_lines.append("```\n")
                     new_lines.append(line)
                     in_code_block = False
                     i += 1
                     modified = True
                     continue

        new_lines.append(line)
        i += 1
        
    if modified:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)

print("Applying fixes...")
for f in files:
    fix_file(f)
print("Done.")
