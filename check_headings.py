
import os
import re

def check_heading_hierarchy(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    heading_pattern = re.compile(r'^(#+) (.*)$', re.MULTILINE)
    headings = heading_pattern.findall(content)

    if not headings:
        return True  # No headings, consider it valid

    last_level = 0
    for heading in headings:
        level = len(heading[0])
        if level > last_level + 1:
            print(f"  Error: Heading level skip in {filepath}: {heading[1]}")
            return False
        last_level = level

    return True


def main():
    blog_dir = "/Users/mac/code/super-individual/projects/20260131_aicodingflow/src/content/blog"
    valid = True
    for filename in os.listdir(blog_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(blog_dir, filename)
            print(f"Checking {filename}...")
            if not check_heading_hierarchy(filepath):
                valid = False

    if valid:
        print("All files passed the heading hierarchy check.")
    else:
        print("Some files failed the heading hierarchy check.")

if __name__ == "__main__":
    main()
