# Annotation Guideline v0.2

## Purpose
Defines the annotation rules for the Tier B pilot and gold-standard set. Used
by both annotators to label US financial headlines with
entity, aspect, and sentiment. Inter-annotator agreement is measured with
Cohen's kappa.

## Task
For each financial headline, annotate three fields:
- **Entity** — the company the sentiment is directed toward.
- **Aspect** — one of the broad classes in `taxonomy_v0.1.md`.
- **Sentiment** — positive, neutral, or negative.

## Rules
1. **Entity:** the company the sentiment targets, not the publisher or author.
   If the headline mentions two companies, annotate each in its own row.
2. **Multiple aspects:** if a headline touches more than one aspect, annotate
   each separately in its own row.
3. **Unclear sentiment:** if the sentiment is ambiguous, choose neutral.
4. **Unclear aspect:** if no aspect from the taxonomy fits, use "Other".
5. **Headlines only:** annotate all items regardless of the FiQA `format`
   field (headline or post).
6. **No inference:** do not use knowledge outside the headline. If the
   sentiment is not clear from the text alone, choose neutral.

## Output format

| headline_id | sentence | entity | aspect | sentiment |
|---|---|---|---|---|
| 001 | Tesco's Sales Pickup Isn't Enough | Tesco | Earnings | negative |
| 002 | Apple beats Q4 earnings expectations | Apple | Earnings | positive |

Sentiment labels must be one of: `positive`, `neutral`, `negative`.
Aspect labels must match exactly one of the classes in `taxonomy_v0.1.md`.

## Annotation template usage
Both annotators use the same CSV template:

    headline_id, sentence, entity, aspect, sentiment

Rules:
- Do not change the column order.
- Do not leave `entity`, `aspect`, or `sentiment` blank.
- Save your file as `dora_pilot_annotations.csv` or
  `janice_pilot_annotations.csv`.
- Do not look at the other annotator's file before submitting yours.

## Worked examples

| headline | entity | aspect | sentiment | reasoning |
|---|---|---|---|---|
| Tesco's Sales Pickup Isn't Enough | Tesco | Earnings | negative | Sales pickup insufficient, negative on earnings |
| Apple beats Q4 earnings expectations | Apple | Earnings | positive | Beat expectations, positive on earnings |
| Twitter CEO steps down | Twitter | Management | neutral | Leadership change, sentiment unclear |
| SEC fines Tesla over Musk tweet | Tesla | Regulation | negative | Regulator fine, negative |
| Tesla recalls 50,000 vehicles over seatbelt defect | Tesla | Other | negative | Operational risk, not regulatory or supply chain |

## Cohen's kappa
Inter-annotator agreement is computed on (entity, aspect, sentiment) triplets
after exact match.

Formula:

    kappa = (Po - Pe) / (1 - Pe)

where `Po` is observed agreement and `Pe` is expected agreement by chance.

Report:
- Kappa on **aspect** alone
- Kappa on **sentiment** alone
- Kappa on the **pair** (aspect, sentiment)

## Ambiguity rule
If kappa on any category is below 0.4, merge that category with the nearest one
and re-annotate the affected items. Recompute kappa after merging.

Target kappa for the final gold set: at least 0.6.

## Pilot
- Pilot batch: 20 to 30 headlines (Janice's Task 29, Week 2).
- Both annotators (Dora and Janice) annotate independently.
- Adjudication call after computing kappa.
- Kappa reported in Week 3 (Task 38).

## Adjudication procedure
1. Merge both annotation files on `headline_id`.
2. Mark rows where the two annotators disagree.
3. Discuss each disagreement and agree on a final label.
4. Record the agreed final label in the gold set.
5. Update the taxonomy if a pattern of disagreements emerges.

## Version history

| Version | Date | Change |
|---|---|---|
| v0.1 | Oct 2025 | First draft, before pilot annotation |
| v0.2 | 16 Oct 2025 | Added template usage and worked examples, ready for pilot |
| v1.0 | TBD | Frozen after adjudication (Task 49) |

## Open questions to resolve after pilot
1. How strict should the "neutral" rule be when sentiment is mixed?
2. Should aspect labels be assigned at the headline level or the entity level?
3. How should rumours be handled — as Valuation or as a separate class?
