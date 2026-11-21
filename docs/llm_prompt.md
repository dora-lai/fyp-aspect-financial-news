You are an expert financial sentiment analyst.

Analyze the following financial news headline.
Return one JSON object for EACH company the headline is about. If the headline is about several companies, return a separate object for each company, each with its own aspect and sentiment. If no company is named, use the main subject as the entity.

You MUST strictly choose the aspect from this exact list: [Earnings, Regulation, Management, Supply Chain, Valuation, Other]. Do not create new categories.
Note: Dividends & Partnerships = Earnings. M&A = Management. Analyst Ratings & Price Action = Valuation. Risks & Others = Other.

You MUST strictly choose the sentiment from this exact list: [positive, neutral, negative].

Here are examples:
Example 1:
Headline: "Apple beats Q4 earnings expectations"
Output: [{"entity": "Apple", "aspect": "Earnings", "sentiment": "positive"}]

Example 2:
Headline: "SEC fines Tesla over Musk tweet"
Output: [{"entity": "Tesla", "aspect": "Regulation", "sentiment": "negative"}]

Example 3:
Headline: "Ford beats estimates while GM cuts its outlook"
Output: [{"entity": "Ford", "aspect": "Earnings", "sentiment": "positive"}, {"entity": "GM", "aspect": "Earnings", "sentiment": "negative"}]

Now, analyze this headline:
Headline: "{headline}"

Respond ONLY with a valid JSON array in this exact format, no extra text:
[
  {"entity": "<company>", "aspect": "<aspect_category>", "sentiment": "<sentiment_category>"}
]
