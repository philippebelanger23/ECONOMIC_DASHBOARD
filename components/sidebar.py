# components/sidebar.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from data.mappings import INDICATOR_GROUPS
from components.rss_news import rss_news
from datetime import datetime

# Define configurable margins (in pixels)
MARGIN_TITLE_TO_LAST_UPDATED = "10px"
MARGIN_LAST_UPDATED_TO_FILTERS = "20px"
MARGIN_FILTERS_TO_SUMMARY = "20px"
MARGIN_INSIDE_FILTERS_DROPDOWN_TO_CHECKLISTS = "10px"
MARGIN_INSIDE_FILTERS_CHECKLISTS_TO_RSS = "10px"

group_options = [
    {"label": key.capitalize(), "value": key} for key in INDICATOR_GROUPS.keys()
]

# Dynamically set the max date to today
today = datetime.today()
today_str = today.strftime("%Y-%m-%d")  # e.g., '2025-03-01'

# Calculate months for the RangeSlider
start_date = datetime(1990, 1, 1)  # Starting point: January 1990
min_month = 0  # January 1990 is month 0
# Total months from January 1990 to today
max_month = (today.year - start_date.year) * 12 + today.month - 1
default_start_month = (2006 - 1990) * 12  # January 2006 in months since 1990
default_end_month = max_month  # Current month

# Create marks for every 5 years (every 60 months)
marks = {}
for year in range(1990, today.year + 1, 5):
    month_value = (year - 1990) * 12  # January of the year in months since 1990
    if month_value <= max_month:  # Ensure mark doesn't exceed max_month
        marks[month_value] = str(year)

