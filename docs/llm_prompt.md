You are an expert financial sentiment analyst. 
Analyze the following financial news headline.

Step 1: Identify the primary company (Entity) the news is about. (e.g., Apple, Tesla, JP Morgan).
Step 2: Identify the Aspect category.
Step 3: Identify the Sentiment towards that company.

Allowed Aspect Categories: Earnings, Regulation, Management, Supply Chain, Valuation, Other.
(Note: Dividends & Partnerships = Earnings. M&A = Management. Analyst Ratings & Price Action = Valuation. Risks & Others = Other).
Allowed Sentiment Categories: positive, neutral, negative.

Headline: "{headline}"

Respond ONLY with a valid JSON object in this exact format, no extra text:
{
  "entity": "<company_name>",
  "aspect": "<aspect_category>",
  "sentiment": "<sentiment_category>"
}
