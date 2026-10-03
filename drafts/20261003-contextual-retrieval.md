---
status: draft
published: false
claim_review: passed
privacy_review: passed
category: Enterprise AI platform
topics:
  - retrieval
  - evals
  - cost
---
<!-- playbook-capture:fingerprint=f73f101c38d638e11a770fba2b1c9b4fecb4d5570aa80759cc93067dacec1f8a -->
# Contextual Retrieval

## Sources

- [Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)
- [Commit-pinned public mirror](https://github.com/sullivan-street-projects/anthropic-docs-local/blob/47546f2f5efa88d5c79f158dd58340c5c315e7d1/engineering/contextual-retrieval.md)

## At a glance

| Question | Rule |
| --- | --- |
| What problem does it solve? | A chunk can lose the document context needed to retrieve it. Add a short, chunk-specific explanation before indexing. |
| Which indexes change? | Prepend the explanation before creating both the semantic embedding and the BM25 lexical index. |
| Should I add reranking? | Test it when retrieval quality justifies another runtime step. Measure latency and cost as well as retrieval failure. |
| How many chunks should I pass on? | Start by testing 20. Anthropic found 20 more effective than 5 or 10 in its evaluation, but recommends testing the local use case ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)). |
| When should I skip retrieval? | If the complete knowledge base is under 200,000 tokens, first test putting it in the prompt with prompt caching ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)). |

Traditional retrieval-augmented generation (RAG) splits a document into
chunks. A chunk can then say "the company" or "the previous quarter" without
naming the company or period. Semantic and lexical search can both miss it
because the evidence needed to identify it was left in another chunk.

Contextual Retrieval keeps the original chunk and prepends a short explanation
of where that chunk sits in the document. The enriched text feeds two separate
retrieval paths:

| Path | What gets indexed | What it is good at |
| --- | --- | --- |
| Contextual Embeddings | Generated context plus the original chunk | Semantic similarity |
| Contextual BM25 | Generated context plus the original chunk | Exact words, identifiers, and phrases |

Combine the two result sets with rank fusion. Reranking is a later, optional
filter. It scores the combined candidates against the query before the final
chunks go into the model prompt.

## Decision guide

### 1. Start with the simplest prompt that fits

If the complete knowledge base is smaller than 200,000 tokens (about 500 pages in Anthropic's rule of thumb), test putting the complete knowledge base in the prompt ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)).
Prompt caching can make that option practical. Do not build a retrieval
pipeline until the simpler option fails the quality, latency, or cost target.

Use Contextual Retrieval when the knowledge base is too large for that approach
and chunk-level retrieval is losing document-level meaning. Keep ordinary RAG
when local evals show that the added preprocessing does not improve retrieval
enough to justify its cost and extra components.

### 2. Generate context once per chunk

Give the context-generation model the complete document and one target chunk.
Ask for only a short explanation that situates the chunk for retrieval. The
prompt pattern is:

1. Delimit the complete document.
2. Delimit the target chunk.
3. Ask for concise context that identifies the chunk's place in the document.
4. Return only that context.

Anthropic says the generated context is typically 50-100 tokens ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)). Prepend it to
the original chunk before creating the embedding and before adding the chunk to
the BM25 index. Keep the context distinct from the original content when the
retrieved chunk later enters the generation prompt.

### 3. Evaluate the combined retriever

Anthropic reports the following results. Its evaluation covered codebases,
fiction, ArXiv papers, and science papers.
The reported comparison used its top-performing embedding configuration (Gemini Text 004), retrieved 20 chunks, and measured retrieval failure as 1 minus recall at 20 ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)).

| Retrieval method | Top-20 retrieval failure | Reported reduction |
| --- | --- | --- |
| Baseline embeddings | 5.7% | Baseline ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)) |
| Contextual Embeddings | 3.7% | 35% ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)) |
| Contextual Embeddings plus Contextual BM25 | 2.9% | 49% ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)) |
| Reranked Contextual Embeddings plus Contextual BM25 | 1.9% | 67% ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)) |

These are Anthropic's evaluation results, not a general performance guarantee.
Build a local eval set before choosing the embedding model, fusion settings,
chunk shape, or reranker.

### 4. Add reranking only when the trade-off works

Anthropic's reranking evaluation retrieved 150 candidates, scored them against the query, and passed the top 20 into the model ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)). Filtering can reduce the amount
of irrelevant text sent to the generation model. The reranker also adds a
runtime step and therefore adds latency. Reranking more candidates can improve
retrieval while increasing latency and cost.

Measure retrieval failure, end-to-end latency, and cost. Skip reranking when
the quality gain is not worth the added latency, cost, and complexity.

### 5. Price preprocessing with the source assumptions visible

Anthropic estimates a one-time contextualization cost of about $1.02 per million document tokens with prompt caching ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)).
Its estimate assumes 800-token chunks, 8,000-token documents, 50 tokens of instructions, and 100 generated context tokens per chunk ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval)). Treat this as the source's estimate, not a current
price quote or a forecast for a different corpus.

## Checklist

- [ ] Test the complete-knowledge-base prompt when the corpus is under 200,000 tokens. ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval))
- [ ] Define a retrieval-failure metric and a local eval set before changing the index.
- [ ] Choose chunk size, boundaries, and overlap through evals.
- [ ] Generate context from the complete document and one target chunk.
- [ ] Preserve the original chunk; prepend generated context for both indexes.
- [ ] Combine semantic and BM25 results with rank fusion.
- [ ] Compare 5, 10, and 20 delivered chunks; use 20 only if local results support it. ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval))
- [ ] Test reranking separately from contextualization.
- [ ] Measure query latency, preprocessing cost, runtime cost, and retrieval quality.
- [ ] Keep generated context distinguishable from source content in the final prompt.

## Rules of thumb

- Added context can restore missing retrieval cues. It does not repair a bad source document.
- Chunking is an eval variable. Size, boundary, and overlap can all change retrieval.
- Keep a lexical path for exact identifiers. Do not replace BM25 with embeddings.
- Twenty chunks is a starting point from Anthropic's tests, not a universal constant. ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval))
- Reranking is a quality-versus-runtime decision, not a default requirement.
- Recheck prices before budgeting. The $1.02 figure is Anthropic's September 2024 estimate under stated assumptions. ([Anthropic](https://www.anthropic.com/engineering/contextual-retrieval))
- Do not use Contextual Retrieval when a complete prompt is simpler and meets the target.
- Do not keep it when local evals cannot show enough gain to pay for the extra pipeline.

## Claim review

- [x] Every figure traces to a cited source or is labelled Own experience.
- [x] Every factual claim stays within the cited evidence.
- [x] Evidence limits and qualifiers remain explicit.

## Privacy review

- [x] No employer material.
- [x] No customer material.
- [x] No private-repository material.
- [x] No trace material.
- [x] No transcript material.

<!-- unslop-writing:passed -->
