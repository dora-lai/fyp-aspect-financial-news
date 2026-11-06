# LLM Selection & Cost Estimate (Task 52)

## Model Choice
- **Model Family:** Google Gemini
- **Model Name:** Gemini 1.5 Flash
- **Fixed Model Version:** `gemini-1.5-flash`
*(Note: Using a fixed model version ensures reproducibility. This model is part of Google's free tier, which guarantees zero cost for the project while providing sufficient capability for NLP tasks.)*

## Pricing (Official Google AI Pricing Page)
- **Input:** $0.00 (Free tier)
- **Output:** $0.00 (Free tier)

## Free Tier Limits
- **15 RPM** (Requests Per Minute)
- **1 Million TPM** (Tokens Per Minute)
- **1,500 RPD** (Requests Per Day)

## Cost Estimate for Project
1. **Pilot/Gold Set (200 Headlines):**
   - Total requests: 200.
   - Well within the 1,500 requests/day limit.
   - **Estimated Cost:** $0.00 USD.

2. **Large-Scale Corpus (Tier C - FNSPID):**
   - If we sample 10,000 headlines for the final volatility engine.
   - The processing can be spread across multiple days (e.g., ~7 days), staying strictly within the 1,500 daily requests limit.
   - **Estimated Cost:** $0.00 USD.

## Conclusion
The Google Gemini API free tier provides a highly cost-effective and zero-budget solution for the entire project. It avoids the need for credit card binding and fulfills the project's scale requirements.
