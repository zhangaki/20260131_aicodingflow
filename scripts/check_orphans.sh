#!/bin/bash

# Set the base directory
BASE_DIR="projects/20260131_aicodingflow/src/content/blog"

# Function to extract markdown links from a file
extract_links() {
  grep -o '\[.*\](\(.*\).md)' "$1" | sed 's/.*(\(.*\).md)/\1.md/g'
}

# Function to check if a file is linked to
is_linked_to() {
  link=$1
  find "$BASE_DIR" -name "*.md" -print0 | while IFS= read -r -d $'' file; do
    if grep -q "$link" "$file"; then
      return 0 # Linked to
    fi
  done
  return 1 # Not linked to
}

# Loop through all markdown files in the base directory
find "$BASE_DIR" -maxdepth 1 -name "*.md" -print0 | while IFS= read -r -d $'' file; do
  filename=$(basename "$file")
  
  # Check if the file is linked to from any other file
  if ! is_linked_to "$filename"; then
    echo "Orphaned file: $filename"
  fi
done
