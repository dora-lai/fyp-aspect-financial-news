"""
news_pipeline.py: reusable Tier C news pipeline (FNSPID -> sector ETF -> trading day).

One place for every rule used in the project, so all notebooks (coverage audit, pilot and gold
samples, and the Semester 2 extraction, volatility and allocation work) use exactly the same logic.

Sections
    1. Settings          folders, backtest window, the 21 ETFs and their roles, ticker renames
    2. Ingestion         stream FNSPID from Hugging Face in chunks, count tables, deduplicate
    3. Reference data    S&P 500 / Russell 3000 lists from iShares holdings, trading calendar,
                         ETF prices (download, start dates, quality, common window, returns)
    4. Mapping           ticker -> company -> GICS sector -> sector ETF (+ Russell 3000 fallback)
    5. Trading days      publication time (UTC) -> NYSE trading day, no look-ahead
    6. Relevance         keep headlines about one named company, drop templates and lists
    7. Build             the mapped table, own-ticker ETF news, the 50%-of-days rule, annotation pool
    8. Sampling          pilot sample, stratified gold sample, shared subset
    9. Aggregation       one daily series per sector ETF (counts now, sentiment later)
   10. Self-tests        quick checks that the rules behave as intended

Use in Colab:
    import sys; sys.path.append('/content/drive/MyDrive/pipeline')
    import news_pipeline as npl
"""

import io
import os
import re

import numpy as np
import pandas as pd


# 1. Settings

DRIVE = '/content/drive/MyDrive'


def paths(drive=DRIVE):
    """All file locations used by the project, in one dictionary."""
    news, etf, ann = drive + '/fnspid_news', drive + '/etf_extraction', drive + '/annotation_data'
    return {
        'news_data': news + '/data',
        'news_results': news + '/results',
        'fnspid_parts': news + '/data/fnspid_parts',
        'fnspid_clean': news + '/data/fnspid_clean.parquet',
        'fnspid_mapped': news + '/data/fnspid_mapped.parquet',
        'etf_data': etf + '/data',
        'etf_results': etf + '/results',
        'ivv_holdings': etf + '/data/ivv_holdings.csv',
        'iwv_holdings': etf + '/data/iwv_holdings.csv',
        'sp500': etf + '/data/sp500_sectors.csv',
        'calendar': etf + '/data/trading_calendar.csv',
        'prices': etf + '/data/etf_prices.csv',
        'universe': etf + '/data/etf_universe.csv',
        'annotation': ann,
        'pilot_key': ann + '/pilot_key.csv',
        'gold_key': ann + '/gold_key.csv',
    }


START, END = pd.Timestamp('2007-05-30'), pd.Timestamp('2023-12-29')    # backtest window (set by BIL)
SIGNAL_START = pd.Timestamp('2010-01-01')                               # company news starts late 2009

SECTOR_TO_ETF = {
    'Information Technology': 'XLK', 'Financials': 'XLF', 'Energy': 'XLE', 'Health Care': 'XLV',
    'Industrials': 'XLI', 'Consumer Discretionary': 'XLY', 'Consumer Staples': 'XLP',
    'Utilities': 'XLU', 'Materials': 'XLB', 'Real Estate': 'VNQ', 'Communication Services': 'VOX',
}
SECTOR_ETFS = list(SECTOR_TO_ETF.values())                              # 11 ETFs with company news
CROSS_ASSET_ETFS = ['AGG', 'IEF', 'TLT', 'LQD', 'GLD', 'DBC', 'BIL']   # no company news
UNIVERSE = SECTOR_ETFS + CROSS_ASSET_ETFS                               # 18 ETFs in the allocation
OWN_NEWS_ETFS = ['GLD', 'AGG']        # cross-asset ETFs that passed the 50%-of-days rule (own-ticker news)
MIN_PCT_DAYS = 50                     # news-signal rule: news on at least 50% of trading days, 2016-2023

