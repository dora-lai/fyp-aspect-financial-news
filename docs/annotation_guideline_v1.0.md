# Annotation Guideline v1.0 (Frozen)

**Status:** Frozen for the 200-headline Gold-Standard Annotation.

## Task
For each financial headline, annotate:
- **Entity** — the company the sentiment is directed toward.
- **Aspect** — one of the broad classes in `taxonomy_v1.0.md`.
- **Sentiment** — positive, neutral, or negative.

## Rules
1. **Entity:** The company the sentiment targets. If the headline mentions two companies, annotate each in its own row.
2. **Multiple aspects:** If a headline touches more than one aspect, annotate each separately.
3. **Unclear sentiment:** If the sentiment is ambiguous, choose `neutral`.
4. **Unclear aspect:** If no aspect fits, use `Other`.
5. **Headlines only:** Annotate all items regardless of the FiQA `format` field.
6. **No inference:** Do not use knowledge outside the headline. 

## Output format
| headline_id | sentence | entity | aspect | sentiment |
|---|---|---|---|---|
| 001 | Tesco's Sales Pickup Isn't Enough | Tesco | Earnings | negative |

## Cohen's kappa
Kappa is computed on (entity, aspect, sentiment) triplets after exact match.
Target kappa for the gold set: at least 0.60.

## Adjudication procedure
1. Merge both annotation files on `headline_id`.
2. Mark rows where the two annotators disagree.
3. Discuss each disagreement and agree on a final label.
4. Record the agreed final label in the gold set.

## Version history
| Version | Date | Change |
|---|---|---|
| v0.1 | Oct 2025 | First draft |
| v0.2 | Oct 2025 | Added template usage and examples |
| v1.0 | Nov 2025 | **Frozen post-pilot.** Added adjudication rules. |
