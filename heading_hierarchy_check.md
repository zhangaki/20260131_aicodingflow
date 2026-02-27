
**Regression Check Command:**

To check the heading hierarchy in the file, you can use the following command:

```
grep -n -E "^##+ " /Users/mac/code/super-individual/projects/20260131_aicodingflow/src/content/blog/10-ai-tools-for-content-creation-updated-final.md
```

This command will list all lines that start with one or more `#` characters, along with their line numbers. You can then manually verify if the heading levels are correct.

**Task Details:**

*   **Title:** Check heading hierarchy in all markdown files in `/Users/mac/code/super-individual/projects/20260131_aicodingflow/src/content/blog/`
*   **Body:** Iterate through all markdown files in the specified directory and check if the heading hierarchy is correct. Specifically, ensure that the main title is `<h1>`, main sections are `<h2>`, and sub-sections are `<h3>` or lower. Use the `grep` command above to help identify heading levels.
