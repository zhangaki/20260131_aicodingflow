
import os
import glob
import frontmatter

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
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
    with open(filepath, 'r') as f:
        try:
            post = frontmatter.load(f)
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            continue

    text_content = (post.get('title', '') + " " + post.content).lower()
    
    assigned_tags = set()
    
    for tag, keywords in TAG_RULES.items():
        for kw in keywords:
            if kw in text_content:
                assigned_tags.add(tag)
                break  # match valid tag once
    
    # Fallback
    if not assigned_tags:
        assigned_tags.add("General")

    # Update frontmatter
    post['tags'] = list(assigned_tags)
    
    # Write back
    with open(filepath, 'wb') as f:
        frontmatter.dump(post, f)
        
    print(f"Tagged {os.path.basename(filepath)} -> {list(assigned_tags)}")
    count += 1

print(f"Processed {count} files.")
