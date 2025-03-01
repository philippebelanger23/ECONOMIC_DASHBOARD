# app/dashboard.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from components.sidebar import sidebar
from components.graphs import content
from app.callbacks import register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(sidebar, width=3, id="sidebar"), # Sidebar Width
            dbc.Col(
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=content
                ),
                width=9,
                id="content"
            ),
        ], className="dbc-row"),
        html.Div(id="error-message", style={"color": "red", "text-align": "center"})
    ], fluid=True, id="main-container")
])

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)