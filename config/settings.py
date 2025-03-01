# config/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRED_API_KEY = os.getenv("FRED_API_KEY", "a734c74dab0f321bd97ed766dc2c8e4f")
RECESSIONS_FILE = BASE_DIR / "data" / "recessions.json"
RSS_FEED_URLS = {
    "NY TIMES": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    "eia": "https://www.eia.gov/rss/todayinenergy.xml"
}
NUM_ARTICLES = 3  # Number of RSS articles to display