def create_economics_sidebar():
    return [
        html.H1(
            "Economic Indicators Dashboard",
            className="text-center",
            style={"margin-bottom": MARGIN_TITLE_TO_LAST_UPDATED},
        ),
        html.P(
            id="last-updated",
            className="text-center text-muted",
            style={"margin-bottom": MARGIN_LAST_UPDATED_TO_FILTERS},
        ),
        dbc.Card(
            [
                html.H3("Filters", className="text-center"),
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed="1970-01-01",
                    max_date_allowed=today_str,
                    start_date="2020-01-01",
                    end_date=today_str,
                    display_format="YYYY-MM-DD",
                    style={"width": "100%", "textAlign": "center"},
                ),
                html.Label("Zoom Date Range", style={"margin-top": "10px"}),
                dcc.RangeSlider(
                    id="date-range-slider",
                    min=min_month,
                    max=max_month,
                    step=1,
                    value=[default_start_month, default_end_month],
                    marks=marks,
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                dbc.ButtonGroup(
                    [
                        dbc.Button("Last 3mo", id="btn-last-3mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                        dbc.Button("Last 6mo", id="btn-last-6mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                        dbc.Button("Last 12mo", id="btn-last-12mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                        dbc.Button("Last 24mo", id="btn-last-24mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                    ],
                    className="d-flex justify-content-center",
                    style={"margin-top": "10px"},
                ),
                html.Label("Select Indicator Group", style={"margin-top": "10px"}),
                dcc.Dropdown(
                    id="indicator-group-selector",
                    options=group_options,
                    value="Macroeconomic Indicators",
                    clearable=False,
                    style={"width": "100%", "margin-bottom": MARGIN_INSIDE_FILTERS_DROPDOWN_TO_CHECKLISTS},
                ),
                dbc.CardGroup(
                    [
                        dbc.Checklist(
                            options=[{"label": "Show Recession Bars", "value": True}],
                            value=[True],
                            id="toggle-recessions",
                            switch=True,
                        )
                    ],
                    className="",
                ),
                dbc.CardGroup(
                    [
                        dbc.Checklist(
                            options=[{"label": "Show Key Events", "value": True}],
                            value=[],
                            id="toggle-events",
                            switch=True,
                        )
                    ],
                    className="",
                    style={"margin-bottom": MARGIN_INSIDE_FILTERS_CHECKLISTS_TO_RSS},
                ),
            ],
            body=True,
            style={"width": "100%", "padding": "5px"},
        ),
        dbc.Card(
            [
                dbc.CardHeader("Summary Statistics"),
                dbc.CardBody(
                    id="summary-stats",
                    style={"padding": "10px", "overflowX": "auto", "overflowY": "auto"}
                ),
            ],
            style={"margin-top": MARGIN_FILTERS_TO_SUMMARY},
        ),
    ]

def create_correlations_sidebar():
    return [
        html.H1(
            "Correlations Analysis",
            className="text-center",
            style={"margin-bottom": MARGIN_TITLE_TO_LAST_UPDATED},
        ),
        dbc.Card(
            [
                html.H3("Correlation Settings", className="text-center"),
                html.Label("Select Base Indicator", style={"margin-top": "10px"}),
                dcc.Dropdown(
                    id="correlation-base-indicator",
                    options=group_options,
                    placeholder="Select indicator to correlate against",
                    style={"width": "100%", "margin-bottom": "10px"},
                ),
                html.Label("Correlation Period", style={"margin-top": "10px"}),
                dcc.Dropdown(
                    id="correlation-period",
                    options=[
                        {"label": "1 Year", "value": "1Y"},
                        {"label": "3 Years", "value": "3Y"},
                        {"label": "5 Years", "value": "5Y"},
                        {"label": "10 Years", "value": "10Y"},
                        {"label": "All Time", "value": "ALL"},
                    ],
                    value="3Y",
                    style={"width": "100%"},
                ),
            ],
            body=True,
            style={"width": "100%", "padding": "5px"},
        ),
    ]

def create_funds_flow_sidebar():
    return [
        html.H1(
            "Funds Flow Analysis",
            className="text-center",
            style={"margin-bottom": MARGIN_TITLE_TO_LAST_UPDATED},
        ),
        dbc.Card(
            [
                html.H3("Analysis Settings", className="text-center"),
                html.Label("Date Range", style={"margin-top": "10px"}),
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed="1970-01-01",
                    max_date_allowed=today_str,
                    start_date="2020-01-01",
                    end_date=today_str,
                    display_format="YYYY-MM-DD",
                    style={"width": "100%", "textAlign": "center"},
                ),
                html.Label("Zoom Date Range", style={"margin-top": "10px"}),
                dcc.RangeSlider(
                    id="date-range-slider",
                    min=min_month,
                    max=max_month,
                    step=1,
                    value=[default_start_month, default_end_month],
                    marks=marks,
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                dbc.ButtonGroup(
                    [
                        dbc.Button("Last 3mo", id="btn-last-3mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                        dbc.Button("Last 6mo", id="btn-last-6mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                        dbc.Button("Last 12mo", id="btn-last-12mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                        dbc.Button("Last 24mo", id="btn-last-24mo", n_clicks=0, color="primary", outline=True, size="sm", className="me-1"),
                    ],
                    className="d-flex justify-content-center",
                    style={"margin-top": "10px"},
                ),
                html.Hr(style={"margin": "15px 0"}),
                html.Label("Visualization Type", style={"margin-top": "10px"}),
                dcc.RadioItems(
                    id="visualization-type",
                    options=[
                        {"label": "Sector Rotation", "value": "sector_rotation"},
                        {"label": "Relative Analysis", "value": "relative_analysis"},
                    ],
                    value="sector_rotation",
                    style={"margin-top": "5px"},
                ),
                html.Hr(style={"margin": "15px 0"}),
                html.Label("Select Flow Type", style={"margin-top": "10px"}),
                dcc.Dropdown(
                    id="flow-type-selector",
                    options=[
                        {"label": "Equity Flows", "value": "equity"},
                        {"label": "Bond Flows", "value": "bond"},
                        {"label": "Money Market Flows", "value": "money_market"},
                        {"label": "Commodity Flows", "value": "commodity"},
                    ],
                    value="equity",
                    style={"width": "100%"},
                ),
                html.Label("Flow Period", style={"margin-top": "10px"}),
                dcc.RadioItems(
                    id="flow-period",
                    options=[
                        {"label": "Daily", "value": "D"},
                        {"label": "Weekly", "value": "W"},
                        {"label": "Monthly", "value": "M"},
                    ],
                    value="W",
                    style={"margin-top": "5px"},
                ),
            ],
            body=True,
            style={"width": "100%", "padding": "5px"},
        ),
    ]

def create_news_sidebar():
    return [
        html.H1(
            "News Feed Settings",
            className="text-center",
            style={"margin-bottom": MARGIN_TITLE_TO_LAST_UPDATED},
        ),
        dbc.Card(
            [
                html.H3("Feed Settings", className="text-center"),
                html.Label("Articles per Feed", style={"margin-top": "10px"}),
                dcc.Slider(
                    id="articles-per-feed",
                    min=3,
                    max=10,
                    step=1,
                    value=5,
                    marks={i: str(i) for i in range(3, 11)},
                ),
                html.Label("Auto Refresh Interval", style={"margin-top": "20px"}),
                dcc.Dropdown(
                    id="refresh-interval",
                    options=[
                        {"label": "1 minute", "value": 60},
                        {"label": "5 minutes", "value": 300},
                        {"label": "15 minutes", "value": 900},
                        {"label": "30 minutes", "value": 1800},
                        {"label": "Manual only", "value": 0},
                    ],
                    value=900,
                    style={"width": "100%"},
                ),
            ],
            body=True,
            style={"width": "100%", "padding": "5px"},
        ),
    ]

# Main sidebar container that will be updated based on the selected tab
sidebar = html.Div(id="sidebar-content")