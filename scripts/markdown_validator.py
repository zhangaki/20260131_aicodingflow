
import os
import re

def validate_markdown(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check Heading Hierarchy
    heading_regex = r"(#+) (.*)"
    headings = re.findall(heading_regex, content)
    
    if headings:
        previous_level = 0
        first_heading = True # Flag to skip the first heading
        for heading in headings:
            level = len(heading[0])
            if first_heading:
                previous_level = level
                first_heading = False
                continue

            if level > previous_level + 1:
                return f"Heading hierarchy error: Found H{level} after H{previous_level} in {filepath}"
            previous_level = level

    # Check for Orphan Links (links to anchors within the same document)
    anchor_regex = r"<a id=\"([a-zA-Z0-9_-]+)\"></a>"
    anchors = re.findall(anchor_regex, content)
    link_regex = r"\[([^\]]+)\]\(#([a-zA-Z0-9_-]+)\)"
    links = re.findall(link_regex, content)

    for link in links:
        anchor_id = link[2]
        if anchor_id not in anchors:
            return f"Orphan link found: Link to anchor #{anchor_id} not found in {filepath}"

    return None


def main():
    blog_dir = "projects/20260131_aicodingflow/src/content/blog"
    for filename in os.listdir(blog_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(blog_dir, filename)
            error = validate_markdown(filepath)
            if error:
                print(error)

if __name__ == "__main__":
    main()
