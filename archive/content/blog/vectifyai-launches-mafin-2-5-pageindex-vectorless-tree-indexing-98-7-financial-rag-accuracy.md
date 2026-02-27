---
title: "VectifyAI Unveils Mafin 2.5 and PageIndex, Claiming 98.7% Financial RAG Accuracy with Open-Source Vectorless Tree Indexing"
description: "VectifyAI debuts Mafin 2.5 and PageIndex, touting 98.7% financial RAG accuracy via open-source vectorless tree indexing."
pubDate: "Feb 23 2026"
heroImage: "/assets/vectifyai-launches-mafin-2-5-pageindex-vectorless-tree-indexing-98-7-financial-rag-accuracy.webp"
tags:
- Financial RAG
- vectorless indexing
- tree-based retrieval
- open-source AI
- LLM accuracy
---

## The What

VectifyAI released an updated `Mafin` alongside `PageIndex`, an open-source index that organizes financial documents into a section/page tree and returns citations with page-level provenance. The stated goal is narrower than “better answers”: reduce wrong-page (and wrong-definition) retrieval in finance-heavy RAG workflows by leaning on document structure and repeatable routing, not embedding similarity as the default.

That target is credible because many failures in finance RAG are retrieval failures: the system pulls a nearby-looking clause that lives on the wrong page, under the wrong definition, or in the wrong time period. Ambiguous terms are the trap. “Capital” is the classic example, but you see the same issue with:

- “Material Adverse Effect” (defined in the credit agreement vs. referenced in a representation)  
- “EBITDA adjustments” (definition section vs. an addback table in an exhibit)  
- “Tier 1 capital” (regulatory definition vs. internal policy shorthand)  

`PageIndex`’s bet is that you can prevent a chunk of these errors by keeping the retrieval unit anchored to the document’s native structure: doc → section → subsection → page → block/snippet, with stable identifiers. Instead of “here’s a similar chunk,” the system can return “here’s the page and section path that matched, plus the offsets where the evidence came from.”

Mini incident (the kind compliance teams actually care about): a risk report asks “What is capital for this covenant?” and the system cites “capital expenditures” from an EBITDA addback section because the embedding neighborhood is close. A structure-aware index can constrain the search to the “Definitions” section (or to pages whose headers match that scope) and surface the correct “Capital” definition with a path you can replay later.

**Governance requirement: reproducible evidence chain.** In model risk review (e.g., SR 11-7) or an audit request, you need to show *exactly* what the system retrieved from *which* document version: query, corpus version, retrieval route, page identifier/hash, and snippet offsets. `PageIndex` is positioned as retrieval infrastructure that makes that evidence chain a default output, not an afterthought.

What’s still unclear from the release materials (and worth verifying in the docs/README): the exact scoring/routing mechanics. A reasonable reading is that it does some combination of (1) section routing using headings/structure, then (2) scoring candidate pages with lexical signals (BM25-like) plus structural constraints, then (3) returning top-k pages/snippets with offsets. If it uses sparse vectors (BM25/SPLADE) or embeddings anywhere, calling it “vectorless” is marketing; the more precise claim is “not embedding-first.”

## The So What

### 1) Fewer wrong-page citations is the metric that matters in finance RAG

“Accuracy” is too vague; for finance workflows the failure mode is often a correct-sounding answer with a bad citation. The measurable implication here should be:

- citation correctness@1 and @3 (does the cited page actually support the claim?)  
- wrong-page rate (citation points to the wrong page even if the doc is right)  
- wrong-definition rate (e.g., pulls a reference to a term, not its definition)  

If `PageIndex` improves those numbers, it reduces the highest-cost errors: customer disputes, incorrect reports, and escalations that turn into audit work.

### 2) Operations: revalidation and update cost can dominate embedding-first stacks

Embedding-first retrieval isn’t just compute; it’s change control. In many regulated teams, the expensive part is proving the system still behaves after a corpus update.

Concrete implications you can measure:

