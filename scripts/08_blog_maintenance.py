#!/usr/bin/env python3
"""
blog_maintenance.py

Unified tool for maintaining blog content structure and metadata.
Merges functionality from:
- cleanup_blog.py (Frontmatter standardization)
- tag_posts_minimal.py (Auto-tagging)
- fix_pubdates.py (Date distribution)
- repair_frontmatter.py (YAML syntax fixes)

Usage:
    python scripts/blog_maintenance.py --action clean
    python scripts/blog_maintenance.py --action tag
    python scripts/blog_maintenance.py --action fix-dates
"""

import os
import re
import glob
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = PROJECT_ROOT / "src" / "content" / "blog"
ASSETS_DIR = PROJECT_ROOT / "public" / "assets"
FALLBACK_IMAGE = "/assets/blog-fallback.webp"

# ---------------------------------------------------------------------------
# 1. CLEAN LOGIC (Frontmatter Standardization)
# ---------------------------------------------------------------------------

def get_best_image(slug):
    """Find the best matching image for a slug."""
    existing_assets = os.listdir(ASSETS_DIR)
    
    # Try exact match with extensions
    for ext in ['.png', '.jpg', '.webp']:
        if f"{slug}{ext}" in existing_assets:
            return f"/assets/{slug}{ext}"
    
    # Try slug without year
    slug_no_year = re.sub(r'-\d{4}$', '', slug)
    for ext in ['.png', '.jpg', '.webp']:
        if f"{slug_no_year}{ext}" in existing_assets:
            return f"/assets/{slug_no_year}{ext}"
            
    return FALLBACK_IMAGE

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    filename = filepath.name
    slug = filename.replace(".md", "").replace(".mdx", "")
    
    # 1. Parse existing frontmatter using regex
    # We look for the first block between ---
    frontmatter_match = re.search(r'^---(.*?)---', content, re.DOTALL)
    
    title = slug.replace('-', ' ').title()
    description = "Autonomous intelligence trends and technical deep dives into the 2026-2030 landscape."
    pub_date = "Feb 01 2026"
    hero_image = get_best_image(slug)
    existing_tags = []

    if frontmatter_match:
        block = frontmatter_match.group(1)
        
        t_match = re.search(r'title:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
        if t_match: title = t_match.group(1).strip()
        
        d_match = re.search(r'description:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
        if d_match: description = d_match.group(1).strip()
        
        date_match = re.search(r'pubDate:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
        if date_match: pub_date = date_match.group(1).strip()
        
        h_match = re.search(r'heroImage:\s*[\'"]?([^\'"\n]+)[\'"]?', block)
        if h_match: 
            candidate = h_match.group(1).strip()
            if (ASSETS_DIR / Path(candidate).name).exists():
                hero_image = candidate
                
        # Extract tags if they exist
        if "tags:" in block:
            # Simple regex for inline tags
            tags_match = re.search(r'tags:\s*\[(.*?)\]', block)
            if tags_match:
                existing_tags = [t.strip().strip("'\"") for t in tags_match.group(1).split(',')]
            
    # 2. Strip all frontmatter and leading whitespace
    body = re.sub(r'^---.*?---', '', content, flags=re.DOTALL).strip()

    # 2.1 Remove potential markdown code block wrappers (from bad LLM output)
    # Remove ```markdown ... ``` or just ``` ... ``` if they wrap the whole content
    if body.startswith("```"):
        body = re.sub(r'^```\w*\n', '', body)
        body = re.sub(r'\n```$', '', body)
        body = body.strip()
    
    # 3. Reconstruct
    tags_line = ""
    if existing_tags:
        tags_str = ", ".join([f'"{t}"' for t in existing_tags])
        tags_line = f"tags: [{tags_str}]\n"

    new_frontmatter = f"""---
title: "{title}"
description: "{description}"
pubDate: "{pub_date}"
heroImage: "{hero_image}"
{tags_line}---

"""
    new_content = new_frontmatter + body + "\n"

    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def run_clean():
    print("=== Cleaning Content ===")
    files = list(BLOG_DIR.glob("*.md")) + list(BLOG_DIR.glob("*.mdx"))
    count = 0
    for f in files:
        if clean_file(f):
            count += 1
            print(f"  Cleaned: {f.name}")
    print(f"Cleaned {count} files.")

# ---------------------------------------------------------------------------
# 2. TAG LOGIC (Auto-Tagging)
# ---------------------------------------------------------------------------

TAG_RULES = {
    "AI Agents": ["agent", "agents", "autonomous", "orchestration", "clawdbot", "swarm", "copilot", "cursor", "assistant"],
    "Security": ["security", "red team", "injection", "hack", "exploit", "vulnerability", "compliance", "audit", "bias", "privacy", "risk"],
    "Infrastructure": ["hardware", "gpu", "latency", "quantization", "local llm", "server", "api", "cloud", "compute", "storage", "memory"],
    "Future Tech": ["bci", "neural", "brain", "space", "mars", "dyson", "quantum", "genetic", "bio", "fusion", "robotics", "llama-4", "llama 4"],
    "Society & Ethics": ["ubi", "labor", "job", "economy", "governance", "law", "legal", "philosophy", "identity", "social", "humanity"],
    "Dev Tools": ["code", "typescript", "python", "debug", "sitemap", "git", "cli", "terminal", "workflow"],
    "Local AI": ["offline ai", "local assistant", "local indexing", "personal files", "privacy-first"]
}

def tag_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lower_content = content.lower()
    assigned_tags = set()
    
    for tag, keywords in TAG_RULES.items():
        for kw in keywords:
            if kw in lower_content:
                assigned_tags.add(tag)
                break
    
    if not assigned_tags:
        assigned_tags.add("General")
        
    # Update tags in frontmatter
    # We use a robust replacement for the tags: [...] line
    tags_str = ", ".join([f'"{t}"' for t in assigned_tags])
    new_tags_line = f"tags: [{tags_str}]"
    
    if "tags:" in content:
        new_content = re.sub(r'tags:\s*\[.*?\]', new_tags_line, content)
        new_content = re.sub(r'tags:\s*\n(\s*-\s*.*?\n)+', new_tags_line + "\n", new_content, flags=re.MULTILINE)
    else:
        # Insert before the closing ---
        new_content = re.sub(r'---\s*\n\n', f"{new_tags_line}\n---\n\n", content, count=1)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def run_tag():
    print("=== Auto-Tagging Content ===")
    files = list(BLOG_DIR.glob("*.md")) + list(BLOG_DIR.glob("*.mdx"))
    count = 0
    for f in files:
        if tag_file(f):
            count += 1
            print(f"  Tagged: {f.name}")
    print(f"Tagged {count} files.")

# ---------------------------------------------------------------------------
# 3. DATE FIX LOGIC (Spread PubDates)
# ---------------------------------------------------------------------------

def run_fix_dates():
    print("=== Fixing PubDates (Spreading Feb 08) ===")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    base_date = datetime(2025, 12, 1)
    
    files = list(BLOG_DIR.glob("*.md"))
    feb8_files = []
    
    # Identify files
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            if "Feb 08 2026" in fh.read():
                feb8_files.append(f)
                
    print(f"Found {len(feb8_files)} articles with Feb 08 date.")
    
    changed = 0
    for f in sorted(feb8_files):
        offset = random.randint(0, 69) # Spread over ~2 months
        new_date = base_date + timedelta(days=offset)
        new_date_str = f'{months[new_date.month-1]} {new_date.day:02d} {new_date.year}'
        
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
            
        new_content = content.replace("Feb 08 2026", new_date_str)
        
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
            changed += 1
            
    print(f"Updated {changed} articles with randomized dates.")

# ---------------------------------------------------------------------------
# 4. NOINDEX LOGIC (For Thin Content)
# ---------------------------------------------------------------------------

def run_noindex(min_words=500):
    print(f"=== Adding Noindex to Thin Articles (<{min_words} words) ===")
    files = sorted(BLOG_DIR.glob("*.md"))
    count = 0
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
            
        wc = len(content.split())
        if wc < min_words:
            if 'noindex: true' in content:
                print(f"  SKIP (already noindex): {f.name} ({wc} words)")
                continue
                
            # Add noindex to frontmatter
            # Try to insert before the closing ---
            new_content = re.sub(r'---\s*\n\n', '---\nnoindex: true\n---\n\n', content, count=1)
            
            if new_content != content:
                with open(f, 'w', encoding='utf-8') as fh:
                    fh.write(new_content)
                print(f"  NOINDEX: {f.name} ({wc} words)")
                count += 1
            else:
                print(f"  WARN: Could not modify {f.name}")
                
    print(f"Updated {count} articles.")

# ---------------------------------------------------------------------------
# 5. AUDIT LOGIC (Read-Only Checks)
# ---------------------------------------------------------------------------

def run_audit():
    print("=== Auditing Content Structure ===")
    files = list(BLOG_DIR.glob("*.md")) + list(BLOG_DIR.glob("*.mdx"))
    issues_found = 0
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        file_issues = []
        content = ''.join(lines)
        
        # 1. Check for mismatched code fences
        fence_count = 0
        for line in lines:
            if line.strip().startswith('```'):
                fence_count += 1
        
        if fence_count % 2 != 0:
            file_issues.append(f"Odd number of code fences ({fence_count})")
        
        # 2. Check for empty or whitespace-only code blocks
        in_fence = False
        fence_start = -1
        fence_content = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('```'):
                if not in_fence:
                    in_fence = True
                    fence_start = i + 1
                    fence_content = []
                else:
                    # Closing fence — check if content is empty
                    block_text = ''.join(fence_content).strip()
                    if not block_text:
                        file_issues.append(f"Empty code block (Line {fence_start})")
                    in_fence = False
                    fence_content = []
            elif in_fence:
                fence_content.append(line)
        
        # 3. Check for unclosed trailing code block (fence opened but never closed)
        if in_fence:
            file_issues.append(f"Unclosed code block at end of file (opened Line {fence_start})")
            
        # 4. Check for missing table headers
        for i, line in enumerate(lines):
            # Detects | --- | --- | roughly
            if '|' in line and set(line.strip().replace('|', '').replace(' ', '')) == {'-'}:
                if i == 0:
                    file_issues.append(f"Table delimiter at start of file (Line {i+1})")
                else:
                    prev = lines[i-1].strip()
                    if not prev or '|' not in prev:
                        file_issues.append(f"Table delimiter without header row (Line {i+1})")

        # 5. Check for prose trapped inside code blocks
        in_fence = False
        fence_start = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('```'):
                in_fence = not in_fence
                if in_fence:
                    fence_start = i + 1
            elif in_fence and _is_prose_line(stripped, line):
                file_issues.append(f"Prose trapped in code block (Line {i+1}): {stripped[:60]}...")
                break  # Report only the first instance per file

        # 6. Check for literal H-tag labels (e.g., **H2: Title** or H3: Title)
        h_tag_pattern = re.compile(r'^\*{0,2}H([2-6]):\s*(.+?)\*{0,2}$')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if h_tag_pattern.match(stripped):
                file_issues.append(f"Literal H-tag label (Line {i+1}): {stripped[:60]}")
                break  # Report only the first instance per file

        if file_issues:
            issues_found += 1
            print(f"File: {filepath.name}")
            for issue in file_issues:
                print(f"  - {issue}")
                
    if issues_found == 0:
        print("Audit passed: No structural issues found.")
    else:
        print(f"Audit failed: Issues found in {issues_found} files.")


def _is_prose_line(stripped, raw_line):
    """Detect if a line inside a code block is actually prose content."""
    if not stripped or len(stripped) < 40:
        return False
    
    # Must not be indented (code is typically indented)
    is_indented = raw_line.startswith('    ') or raw_line.startswith('\t')
    if is_indented:
        return False
    
    # Strong prose indicators
    prose_signals = 0
    
    # Markdown headings inside code blocks are almost always errors
    if stripped.startswith('## ') or stripped.startswith('### '):
        return True
    
    # Contains markdown formatting (bold, italic, backtick-quoted terms in prose)
    if '**' in stripped and not stripped.startswith('//'):
        prose_signals += 2
    if '`' in stripped and not stripped.startswith('//') and not stripped.startswith('#'):
        # Backticks used to quote terms in prose (e.g., the `filterProducts` function)
        backtick_pairs = stripped.count('`') // 2
        if backtick_pairs >= 1 and any(stripped.startswith(p) for p in [
            'In ', 'The ', 'This ', 'These ', 'For ', 'With ', 'After ',
            'I\'ve ', 'Early ', 'Consider', 'Note ', 'It ', 'By ',
            'We ', 'You ', 'When ', 'If ', 'As ', 'Google', 'WebMCP',
            'Here ', 'However', 'Although', 'Because', 'Since '
        ]):
            prose_signals += 2
    
    # Starts with common prose sentence patterns
    if any(stripped.startswith(p) for p in [
        'In this example', 'The implications', 'This is ', 'This function',
        'I\'ve been', 'Early preview', 'Consider a', 'For instance',
        'The following', 'Note that', 'Keep in mind', 'It is ',
        'This site is', 'This approach', 'The core idea',
    ]):
        prose_signals += 2
    
    # Long line (> 100 chars) without indentation, containing sentence-like punctuation
    if len(stripped) > 100:
        period_count = stripped.count('.')
        comma_count = stripped.count(',')
        if period_count >= 1 or comma_count >= 2:
            prose_signals += 1
    
    # Line ending with a period (very common in prose, rare in code)
    if stripped.endswith('.') and not stripped.startswith('//') and not stripped.startswith('#'):
        prose_signals += 1
    
    return prose_signals >= 3

# ---------------------------------------------------------------------------
# 6. FORMAT LOGIC (Auto-Fix Structures)
# ---------------------------------------------------------------------------

def run_format():
    print("=== Formatting Content (Fixing Structures) ===")
    files = list(BLOG_DIR.glob("*.md")) + list(BLOG_DIR.glob("*.mdx"))
    count = 0
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        modified = False
        in_code_block = False
        
        # Pass 1: Fix Trapped Text + H-tag Labels
        h_tag_pattern = re.compile(r'^(\*{2})H([2-6]):\s*(.+?)\1$')  # **H2: Title**
        h_tag_bare = re.compile(r'^H([2-6]):\s*(.+)$')  # H2: Title
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                new_lines.append(line)
                i += 1
                continue
                
            if in_code_block and _is_prose_line(stripped, line):
                # Prose detected inside code block — close the block here
                new_lines.append("```\n\n")
                new_lines.append(line)
                in_code_block = False
                modified = True
                i += 1
                print(f"    Closed code block before prose at line {i}")
                continue
            
            # Fix **H2: Title** → ## Title
            if not in_code_block:
                m = h_tag_pattern.match(stripped)
                if m:
                    level = int(m.group(2))
                    title = m.group(3).rstrip('*').strip()
                    new_lines.append('#' * level + ' ' + title + '\n')
                    modified = True
                    i += 1
                    print(f"    Converted H{level} label at line {i}")
                    continue
                m = h_tag_bare.match(stripped)
                if m:
                    level = int(m.group(1))
                    title = m.group(2).strip()
                    new_lines.append('#' * level + ' ' + title + '\n')
                    modified = True
                    i += 1
                    print(f"    Converted H{level} label at line {i}")
                    continue
            
            new_lines.append(line)
            i += 1

        # Pass 2: Remove empty code blocks and close unclosed trailing blocks
        pass2_lines = []
        j = 0
        while j < len(new_lines):
            line = new_lines[j]
            stripped = line.strip()
            
            # Detect empty code blocks: ``` immediately followed by ```
            if stripped.startswith('```'):
                # Look ahead for closing fence
                k = j + 1
                while k < len(new_lines) and not new_lines[k].strip():
                    k += 1  # skip blank lines
                if k < len(new_lines) and new_lines[k].strip().startswith('```'):
                    # Empty code block — skip both fences and blanks between
                    j = k + 1
                    modified = True
                    print(f"    Removed empty code block at line {j}")
                    continue
            
            pass2_lines.append(line)
            j += 1
        
        # Check if fences are balanced; if odd, append closing fence
        fence_count = sum(1 for l in pass2_lines if l.strip().startswith('```'))
        if fence_count % 2 != 0:
            pass2_lines.append("\n```\n")
            modified = True
            print(f"    Closed unclosed trailing code block (total fences was {fence_count})")

        # Pass 3: Fix Tables
        pass3_lines = []
        for j, line in enumerate(pass2_lines):
            if '|' in line and set(line.strip().replace('|', '').replace(' ', '')) == {'-'}:
                # It's a delimiter
                if pass3_lines and (not pass3_lines[-1].strip() or '|' not in pass3_lines[-1]):
                    # Missing header
                    cols = line.count('|') - 1
                    if cols < 1: cols = 2
                    header = "| **Metric** | " + " | ".join(["**Value**"] * (cols-1)) + " |\n"
                    pass3_lines.append(header)
                    pass3_lines.append(line)
                    modified = True
                else:
                    pass3_lines.append(line)
            else:
                pass3_lines.append(line)
                
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(pass3_lines)
            print(f"  Formatted: {filepath.name}")
            count += 1
            
    print(f"Formatted {count} files.")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Blog Maintenance Tool")
    parser.add_argument("--action", choices=["clean", "tag", "fix-dates", "noindex", "audit", "format"], required=True, help="Action to perform")
    parser.add_argument("--min-words", type=int, default=500, help="Minimum word count for noindex (default: 500)")
    args = parser.parse_args()
    
    if args.action == "clean":
        run_clean()
    elif args.action == "tag":
        run_tag()
    elif args.action == "fix-dates":
        run_fix_dates()
    elif args.action == "noindex":
        run_noindex(args.min_words)
    elif args.action == "audit":
        run_audit()
    elif args.action == "format":
        run_format()

if __name__ == "__main__":
    main()
