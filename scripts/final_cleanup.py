
import os

blog_dir = "/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog"

def final_cleanup():
    for filename in os.listdir(blog_dir):
        if not filename.endswith((".md", ".mdx")): continue
        
        filepath = os.path.join(blog_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        in_frontmatter = False
        frontmatter_count = 0
        seen_keys = set()
        
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                frontmatter_count += 1
                new_lines.append(line)
                if not in_frontmatter:
                    # Reset seen keys when exiting frontmatter
                    seen_keys = set()
                continue
            
            if in_frontmatter and frontmatter_count == 1:
                # We are in the REAL frontmatter at the top
                key_match = line.split(":", 1)
                if len(key_match) == 2:
                    key = key_match[0].strip()
                    if key in seen_keys:
                        continue # Skip duplicate keys in frontmatter
                    seen_keys.add(key)
                new_lines.append(line)
            else:
                # Outside main frontmatter, also check for any remaining ```markdown wraps
                if line.strip() in ["```markdown", "```"]:
                    continue
                new_lines.append(line)
                
        if len(new_lines) != len(lines):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Cleaned up {filename}")

if __name__ == "__main__":
    final_cleanup()
