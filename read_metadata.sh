
#!/bin/bash
# Read the first 10 lines of each markdown file in the specified directory
# and extract the title and description.

dir="projects/20260131_aicodingflow/src/content/blog"

for file in "$dir"/*.md; do
  if [ -f "$file" ]; then
    echo "File: $file"
    head -n 10 "$file"
    echo "--------------------"
  fi
done