# The 21 ETFs downloaded
ETF_UNIVERSE = pd.DataFrame([
    ('XLK', 'Technology Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLF', 'Financial Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLE', 'Energy Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLV', 'Health Care Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLI', 'Industrial Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLY', 'Consumer Discretionary Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLP', 'Consumer Staples Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLU', 'Utilities Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('XLB', 'Materials Select Sector SPDR', 'Equity sector', 'Universe', 'Yes'),
    ('VNQ', 'Vanguard Real Estate ETF', 'Real estate', 'Universe', 'Yes'),
    ('VOX', 'Vanguard Communication Services ETF', 'Equity sector', 'Universe', 'Yes'),
    ('AGG', 'iShares Core U.S. Aggregate Bond ETF', 'Bond', 'Universe', 'No'),
    ('IEF', 'iShares 7-10 Year Treasury Bond ETF', 'Bond', 'Universe', 'No'),
    ('TLT', 'iShares 20+ Year Treasury Bond ETF', 'Bond', 'Universe', 'No'),
    ('LQD', 'iShares iBoxx $ Investment Grade Corporate Bond ETF', 'Bond', 'Universe', 'No'),
    ('GLD', 'SPDR Gold Shares', 'Gold', 'Universe', 'No'),
    ('DBC', 'Invesco DB Commodity Index Tracking Fund', 'Commodities', 'Universe', 'No'),
    ('BIL', 'SPDR Bloomberg 1-3 Month T-Bill ETF', 'Cash proxy', 'Universe', 'No'),
    ('SPY', 'SPDR S&P 500 ETF Trust', 'Broad equity', 'Benchmark only', 'No'),
    ('XLC', 'Communication Services Select Sector SPDR', 'Equity sector', 'Candidate (short history)', 'Yes'),
    ('XLRE', 'Real Estate Select Sector SPDR', 'Real estate', 'Candidate (short history)', 'Yes'),
], columns=['ticker', 'name', 'group', 'role', 'news_signal'])
# news_signal above is the column as first written (company news only). The final decision, after the coverage audit, is: Yes for the 11 sector ETFs plus GLD and AGG (own-ticker news); see etf_news_coverage().

TICKER_RENAMES = {'FB': 'META', 'BRK': 'BRK.B'}     # FNSPID ticker at the time -> current ticker

# 2. Ingestion

FNSPID_SOURCE = 'datasets/Zihan1004/FNSPID/Stock_news/nasdaq_exteral_data.csv'
FNSPID_COLUMNS = ['Date', 'Article_title', 'Stock_symbol', 'Publisher']


def profile_counts(chunks, columns=FNSPID_COLUMNS):
    """Count tables built piece by piece, as in Tier_C_FNSPID: rows and date-only rows per year,
    rows per ticker, empty values per column. `chunks` is any sequence of tables.
    Returns (year_table, ticker_table, empty_table)."""
    per_year = pd.Series(dtype='int64')
    per_year_date_only = pd.Series(dtype='int64')
    per_ticker = pd.Series(dtype='int64')
    empty = pd.Series(0, index=columns)
    rows = 0
    for chunk in chunks:
        year = chunk['Date'].str[:4]
        date_only = chunk['Date'].str[11:19] == '00:00:00'
        per_year = per_year.add(year.value_counts(), fill_value=0)
        per_year_date_only = per_year_date_only.add(year[date_only].value_counts(), fill_value=0)
        per_ticker = per_ticker.add(chunk['Stock_symbol'].value_counts(), fill_value=0)
        empty += chunk[columns].isna().sum()
        rows += len(chunk)

    year_table = pd.DataFrame({'rows': per_year, 'date_only_rows': per_year_date_only}).fillna(0).astype(int)
    year_table['date_only_pct'] = (year_table['date_only_rows'] / year_table['rows'] * 100).round(1)
    year_table = year_table.sort_index()
    year_table.index.name = 'year'
    ticker_table = per_ticker.astype(int).sort_values(ascending=False).rename('rows')
    ticker_table.index.name = 'ticker'
    empty_table = pd.DataFrame({'empty': empty.astype(int), 'empty_pct': (empty / rows * 100).round(2)})
    empty_table.index.name = 'column'
    return year_table, ticker_table, empty_table


def save_profile(year_table, ticker_table, empty_table, results_dir):
    """Save the three count tables with the same file names as Tier_C_FNSPID."""
    year_table.to_csv(results_dir + '/fnspid_rows_per_year.csv', index_label='year')
    ticker_table.to_csv(results_dir + '/fnspid_rows_per_ticker.csv', index_label='ticker', header=['rows'])
    empty_table.to_csv(results_dir + '/fnspid_empty_per_column.csv', index_label='column')


def stream_fnspid(parts_dir, results_dir=None, chunk_size=500_000, source=FNSPID_SOURCE):
    """Read the 23 GB FNSPID file straight from Hugging Face in chunks of 500,000 rows, save each
    chunk as a small Parquet file (4 columns only) and, if results_dir is given, save the three
    count tables. Skips the work if it was finished before (done.txt). Returns the number of rows."""
    os.makedirs(parts_dir, exist_ok=True)
    done = parts_dir + '/done.txt'
    if os.path.exists(done):
        print('Already done earlier:', open(done).read())
        return int(open(done).read().split()[0])

    from huggingface_hub import HfFileSystem    
    rows, pieces = 0, 0

    def chunks():
        nonlocal rows, pieces
        with HfFileSystem().open(source, 'rb') as f:
            reader = pd.read_csv(f, usecols=FNSPID_COLUMNS, dtype=str, keep_default_na=False, na_values=[''],
                                 chunksize=chunk_size, on_bad_lines='skip')
            for i, chunk in enumerate(reader):
                chunk.to_parquet(f'{parts_dir}/part_{i:03d}.parquet', index=False)
                rows, pieces = rows + len(chunk), i + 1
                print(f'piece {i:03d}: {rows:,} rows read')
                yield chunk

    tables = profile_counts(chunks())
    if results_dir:
        save_profile(*tables, results_dir)
    open(done, 'w').write(f'{rows} rows, {pieces} pieces')
    return rows


def read_parts(parts_dir):
    """Join all saved chunks into one table."""
    files = sorted(p for p in os.listdir(parts_dir) if p.endswith('.parquet'))
    return pd.concat([pd.read_parquet(f'{parts_dir}/{p}') for p in files], ignore_index=True)


def clean_title(titles):
    """Lower case, punctuation -> space, single spaces. Used to find near-duplicates."""
    t = titles.str.lower().str.replace(r'[^a-z0-9 ]', ' ', regex=True)
    return t.str.replace(r'\s+', ' ', regex=True).str.strip()


def deduplicate(news):
    """Remove unusable rows, exact duplicates (ticker + time + headline) and near-duplicates
    (ticker + calendar day + cleaned headline). Returns (clean table, counts table)."""
    counts = [('1. Read from FNSPID', len(news))]
    news = news.dropna(subset=['Date', 'Article_title', 'Stock_symbol'])
    counts.append(('2. After removing rows with no date, headline or ticker', len(news)))
    news = news.drop_duplicates(subset=['Stock_symbol', 'Date', 'Article_title'])
    counts.append(('3. After removing exact duplicates', len(news)))
    news = news.assign(day=news['Date'].str[:10], title_clean=clean_title(news['Article_title']))
    news = news.drop_duplicates(subset=['Stock_symbol', 'day', 'title_clean']).drop(columns='title_clean')
    counts.append(('4. After removing near-duplicates per ticker per day', len(news)))

    table = pd.DataFrame(counts, columns=['step', 'rows'])
    table['removed'] = (-table['rows'].diff()).fillna(0).astype(int)
    table['remaining_pct'] = (table['rows'] / table['rows'].iloc[0] * 100).round(1)
    return news, table


def load_clean_news(path=None):
    """The cleaned FNSPID table (5,541,739 headlines)."""
    return pd.read_parquet(path or paths()['fnspid_clean'])


# 3. Reference data

def normalise_ticker(tickers):
    """FNSPID ticker -> current ticker: upper case, '-' or ' ' -> '.', old tickers renamed
    (FB -> META, BRK -> BRK.B). Same rule as the coverage audit. Works on a pandas Series."""
    return tickers.str.upper().str.replace(r'[- ]', '.', regex=True).replace(TICKER_RENAMES)


def holdings_ticker(tickers):
    """iShares holdings ticker -> standard ticker: iShares writes BRKB / BFB and 'BRK B', so these
    become BRK.B / BF.B. Same rule as section 10 of Tier_C_ETF_Extraction."""
    t = tickers.astype(str).str.strip().replace({'BRKB': 'BRK.B', 'BFB': 'BF.B'})
    return t.str.upper().str.replace(r'[- ]', '.', regex=True)


def parse_ishares_holdings(path, dedup=True):
    """Read an iShares holdings CSV (IVV = S&P 500, IWV = Russell 3000).
    Returns (equity rows with ticker, company, gics_sector; the 'Fund Holdings as of' date)."""
    text = open(path, encoding='utf-8-sig').read()
    lines = text.splitlines()
    date_line = next(l for l in lines if l.startswith('Fund Holdings as of'))
    list_date = pd.to_datetime(re.search(r'"(.+)"', date_line).group(1)).date()
    header = next(i for i, l in enumerate(lines) if l.startswith('Ticker,'))
    h = pd.read_csv(io.StringIO(text), skiprows=header, on_bad_lines='skip')
    h = h[h['Asset Class'] == 'Equity']
    table = pd.DataFrame({'ticker': holdings_ticker(h['Ticker']),
                          'company': h['Name'],
                          'gics_sector': h['Sector'].replace({'Communication': 'Communication Services'})})
    if dedup:
        table = table.drop_duplicates('ticker')
    return table.reset_index(drop=True), list_date


def download_holdings(url, path):
    """Download an iShares holdings file once and keep the copy (later runs reuse it)."""
    if not os.path.exists(path):
        import requests
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
        r.raise_for_status()
        open(path, 'wb').write(r.content)
    return path


IVV_URL = 'https://www.ishares.com/us/products/239726/ishares-core-s-p-500-etf/latest-holdings.csv'
IWV_URL = 'https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/latest-holdings.csv'


def build_sp500(ivv_path=None, min_companies=400):
    """S&P 500 companies with their sector ETF, from the IVV holdings file."""
    sp500, list_date = parse_ishares_holdings(ivv_path or paths()['ivv_holdings'])
    sp500['sector_etf'] = sp500['gics_sector'].map(SECTOR_TO_ETF)
    sp500['list_date'] = list_date
    assert len(sp500) >= min_companies, f'Only {len(sp500)} companies: check the holdings file'
    return sp500


def load_sp500(path=None):
    """The saved S&P 500 list (sp500_sectors.csv)."""
    return pd.read_csv(path or paths()['sp500'])


def build_us_companies(iwv_path=None):
    """Russell 3000 companies (about 2,600 US stocks) with their sector ETF, from the IWV holdings
    file. Used only for the fallback mapping rate (43.9%), as in section 3b of the coverage audit."""
    us, list_date = parse_ishares_holdings(iwv_path or paths()['iwv_holdings'], dedup=False)
    us['sector_etf_us'] = us['gics_sector'].map(SECTOR_TO_ETF)
    us = us.dropna(subset=['sector_etf_us']).drop_duplicates('ticker').reset_index(drop=True)
    us['list_date'] = list_date
    return us


def load_calendar(path=None):
    """NYSE trading days with each day's close time (New York and UTC)."""
    cal = pd.read_csv(path or paths()['calendar'], index_col=0)
    cal.index = pd.to_datetime(cal.index)
    cal['close_utc'] = pd.to_datetime(cal['close_ny'], utc=True)
    return cal


def make_calendar(start='1998-01-01', end='2024-01-31'):
    """Build the NYSE calendar (needs: pip install pandas_market_calendars)."""
    import pandas_market_calendars as mcal
    s = mcal.get_calendar('NYSE').schedule(start_date=start, end_date=end)
    s.index = pd.to_datetime(s.index)
    cal = pd.DataFrame({'close_ny': s['market_close'].dt.tz_convert('America/New_York')}, index=s.index)
    cal['close_utc'] = cal['close_ny'].dt.tz_convert('UTC')
    return cal


# ETF prices (same steps as sections 3-7 of Tier_C_ETF_Extraction)

def download_prices(tickers, start='1998-01-01', end='2024-01-01'):
    """Daily adjusted close from Yahoo Finance (needs: pip install yfinance). Tickers are downloaded
    one after another, each failed ticker is retried once, and it stops if any ETF has no prices."""
    import yfinance as yf
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False, threads=False)
    prices = raw['Close'][tickers].sort_index()
    prices.index.name = 'date'
    for t in [t for t in tickers if prices[t].notna().sum() == 0]:
        print('Retrying', t)
        one = yf.download(t, start=start, end=end, auto_adjust=True, progress=False)
        prices[t] = one['Close'].squeeze()
    missing = [t for t in tickers if prices[t].notna().sum() == 0]
    assert not missing, f'No prices for {missing}: run again'
    return prices


