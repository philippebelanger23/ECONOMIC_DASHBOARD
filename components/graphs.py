# components/graphs.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from components.rss_news import rss_news
from data.mappings import INDICATOR_GROUPS

content = dbc.Container(
    [
        dcc.Tabs(
            id="dashboard-tabs",
            value="tab-graphs",  # Default active tab
            children=[
                dcc.Tab(
                    label="Economic Graphs",
                    value="tab-graphs",
                    children=[
                        dbc.Row(
                            id="graph-container",
                            style={"margin-top": "10px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="News Feed",
                    value="tab-news",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(rss_news, width=12),
                            ],
                            style={"margin-top": "10px"},
                        )
                    ],
                ),
                dcc.Tab(
                    label="Summary Stats",
                    value="tab-summary",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(id="summary-stats-container"),
                                    width=12,
                                ),
                            ],
                            style={"margin-top": "10px"},
                        )
                    ],
                ),
            ],
            style={"margin-top": "10px"},
        )
    ],
    fluid=True,
)