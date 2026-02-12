
import os
import glob
import frontmatter
import json
import random

CONTENT_DIR = "src/content/blog"
OUTPUT_JSON = "image_generation_tasks.json"

STYLES = [
    # Clean / Minimalist
    "Minimalist line art, single continuous line drawing, black ink on white background, elegant",
    "Swiss Design style, bold typography elements, grid layout, clean negative space, geometric abstraction",
    "Bauhaus poster style, primary colors (red blue yellow), geometric shapes, balanced composition",
    "Technical blueprint schematics, white lines on deep blue background, detailed engineering diagram",
    
    # Artistic / Textured
    "Risograph print style, grainy texture, misaligned layers, limited color palette (neon pink and blue)",
    "Ukiyo-e woodblock print style, flat perspective, textured washi paper, natural color palette",
    "Abstract expressionist oil painting, thick impasto brushstrokes, vibrant energy, emotional abstraction",
    "Collage art style, mixed media, torn paper textures, vintage found imagery, analog feel",
    "Matisse-inspired paper cutouts, organic shapes, bold flat colors, playful composition",
    "Etching style illustration, detailed cross-hatching, classic scientific diagram aesthetic",
    "Watercolor and ink illustration, loose wash, architectural sketch style",
    "Pop Art style, halftone dots, bold black outlines, vibrant commercial colors"
]

def get_files_needing_update():
    files = glob.glob(os.path.join(CONTENT_DIR, "*.md"))
    targets = []
    print(f"Found {len(files)} files in {CONTENT_DIR}")
    
    for f in files:
        try:
            post = frontmatter.load(f)
            hero_image = post.get('heroImage', '')
            
            # Case 1: Uses the generic fallback
            is_fallback = hero_image == "/assets/blog-fallback.jpg"
            
            # Case 2: Referenced image file is missing on disk
            is_missing = False
            if hero_image.startswith("/assets/"):
                image_path = os.path.join("public", hero_image.lstrip("/"))
                if not os.path.exists(image_path):
                    is_missing = True
            
            if is_fallback or is_missing:
                targets.append({
                    'path': f,
                    'title': post.get('title', ''),
                    'description': post.get('description', ''),
                    'filename': os.path.basename(f),
                    'existing_hero': hero_image
                })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    return targets

def generate_prompt(title, description, style):
    # Enhanced prompt generation using title + description for context
    subject = title.replace("2026", "").replace("Review", "").strip()
    
    # Clean up description to be prompt-friendly
    context = ""
    if description:
        context = description.replace('"', '').replace("'", "").replace("\n", " ")
        if len(context) > 150:
            context = context[:150] + "..."
    
    # Construct a more detailed prompt
    return f"Editorial illustration representing '{subject}'. Context: {context}. Style: {style}. High quality, artistic, authentic, no text, no words, abstract interpretation."

def main():
    targets = get_files_needing_update()
    print(f"Found {len(targets)} files using blog-fallback.jpg")
    
    tasks = []
    for t in targets:
        style = random.choice(STYLES)
        prompt = generate_prompt(t['title'], t['description'], style)
        
        # If the existing hero image is already a specific (but missing) JPG, use its name
        if t['existing_hero'] and t['existing_hero'] != "/assets/blog-fallback.jpg":
            rel_image_path = t['existing_hero']
            image_filename = os.path.basename(rel_image_path)
        else:
            slug = t['filename'].replace('.md', '')
            image_filename = f"{slug}.jpg"
            rel_image_path = f"/assets/{image_filename}"
        
        tasks.append({
            'file_path': t['path'],
            'title': t['title'],
            'style': style,
            'prompt': prompt,
            'output_image_path': rel_image_path,
            'absolute_image_path': os.path.abspath(os.path.join("public", rel_image_path.lstrip("/")))
        })
        
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(tasks, f, indent=2)
        
    print(f"Generated plan for {len(tasks)} images in {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
