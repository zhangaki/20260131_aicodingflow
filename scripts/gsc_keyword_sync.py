import json
import os

KEYWORDS_FILE = '/Users/mac/code/super-individual/projects/20260131_seo-site/scripts/winning_keywords.json'

def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, 'r') as f:
            return json.load(f)
    return {"keywords": [], "last_updated": ""}

def save_keywords(data):
    os.makedirs(os.path.dirname(KEYWORDS_FILE), exist_ok=True)
    with open(KEYWORDS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_keyword(keyword, impressions, clicks):
    data = load_keywords()
    # Update or add
    found = False
    for item in data['keywords']:
        if item['query'] == keyword:
            item['impressions'] = impressions
            item['clicks'] = clicks
            found = True
            break
    if not found:
        data['keywords'].append({
            "query": keyword,
            "impressions": impressions,
            "clicks": clicks
        })
    from datetime import datetime
    data['last_updated'] = datetime.now().isoformat()
    save_keywords(data)
    print(f"Synced keyword: {keyword}")

if __name__ == "__main__":
    # Example usage for manual sync from GSC image data
    winning_queries = [
        ("best local offline ai assistant for accessing personal files projects documents 2026", 2, 0),
        ("llama-4-coder model", 2, 0),
        ("keyboard era cpu blog engineer", 1, 0),
        ("multi-agent orchestration research 2026", 1, 0)
    ]
    
    for q, imp, clk in winning_queries:
        add_keyword(q, imp, clk)
