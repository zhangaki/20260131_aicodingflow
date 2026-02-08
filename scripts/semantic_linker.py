
import os
import json
import re

# Configuration
DATA_FILE = "/Users/mac/code/super-individual/projects/20260131_seo-site/scripts/data/ai_tools.json"
CONTENT_DIR = "/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog"

def load_tools():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def get_related_tools(current_tool_id, tools, limit=5):
    current_tool = next((t for t in tools if t['id'] == current_tool_id), None)
    if not current_tool:
        return []
    
    related = []
    # Priority 1: Same category
    same_cat = [t for t in tools if t['category'] == current_tool['category'] and t['id'] != current_tool_id]
    related.extend(same_cat)
    
    # Priority 2: Cross-category bridges (Fintech for AI tools)
    if 'Fintech' not in current_tool['category']:
        fintech = [t for t in tools if 'Fintech' in t['category']]
        related.extend(fintech)
    else:
        # If it IS a fintech tool, recommend AI tools
        ai_tools = [t for t in tools if 'Coding' in t['category'] or 'LLM' in t['category']]
        related.extend(ai_tools)
        
    return related[:limit]

def inject_links():
    tools = load_tools()
    blog_files = [f for f in os.listdir(CONTENT_DIR) if f.endswith('.md')]
    count = 0

    tool_names = {t['name'].lower(): t for t in tools}
    tool_ids = {t['id']: t for t in tools}
    
    for filename in blog_files:
        filepath = os.path.join(CONTENT_DIR, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Identify matching tool IDs from filename
        # Pattern: tool-a-vs-tool-b-2026.md
        matching_ids = []
        for tid in tool_ids.keys():
            if tid in filename:
                matching_ids.append(tid)
        
        if not matching_ids:
            continue
            
        # Get related tools for the first matching tool ID
        base_tool_id = matching_ids[0]
        related = get_related_tools(base_tool_id, tools)
        
        if not related:
            continue
            
        related_links = []
        for r in related:
            # Check both directions for the comparison file
            slug_a = f"{base_tool_id}-vs-{r['id']}-2026"
            slug_b = f"{r['id']}-vs-{base_tool_id}-2026"
            
            target_slug = None
            if os.path.exists(os.path.join(CONTENT_DIR, f"{slug_a}.md")):
                target_slug = slug_a
            elif os.path.exists(os.path.join(CONTENT_DIR, f"{slug_b}.md")):
                target_slug = slug_b
                
            if target_slug:
                related_links.append(f"- [{tool_ids[base_tool_id]['name']} vs {r['name']} 2026 Full Analysis](file:///blog/{target_slug})")

        if related_links:
            # Remove any existing related section
            content = re.sub(r'### Related Comparisons.*?(?=---|\Z)', '', content, flags=re.DOTALL)
            
            section = "\n### Related Comparisons & Resources\n"
            section += "If you're evaluating tools for your digital empire, these deep dives provide critical context:\n\n"
            section += "\n".join(related_links)
            section += "\n\n*Optimized for US/UK SaaS and Fintech standards.*\n"
            
            # Inject before the final metadata separator
            if "---" in content[10:]:
                 parts = content.rsplit("---", 1)
                 content = parts[0] + section + "\n---" + parts[1]
            else:
                content += section
                
            with open(filepath, 'w') as f:
                f.write(content)
            count += 1

    print(f"Interlinking complete. Updated {count} files with contextual links.")

if __name__ == "__main__":
    inject_links()
