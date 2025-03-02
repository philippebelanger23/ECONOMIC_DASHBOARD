# app/callbacks.py
# Standard library imports
import json
import math
from datetime import datetime

# Third-party imports
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, ALL, MATCH, State

# Local imports
from config.settings import RECESSIONS_FILE, RSS_FEED_URLS
from data.data_fetcher import fetch_rss_feed, get_all_next_release_dates
from data.data_processing import get_economic_data
from data.mappings import INDICATORS, INDICATOR_GROUPS


# -------------------
# Global Data Loading
# -------------------
economic_data = get_economic_data()

with open(RECESSIONS_FILE, "r") as f:
    recessions = json.load(f)

with open("data/events.json", "r") as f:
    key_events = json.load(f)

next_release_dates = get_all_next_release_dates()


# -------------------
# Helper Functions
# -------------------
def months_to_date(months):
    """Convert a number of months since January 1990 to a pandas Timestamp.

    Args:
        months (int): Number of months since January 1990 (e.g., 192 for January 2006).

    Returns:
        pandas.Timestamp: The corresponding date (e.g., '2006-01-01').
    """
    start_date = pd.to_datetime("1990-01-01")
    year = 1990 + (months // 12)
    month = (months % 12) + 1  # 0-based months, so +1 to get 1-12
    date = pd.to_datetime(f"{year}-{month:02d}-01")
    return date


def colname(ind, trans, for_display=False):
    """Generate a column name for an indicator with the specified transformation.

    Args:
        ind (str): Indicator key (e.g., 'GDP').
        trans (str): Transformation type ('raw', 'mom', 'qoq', 'yoy').
        for_display (bool): If True, use the indicator's description; otherwise, use the key.

    Returns:
        str: The column name (e.g., 'Gross Domestic Product MoM (%)').
    """
    base = INDICATORS.get(ind, {}).get("description", ind) if for_display else ind
    if trans == "raw":
        return base
    elif trans == "mom":
        return f"{base} MoM (%)"
    elif trans == "qoq":
        return f"{base} QoQ (%)"
    else:  # yoy
        return f"{base} YoY (%)"


def create_graph(data, col, graph_type):
    """Create a Plotly graph for the given data column and graph type.

    Args:
        data (pandas.DataFrame): DataFrame containing the data.
        col (str): Column name to plot.
        graph_type (str): Type of graph ('line', 'bar', 'area').

    Returns:
        plotly.graph_objs.Figure: The generated Plotly figure.
    """
    display_col = colname(
        col.split()[0] if "YoY" in col else col,
        "yoy" if "YoY" in col else "raw",
        for_display=True,
    )
    if graph_type == "line":
        fig = px.line(data, x=data.index, y=col, title=f"{display_col} Over Time")
    elif graph_type == "bar":
        fig = px.bar(data, x=data.index, y=col, title=f"{display_col} Over Time")
    else:  # area
        fig = px.area(data, x=data.index, y=col, title=f"{display_col} Over Time")

    fig.update_traces(
        hovertemplate="<b>%{y:.2f}</b><br>Date: %{x|%Y-%m-%d}<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def add_annotations(fig, indicator, show_recessions, show_events, start_dt, end_dt):
    """Add annotations, recession bars, and key events to a Plotly figure.

    Args:
        fig (plotly.graph_objs.Figure): The Plotly figure to annotate.
        indicator (str): The indicator key (e.g., 'GDP').
        show_recessions (list): List of booleans indicating whether to show recession bars.
        show_events (list): List of booleans indicating whether to show key events.
        start_dt (pandas.Timestamp): Start date of the data range.
        end_dt (pandas.Timestamp): End date of the data range.

    Returns:
        plotly.graph_objs.Figure: The annotated Plotly figure.
    """
    series_id = INDICATORS.get(indicator, {}).get("id", None)
    next_release = (
        next_release_dates.get(series_id, "Unknown") if series_id else "Unknown"
    )

    fig.add_annotation(
        text=f"Next Release: {next_release}",
        xref="paper",
        yref="paper",
        x=1,
        y=-0.1,
        showarrow=False,
        font={"size": 10, "color": "gray"},
    )
    fig.update_layout(margin={"b": 80})

    if show_recessions:
        for rec in recessions:
            peak, trough = rec.get("peak", ""), rec.get("trough", "")
            if peak and trough:
                rs, re = pd.to_datetime(peak), pd.to_datetime(trough)
                if re >= start_dt and rs <= end_dt:
                    fig.add_vrect(
                        x0=max(rs, start_dt),
                        x1=min(re, end_dt),
                        fillcolor="grey",
                        opacity=0.2,
                        layer="below",
                        line_width=0,
                    )
    if show_events:
        for event in key_events:
            event_date = pd.to_datetime(event["date"])
            if start_dt <= event_date <= end_dt:
                event_date_ms = int(event_date.timestamp() * 1000)
                fig.add_vline(
                    x=event_date_ms,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=event["event"],
                    annotation_position="top",
                    annotation={"font_size": 10, "font_color": "red"},
                )
    return fig


# -------------------
# Callbacks
# -------------------
def register_callbacks(app):
    # Graph Layout Callback
    @app.callback(
        Output("graph-container", "children"),
        Input("indicator-group-selector", "value"),
    )
    def update_graph_layout(group):
        """Update the layout of graphs based on the selected indicator group.

        Args:
            group (str): The selected indicator group (e.g., 'macro').

        Returns:
            list: A list of dash components representing the graph layout.
        """
        num_graphs = len(INDICATOR_GROUPS.get(group, []))
        if num_graphs == 0:
            return [html.Div("No indicators available for this group.")]

        if num_graphs % 2 == 0:
            graphs_per_row = num_graphs // 2
            first_row_count = graphs_per_row
            second_row_count = graphs_per_row
        else:
            first_row_count = math.ceil(num_graphs / 2)
            second_row_count = num_graphs - first_row_count

        num_rows = 1 if num_graphs <= first_row_count else 2
        first_row_width = 12 // first_row_count if first_row_count > 0 else 12
        second_row_width = 12 // second_row_count if second_row_count > 0 else 12

        available_height = 76
        graph_height = available_height / num_rows

        graph_cards = []
        for i in range(1, num_graphs + 1):
            default_indicator = (
                INDICATOR_GROUPS[group][i - 1]
                if i <= len(INDICATOR_GROUPS[group])
                else INDICATOR_GROUPS[group][0]
            )
            card = dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(
                                        id={"type": "indicator-selector", "index": i},
                                        value=default_indicator,
                                        clearable=False,
                                        style={"width": "100%"},
                                    ),
                                    width=6,
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id={"type": "transform-selector", "index": i},
                                        options=[
                                            {"label": "Raw", "value": "raw"},
                                            {"label": "MoM %", "value": "mom"},
                                            {"label": "QoQ %", "value": "qoq"},
                                            {"label": "YoY %", "value": "yoy"},
                                        ],
                                        value="raw",
                                        clearable=False,
                                        style={"width": "100%"},
                                    ),
                                    width=3,
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id={"type": "graph-type-selector", "index": i},
                                        options=[
                                            {"label": "Line", "value": "line"},
                                            {"label": "Bar", "value": "bar"},
                                            {"label": "Area", "value": "area"},
                                        ],
                                        value="line",
                                        clearable=False,
                                        style={"width": "100%"},
                                    ),
                                    width=3,
                                ),
                            ],
                            align="center",
                        ),
                        style={"padding": "5px"},
                    ),
                    dbc.CardBody(
                        [
                            dcc.Graph(
                                id={"type": "indicator", "index": i},
                                config={"displayModeBar": False},
                                style={
                                    "height": f"{graph_height}vh",
                                    "width": "100%",
                                    "margin": "0",
                                },
                            ),
                            dcc.Store(id={"type": "zoom-store", "index": i}, data=None),
                        ],
                        style={"padding": "5px"},
                    ),
                ],
                id=f"graph{i}-card",
                style={"margin": "0", "padding": "0"},
            )

            col_width = first_row_width if i <= first_row_count else second_row_width
            graph_cards.append(dbc.Col(card, width=col_width))

        rows = []
        if first_row_count > 0:
            rows.append(dbc.Row(graph_cards[:first_row_count], className="gx-0"))
        if second_row_count > 0:
            rows.append(dbc.Row(graph_cards[first_row_count:], className="gx-0"))

        return rows

    # Zoom State Callback
    @app.callback(
        Output({"type": "zoom-store", "index": MATCH}, "data"),
        Input({"type": "indicator", "index": MATCH}, "relayoutData"),
        State({"type": "zoom-store", "index": MATCH}, "data"),
    )
    def update_zoom_state(relayout_data, previous_zoom):
        """Update the zoom state of a graph based on user interactions.

        Args:
            relayout_data (dict): Layout data from the graph (e.g., zoom range).
            previous_zoom (dict): Previous zoom state.

        Returns:
            dict: Updated zoom state or None to reset.
        """
        if relayout_data is None:
            return previous_zoom

        if "autosize" in relayout_data and relayout_data["autosize"]:
            return None

        if "xaxis.range[0]" in relayout_data and "xaxis.range[1]" in relayout_data:
            return {
                "xaxis.range": [
                    relayout_data["xaxis.range[0]"],
                    relayout_data["xaxis.range[1]"],
                ]
            }
        if "xaxis.range" in relayout_data and len(relayout_data["xaxis.range"]) == 2:
            return {
                "xaxis.range": [
                    relayout_data["xaxis.range"][0],
                    relayout_data["xaxis.range"][1],
                ]
            }

        return previous_zoom

    # Individual Graph Callback
    @app.callback(
        Output({"type": "indicator", "index": MATCH}, "figure"),
        Input({"type": "indicator-selector", "index": MATCH}, "value"),
        Input({"type": "transform-selector", "index": MATCH}, "value"),
        Input({"type": "graph-type-selector", "index": MATCH}, "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("toggle-recessions", "value"),
        Input("toggle-events", "value"),
        Input("date-range-slider", "value"),
        State({"type": "zoom-store", "index": MATCH}, "data"),
    )
    def update_individual_graph(
        indicator,
        transform,
        graph_type,
        start_date,
        end_date,
        toggle_recessions,
        toggle_events,
        slider_range,
        zoom_state,
    ):
        """Update an individual graph based on user selections and date range.

        Args:
            indicator (str): Selected indicator (e.g., 'GDP').
            transform (str): Selected transformation ('raw', 'mom', 'qoq', 'yoy').
            graph_type (str): Selected graph type ('line', 'bar', 'area').
            start_date (str): Start date from DatePickerRange.
            end_date (str): End date from DatePickerRange.
            toggle_recessions (list): Whether to show recession bars.
            toggle_events (list): Whether to show key events.
            slider_range (list): RangeSlider value (months since 1990).
            zoom_state (dict): Current zoom state of the graph.

        Returns:
            plotly.graph_objs.Figure: The updated Plotly figure.
        """
        today = pd.to_datetime(datetime.today().strftime("%Y-%m-%d"))
        start_months, end_months = slider_range
        start_dt = months_to_date(start_months)
        end_dt = months_to_date(end_months)
        end_dt = min(end_dt, today)

        picker_start = pd.to_datetime(start_date)
        picker_end = pd.to_datetime(end_date)
        start_dt = max(start_dt, picker_start)
        end_dt = min(end_dt, picker_end)

        data = economic_data.loc[start_dt:end_dt]
        if data.empty:
            return {}

        col = colname(indicator, transform)
        if col not in data.columns:
            return {}

        fig = create_graph(data, col, graph_type)
        fig = add_annotations(
            fig, indicator, toggle_recessions, toggle_events, start_dt, end_dt
        )

        if zoom_state and "xaxis.range" in zoom_state:
            fig.update_layout(xaxis={"range": zoom_state["xaxis.range"]})

        return fig

    # Indicator Options Callback
    @app.callback(
        Output({"type": "indicator-selector", "index": MATCH}, "options"),
        Output({"type": "indicator-selector", "index": MATCH}, "value"),
        Input("indicator-group-selector", "value"),
        Input({"type": "indicator-selector", "index": MATCH}, "id"),
    )
    def update_indicator_options(group, selector_id):
        """Update the options and default value of an indicator selector dropdown.

        Args:
            group (str): Selected indicator group.
            selector_id (dict): ID of the indicator selector dropdown.

        Returns:
            tuple: (list of options, default value) for the dropdown.
        """
        group_indicators = INDICATOR_GROUPS.get(group, [])
        if not group_indicators:
            return [], None

        options = [
            {
                "label": INDICATORS[i]["description"],
                "value": i,
                "title": INDICATORS[i]["description"],
            }
            for i in group_indicators
        ]
        idx = selector_id["index"] - 1
        default = (
            group_indicators[idx]
            if idx < len(group_indicators)
            else group_indicators[0]
        )
        return options, default

    # Date Range Callbacks
    @app.callback(
        Output("date-picker", "start_date"),
        Output("date-picker", "end_date"),
        Input("date-range-slider", "value"),
    )
    def update_date_picker(slider_range):
        """Update the DatePickerRange based on the RangeSlider's monthly values.

        Args:
            slider_range (list): RangeSlider value (months since 1990, e.g., [192, 422]).

        Returns:
            tuple: (start_date, end_date) in 'YYYY-MM-DD' format.
        """
        today = pd.to_datetime(datetime.today().strftime("%Y-%m-%d"))
        start_months, end_months = slider_range
        start_date = months_to_date(start_months).strftime("%Y-%m-%d")
        end_date = min(months_to_date(end_months), today).strftime("%Y-%m-%d")
        return start_date, end_date

    @app.callback(
        Output("date-range-display", "children"), Input("date-range-slider", "value")
    )
    def update_date_range_display(slider_range):
        """Update the date range display label below the RangeSlider in YYYY-MM format.

        Args:
            slider_range (list): RangeSlider value (months since 1990).

        Returns:
            str: Formatted string showing the selected range (e.g., '2006-01 to 2025-03').
        """
        start_months, end_months = slider_range
        start_date = months_to_date(start_months)
        end_date = months_to_date(end_months)
        start_str = start_date.strftime("%Y-%m")
        end_str = end_date.strftime("%Y-%m")
        return f"Selected Range: {start_str} to {end_str}"

    # Summary Statistics Callback
    @app.callback(
        Output("last-updated", "children"),
        Output("error-message", "children"),
        Output("summary-stats", "children"),
        [
            Input({"type": "indicator-selector", "index": ALL}, "value"),
            Input({"type": "transform-selector", "index": ALL}, "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
            Input("date-range-slider", "value"),
        ],
    )
    def update_summary(indicators, transformations, start_date, end_date, slider_range):
        """Update the summary statistics based on the selected indicators and date range.

        Args:
            indicators (list): List of selected indicators.
            transformations (list): List of selected transformations.
            start_date (str): Start date from DatePickerRange.
            end_date (str): End date from DatePickerRange.
            slider_range (list): RangeSlider value (months since 1990).

        Returns:
            tuple: (last updated text, error message, summary items).
        """
        today = pd.to_datetime(datetime.today().strftime("%Y-%m-%d"))
        print("economic_data columns:", economic_data.columns.tolist())
        start_months, end_months = slider_range
        start_dt = months_to_date(start_months)
        end_dt = months_to_date(end_months)
        end_dt = min(end_dt, today)

        picker_start = pd.to_datetime(start_date)
        picker_end = pd.to_datetime(end_date)
        start_dt = max(start_dt, picker_start)
        end_dt = min(end_dt, picker_end)

        data = economic_data.loc[start_dt:end_dt].dropna()
        if data.empty:
            return (
                "No data available",
                "Error: No data for selected range",
                "No data available",
            )

        cols = [colname(ind, trans) for ind, trans in zip(indicators, transformations)]
        missing_cols = [c for c in cols if c and c not in data.columns]
        if missing_cols:
            return (
                "No data available",
                f"Error: Missing columns {missing_cols}",
                "No data available",
            )

        last_date = data.index.max().strftime("%Y-%m-%d")

        summary_items = []
        for ind, trans, col in zip(indicators, transformations, cols):
            if col in data.columns:
                latest_value = data[col].iloc[-1]
                change = (
                    (data[col].iloc[-1] - data[col].iloc[-2]) / data[col].iloc[-2] * 100
                    if len(data) > 1
                    else 0
                )
                display_name = colname(ind, trans, for_display=True)
                style_dict = {"color": "green" if change >= 0 else "red"}
                summary_items.append(
                    html.Div(
                        [
                            html.Strong(f"{display_name}:"),
                            html.Span(
                                f" {latest_value:.2f}", style={"margin-left": "5px"}
                            ),
                            html.Span(f" (Change: {change:.2f}%)", style=style_dict),
                        ],
                        style={"margin-bottom": "10px"},
                    )
                )

        return f"Last Updated: {last_date}", "", summary_items

    # RSS News Callback
    @app.callback(
        Output("rss-news-list", "children"),
        Input("rss-feed-selector", "value"),
        Input("refresh-rss-button", "n_clicks"),
        State("rss-feed-selector", "value"),
    )
    def update_rss_news(selected_feed, n_clicks, current_feed):
        """Update the RSS news feed based on the selected feed or refresh action.

        Args:
            selected_feed (str): Value of the RSS feed selector dropdown.
            n_clicks (int): Number of clicks on the refresh button.
            current_feed (str): Current value of the RSS feed selector (state).

        Returns:
            list: List of dash components representing RSS articles.
        """
        ctx = callback_context
        triggered_id = (
            ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        )

        feed_to_fetch = (
            current_feed if triggered_id == "refresh-rss-button" else selected_feed
        )

        if feed_to_fetch not in RSS_FEED_URLS:
            feed_to_fetch = list(RSS_FEED_URLS.keys())[0]

        articles = fetch_rss_feed(RSS_FEED_URLS[feed_to_fetch])
        if not articles:
            return [html.Li("Failed to load articles.", style={"color": "red"})]

        return [
            html.Li(
                [
                    html.Div(
                        [
                            html.A(
                                article["title"],
                                href=article["link"],
                                target="_blank",
                                style={
                                    "font-weight": "bold",
                                    "color": "#007bff",
                                    "text-decoration": "none",
                                },
                                className="rss-title",
                            ),
                            html.Div(
                                f"Published: {article['pub_date']}",
                                style={
                                    "font-size": "12px",
                                    "color": "gray",
                                    "margin-top": "2px",
                                },
                            ),
                            html.Div(
                                article["summary"],
                                style={
                                    "font-size": "14px",
                                    "color": "#333",
                                    "margin-top": "4px",
                                },
                            ),
                        ],
                        style={"margin-bottom": "10px"},
                    )
                ]
            )
            for article in articles
        ]
