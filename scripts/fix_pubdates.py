"""Spread out Feb 08 pubDates across Dec 2025 - Feb 2026 to avoid bulk-publish signal"""
import glob
import os
import random
import re
from datetime import datetime, timedelta

blog_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'blog')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Find all articles with Feb 08 pubDate
feb8_files = []
for f in glob.glob(os.path.join(blog_dir, '*.md')):
    with open(f) as fh:
        content = fh.read()
    if re.search(r'pubDate.*Feb 08 202', content):
        feb8_files.append(f)

print(f'Found {len(feb8_files)} articles with Feb 08 pubDate')

# Spread across Dec 1 2025 - Feb 7 2026 (69 days)
random.seed(42)
base_date = datetime(2025, 12, 1)
days_range = 69

changed = 0
for f in sorted(feb8_files):
    offset = random.randint(0, days_range)
    new_date = base_date + timedelta(days=offset)
    new_date_str = f'{months[new_date.month-1]} {new_date.day:02d} {new_date.year}'

    with open(f) as fh:
        content = fh.read()

    # Replace Feb 08 2026 with random date
    new_content = re.sub(
        r"""(pubDate:\s*['"])Feb 08 202\d(['"])""",
        lambda m: f'{m.group(1)}{new_date_str}{m.group(2)}',
        content
    )

    if new_content != content:
        with open(f, 'w') as fh:
            fh.write(new_content)
        changed += 1

print(f'Updated {changed} articles with randomized dates')

# Verify distribution
date_counts = {}
for f in glob.glob(os.path.join(blog_dir, '*.md')):
    with open(f) as fh:
        content = fh.read()
    m = re.search(r"""pubDate:\s*['"](.+?)['"]""", content)
    if m:
        d = m.group(1)[:3]
        date_counts[d] = date_counts.get(d, 0) + 1

print(f'\nDate distribution by month:')
for mo in sorted(date_counts.keys()):
    print(f'  {mo}: {date_counts[mo]} articles')
