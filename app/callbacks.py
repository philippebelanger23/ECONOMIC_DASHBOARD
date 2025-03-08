# app/callbacks.py (corrected version)
# Standard library imports
import json
import math
import dash_table
from datetime import datetime
from dash import html

# Third-party imports
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, ALL, MATCH, State

# Local imports
from config.settings import RECESSIONS_FILE, RSS_FEED_URLS
from data.data_fetcher import fetch_rss_feed, get_all_next_release_dates
from data.data_processing import get_economic_data
from data.mappings import INDICATORS, INDICATOR_GROUPS
from components.sidebar import (
    create_economics_sidebar,
    create_correlations_sidebar,
    create_funds_flow_sidebar,
    create_news_sidebar,
)

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
    start_date = pd.to_datetime("1990-01-01")
    year = 1990 + (months // 12)
    month = (months % 12) + 1
    date = pd.to_datetime(f"{year}-{month:02d}-01")
    return date

def colname(ind, trans, for_display=False):
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
    # Wrap title by inserting <br> after a certain number of characters or words
    max_chars_per_line = 50
    wrapped_title = ""
    current_line = ""
    for word in f"{display_col} Over Time".split():
        if len(current_line) + len(word) > max_chars_per_line:
            wrapped_title += current_line + "<br>"
            current_line = word
        else:
            current_line += (" " if current_line else "") + word
    wrapped_title += current_line

    if graph_type == "line":
        fig = px.line(
            data,
            x=data.index,
            y=col,
            title=wrapped_title,
            line_shape="spline"  # Smooths the line with rounded corners
        )
    elif graph_type == "bar":
        fig = px.bar(data, x=data.index, y=col, title=wrapped_title)
    else:  # area
        fig = px.area(data, x=data.index, y=col, title=wrapped_title)

    fig.update_traces(
        hovertemplate="<b>%{y:.2f}</b><br>Date: %{x|%Y-%m-%d}<extra></extra>",
        line=dict(width=2, shape="spline")  # Ensure smooth line and set width
    )
    fig.update_layout(
        title_font=dict(size=18, weight="bold"),
        title_x=0.5,
        xaxis_title="",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, autorange=True),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig

def add_annotations(fig, indicator, show_recessions, show_events, start_dt, end_dt):
    series_id = INDICATORS.get(indicator, {}).get("id", None)
    next_release = next_release_dates.get(series_id, "Unknown") if series_id else "Unknown"

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
    @app.callback(
        Output("graph-container", "children"),
        Input("indicator-group-selector", "value"),
    )
    def update_graph_layout(group):
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

        available_height = 80
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
            rows.append(dbc.Row(graph_cards[:first_row_count], className="g-1"))
        if second_row_count > 0:
            rows.append(dbc.Row(graph_cards[first_row_count:], className="g-1"))

        return rows

    @app.callback(
        Output({"type": "zoom-store", "index": MATCH}, "data"),
        Input({"type": "indicator", "index": MATCH}, "relayoutData"),
        State({"type": "zoom-store", "index": MATCH}, "data"),
    )
    def update_zoom_state(relayout_data, previous_zoom):
        if relayout_data is None:
            return previous_zoom

        if "autosize" in relayout_data and relayout_data["autosize"]:
            return None

        print(f"Relayout data: {relayout_data}")

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
            x_start, x_end = zoom_state["xaxis.range"]
            fig.update_xaxes(range=[x_start, x_end])
            fig.update_yaxes(autorange=True)
        else:
            fig.update_yaxes(autorange=True)

        print(f"Final y-axis layout: {fig.layout.yaxis}")

        return fig

    @app.callback(
        Output({"type": "indicator-selector", "index": MATCH}, "options"),
        Output({"type": "indicator-selector", "index": MATCH}, "value"),
        Input("indicator-group-selector", "value"),
        Input({"type": "indicator-selector", "index": MATCH}, "id"),
    )
    def update_indicator_options(group, selector_id):
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

    @app.callback(
        Output("date-picker", "start_date"),
        Output("date-picker", "end_date"),
        Input("date-range-slider", "value"),
        prevent_initial_call=True
    )
    def update_date_picker(slider_range):
        today = pd.to_datetime(datetime.today().strftime("%Y-%m-%d"))
        start_months, end_months = slider_range
        start_date = months_to_date(start_months).strftime("%Y-%m-%d")
        end_date = min(months_to_date(end_months), today).strftime("%Y-%m-%d")
        return start_date, end_date

    @app.callback(
        Output("date-range-display", "children"), Input("date-range-slider", "value")
    )
    def update_date_range_display(slider_range):
        start_months, end_months = slider_range
        start_date = months_to_date(start_months)
        end_date = months_to_date(end_months)
        start_str = start_date.strftime("%Y-%m")
        end_str = end_date.strftime("%Y-%m")
        return f"Selected Range: {start_str} to {end_str}"

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
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in ["Indicator", "Value", "Δ MoM", "Δ YoY"]],
                    data=[],
                ),
            )

        cols = [colname(ind, trans) for ind, trans in zip(indicators, transformations)]
        missing_cols = [c for c in cols if c and c not in data.columns]
        if missing_cols:
            return (
                "No data available",
                f"Error: Missing columns {missing_cols}",
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in ["Indicator", "Value", "Δ MoM", "Δ YoY"]],
                    data=[],
                ),
            )

        last_date = data.index.max().strftime("%Y-%m-%d")

        table_data = []
        for ind, trans, col in zip(indicators, transformations, cols):
            if col in data.columns:
                latest_value = data[col].iloc[-1]
                mom_col = colname(ind, "mom")
                yoy_col = colname(ind, "yoy")
                change_mom = data[mom_col].iloc[-1] if mom_col in data.columns and len(data) > 1 else 0
                change_yoy = data[yoy_col].iloc[-1] if yoy_col in data.columns and len(data) > 12 else 0

                # Truncate long indicator names with ...
                indicator_name = INDICATORS[ind]["description"]
                max_length = 20  # Adjust this value based on your preference
                truncated_indicator = (indicator_name[:max_length] + "...") if len(indicator_name) > max_length else indicator_name

                table_data.append({
                    "Indicator": truncated_indicator,
                    "Value": f"{latest_value:.2f}",
                    "Δ MoM": f"{change_mom:.2f}%",
                    "Δ YoY": f"{change_yoy:.2f}%",
                })

        summary_table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in ["Indicator", "Value", "Δ MoM", "Δ YoY"]],
            data=table_data,
            style_table={},
            style_cell={
                "textAlign": "left",
                "padding": "5px",
                "fontSize": "14px",
                "whiteSpace": "normal",  # Allow text to wrap
                "overflow": "hidden",    # Hide overflow
                "textOverflow": "ellipsis",  # Add ... for truncated text
                "maxWidth": "150px",     # Set a max width for the Indicator column
            },
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
            },
            style_data_conditional=[
                {
                    "if": {"filter_query": "{Δ MoM} < 0"},
                    "color": "red",
                },
                {
                    "if": {"filter_query": "{Δ YoY} < 0"},
                    "color": "red",
                },
            ],
        )

        return f"Last Updated: {last_date}", "", summary_table

    @app.callback(
        Output("date-range-slider", "value"),
        [
            Input("btn-last-3mo", "n_clicks"),
            Input("btn-last-6mo", "n_clicks"),
            Input("btn-last-12mo", "n_clicks"),
            Input("btn-last-24mo", "n_clicks")
        ],
        [State("date-range-slider", "value")],
        prevent_initial_call=True
    )
    def update_date_range_from_buttons(n_clicks_3mo, n_clicks_6mo, n_clicks_12mo, n_clicks_24mo, current_range):
        ctx = callback_context
        if not ctx.triggered:
            return current_range

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        today = datetime.today()
        current_month = (today.year - 1990) * 12 + today.month - 1  # Months since 1990

        if triggered_id == "btn-last-3mo" and n_clicks_3mo:
            end_month = current_month
            start_month = max(0, end_month - 3)
        elif triggered_id == "btn-last-6mo" and n_clicks_6mo:
            end_month = current_month
            start_month = max(0, end_month - 6)
        elif triggered_id == "btn-last-12mo" and n_clicks_12mo:
            end_month = current_month
            start_month = max(0, end_month - 12)
        elif triggered_id == "btn-last-24mo" and n_clicks_24mo:
            end_month = current_month
            start_month = max(0, end_month - 24)
        else:
            return current_range

        return [start_month, end_month]

    @app.callback(
        Output({"type": "news-list", "feed": ALL}, "children"),
        [Input({"type": "refresh-button", "feed": ALL}, "n_clicks")],
        prevent_initial_call=False
    )
    def update_all_rss_news(n_clicks):
        feeds = list(RSS_FEED_URLS.keys())
        all_news_lists = []
        
        for feed_key in feeds:
            articles = fetch_rss_feed(RSS_FEED_URLS[feed_key])
            if not articles:
                news_list = [html.Li("Failed to load articles.", style={"color": "red"})]
            else:
                news_list = [
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
                                        style={"font-size": "12px", "color": "gray", "margin-top": "2px"},
                                    ),
                                    html.Div(
                                        article["summary"],
                                        style={"font-size": "14px", "color": "#333", "margin-top": "4px"},
                                    ),
                                ],
                                style={"margin-bottom": "10px"},
                            )
                        ]
                    )
                    for article in articles
                ]
            all_news_lists.append(news_list)
        
        return all_news_lists

    @app.callback(
        Output("summary-stats-container", "children"),
        [
            Input({"type": "indicator-selector", "index": ALL}, "value"),
            Input({"type": "transform-selector", "index": ALL}, "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
            Input("date-range-slider", "value"),
        ],
    )
    def update_summary_tab(indicators, transformations, start_date, end_date, slider_range):
        # Reuse the existing update_summary logic
        last_updated, error_message, summary_table = update_summary(
            indicators, transformations, start_date, end_date, slider_range
        )
        return [
            html.P(last_updated, style={"text-align": "center", "margin-bottom": "10px"}),
            html.Div(error_message, style={"color": "red", "text-align": "center", "margin-bottom": "10px"}) if error_message else "",
            summary_table,
        ]

    @app.callback(
        Output("sidebar-content", "children"),
        Input("dashboard-tabs", "value")
    )
    def update_sidebar(selected_tab):
        if selected_tab == "tab-economics":
            return create_economics_sidebar()
        elif selected_tab == "tab-correlations":
            return create_correlations_sidebar()
        elif selected_tab == "tab-funds-flow":
            return create_funds_flow_sidebar()
        elif selected_tab == "tab-news":
            return create_news_sidebar()
        return create_economics_sidebar()  # Default to economics sidebar

    @app.callback(
        Output("funds-flow-container", "children"),
        [
            Input("date-range-slider", "value"),
            Input("visualization-type", "value"),
            Input("flow-type-selector", "value"),
            Input("flow-period", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date")
        ]
    )
    def update_funds_flow(slider_range, viz_type, flow_type, flow_period, start_date, end_date):
        today = pd.to_datetime(datetime.today().strftime("%Y-%m-%d"))
        start_months, end_months = slider_range
        start_dt = months_to_date(start_months)
        end_dt = months_to_date(end_months)
        end_dt = min(end_dt, today)

        picker_start = pd.to_datetime(start_date)
        picker_end = pd.to_datetime(end_date)
        start_dt = max(start_dt, picker_start)
        end_dt = min(end_dt, picker_end)
        
        if viz_type == "sector_rotation":
            # Create a figure for sector rotation
            sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 
                      'Consumer Staples', 'Industrials', 'Energy', 'Materials', 
                      'Utilities', 'Real Estate', 'Communication Services']
            
            # Sample data - in production this would come from your data source
            flows = [15, 10, -5, 8, 3, -2, 12, -4, 6, -8, 7]  # Example fund flows in billions
            performance = [8, 5, -2, 6, 2, -1, 10, -3, 4, -5, 5]  # Example sector performance %
            
            fig = px.scatter(
                x=performance,
                y=flows,
                size=[abs(f) * 2 for f in flows],
                text=sectors,
                title=f"Sector Rotation Analysis ({flow_type.replace('_', ' ').title()} - {flow_period})",
                labels={
                    'x': 'Sector Performance (%)',
                    'y': 'Fund Flows (Billions $)',
                    'size': 'Absolute Flow'
                }
            )
            
            fig.update_traces(
                textposition='top center',
                marker=dict(
                    sizemode='area',
                    sizeref=2.*max(flows)/(40.**2),
                    sizemin=4,
                    color=['#2ecc71' if f > 0 else '#e74c3c' for f in flows]
                )
            )
            
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                title_x=0.5,
                title_font_size=20,
                margin=dict(l=50, r=50, t=80, b=50),
                shapes=[
                    dict(
                        type="line",
                        x0=min(performance),
                        y0=0,
                        x1=max(performance),
                        y1=0,
                        line=dict(color="black", width=1, dash="dash")
                    ),
                    dict(
                        type="line",
                        x0=0,
                        y0=min(flows),
                        x1=0,
                        y1=max(flows),
                        line=dict(color="black", width=1, dash="dash")
                    )
                ],
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
                paper_bgcolor='white',
                annotations=[
                    dict(
                        x=max(performance) * 0.75,
                        y=max(flows) * 0.75,
                        text="Leaders<br>(Strong Performance,<br>Inflows)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    ),
                    dict(
                        x=min(performance) * 0.75,
                        y=max(flows) * 0.75,
                        text="Contrarian Bets<br>(Weak Performance,<br>Inflows)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    ),
                    dict(
                        x=max(performance) * 0.75,
                        y=min(flows) * 0.75,
                        text="Profit Taking<br>(Strong Performance,<br>Outflows)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    ),
                    dict(
                        x=min(performance) * 0.75,
                        y=min(flows) * 0.75,
                        text="Laggards<br>(Weak Performance,<br>Outflows)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    )
                ]
            )
        
        else:  # relative_analysis
            # Sample data for relative analysis
            sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 
                      'Consumer Staples', 'Industrials', 'Energy', 'Materials', 
                      'Utilities', 'Real Estate', 'Communication Services']
            
            # Sample data - in production this would come from your data source
            relative_strength = [1.2, 0.8, 0.9, 1.1, 0.95, 1.05, 1.3, 0.85, 0.75, 0.9, 1.15]
            relative_momentum = [0.1, -0.05, 0.02, 0.08, -0.03, 0.04, 0.15, -0.07, -0.12, 0.03, 0.07]
            
            fig = px.scatter(
                x=relative_strength,
                y=relative_momentum,
                size=[abs(m) * 20 for m in relative_momentum],  # Size based on momentum
                text=sectors,
                title=f"Relative Strength vs Momentum Analysis ({flow_type.replace('_', ' ').title()} - {flow_period})",
                labels={
                    'x': 'Relative Strength (vs Index)',
                    'y': 'Relative Momentum (WoW Change)',
                    'size': 'Absolute Momentum'
                }
            )
            
            fig.update_traces(
                textposition='top center',
                marker=dict(
                    sizemode='area',
                    sizeref=2.*max(abs(min(relative_momentum)), abs(max(relative_momentum)))/(40.**2),
                    sizemin=4,
                    color=['#2ecc71' if m > 0 else '#e74c3c' for m in relative_momentum]
                )
            )
            
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                title_x=0.5,
                title_font_size=20,
                margin=dict(l=50, r=50, t=80, b=50),
                shapes=[
                    dict(
                        type="line",
                        x0=min(relative_strength),
                        y0=0,
                        x1=max(relative_strength),
                        y1=0,
                        line=dict(color="black", width=1, dash="dash")
                    ),
                    dict(
                        type="line",
                        x0=1,  # Reference line at 1.0 (index level)
                        y0=min(relative_momentum),
                        x1=1,
                        y1=max(relative_momentum),
                        line=dict(color="black", width=1, dash="dash")
                    )
                ],
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
                paper_bgcolor='white',
                annotations=[
                    dict(
                        x=max(relative_strength) * 0.75,
                        y=max(relative_momentum) * 0.75,
                        text="Strong & Improving<br>(High RS, Rising)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    ),
                    dict(
                        x=min(relative_strength) * 1.1,
                        y=max(relative_momentum) * 0.75,
                        text="Weak but Improving<br>(Low RS, Rising)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    ),
                    dict(
                        x=max(relative_strength) * 0.75,
                        y=min(relative_momentum) * 0.75,
                        text="Strong but Weakening<br>(High RS, Falling)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    ),
                    dict(
                        x=min(relative_strength) * 1.1,
                        y=min(relative_momentum) * 0.75,
                        text="Weak & Weakening<br>(Low RS, Falling)",
                        showarrow=False,
                        font=dict(size=10, color='rgba(0,0,0,0.5)'),
                        align='center'
                    )
                ]
            )
        
        return dbc.Card(
            dbc.CardBody(
                dcc.Graph(
                    figure=fig,
                    config={'displayModeBar': False},
                    style={
                        'height': '80vh',
                        'width': '100%'
                    }
                ),
                style={'padding': '5px'}
            ),
            style={'margin': '10px', 'height': '85vh'}
        )