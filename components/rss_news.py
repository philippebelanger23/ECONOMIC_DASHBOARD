# components/rss_news.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from data.data_fetcher import fetch_rss_feed
from config.settings import RSS_FEED_URLS

# Configurable margins
MARGIN_DROPDOWN_TO_LIST = "10px"
MARGIN_BETWEEN_ARTICLES = "10px"

# Define the RSS card structure
rss_news = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="rss-feed-selector",
                            options=[
                                {"label": k.capitalize(), "value": k}
                                for k in RSS_FEED_URLS.keys()
                            ],
                            value="NY TIMES",
                            clearable=False,
                        ),
                        width=9,
                    ),
                    dbc.Col(
                        html.Button(
                            "Refresh",
                            id="refresh-rss-button",
                            className="btn btn-primary btn-sm",
                            style={"height": "100%", "width": "100%"},
                        ),
                        width=3,
                    ),
                ],
                align="center",
            ),
            style={"padding": "5px"},
        ),
        dbc.CardBody(
            html.Ul(
                id="rss-news-list",
                style={"padding": "0", "margin": "0", "list-style-type": "none"},
            ),
            style={"padding": "10px", "margin-top": MARGIN_DROPDOWN_TO_LIST},
        ),
    ],
    style={"padding": "0"},
)