def load_prices(path=None):
    """The saved daily prices (etf_prices.csv)."""
    return pd.read_csv(path or paths()['prices'], index_col='date', parse_dates=True)


def start_dates(prices, universe=ETF_UNIVERSE):
    """First and last price date and number of trading days per ETF."""
    table = pd.DataFrame({'first_date': prices.apply(lambda c: c.first_valid_index()),
                          'last_date': prices.apply(lambda c: c.last_valid_index()),
                          'trading_days': prices.notna().sum()})
    return universe.set_index('ticker')[['group', 'role']].join(table).sort_values('first_date')


def price_quality(prices):
    """Gaps inside each ETF's history (should be 0), lowest and highest price."""
    def gaps_inside(col):
        first, last = col.first_valid_index(), col.last_valid_index()
        return None if first is None else int(col.loc[first:last].isna().sum())
    return pd.DataFrame({'gaps_inside_history': prices.apply(gaps_inside),
                         'min_price': prices.min(), 'max_price': prices.max()})


def common_window(prices, tickers=UNIVERSE):
    """First and last date on which every ETF in `tickers` has a price (30 May 2007 to 29 Dec 2023)."""
    return (prices[tickers].apply(lambda c: c.first_valid_index()).max(),
            prices[tickers].apply(lambda c: c.last_valid_index()).min())


