# Tier C news pipeline

`news_pipeline.py` holds every rule of the Tier C news pipeline in one file, so all notebooks use the same logic.

```
FNSPID
  -> stream in chunks, keep 4 columns          stream_fnspid, read_parts
  -> remove exact and near-duplicates          deduplicate
  -> ticker -> S&P 500 company -> sector ETF   build_sp500, map_to_sector_etf
  -> publication time -> NYSE trading day      load_calendar, trading_dates
  -> about one named company, no templates     add_relevance, keep_informative
  -> one daily series per sector ETF           daily_by_etf
```

## Files

| File | What it is |
|---|---|
| `news_pipeline.py` | The module |
| `Pipeline_Check.ipynb` | To check if the module reproduces the results of all five notebooks from the real files in Google Drive|

## Setup in Colab

1. Upload `news_pipeline.py` to **My Drive/pipeline/**.
2. In a notebook:

```python
import sys; sys.path.append('/content/drive/MyDrive/pipeline')
import news_pipeline as npl
```

The module reads from the same Drive folders as the notebooks: `fnspid_news/data`, `fnspid_news/results`, `etf_extraction/data` and `annotation_data` (see `npl.paths()`).

## Functions

| Section | Function | Does |
|---|---|---|
| Settings | `paths()` | All file locations in one dictionary |
| | `START`, `END`, `SIGNAL_START` | Backtest window (30 May 2007 to 29 Dec 2023); news signal used from 2010 |
| | `ETF_UNIVERSE` | The 21 downloaded ETFs with group and role (= `etf_universe.csv`) |
| | `SECTOR_TO_ETF`, `SECTOR_ETFS`, `CROSS_ASSET_ETFS`, `UNIVERSE`, `OWN_NEWS_ETFS`, `MIN_PCT_DAYS` | The 18-ETF universe; GLD and AGG get own-ticker news; the 50%-of-days rule |
| Ingestion | `stream_fnspid(parts_dir, results_dir)` | Reads FNSPID from Hugging Face in chunks of 500,000 rows and saves the count tables |
| | `profile_counts(chunks)`, `save_profile(...)` | Rows and date-only rows per year, rows per ticker, empty values per column |
| | `read_parts(parts_dir)` | Joins the saved chunks |
| | `deduplicate(news)` | Exact and near-duplicates removed; returns the clean table and a counts table |
| | `load_clean_news()` | The cleaned table (5,541,739 headlines) |
| Reference data | `parse_ishares_holdings(path)` | Reads an iShares holdings file (IVV or IWV) and its list date |
| | `build_sp500()`, `load_sp500()` | S&P 500 companies with sector ETF |
| | `build_us_companies()` | Russell 3000 companies with sector ETF (fallback) |
| | `download_holdings(url, path)`, `IVV_URL`, `IWV_URL` | Download an iShares holdings file once |
| | `load_calendar()`, `make_calendar()` | NYSE trading days with close times |
| Prices | `download_prices(tickers)`, `load_prices()` | Daily adjusted close |
| | `start_dates(prices)`, `price_quality(prices)` | First and last date per ETF; gaps inside each history |
| | `common_window(prices)`, `log_returns(prices)` | 30 May 2007 – 29 Dec 2023; daily log returns |
| Mapping | `normalise_ticker(series)` | FNSPID side: FB → META, BRK → BRK.B, BRK-B / BRK B → BRK.B |
| | `holdings_ticker(series)` | iShares side: BRKB → BRK.B, BFB / BF B → BF.B |
| | `map_to_sector_etf(news, sp500)` | Adds company, GICS sector, sector ETF, `mapped` flag |
| | `map_with_fallback(news, us)` | Adds the Russell 3000 fallback (`mapped_broad`) |
| | `mapping_rate(news, column)` | Share mapped, in % (23.9%; 43.9% with `'mapped_broad'`) |
| Trading days | `to_trading_day(published, cal)` | One headline (readable version) |
| | `trading_dates(series, cal)` | Millions of headlines at once, same rule |
| Relevance | `is_relevant(title, company, ticker)` | Names its company and is not a template or list |
| | `add_relevance(news)` | Adds the `relevant` column |
| | `keep_informative(news)` | Relevant, no extra template, at least 4 words: the rule for the gold set **and** Tier C |
| Build | `build_mapped(news, sp500, cal)` | Clean FNSPID → the mapped table (= `fnspid_mapped.parquet`) |
| | `own_ticker_news(news, cal, etfs)` | Headlines tagged with an ETF's own ticker (all 21 by default) |
| | `etf_news_coverage(mapped, own, cal)` | The 50%-of-days rule for every ETF (= `coverage_all_etf_news.csv`) |
| | `news_signal_etfs(coverage)` | The ETFs that pass: 11 sector ETFs + GLD + AGG |
| | `annotation_pool(mapped, years, exclude_titles)` | Headlines that can be sampled for annotation |
| Sampling | `pilot_pool(news, sp500)`, `sector_sample(pool, 4, 42)` | Reproduces the 44-headline pilot |
| | `stratified_sample(pool, total, seed)` | 1 per sector-year cell, then random within sector |
| | `shared_subset(sample, size, seed)` | The double-annotated subset |
| | `blank_annotation_file(sample)` | The 5-column annotation template |
| Aggregation | `daily_by_etf(df, days, value=None)` | Headlines per day per ETF; with `value='score'`, the daily mean sentiment |
| | `coverage_table(df, days)` | Median headlines per day and share of days with news |
| Self-tests | `run_self_tests(cal)` | 33 checks: trading-day cases, tickers (both sides), relevance, templates |

## Data source

News headlines: FNSPID (Dong, Fan & Peng, 2024), https://huggingface.co/datasets/Zihan1004/FNSPID, CC BY-NC 4.0, used for non-commercial academic research.
S&P 500 constituents and GICS sectors: iShares Core S&P 500 ETF (IVV) holdings, BlackRock iShares.
