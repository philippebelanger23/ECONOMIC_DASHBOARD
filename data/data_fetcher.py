# data/data_fetcher.py
import pandas as pd
from fredapi import Fred
from tenacity import retry, stop_after_attempt, wait_fixed
import feedparser
from config.settings import FRED_API_KEY, BASE_DIR, RSS_FEED_URLS, NUM_ARTICLES  # Added NUM_ARTICLES
from datetime import datetime
import json

fred = Fred(api_key=FRED_API_KEY)
CACHE_FILE = BASE_DIR / "data" / "fred_cache.pkl"
RELEASE_DATES_CACHE = BASE_DIR / "data" / "release_dates_cache.json"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_series(series):
    return fred.get_series(series)

def fetch_fred_data(force_refresh=False):
    if CACHE_FILE.exists() and not force_refresh:
        return pd.read_pickle(CACHE_FILE)
    from data.mappings import INDICATORS
    data = {}
    for key, info in INDICATORS.items():
        try:
            print(f"Fetching data for {key} ({info['id']})...")
            data[key] = fetch_series(info["id"])
        except Exception as e:
            print(f"❌ Error fetching {key}: {e}")
    
    df = pd.DataFrame(data)
    df.index = pd.to_datetime(df.index)
    
    if not df.empty:
        date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        df = df.reindex(date_range)
    
    df.to_pickle(CACHE_FILE)
    return df

def fetch_rss_feed(url):
    """
    Fetch and return the latest RSS feed articles from the specified URL.
    
    Parameters:
        url (str): The URL of the RSS feed.
        
    Returns:
        list: A list of dictionaries, each containing the title, link, publication date, and summary.
        Returns an empty list if the fetch fails.
    """
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            print(f"❌ Error parsing RSS feed from {url}: {feed.bozo_exception}")
            return []
        
        articles = []
        for entry in feed.entries[:NUM_ARTICLES]:
            pub_date = entry.get('published', '') or entry.get('updated', 'Unknown')
            if pub_date and pub_date != 'Unknown':
                try:
                    pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    pub_date = 'Unknown'
            
            summary = entry.get('summary', '')
            
            articles.append({
                "title": entry.get('title', 'No Title'),
                "link": entry.get('link', '#'),
                "pub_date": pub_date,
                "summary": summary[:200] + "..." if summary and len(summary) > 200 else summary
            })
        return articles
    
    except Exception as e:
        print(f"❌ Error fetching RSS feed from {url}: {e}")
        return []

def fetch_next_release_date(series_id):
    try:
        release_info = fred.get_series_release(series_id)
        release_id = release_info['id']
        today = datetime.today().strftime('%Y-%m-%d')
        future_dates = fred.get_release_dates(
            release_id=release_id,
            include_release_dates_with_no_data=False,
            realtime_start=today,
            limit=1,
            sort_order='asc'
        )
        if future_dates and len(future_dates) > 0:
            next_date = future_dates[0]['date']
            return next_date
        past_dates = fred.get_release_dates(
            release_id=release_id,
            include_release_dates_with_no_data=False,
            realtime_end=today,
            limit=1,
            sort_order='desc'
        )
        if past_dates and len(past_dates) > 0:
            last_date = past_dates[0]['date']
            return f"Last Release: {last_date} (Next TBD)"
        return "Unknown"
    except Exception as e:
        print(f"❌ Error fetching release date for {series_id}: {e}")
        return "Unknown"

def get_all_next_release_dates(force_refresh=False):
    if RELEASE_DATES_CACHE.exists() and not force_refresh:
        with open(RELEASE_DATES_CACHE, 'r') as f:
            return json.load(f)
    
    from data.mappings import INDICATORS
    release_dates = {}
    for key, info in INDICATORS.items():
        series_id = info["id"]
        print(f"Fetching next release date for {key} ({series_id})...")
        next_date = fetch_next_release_date(series_id)
        release_dates[series_id] = next_date
    
    with open(RELEASE_DATES_CACHE, 'w') as f:
        json.dump(release_dates, f)
    
    return release_dates

if __name__ == "__main__":
    df = fetch_fred_data()
    print("✅ Data fetched. Available columns:", df.columns)
    print("Data available from:", df.index.min(), "to", df.index.max())