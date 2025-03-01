#data/rss_fetcher.py

import feedparser

def fetch_rss_feed(url="https://www.bankofcanada.ca/feed/"):
    """
    Fetch and return the latest RSS feed articles from the specified URL.
    
    Parameters:
        url (str): The URL of the RSS feed.
        
    Returns:
        list: A list of dictionaries, each containing the title and link of an article.
    """
    feed = feedparser.parse(url)
    articles = [{"title": entry.title, "link": entry.link} for entry in feed.entries[:5]]
    return articles

if __name__ == "__main__":
    news = fetch_rss_feed()
    for article in news:
        print(f"{article['title']} - {article['link']}")
