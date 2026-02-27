---
am_last_deterministic_review_at: '2026-02-25T14:26:43.679111'
am_last_deterministic_review_by: worker-04
---

*   **SEO Optimization:**
    *   **Action:** Draft content around 1 primary query + 2–4 close variants, then run a quick on-page check with our [SEO Audit Tool](/tools/seo-audit). For deeper research and SERP competitive analysis, use a dedicated suite (e.g., Semrush or Ahrefs).
    *   **Pass:** Titles and headings reflect search intent, keywords appear naturally (no stuffing), internal links point to relevant pages, and the page earns impressions/clicks over time in Google Search Console.
    *   **Fail:** The draft is generic, mismatches intent, overuses exact-match keywords, or ships without basic on-page elements (title/meta/headers), leading to weak impressions.

*   **Checking for Plagiarism, “AI Detection”, and Hallucination:**
    *   **Action:** First, verify factual claims with primary sources (docs, standards, official announcements) and add citations/links. Then run a plagiarism scan (e.g., Copyscape) to catch accidental copying. Treat “AI detection” scores (e.g., Originality.ai) as a risk signal—not a truth test—because detectors are unreliable and can false-flag human writing.
    *   **Pass:** Key claims are source-backed, the draft is original, and any uncertain statements are qualified or removed.
    *   **Fail:** The content repeats unverified numbers/claims, contains copied passages, or presents shaky statements as facts.

*   **New: Source-Backed Freshness Checklist (10 minutes):**
    *   **Action:** Before publishing (or updating), do a fast “freshness pass”:
        1) Replace relative time words like “this year/recently” with a date or version.
        2) Re-check tool names/pricing and update screenshots/examples.
        3) Verify every statistic; if you can’t find a primary source, remove it.
        4) Add one internal link to a relevant tool or guide (and ensure it resolves).
        5) Re-run the page through Search Console’s URL Inspection after deployment.
    *   **Pass:** The page contains dated/versioned claims where needed, links resolve, and readers can verify important statements.
    *   **Fail:** The page relies on vague time references, outdated tool screenshots/pricing, or unsourced stats.

*   **Bias Detection:**
    *   **Action:** Review the draft for stereotypes, loaded wording, and unequal framing. If you’re operating at scale, use an automated toxicity/bias signal (e.g., Google’s Perspective API) as a queueing tool, then do human review for anything flagged.
    *   **Pass:** The content avoids harmful generalizations, uses neutral language, and treats sensitive topics carefully.
    *   **Fail:** The content contains discriminatory language, unfair assumptions, or one-sided framing.
