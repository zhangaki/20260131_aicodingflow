
import os
import re

BLOG_DIR = "/Users/mac/code/super-individual/projects/seo-site/src/content/blog"

# Mapping of filenames to their new covers
COVER_MAP = {
    # Existing GEO Alerts (Batch 1 & 2)
    "manus-ai-2026": "/assets/manus-ai-cover.png",
    "grok-3-ai-2026": "/assets/grok-3-ai-cover.png",
    "deepseek-2026": "/assets/deepseek-cover.png",
    "higgsfield-ai-2026": "/assets/higgsfield-ai-cover.png",
    "veo-3-ai-2026": "/assets/veo-3-ai-cover.png",
    "gemini-ai-2026": "/assets/gemini-ai-cover.png",
    "lovable-ai-2026": "/assets/lovable-ai-cover.png",
    "qwen-ai-2026": "/assets/qwen-ai-cover.png",
    "agentic-ai-2026": "/assets/agentic-ai-cover.png",
    "ai-news-today-2026": "/assets/ai-news-today-cover.png",
    "cursor-ai-2026": "/assets/cursor-ai-cover.png",
    "digen-ai-2026": "/assets/digen-ai-cover.png",
    "lmarena-ai-2026": "/assets/lmarena-ai-cover.png",
    "nano-banana-ai-2026": "/assets/nano-banana-ai-cover.png",
    "notebooklm-2026": "/assets/notebooklm-cover.png",
    "openai-news-today-2026": "/assets/ai-news-today-cover.png",
    
    # New Batch: Sci-Fi / Futurist
    "cognitive-sovereignty-hive-mind-2030": "/assets/cognitive-sovereignty-cover.png",
    "digital-twin-estate-planning-2028": "/assets/digital-twin-estate-cover.png",
    "dyson-sphere-of-one-2028": "/assets/dyson-sphere-cover.png",
    "interplanetary-internet-2030": "/assets/interplanetary-internet-cover.png",
    "network-state-governance-2030": "/assets/network-state-cover.png",
    "omega-point-2030": "/assets/omega-point-cover.png",
    "personal-bio-foundries-2030": "/assets/bio-foundries-cover.png",
    "post-scarcity-asset-theory-2028": "/assets/post-scarcity-cover.png",
    "the-algorithmic-judiciary-2030": "/assets/algorithmic-judiciary-cover.png",
    "the-exocortex-integration-2028": "/assets/exocortex-cover.png",
}

def update_hero_image(filepath, new_image):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has heroImage
    if 'heroImage:' in content:
        updated = re.sub(
            r'heroImage:\s*"[^"]*"',
            f'heroImage: "{new_image}"',
            content
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        return True
    return False

if __name__ == "__main__":
    for slug, cover in COVER_MAP.items():
        filepath = os.path.join(BLOG_DIR, f"{slug}.md")
        if os.path.exists(filepath):
            if update_hero_image(filepath, cover):
                print(f"Updated: {slug}")
        else:
            print(f"Skipping missing file: {slug}")
