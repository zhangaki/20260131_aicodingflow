
import os
import glob
import re

blog_dir = '/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

TAG_RULES = {
    "AI Agents": ["agent", "agents", "autonomous", "orchestration", "clawdbot", "swarm", "copilot", "cursor", "assistant"],
    "Security": ["security", "red team", "injection", "hack", "exploit", "vulnerability", "compliance", "audit", "bias", "privacy", "risk"],
    "Infrastructure": ["hardware", "gpu", "latency", "quantization", "local llm", "server", "api", "cloud", "compute", "storage", "memory"],
    "Future Tech": ["bci", "neural", "brain", "space", "mars", "dyson", "quantum", "genetic", "bio", "fusion", "robotics", "llama-4", "llama 4"],
    "Society & Ethics": ["ubi", "labor", "job", "economy", "governance", "law", "legal", "philosophy", "identity", "social", "humanity"],
    "Dev Tools": ["code", "typescript", "python", "debug", "sitemap", "git", "cli", "terminal", "workflow"],
    "Local AI": ["offline ai", "local assistant", "local indexing", "personal files", "privacy-first"]
}

count = 0

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter
    parts = re.split(r'^---$', content, flags=re.MULTILINE)
    if len(parts) < 3:
        print(f"Skipping {filepath}: No frontmatter found.")
        continue
        
    frontmatter_raw = parts[1]
    body = parts[2]
    
    text_to_scan = (frontmatter_raw + body).lower()
    
    assigned_tags = set()
    for tag, keywords in TAG_RULES.items():
        for kw in keywords:
            if kw in text_to_scan:
                assigned_tags.add(tag)
                break
    
    if not assigned_tags:
        assigned_tags.add("General")
    
    # Update or insert tags in frontmatter
    tags_list = ", ".join([f'"{t}"' for t in assigned_tags])
    tags_line = f"tags:\n" + "\n".join([f"- {t}" for t in assigned_tags])
    
    if "tags:" in frontmatter_raw:
        # Replace existing tags section
        new_frontmatter = re.sub(r'tags:.*?(?=\n\w+:|$)', tags_line, frontmatter_raw, flags=re.DOTALL)
    else:
        new_frontmatter = frontmatter_raw.strip() + "\n" + tags_line + "\n"
    
    new_content = f"---{new_frontmatter}---\n{body}"
    
    with os.fdopen(os.open(filepath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644), 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Tagged {os.path.basename(filepath)} -> {list(assigned_tags)}")
    count += 1

print(f"Processed {count} files successfully.")
