# dashboard_project/pages/covid_stats.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from utils.db_utils import fetch_data

dash.register_page(
    __name__,
    path='/covid-19-statistics',
    name='COVID-19 Statistics',
    title='COVID-19 Data',
    description='Dashboard for COVID-19 statistics.',
    order=2
)

def layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(html.H2("COVID-19 Statistics", className="text-center my-4"), width=12)
            ),
            dbc.Tabs(
                [
                    dbc.Tab(label="Data Table", tab_id="covid-tab-data-table", children=[
                        dbc.Card(dbc.CardBody(id='covid-tab-content-data-table', className="p-4"))
                    ]),
                    dbc.Tab(label="Map Visualization", tab_id="covid-tab-map-viz", children=[
                         dbc.Card(dbc.CardBody(id='covid-tab-content-map-viz', className="p-4", children=[
                            html.P("Map visualization placeholder for COVID-19 data.")
                        ]))
                    ]),
                    dbc.Tab(label="Trend Analysis", tab_id="covid-tab-trend-analysis", children=[
                         dbc.Card(dbc.CardBody(id='covid-tab-content-trend-analysis', className="p-4", children=[
                             html.P("Trend analysis placeholder for COVID-19 data.")
                        ]))
                    ]),
                ],
                id="covid-page-tabs",
                active_tab="covid-tab-data-table",
                className="mb-3"
            ),
        ],
        fluid=True
    )

@callback(
    Output('covid-tab-content-data-table', 'children'),
    Input('covid-page-tabs', 'active_tab')
)
def render_covid_data_table_tab(active_tab):
    if active_tab == "covid-tab-data-table":
        # query_covid_data = "SELECT * FROM covid_cases_table LIMIT 100;"
        # df_covid = fetch_data(query_covid_data)
        df_covid = fetch_data("SELECT * FROM covid_cases_table LIMIT 10;") # Using mock

        if not df_covid.empty:
            return dbc.Table.from_dataframe(df_covid, striped=True, bordered=True, hover=True, responsive=True)
        else:
            return html.Div([
                html.P("No COVID-19 data available or error fetching data.", className="text-danger"),
                html.Small("Using placeholder data from db_connector.py if no database is connected.")
            ])
    return None

# Add other callbacks for map and trend analysis for COVID-19 page as needed