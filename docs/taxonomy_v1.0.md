# Aspect Taxonomy v1.0 (Frozen)

**Status:** Frozen for the 200-headline Gold-Standard Annotation.
This version incorporates the rules standardized during the pilot adjudication.

## Broad Classes

### 1. Earnings
**Definition:** Revenue, profit, EPS, quarterly results, guidance, dividends, and partnership announcements that affect earnings.
**FiQA prefix:** `Corporate/Sales`, `Corporate/Dividend Policy`, `Corporate/Financial/*/Earnings`
**Examples:**
- "Tesco's Sales Pickup Isn't Enough"
- "Apple beats Q4 earnings expectations"

### 2. Regulation
**Definition:** Laws, regulatory investigations, fines, sanctions, and central bank policy changes.
**FiQA prefix:** `Corporate/Regulatory`, `Corporate/Legal`, `Economy/Central Banks`, `Economy/Trade/Sanctions`
**Examples:**
- "Facebook faces new EU privacy probe"
- "SEC fines Tesla over Musk tweet"

### 3. Management
**Definition:** Executive appointments, board actions, corporate strategy, mergers, acquisitions, and reorganisations.
**FiQA prefix:** `Corporate/Appointment`, `Corporate/Strategy`, `Corporate/M&A`
**Examples:**
- "Twitter CEO steps down"
- "Boeing board fires CEO"

### 4. Supply Chain
**Definition:** Suppliers, logistics, production, raw materials, and manufacturing disruptions.
**FiQA prefix:** (no direct FiQA equivalent; assigned during manual annotation)
**Examples:**
- "Nike warns of Vietnam factory delays"
- "Chip shortage hits auto makers"

### 5. Valuation
**Definition:** Stock price movements, multiples, analyst ratings, buybacks, rumours affecting price, and index changes (e.g., S&P 500 additions).
**FiQA prefix:** `Stock/*`, `Market/*`, `Corporate/Rumors`
**Examples:**
- "Tesla trades at 100x forward earnings"
- "Analysts cut Apple price target"

### 6. Other
**Definition:** Any aspect that does not fit the five classes above, including operational risks.
**FiQA prefix:** `Corporate/Risks/*` and any unmapped category.
**Examples:**
- "Tesla recalls 50,000 vehicles over seatbelt defect"

---
## Adjudication Rules Applied (from Pilot)
- **Dividends & Buybacks:** Classified as `Earnings`.
- **Partnerships & Collaborations:** Classified as `Earnings`.
- **Index Changes & Price Action:** Classified as `Valuation`.
- **Acquisitions (M&A):** Classified as `Management`.
