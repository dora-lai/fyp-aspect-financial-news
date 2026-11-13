# Error Analysis: FinBERT on the US Gold Set (Task 73)

After running FinBERT on the 200 US Gold Set headlines, the model made errors on approximately 40% of the data. A manual review of the misclassifications reveals three main failure modes:

1. **Misinterpreting Questions:** FinBERT struggles with headlines phrased as questions (e.g., "Will J.M Smucker's Earnings Disappoint?"). It focuses on the word "Earnings" and predicts positive, failing to understand the negative implication of the word "disappoint".
2. **Mixed Sentiments:** Headlines containing both good and bad news (e.g., "Waste Management misses by $0.02, beats on revenue") confuse the model, leading to incorrect or neutral predictions.
3. **Analyst Jargon & Multi-Entity Headlines:** Headlines with multiple companies or complex analyst ratings (e.g., "JP Morgan Downgrades Dow Chemical from Overweight to Neutral") often lead to incorrect sentiment assignment because FinBERT cannot differentiate which company the sentiment applies to.

**Conclusion:** Document-level models like FinBERT lack entity-awareness and aspect-level reasoning. This confirms the need for the Gemini LLM, which can process specific targets and aspects.
