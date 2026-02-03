
import os
import glob
import frontmatter
import random
from datetime import date, timedelta

blog_dir = '/Users/mac/code/super-individual/projects/seo-site/src/content/blog'
files = glob.glob(os.path.join(blog_dir, '*.md')) + glob.glob(os.path.join(blog_dir, '*.mdx'))

# Define date range: Dec 1, 2025 to Jan 31, 2026
# This covers the "12月-1月" requirement
start_date = date(2025, 12, 1)
end_date = date(2026, 2, 2) # Up to roughly today

days_diff = (end_date - start_date).days

print(f"Found {len(files)} files. Randomizing dates between {start_date} and {end_date}...")

for filepath in files:
    try:
        # Load file
        with open(filepath, 'r') as f:
            post = frontmatter.load(f)
        
        # Generate random date
        random_days = random.randint(0, days_diff)
        new_date = start_date + timedelta(days=random_days)
        
        # Format: "MMM DD YYYY" e.g., "Dec 15 2025"
        formatted_date = new_date.strftime("%b %d %Y")
        
        # Update frontmatter
        post['pubDate'] = formatted_date
        
        # Write back
        with open(filepath, 'wb') as f:
            frontmatter.dump(post, f)
            
        # print(f"Updated {os.path.basename(filepath)} -> {formatted_date}")
        
    except Exception as e:
        print(f"Skipping {os.path.basename(filepath)}: {e}")

print("Batch update complete.")
