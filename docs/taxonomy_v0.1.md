# Aspect Taxonomy v0.1

## Purpose
Defines the aspect categories used for annotating financial headlines in the
Tier B gold-standard set and for aspect-level LLM prompting in Tier A.

## Source
Derived from the FiQA 2018 aspect categories and merged into five broad classes
plus an "Other" fallback.

## Broad classes

### 1. Earnings
**Definition:** Revenue, profit, EPS, quarterly results, guidance, dividends,
and partnership announcements that affect earnings.

**FiQA prefix:** `Corporate/Sales`, `Corporate/Dividend Policy`,
`Corporate/Financial/*/Earnings`

**Examples:**
- "Tesco's Sales Pickup Isn't Enough"
- "Apple beats Q4 earnings expectations"

### 2. Regulation
**Definition:** Laws, regulatory investigations, fines, sanctions, and central
bank policy changes.

**FiQA prefix:** `Corporate/Regulatory`, `Corporate/Legal`,
`Economy/Central Banks`, `Economy/Trade/Sanctions`

**Examples:**
- "Facebook faces new EU privacy probe"
- "SEC fines Tesla over Musk tweet"

### 3. Management
**Definition:** Executive appointments, board actions, corporate strategy,
mergers, acquisitions, and reorganisations.

**FiQA prefix:** `Corporate/Appointment`, `Corporate/Strategy`, `Corporate/M&A`

**Examples:**
- "Twitter CEO steps down"
- "Boeing board fires CEO"

### 4. Supply Chain
**Definition:** Suppliers, logistics, production, raw materials, and
manufacturing disruptions.

**FiQA prefix:** (no direct FiQA equivalent; assigned during manual annotation)

**Examples:**
- "Nike warns of Vietnam factory delays"
- "Chip shortage hits auto makers"

### 5. Valuation
**Definition:** Stock price movements, multiples, analyst ratings, buybacks,
rumours affecting price, and market volatility.

**FiQA prefix:** `Stock/*`, `Market/*`, `Corporate/Rumors`

**Examples:**
- "Tesla trades at 100x forward earnings"
- "Analysts cut Apple price target"

### 6. Other
**Definition:** Any aspect that does not fit the five classes above, including
operational risks that are not regulatory or supply-chain related.

**FiQA prefix:** `Corporate/Risks/*` and any unmapped category.

**Examples:**
- "Tesla recalls 50,000 vehicles over seatbelt defect"

## FiQA aspect mapping table

| FiQA top-level prefix | Broad class | Count in FiQA test set |
|---|---|---|
| Corporate/Appointment | Management | 17 |
| Corporate/Dividend Policy | Earnings | 9 |
| Corporate/Financial/*/Earnings | Earnings | 1 |
| Corporate/Legal | Regulation | 1 |
| Corporate/M&A | Management | 7 |
| Corporate/Regulatory | Regulation | 2 |
| Corporate/Risks | Other | 10 |
| Corporate/Rumors | Valuation | 6 |
| Corporate/Sales | Earnings | 9 |
| Corporate/Strategy | Management | 3 |
| Economy/Central Banks | Regulation | 2 |
| Economy/Trade/Sanctions | Regulation | 1 |
| Market/* | Valuation | 8 |
| Stock/* | Valuation | 70 |

## Notes
- Taxonomy v0.1 is a draft. It will be revised after the pilot annotation
  (Task 38) and frozen as v1.0 in Week 4 (Task 49).
- If two broad classes cover the same headline, annotate each separately.
- Data quality note: some FiQA aspect labels are malformed
  (e.g., `['Market/Volatility]` is missing a closing quote). These records are
  flagged in the audit and excluded from the mapping counts.

## Open questions for the pilot
1. Should "Earnings" and "Valuation" be merged into a single "Financials" class?
2. Should `Corporate/Risks/*` be split into "Legal Risk" and "Operational Risk"?
3. Should "Management" be renamed to "Corporate Strategy" to cover M&A activity?
4. Is "Supply Chain" sufficiently represented in FiQA to justify its own class?