def log_returns(prices):
    """Daily log returns."""
    return np.log(prices / prices.shift(1)).dropna(how='all')


# 4. Mapping

def map_to_sector_etf(news, sp500):
    """Add ticker, company, gics_sector and sector_etf to every headline (empty if the ticker is not an S&P 500 company), and a 'mapped' flag for the 11 sector ETFs."""
    news = news.copy()
    news['ticker'] = normalise_ticker(news['Stock_symbol'])
    news = news.merge(sp500[['ticker', 'company', 'gics_sector', 'sector_etf']], on='ticker', how='left')
    news['mapped'] = news['sector_etf'].isin(SECTOR_ETFS)
    return news


def map_with_fallback(news, us):
    """Adds the fallback mapping (all US companies in the Russell 3000): S&P 500 companies keep their
    ETF, other US companies are added through their sector. Adds 'sector_etf_broad', 'mapped_broad'.
    `news` must already have gone through map_to_sector_etf."""
    news = news.merge(us[['ticker', 'sector_etf_us']], on='ticker', how='left')
    news['sector_etf_broad'] = news['sector_etf'].fillna(news['sector_etf_us'])
    news['mapped_broad'] = news['sector_etf_broad'].isin(SECTOR_ETFS)
    return news


def mapping_rate(news, column='mapped'):
    """Share of headlines (in %) that map to a sector ETF ('mapped_broad' for the fallback)."""
    return round(news[column].mean() * 100, 1)


