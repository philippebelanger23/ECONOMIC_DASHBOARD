# components/sidebar.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from data.mappings import INDICATOR_GROUPS
from components.rss_news import rss_news

# Define configurable margins (in pixels)
MARGIN_TITLE_TO_LAST_UPDATED = "10px"  # Space between title and "Last Updated"
MARGIN_LAST_UPDATED_TO_FILTERS = "20px"  # Space between "Last Updated" and "Filters" card
MARGIN_FILTERS_TO_SUMMARY = "20px"  # Space between "Filters" card and "Summary Statistics" card
MARGIN_INSIDE_FILTERS_DROPDOWN_TO_CHECKLISTS = "20px"  # Space between dropdown and checklists in "Filters"
MARGIN_INSIDE_FILTERS_CHECKLISTS_TO_RSS = "10px"  # Space between checklists and RSS news in "Filters"
MARGIN_RSS_TO_SUMMARY = "20px"  # Space between RSS news and "Summary Statistics" card

group_options = [{"label": key.capitalize(), "value": key} for key in INDICATOR_GROUPS.keys()]

sidebar = html.Div([
    html.H1(
        "Economic Indicators Dashboard",
        className="text-center",
        style={"margin-bottom": MARGIN_TITLE_TO_LAST_UPDATED}
    ),
    html.P(
        id="last-updated",
        className="text-center text-muted",
        style={"margin-bottom": MARGIN_LAST_UPDATED_TO_FILTERS}
    ),
    
    dbc.Card([
        dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed="2000-01-01",
            max_date_allowed="2025-12-31",
            start_date="2006-01-01",
            end_date="2025-12-31",
            display_format='YYYY-MM-DD',
            style={"width": "100%", "textAlign": "center"}
        ),
        html.Label("Zoom Date Range", style={"margin-top": "10px"}),
        dcc.RangeSlider(
            id='date-range-slider',
            min=1990,
            max=2025,
            step=1,
            value=[2006, 2025],
            marks={year: str(year) for year in range(1990, 2026, 5)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Label("Select Indicator Group", style={"margin-top": "10px"}),
        dcc.Dropdown(
            id='indicator-group-selector',
            options=group_options,
            value='macro',
            clearable=False,
            style={"width": "100%", "margin-bottom": MARGIN_INSIDE_FILTERS_DROPDOWN_TO_CHECKLISTS}
        ),
        dbc.CardGroup([
            dbc.Checklist(
                options=[{"label": "Show Recession Bars", "value": True}],
                value=[True],
                id="toggle-recessions",
                switch=True,
            )
        ], className=""),  # Removed mt-3, spacing controlled by margins
        dbc.CardGroup([
            dbc.Checklist(
                options=[{"label": "Show Key Events", "value": True}],
                value=[],
                id="toggle-events",
                switch=True,
            )
        ], className="", style={"margin-bottom": MARGIN_INSIDE_FILTERS_CHECKLISTS_TO_RSS}),  # Removed mt-3, added margin
     
    ], body=True, style={"width": "100%", "padding": "5px"}),
    
    dbc.Card([
        dbc.CardHeader("RSS NEWS"),
        dbc.CardBody(rss_news)
    ], style={"margin-top": MARGIN_RSS_TO_SUMMARY}),

    dbc.Card([
        dbc.CardHeader("Summary Statistics"),
        dbc.CardBody(id="summary-stats")
    ], style={"margin-top": MARGIN_FILTERS_TO_SUMMARY})
])