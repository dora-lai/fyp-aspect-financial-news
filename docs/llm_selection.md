# LLM Selection & Cost Estimate (Task 52)

## Model Choice
- **Provider:** Google AI Studio (Gemini API)
- **Model Family:** Gemini 3.5 Flash-Lite
- **Model Name:** `gemini-3.5-flash-lite`
*(Note: This model was selected for the Phase 1 evaluation due to its high inference speed and generous free-tier quota, which ensures zero operational costs for the project while providing highly accurate aspect-level extraction.)*

## Pricing (Google AI Studio)
- **Input:** $0.00 (Free Tier)
- **Output:** $0.00 (Free Tier)

## Rate Limits (Free Tier)
- **RPM (Requests Per Minute):** 15 requests
- **RPD (Requests Per Day):** 500 requests

## Cost Estimate for Project
1. **Phase 1: Gold Set Evaluation (200 Headlines)**
   - **Total requests:** 200 headlines × 3 runs (for variance testing) = 600 calls.
   - **Execution Plan:** To stay within the 500 RPD limit, the 3 runs will be executed across 2 days (e.g., Run 1 & 2 on Day 1, Run 3 on Day 2).
   - **Estimated Cost:** $0.00 USD.

2. **Phase 2: Large-Scale Corpus (Semester 2)**
   - If we sample 5,000 to 10,000 headlines for the final volatility engine.
   - **Estimated Cost:** $0.00 USD (Processing will be batched over several days or transitioned to the CUHK Foundry API WUS3 `gpt-5.6-sol` once the institutional quota is approved).

## Conclusion
The Google Gemini 3.5 Flash-Lite provides a highly capable, zero-cost solution for the project's evaluation phase. It successfully meets the project's scale requirements and avoids the need for personal credit card binding.
