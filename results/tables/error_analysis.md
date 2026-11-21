# Error Analysis: Extraction Methods (Task 73)

During the evaluation of the baseline models on the 200 US Gold Set, FinBERT achieved an accuracy of **60.19%** (Macro F1: 0.6023), while the lexicon-based VADER model performed even lower with an accuracy of **45.83%**. This means FinBERT made errors on roughly 80 out of 200 headlines. 

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

## LLM Comparison & Run-to-Run Variance
In stark contrast to FinBERT's 60.19% accuracy, the Gemini 3.5 Flash-Lite LLM achieved an average Sentiment Accuracy of **86.87%** on the same Gold Set. 
While the LLM's consistency across 3 runs was exceptionally high (96.95% for sentiment), a review of its minor inconsistencies (e.g., predicting 'negative' in Run 1/2 but 'neutral' in Run 3 for Ulta Beauty) shows that LLMs are occasionally sensitive to borderline analyst ratings. However, the LLM successfully handled the multi-entity and jargon-related errors that plagued FinBERT, proving its superiority for this task.
