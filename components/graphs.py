# components/graphs.py
import dash_bootstrap_components as dbc
from dash import dcc, html
from data.mappings import INDICATOR_GROUPS, INDICATORS

content = dbc.Container([
    dbc.Row(id="graph-container")
], fluid=True)