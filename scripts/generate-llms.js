import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

const CONTENT_DIR = path.join(process.cwd(), 'src/content/blog');
const OUTPUT_FILE = path.join(process.cwd(), 'public/llms-full.txt');

console.log('Generating llms-full.txt...');

if (!fs.existsSync(CONTENT_DIR)) {
    console.error(`Content directory not found: ${CONTENT_DIR}`);
    process.exit(1);
}

const files = fs.readdirSync(CONTENT_DIR).filter(file => file.endsWith('.md'));
let fullContent = `# Super Individual - Full Content Bundle\n\nGenerated: ${new Date().toISOString()}\n\n`;

files.forEach(file => {
    const filePath = path.join(CONTENT_DIR, file);
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const { data, content } = matter(fileContent);

    fullContent += `\n---\n\n`;
    fullContent += `## Title: ${data.title}\n`;
    fullContent += `Description: ${data.description || 'No description'}\n`;
    fullContent += `Date: ${data.pubDate}\n`;
    fullContent += `URL: https://ai-coding-flow.com/blog/${file.replace('.md', '')}\n\n`;
    fullContent += `### Content:\n\n${content.trim()}\n`;
});

fs.writeFileSync(OUTPUT_FILE, fullContent);
console.log(`Successfully generated ${OUTPUT_FILE} with ${files.length} articles.`);
