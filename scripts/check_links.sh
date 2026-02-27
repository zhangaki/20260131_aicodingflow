#!/bin/bash

# Set the base directory
BASE_DIR="projects/20260131_aicodingflow/src/content/blog"

# Function to extract markdown links from a file
extract_links() {
  grep -o '\[.*\](\(.*\).md)' "$1" | sed 's/.*(\(.*\).md)/\1.md/g'
}

# Function to check if a file exists
file_exists() {
  if [ -f "$1" ]; then
    return 0  # File exists
  else
    return 1  # File does not exist
  fi
}

# Loop through all markdown files in the base directory
find "$BASE_DIR" -name "*.md" -print0 | while IFS= read -r -d $'' file; do
  echo "Checking file: $file"
  
  # Extract links from the current file
  links=$(extract_links "$file")
  
  # Loop through each extracted link
  while IFS= read -r link; do
    # Construct the full path to the linked file
    linked_file="$BASE_DIR/$link"
    
    # Check if the linked file exists
    if ! file_exists "$linked_file"; then
      echo "  Broken link: $link"
    fi
  done <<< "$links"
done
