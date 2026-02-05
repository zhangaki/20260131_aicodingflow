
import os
import sys
from trend_sentinel import generate_trend_post

# Configuration
RAW_DATA = """
haven ai song removed	0	3550%
twg ai	0	1900%
anthropic ai tools	1	200%
anthropic ai it stocks	0	70%
anthropic	7	60%
anthropic ai	7	60%
anthropic new ai tool	1	40%
rentahuman ai	0	30%
anthropic ai tool	2	20%
ai モード	1	20%
claude ai	17	10%
turbo ai	1	10%
kling ai	4	10%
ai video generator	5	9%
ai video	24	8%
king ai	1	8%
suno ai music	1	8%
black box ai	1	7%
napkin ai	1	7%
magic school ai	1	7%
krea ai	1	6%
google ai mode	1	5%
astra ai	1	5%
ai photo editor	2	4%
banana ai	3	4%
elevenlabs	1	4%
ai image generator	5	4%
google ai pro	1	4%
ai voice generator	1	3%
ai checker	7	3%
heygen ai	1	2%
cursor ai	2	2%
quillbot ai detector	0	2%
poe ai	0	2%
invideo ai	1	1%
nano banana ai	2	1%
humanize ai	5	1%
ai detector	15	1%
lovart ai	1	0%
ai picture generator	1	0%
ai image generator free	1	0%
"""

def parse_and_generate():
    lines = RAW_DATA.strip().split('\n')
    count = 0
    for line in lines:
        parts = line.split('\t')
        if len(parts) < 1:
            continue
        
        query = parts[0].strip()
        
        # Simple dynamic summary generation based on the query name
        # In a production environment, this would call an LLM to generate a specific summary.
        # For this batch, we use high-context generic technical summaries.
        
        summary = f"The rise of {query} indicates a shift in specialized AI applications. Users are increasingly searching for focused solutions that bypass general-purpose models in favor of niche efficiency."
        
        if "anthropic" in query.lower() or "claude" in query.lower():
            summary = f"Anthropic's latest ecosystem updates, including {query}, are challenging the dominant RAG benchmarks. Optimizing for Claude's unique context handling is now a priority for technical SEO."
        elif "video" in query.lower() or "kling" in query.lower() or "heygen" in query.lower():
            summary = f"Generative video is moving from toys to tools. {query} represents the next wave of 'Resolution-as-a-Service' where frame-level semantic data becomes a ranking signal."
        elif "music" in query.lower() or "song" in query.lower():
            summary = f"Audio AI and digital rights management are colliding. {query} reflects the growing tension between generative creativity and existing copyright frameworks."
        elif "detector" in query.lower() or "checker" in query.lower() or "humanize" in query.lower():
            summary = f"The 'Verification Layer' of the web is hardening. {query} tools are becoming gatekeepers for content authenticity, making AI-native signals more visible to crawlers."
            
        try:
            generate_trend_post(query, summary)
            count += 1
        except Exception as e:
            print(f"Failed to generate for {query}: {e}")
            
    print(f"Batch processing complete. Generated {count} posts.")

if __name__ == "__main__":
    parse_and_generate()
