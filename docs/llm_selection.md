# LLM Selection & Cost Estimate (Task 52)

## Model Choice
- **Provider:** CUHK API Portal (Microsoft Azure Foundry)
- **Model Family:** CUHK Foundry Models WUS3
- **Model Name:** `gpt-5.6-sol`
*(Note: Using this fixed model version ensures reproducibility. This model is accessed via the university's APIM subscription, which provides a secure, enterprise-grade environment for FYP and academic research.)*

## Pricing (CUHK API Portal)
- **Input:** $0.00 (Covered by CUHK academic allocation)
- **Output:** $0.00 (Covered by CUHK academic allocation)

## Rate Limits (Starter Tier & FYP Allocation)
- **Starter Base Limit:** 5 calls per minute (RPM), 100 calls per week.
- **FYP Requested Quota:** We have requested a project-specific quota increase to 1,500 calls to accommodate the 200-headline dataset (3 runs = 600 calls) plus debugging.

## Cost Estimate for Project
1. **Phase 1: Gold Set Evaluation (200 Headlines)**
   - **Total requests:** 200 headlines × 3 runs (for variance testing) = 600 calls.
   - **Estimated Cost:** $0.00 USD (Within requested FYP quota).

2. **Phase 2: Large-Scale Corpus (Tier C - FNSPID)**
   - If we sample 5,000 to 10,000 headlines for the final volatility engine in Semester 2.
   - We will submit a separate quota request for Semester 2 based on the baseline performance.
   - **Estimated Cost:** $0.00 USD.

## Conclusion
The CUHK Foundry Models WUS3 (gpt-5.6-sol) provides a highly capable, enterprise-grade LLM for zero direct cost to the students. It successfully meets the project's data privacy and scale requirements, and avoids the need for personal credit card binding.
