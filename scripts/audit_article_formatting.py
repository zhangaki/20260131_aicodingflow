#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = PROJECT_ROOT / "src" / "content" / "blog"

AI_INTRO_PATTERNS = [
    r"^Okay, here's a draft",
    r"^Here is a blog article draft",
    r"^I have crafted a data-driven article",
    r"^I have enough information to create a solid draft",
    r"^Sure, here is the article",
    r"^Here is the markdown for the article",
    r"^Based on your request, here is the article",
    r"^Okay, I'll craft a data-driven article",
    r"^Okay, here's a draft of the article",
]

CODE_BLOCK_WRAPPER_PATTERN = r"^```markdown\s+(.*?)```$"

def audit_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []
    
    # Check for frontmatter
    if not content.startswith("---"):
        issues.append("Missing frontmatter at start")
        return issues # Can't reliably check other stuff if frontmatter is missing

    # Extract body (everything after second ---)
    parts = content.split("---", 2)
    if len(parts) < 3:
        issues.append("Malformed frontmatter (less than two delimiters)")
        return issues
        
    frontmatter = parts[1]
    body = parts[2].strip()

    # Check for AI intro filler in body
    for pattern in AI_INTRO_PATTERNS:
        if re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
            issues.append(f"Detected AI intro filler: {pattern}")

    # Check for markdown code block wrappers in body
    if body.startswith("```markdown") and body.endswith("```"):
        issues.append("Body is wrapped in ```markdown code block")
    elif body.startswith("```") and body.endswith("```"):
        issues.append("Body is wrapped in generic code block")

    # Check for redundant H1 (if title is in frontmatter, we usually don't want H1 in body)
    # This project seems to use H1 sometimes, but some articles had double titles.
    # We'll flag it if there's an H1 that exactly matches the title in frontmatter.
    title_match = re.search(r"^title:\s*[\"']?(.*?)[\"']?$", frontmatter, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        if f"# {title}" in body or f"## {title}" in body:
            # We often use ## {title} as the first header, which is fine, 
            # but if it's there twice or combined with AI filler, it's an issue.
            pass

    return issues

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False
        
    frontmatter = parts[1]
    body = parts[2].strip()

    # 1. Strip code block wrappers
    markdown_match = re.match(r"^```markdown\s*(.*?)\s*```$", body, re.DOTALL)
    if markdown_match:
        body = markdown_match.group(1).strip()
    else:
        generic_match = re.match(r"^```\s*(.*?)\s*```$", body, re.DOTALL)
        if generic_match:
            body = generic_match.group(1).strip()

    # 2. Strip AI intro filler (line by line at the start)
    lines = body.split("\n")
    new_lines = []
    skipped_intro = False
    for i, line in enumerate(lines):
        is_filler = False
        if not skipped_intro:
            for pattern in AI_INTRO_PATTERNS:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_filler = True
                    break
        
        if is_filler:
            continue
        else:
            # Once we hit a real line, stop checking for filler
            if line.strip():
                skipped_intro = True
            new_lines.append(line)

    new_body = "\n".join(new_lines).strip()
    
    # Reconstruct
    new_content = f"---{frontmatter}--- \n\n{new_body}\n"
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit and fix blog article formatting.")
    parser.add_argument("--fix", action="store_true", help="Automatically fix issues without prompting.")
    args = parser.parse_args()

    print(f"Auditing blog articles in {BLOG_DIR}...")
    files = list(BLOG_DIR.glob("*.md"))
    faulty_files = 0
    total_issues = 0

    for file_path in files:
        issues = audit_file(file_path)
        if issues:
            faulty_files += 1
            total_issues += len(issues)
            print(f"\n[ISSUE] {file_path.name}:")
            for issue in issues:
                print(f"  - {issue}")
            
            # Auto-fix option
            should_fix = args.fix
            if not should_fix:
                should_fix = input(f"Attempt to fix {file_path.name}? (y/n): ").lower() == 'y'
            
            if should_fix:
                if fix_file(file_path):
                    print(f"  ✅ Fixed {file_path.name}")
                else:
                    print(f"  ❌ Failed to fix {file_path.name}")

    print(f"\nAudit complete. Found {total_issues} issues in {faulty_files} files.")

if __name__ == "__main__":
    main()