# 5. Trading days

# Rule: before that day's close (16:00 New York, 13:00 on half-days) -> that day;
#       after the close, weekend or holiday -> next trading day;
#       no time of day (00:00:00 UTC) -> next trading day after the date (too ensure never use news too early).

def to_trading_day(published, cal):
    """One FNSPID time such as '2020-03-10 21:30:00 UTC' -> its trading day"""
    days = cal.index
    t = pd.Timestamp(published.replace(' UTC', ''), tz='UTC')
    if t.hour == 0 and t.minute == 0 and t.second == 0:
        return days[days > pd.Timestamp(t.date())][0]
    t_ny = t.tz_convert('America/New_York')
    day = pd.Timestamp(t_ny.date())
    if day in days and t < cal.loc[day, 'close_utc']:
        return day
    return days[days > day][0]


def trading_dates(published, cal):
    """Same rule as to_trading_day, for millions of rows at once. Returns NaT if no trading day."""
    ts = pd.to_datetime(pd.Series(published).str.replace(' UTC', '', regex=False),
                        format='%Y-%m-%d %H:%M:%S', errors='coerce', utc=True)
    utc = ts.dt.tz_convert(None)
    date_only = (utc.dt.hour == 0) & (utc.dt.minute == 0) & (utc.dt.second == 0)
    ny_day = ts.dt.tz_convert('America/New_York').dt.tz_localize(None).dt.normalize()
    ref_day = ny_day.where(~date_only, utc.dt.normalize()).to_numpy(dtype='datetime64[ns]')

    days = cal.index.to_numpy(dtype='datetime64[ns]')
    closes = cal['close_utc'].dt.tz_convert(None).to_numpy(dtype='datetime64[ns]')
    n = len(days)
    pos = np.searchsorted(days, ref_day, side='left')                   # first trading day >= ref_day
    pc = np.clip(pos, 0, n - 1)
    is_trading = (pos < n) & (days[pc] == ref_day)
    before_close = is_trading & ~date_only.to_numpy() & (utc.to_numpy(dtype='datetime64[ns]') < closes[pc])
    out = np.where(before_close, pos, np.where(is_trading, pos + 1, pos))
    ok = ts.notna().to_numpy() & (out < n) & (ref_day >= days[0])
    return pd.to_datetime(np.where(ok, days[np.clip(out, 0, n - 1)], np.datetime64('NaT', 'ns')))


# 6. Relevance

# Templates and lists found in the pilot (used for the coverage audit 'relevant' flag)
TEMPLATES = (r'\bBuys\b.*,|\bSells\b.*,|Movers|Sector Update|Lightning Round|Option Alert|Options? Activity|'
             r'Dividend Report|Ex-Dividend Date|Stocks? (You|To|That|Hitting)|\d+ (AI )?Stocks?\b|Markets Now|'
             r'Put And Call|Pre-?market|After-?Hours|Midday|Mid-Day|Biggest Movers|52-Week')
# Extra templates found in the pilot and the first gold draw (used for the gold pool and Tier C)
EXTRA_TEMPLATES = (r'Ex-Dividend|Analyst Blog Highlights|Presenters Include|to Replace .+ in S&P|featured highlights|'
                   r'Bulls & Bears|Insider Buying Report|Earnings Call (?:Transcript|Slides)|Earnings Conference Call|'
                   r'Conf\. Call|Options (?:Now Available|Begin Trading)|Halted News Pending|\b\d+ \w+ Stocks?\b|'
                   r'Guru Fundamental Report|Cramer Likes')
GENERIC = {'THE', 'FIRST', 'GENERAL', 'AMERICAN', 'UNITED', 'INTERNATIONAL', 'NATIONAL', 'PUBLIC', 'DIGITAL',
           'SOUTHERN', 'WESTERN', 'NORTHERN', 'CAPITAL', 'HEALTH', 'UNIVERSAL', 'GLOBAL', 'ROYAL', 'CHARLES', 'HOST'}


