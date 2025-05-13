import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from utils.db_utils import fetch_data

dash.register_page(
    __name__,
    path='/test',
    name='Function Test page',
    title='Function Test page',
    description='Function Test page',
    order=4
)

layout = html.Div([
    html.H3("🧪 Function Test - Static Choropleth Map"),

    dcc.Graph(
        id="static-map",
        figure={
            "layout": {
                "mapbox": {
                    "style": "carto-positron",
                    "center": {"lat": 37.5, "lon": -119.5},
                    "zoom": 5,
                },
                "margin": {"r":0,"t":0,"l":0,"b":0}
            },
            "data": []
        }
    ),

    html.P("这是一个静态测试页面，地图尚未绑定任何动态数据。")
])