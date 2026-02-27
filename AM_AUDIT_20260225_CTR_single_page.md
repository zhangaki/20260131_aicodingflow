---
date: '2026-02-25'
goal: Improve title/description/first-120-words for intent fit
project: projects/20260131_aicodingflow
---

# CTR Improvement (Single Page)

## 1) Target + baseline

- **Target URL:** `/tools/aeo-audit/` (file: `src/pages/tools/aeo-audit.astro`)
- **Baseline CTR (last 28 days):** **0.6%** (high impressions / low clicks)

> Data source: Google Search Console → Performance → Search results → Page filter = `/tools/aeo-audit/`.

## 2) Changes made (what + rationale)

### Title
- **Before:** `Free AEO Audit Tool: Check ChatGPT + Perplexity Visibility`
- **After:** `Free AEO Audit: ChatGPT + Perplexity Visibility Checker (URL)`
- **Rationale:** Put the core query (“AEO audit”) first; add “Visibility Checker” to match common tool intent; add “(URL)” to pre-qualify the input action and reduce pogo-sticking.

### Meta description
- **Before:** “Run a free AEO audit on any URL. See if ChatGPT and Perplexity can find, cite, and summarize your page, then get a pass/fail score plus prioritized fixes (schema, crawlability, citations).”
- **After:** “Paste a URL to see if ChatGPT + Perplexity can find, cite, and summarize your page. Get a pass/fail AEO score and prioritized fixes for schema, crawlability, citations, and internal links.”
- **Rationale:** Lead with the action (“Paste a URL”) and the outcome; keep it scannable; list fix categories users expect from audits.

### First ~120 words (on-page hero intro)
- **Before:** “If your page isn’t being cited by ChatGPT or Perplexity, you’re invisible in AI answers. Paste a URL to see what they can actually access and quote—then get a pass/fail score and the top fixes to ship first (schema, crawlability, citations).”
- **After:** “Paste a URL to check if ChatGPT and Perplexity can find, cite, and summarize your page. You’ll get a simple pass/fail AEO score plus the top fixes to improve AI visibility: schema markup, crawlability, citations, and internal links.”
- **Rationale:** Mirrors the SERP promise (“AEO audit” + “paste a URL”), reduces fear-based framing, and makes the deliverable explicit within the first 1–2 sentences.

## 3) Expected impact + follow-up

- **Expected impact:** Higher CTR from clearer tool intent (“URL checker” + “paste a URL”), better snippet relevance for queries like “AEO audit”, “AI visibility checker”, “ChatGPT visibility”, and fewer misclicks.
- **Follow-up window:** Re-check in **14 days** (and again at **28 days**) in GSC: CTR, clicks, and top queries for `/tools/aeo-audit/`.