def simple(text):
    """Lower case, punctuation -> spaces, padded with spaces (for whole-word matching)."""
    return ' ' + re.sub(r'[^a-z0-9&]+', ' ', str(text).lower().replace('.com', '')).strip() + ' '


def name_key(company):
    """The word(s) a headline would use for a company, e.g. 'Apple Inc' -> 'apple',
    'General Motors' -> 'general motors', 'T-Mobile US' -> 't mobile'."""
    words = simple(company).split()
    if not words:
        return ''
    if (words[0].upper() in GENERIC or len(words[0]) < 3) and len(words) > 1:
        return words[0] + ' ' + words[1]
    return words[0]


def is_relevant(title, company, ticker):
    """True if the headline names the company it is tagged to (name or ticker) and is not a template or a multi-company list."""
    if re.search(TEMPLATES, title, flags=re.IGNORECASE):
        return False
    caps = re.findall(r'\b[A-Z]{1,5}\b', title)
    if title.count(',') >= 2 and len(caps) >= 3:                 
        return False
    key = name_key(company)
    names_company = bool(key) and f' {key} ' in simple(title)
    names_ticker = len(ticker) >= 2 and re.search(rf'\b{re.escape(ticker)}\b', title) is not None
    return names_company or names_ticker


def add_relevance(news):
    """Add the 'relevant' column (about one minute per million rows)."""
    news = news.copy()
    news['relevant'] = [is_relevant(t, c, k) for t, c, k in
                        zip(news['Article_title'], news['company'].fillna(''), news['ticker'])]
    return news


def keep_informative(news, min_words=4):
    """The headlines worth annotating or scoring: relevant, not an extra template, at least 4 words.
    Use the same function for the gold pool and for Tier C, so both follow the same rule."""
    keep = (news['relevant']
            & ~news['Article_title'].str.contains(EXTRA_TEMPLATES, case=False, regex=True)
            & (news['Article_title'].str.split().str.len() >= min_words))
    return news[keep]


# 7. Build

def build_mapped(news, sp500, cal, start=START, end=END):
    """Clean FNSPID -> mapped table: sector ETF, trading day, relevance flag, inside the backtest
    window. Same result as fnspid_mapped.parquet from the coverage audit."""
    news = map_to_sector_etf(news, sp500)
    news['trading_date'] = trading_dates(news['Date'], cal)
    news['in_window'] = news['trading_date'].between(start, end)
    m = add_relevance(news[news['in_window'] & news['mapped']])
    keep = ['Date', 'trading_date', 'Article_title', 'Stock_symbol', 'ticker', 'company', 'gics_sector',
            'sector_etf', 'relevant']
    return m[keep]


def own_ticker_news(news, cal, etfs=None, start=START, end=END):
    """Headlines tagged with an ETF's own ticker (e.g. 'GLD sees record inflows'), with their trading
    day, inside the backtest window. Default: all 21 ETFs (as in the coverage audit); for the news
    signal use etfs=OWN_NEWS_ETFS (GLD, AGG)."""
    etfs = list(ETF_UNIVERSE['ticker']) if etfs is None else etfs
    news = news.copy()
    news['ticker'] = normalise_ticker(news['Stock_symbol'])
    own = news[news['ticker'].isin(etfs)].copy()
    own['trading_date'] = trading_dates(own['Date'], cal)
    keep = ['Date', 'trading_date', 'Article_title', 'Stock_symbol', 'ticker']
    return own[own['trading_date'].between(start, end)][keep]


def etf_news_coverage(mapped, own, cal, universe=ETF_UNIVERSE, min_pct=MIN_PCT_DAYS, end=END):
    """For every ETF: own-ticker headlines, company headlines (sector ETFs only), headlines per day and
    share of trading days with news, for 2010-2023 and 2016-2023. 'signal_possible' applies the
    rule (news on at least 50% of days). Same table as coverage_all_etf_news.csv (audit section 6c)."""
    rows = []
    for period, a in {'2010-2023': pd.Timestamp('2010-01-01'), '2016-2023': pd.Timestamp('2016-01-01')}.items():
        days = cal.index[(cal.index >= a) & (cal.index <= end)]
        for e in universe.itertuples():
            own_days = own.loc[(own['ticker'] == e.ticker) & (own['trading_date'] >= a), 'trading_date']
            comp_days = mapped.loc[(mapped['sector_etf'] == e.ticker) & (mapped['trading_date'] >= a), 'trading_date']
            all_days = pd.concat([own_days, comp_days])
            rows.append({'period': period, 'etf': e.ticker, 'group': e.group, 'role': e.role,
                         'own_ticker_headlines': len(own_days), 'company_headlines': len(comp_days),
                         'headlines_per_day': round(len(all_days) / len(days), 2),
                         'pct_days_with_news': round(all_days.nunique() / len(days) * 100, 1)})
    table = pd.DataFrame(rows)
    table['signal_possible'] = table['pct_days_with_news'] >= min_pct
    return table