- reindex time after a 5% corpus update (wall time + human validation time)  
- percent of corpus requiring re-embedding (if embeddings are used at all)  
- rollback complexity (can you pin retrieval to a corpus version and reproduce prior answers?)  

A structure/page index can reduce the “everything must be rebuilt” feeling by making updates more local and by producing stable identifiers you can diff and audit.

### 3) Auditability becomes a first-class output, not a screenshot exercise

Most production “explainability” is a citation link and a relevance score. That’s rarely enough when someone asks, “Why did it pick *this* clause from *this* version?”

A better standard is: every retrieved result ships with a replayable trace (routing + scoring inputs + identifiers). One concrete way to express that is a log payload you can hand to audit or use in incident response:

```json
{
  "query_id": "q-2026-02-23-001928",
  "corpus_version": "2026-02-15T03:10:22Z",
  "doc_id": "credit_agreement_2024_09_01",
  "node_path": "Definitions > Capital > Page 17",
  "page_id": "p17",
  "page_hash": "sha256:8d5c...e21a",
  "matcher": "structure+lexical",
  "rank_features": {
    "heading_match": true,
    "bm25_score": 12.84,
    "scope_constraint": "Definitions"
  },
  "snippet_offsets": [
    { "start": 1832, "end": 2144 }
  ],
  "k": 3,
  "rank": 1
}
```

That’s not “nice to have.” It’s the difference between a 10-minute replay and a multi-day scramble when a citation is challenged.

## The Now What

### Run a retrieval bake-off (3 configs, one scorecard)

Compare:

- `PageIndex` retrieval  
- Hybrid: `PageIndex` for primary retrieval + embeddings/reranker for fuzzy queries  
- Baseline: your current vector-first approach  

Use an evaluation set that reflects finance ambiguity and version drift (not generic Q&A). Include queries like:

- “Define Capital for covenant compliance”  
- “What counts as a Material Adverse Effect?”  
- “List permitted EBITDA addbacks and where they’re defined”  
- “What is Tier 1 capital in this policy vs. the regulatory filing?”  
- “Which section defines ‘Affiliate’ and does it include subsidiaries?”  

**Metrics + thresholds (example rubric you can actually enforce):**

- citation correctness@1: target ≥ 0.90 on your labeled set  
- citation correctness@3: target ≥ 0.97  
- wrong-page rate@1: target ≤ 0.05  
- determinism: ≥ 0.99 identical top-1 citations across 20 repeated runs (same corpus version)  
- reindex time after 5% corpus update: record wall time and analyst time; set an internal SLA  
- audit replay time: reconstruct full evidence chain in < 10 minutes from logs alone  

### Treat the audit trail as a deliverable, not telemetry

If you operate under compliance, define the minimum evidence chain your system must store *per answer*:

- `query_id`, `timestamp`  
- `corpus_version` (and ingestion job/build id)  
- `doc_id`, `doc_version`, `page_id`, `page_hash`  
- `node_path` (doc → section → page)  
- `matcher` + key rank features (lexical/structure/embedding if used)  
- `snippet_offsets` (byte/char offsets or normalized coordinates for PDFs)  

Then run one incident simulation: pick a disputed answer, change the document version, and verify you can (1) replay the original retrieval exactly and (2) explain what changed after the update.

### One clarification to resolve before you buy in

Write down, in one paragraph, how `PageIndex` selects pages:

- How does it route into the tree (heading match, section numbers, metadata rules)?  
- What does it score with (BM25, sparse vectors, embeddings, rules)?  
- What does “page” mean for reflowed HTML, multi-column PDFs, exhibits, and tables?  
- How are offsets computed and made stable across re-ingestion?  

If the docs don’t answer these, that’s not a nit—it’s a credibility gap. The core promise here is reproducibility; reproducibility requires precise definitions of “page,” “path,” and “match.”

If you can share VectifyAI’s benchmark claims (or the `PageIndex` README describing routing/scoring), I can tighten the lead further by replacing generic language with their exact metrics, corpus size, and retrieval method—without turning it into product copy.