# data/rss_fetcher.py

import feedparser


def fetch_rss_feed(url="https://www.bankofcanada.ca/feed/"):
 
    feed = feedparser.parse(url)
    articles = [
        {"title": entry.title, "link": entry.link} for entry in feed.entries[:5]
    ]
    return articles


if __name__ == "__main__":
    news = fetch_rss_feed()
    for article in news:
        print(f"{article['title']} - {article['link']}")
