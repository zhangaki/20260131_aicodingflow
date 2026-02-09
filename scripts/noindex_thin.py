"""Add noindex to articles under 500 words to prevent thin content penalty"""
import glob
import os
import re

blog_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'blog')
MIN_WORDS = 500

thin = []
for f in sorted(glob.glob(os.path.join(blog_dir, '*.md'))):
    with open(f) as fh:
        content = fh.read()
    wc = len(content.split())
    if wc < MIN_WORDS:
        name = os.path.basename(f)
        # Skip if already noindex
        if 'noindex: true' in content:
            print(f'  SKIP (already noindex): {name} ({wc} words)')
            continue
        # Add noindex: true to frontmatter
        new_content = content.replace('---\n\n', '---\nnoindex: true\n---\n\n', 1)
        if new_content == content:
            # Try alternate frontmatter ending
            new_content = re.sub(r'---\s*\n\n', '---\nnoindex: true\n---\n\n', content, count=1)
        if new_content != content:
            with open(f, 'w') as fh:
                fh.write(new_content)
            print(f'  NOINDEX: {name} ({wc} words)')
            thin.append(name)
        else:
            print(f'  WARN: could not modify {name}')

print(f'\nTotal: {len(thin)} articles set to noindex')