def news_signal_etfs(coverage, period='2016-2023'):
    """Universe ETFs that pass the rule: the 11 sector ETFs plus GLD and AGG."""
    t = coverage[(coverage['period'] == period) & (coverage['role'] == 'Universe')]
    return t.loc[t['signal_possible'], 'etf'].tolist()


def annotation_pool(mapped, years=(2010, 2023), exclude_titles=()):
    """Headlines that can be sampled for annotation: informative, in the years, not already used
    (e.g. the pilot), each title once."""
    pool = mapped.assign(year=mapped['trading_date'].dt.year)
    pool = pool[pool['year'].between(*years)]
    pool = keep_informative(pool)
    pool = pool[~pool['Article_title'].isin(set(exclude_titles))]
    return pool.drop_duplicates('Article_title').reset_index(drop=True)


# 8. Sampling

def stratified_sample(pool, total=200, seed=42, prefix='G'):
    """Step A: 1 headline from every sector-year cell. Step B: the rest at random within each
    sector, so the sectors get equal shares (the largest sectors get the remainder).
    IDs G001, G002, ... in shuffled order."""
    cells = pool.groupby(['sector_etf', 'year']).size().unstack(fill_value=0)
    assert (cells > 0).all().all(), 'A sector-year cell is empty'
    sectors = sorted(pool['sector_etf'].unique())

    step_a = pool.groupby(['sector_etf', 'year']).sample(1, random_state=seed)
    target = {etf: total // len(sectors) for etf in sectors}
    for etf in pool['sector_etf'].value_counts().index[:total - sum(target.values())]:
        target[etf] += 1
    rest = pool.drop(step_a.index)
    step_b = pd.concat([rest[rest['sector_etf'] == etf].sample(target[etf] - (step_a['sector_etf'] == etf).sum(),
                                                               random_state=seed) for etf in sectors])
    sample = pd.concat([step_a, step_b]).sample(frac=1, random_state=seed).reset_index(drop=True)
    sample['headline_id'] = [f'{prefix}{i:03d}' for i in range(1, len(sample) + 1)]
    assert len(sample) == total and sample['Article_title'].is_unique
    return sample


def pilot_pool(news, sp500):
    """The pool the 44-headline pilot was drawn from (TierB_Pilot_Sample, Oct 2026). Kept so the pilot
    can be reproduced. Two small differences from build_mapped, both from the first version of the
    code: the window uses the calendar year of the UTC date (2007-2023) instead of the trading day,
    and tickers only turn '-' into '.'. This gives 1,321,949 mapped headlines instead of 1,321,935."""
    news = news.copy()
    news['ticker'] = news['Stock_symbol'].str.upper().str.replace('-', '.', regex=False).replace(TICKER_RENAMES)
    news['year'] = news['Date'].str[:4].astype(int)
    news = news.merge(sp500[['ticker', 'company', 'gics_sector', 'sector_etf']], on='ticker', how='left')
    pool = news[news['sector_etf'].notna() & news['year'].between(2007, 2023)].copy()
    pool['relevant'] = [is_relevant(t, c, k) for t, c, k in zip(pool['Article_title'], pool['company'], pool['ticker'])]
    return pool


def sector_sample(pool, per_sector=4, seed=42, prefix='P', min_words=4):
    """`per_sector` random headlines from each sector ETF, shuffled, IDs P001, ... (the pilot rule:
    relevant headlines with at least 4 words)."""
    pool = pool[pool['relevant']]
    pool = pool[pool['Article_title'].str.split().str.len() >= min_words]
    sample = (pool.groupby('sector_etf').sample(per_sector, random_state=seed)
                  .sample(frac=1, random_state=seed).reset_index(drop=True))
    sample['headline_id'] = [f'{prefix}{i:03d}' for i in range(1, len(sample) + 1)]
    return sample


def shared_subset(sample, size=100, seed=42):
    """Headline IDs annotated by both annotators, spread over sectors in proportion."""
    from sklearn.model_selection import train_test_split
    shared, _ = train_test_split(sample, train_size=size, stratify=sample['sector_etf'], random_state=seed)
    return set(shared['headline_id'])


def blank_annotation_file(sample):
    """The annotation template: headline_id, sentence, entity, aspect, sentiment."""
    return pd.DataFrame({'headline_id': sample['headline_id'], 'sentence': sample['Article_title'],
                         'entity': '', 'aspect': '', 'sentiment': ''})


# 9. Aggregation (sector-level, the planned fallback for a mapping rate below 60%)

def daily_by_etf(df, days, value=None, how='mean', etf_col='sector_etf'):
    """One row per trading day, one column per ETF.
    value=None -> number of headlines per day (0 on days with no news).
    value='score' -> the daily mean (or sum) of that column, empty on days with no news.
    In Semester 2 the same function turns headline sentiment into a daily news signal."""
    if value is None:
        out = df.groupby(['trading_date', etf_col]).size().unstack(fill_value=0)
        return out.reindex(days, fill_value=0)
    out = df.groupby(['trading_date', etf_col])[value].agg(how).unstack()
    return out.reindex(days)


def coverage_table(df, days, etf_col='sector_etf'):
    """Per ETF: median headlines per day and share of days with news (as in the coverage audit)."""
    counts = daily_by_etf(df, days, etf_col=etf_col)
    return pd.DataFrame({'median_per_day': counts.median(),
                         'pct_days_with_news': ((counts > 0).mean() * 100).round(1)})


# 10. Self-tests

TRADING_DAY_CASES = [
    ('During trading hours', '2020-03-10 15:00:00 UTC', '2020-03-10'),
    ('After the 16:00 close', '2020-03-10 21:30:00 UTC', '2020-03-11'),
    ('Friday night -> Monday', '2021-01-08 22:00:00 UTC', '2021-01-11'),
    ('Holiday (Christmas)', '2019-12-25 15:00:00 UTC', '2019-12-26'),
    ('Half-day, closed 13:00', '2019-11-29 19:00:00 UTC', '2019-12-02'),
    ('No time of day recorded', '2020-05-22 00:00:00 UTC', '2020-05-26'),
]


def run_self_tests(cal):
    """Checks every rule on small hand-made examples. Returns a table; stops if any check fails."""
    rows = []

    def check(area, case, got, expected):
        rows.append({'area': area, 'case': case, 'got': str(got), 'expected': str(expected),
                     'pass': got == expected})

    # Trading days: the six cases from the ETF notebook, one by one and all at once
    vec = trading_dates([p for _, p, _ in TRADING_DAY_CASES], cal).strftime('%Y-%m-%d').tolist()
    for (case, published, expected), v in zip(TRADING_DAY_CASES, vec):
        check('trading day', case, to_trading_day(published, cal).strftime('%Y-%m-%d'), expected)
        check('trading day (vectorised)', case, v, expected)

    # Tickers: FNSPID side and iShares side
    for raw, expected in [('FB', 'META'), ('BRK', 'BRK.B'), ('BRK-B', 'BRK.B'), ('BRK B', 'BRK.B'),
                          ('bf-b', 'BF.B'), ('aapl', 'AAPL')]:
        check('ticker (FNSPID)', raw, normalise_ticker(pd.Series([raw]))[0], expected)
    for raw, expected in [('BRKB', 'BRK.B'), ('BFB', 'BF.B'), ('BRK B', 'BRK.B'), (' AAPL ', 'AAPL')]:
        check('ticker (iShares)', raw, holdings_ticker(pd.Series([raw]))[0], expected)

    # Relevance (title, company, ticker, expected)
    for title, company, ticker, expected in [
        ('Microsoft beats Q2 revenue estimates', 'MICROSOFT CORP', 'MSFT', True),
        ('T-Mobile adds 1 million subscribers', 'T MOBILE US INC', 'TMUS', True),
        ('Interesting AAL Put And Call Options For August', 'AMERICAN AIRLINES GROUP INC', 'AAL', False),
        ('HDV, DUK, D, UPS: Large Outflows Detected at ETF', 'DUKE ENERGY CORP', 'DUK', False),
        ('10 Stocks To Watch This Week', 'APPLE INC', 'AAPL', False),
        ('Fed holds rates steady', 'APPLE INC', 'AAPL', False),
    ]:
        check('relevance', title, is_relevant(title, company, ticker), expected)

    # Extra templates (True = removed)
    for title, expected in [('Evergy Q2 23 Earnings Conference Call At 9:00 AM ET', True),
                            ('DHR April 14th Options Begin Trading', True),
                            ('Zacks.com featured highlights Archer Daniels Midland, Conagra Brands', True),
                            ('Tesla Stock Falls After Recall', False),
                            ('Delta Air Lines Updates Q3 Guidance', False)]:
        check('extra template', title, bool(re.search(EXTRA_TEMPLATES, title, flags=re.IGNORECASE)), expected)

    table = pd.DataFrame(rows)
    failed = table[~table['pass']]
    assert failed.empty, 'Self-test failed:\n' + failed.to_string()
    return table
