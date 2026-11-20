# Error Analysis: FinBERT on the US Gold Set (Task 73)

During the evaluation of the baseline models on the 200 US Gold Set, FinBERT achieved an accuracy of 60.19%. This means it made errors on 80 out of 200 headlines. 

A manual review of the misclassifications reveals that the errors fall into three main categories:

## 1. Failure to Understand Analyst Jargon & Context
FinBERT often gets confused by the combination of positive and negative words in analyst ratings.
- **Example 1:** *"JP Morgan Downgrades Dow Chemical from Overweight to Neutral, Maintains PT from $36"*
  - **True Label:** negative
  - **FinBERT Prediction:** positive
  - *(Reason: FinBERT likely focused on the word "Overweight" which usually implies a positive sentiment, completely missing the context of the word "Downgrades".)*
- **Example 2:** *"DA Davidson Upgrades EMCOR Group, Inc. to Buy"*
  - **True Label:** positive
  - **FinBERT Prediction:** neutral
  - *(Reason: FinBERT failed to recognize that an "Upgrade to Buy" is a strong positive signal.)*

## 2. Confusion with Financial Phrasing
FinBERT sometimes misinterprets standard financial phrases or action verbs.
- **Example 3:** *"Cigna Hikes 2011 View After 2Q Earnings Beat"*
  - **True Label:** positive
  - **FinBERT Prediction:** negative
  - *(Reason: Despite "Earnings Beat", the model likely got confused by the phrasing "Hikes View" or other token combinations.)*

## 3. Overreacting to Neutral Corporate Events
FinBERT sometimes assigns negative sentiment to routine corporate filings that are actually neutral.
- **Example 4:** *"Vulcan Materials Company Files Mixed Security Shelf"*
  - **True Label:** neutral
  - **FinBERT Prediction:** negative
  - *(Reason: The model likely reacted to the word "Mixed" or "Security Shelf" and incorrectly flagged it as a negative event.)*

## Conclusion
Document-level models like FinBERT lack entity-aware and aspect-level reasoning. They rely heavily on isolated keywords rather than the full sentence context. This justifies the need for the zero-shot LLM (Gemini) approach, which can successfully distinguish between the target entity, the specific aspect, and the overall sentiment.
