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
# Total months from January 1990 to today (e.g., March 2025)
max_month = (
    (today.year - start_date.year) * 12 + today.month - 1
)  # -1 because months are 0-based
default_start_month = (2006 - 1990) * 12  # January 2006 in months since 1990
default_end_month = max_month  # Current month

# Create marks for every 5 years (every 60 months)
marks = {}
for year in range(1990, today.year + 1, 5):
    month_value = (year - 1990) * 12  # January of the year in months since 1990
    if month_value <= max_month:  # Ensure mark doesn’t exceed max_month
        marks[month_value] = str(year)

sidebar = html.Div(
    [
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
                    max_date_allowed=today_str,  # Set to today's date (e.g., '2025-03-01')
                    start_date="2006-01-01",
                    end_date=today_str,  # Set default end date to today
                    display_format="YYYY-MM-DD",
                    style={"width": "100%", "textAlign": "center"},
                ),
                html.Label("Zoom Date Range", style={"margin-top": "10px"}),
                dcc.RangeSlider(
                    id="date-range-slider",
                    min=min_month,
                    max=max_month,  # Max is the current month (e.g., March 2025 = 420 months since Jan 1990)
                    step=1,  # Step by month
                    value=[
                        default_start_month,
                        default_end_month,
                    ],  # Default range from Jan 2006 to today
                    marks=marks,  # Marks every 5 years (e.g., 1990, 1995, ..., 2025)
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                html.Label("Select Indicator Group", style={"margin-top": "10px"}),
                dcc.Dropdown(
                    id="indicator-group-selector",
                    options=group_options,
                    value="Macroeconomic Indicators",
                    clearable=False,
                    style={
                        "width": "100%",
                        "margin-bottom": MARGIN_INSIDE_FILTERS_DROPDOWN_TO_CHECKLISTS,
                    },
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
                rss_news,
            ],
            body=True,
            style={"width": "100%", "padding": "5px"},
        ),
        dbc.Card(
            [dbc.CardHeader("Summary Statistics"), dbc.CardBody(id="summary-stats")],
            style={"margin-top": MARGIN_FILTERS_TO_SUMMARY},
        ),
    ]
)
