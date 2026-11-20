# Domain Gap Analysis (Task 72)

## Results
- **FiQA 2018 Test Set:** FinBERT achieved a Macro F1 of 0.5619.
- **US Gold Set (FNSPID):** FinBERT achieved a Macro F1 of 0.6023.

## Analysis
Contrary to the typical expectation of performance degradation, FinBERT performed slightly better on the US Gold Set than on the FiQA benchmark (an improvement of ~4%). 

This positive domain gap can be attributed to two main factors:
1. **Vocabulary Alignment:** The FNSPID dataset consists of standard US financial news headlines. FinBERT (ProsusAI) was originally pre-trained on US financial text (Reuters, Yahoo Finance). Therefore, the FNSPID Gold Set is linguistically closer to FinBERT's training domain than the FiQA dataset, which contains many short, informal social media posts and complex multi-target headlines.
2. **Annotation Standards:** The human-annotated Gold Set labels were derived from the strict Taxonomy v1.0, which provides a clearer and more consistent ground truth compared to the FiQA baseline thresholds.

Despite FinBERT's relatively stable performance, its overall Macro F1 remains relatively low (~0.60). This confirms that document-level models lack aspect-level reasoning and entity-awareness, justifying the use of the Gemini LLM for the final system.
