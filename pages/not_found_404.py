# dashboard_project/pages/not_found_404.py
import dash
from dash import html, dcc # <<< --- ADDED 'dcc' HERE ---
import dash_bootstrap_components as dbc

# --- Register this page as the 404 error handler ---
dash.register_page(
    __name__, path="/404", title="Page Not Found"
    )

layout = dbc.Container([


    dbc.Row([
        dbc.Col([
            html.H1("404 - Page Not Found", className="text-danger"),
            html.P("The page you are looking for does not exist."),
            # Using dcc.Link for internal navigation
            html.P(dcc.Link('Go back to the home page', href=dash.page_registry['pages.acs_data']['path'] if 'pages.acs_data' in dash.page_registry else '/')),
        ],
        className="text-center py-5 ps-0"
        )
    ])
], fluid=True)

# --- How Dash handles 404 ---
# If you have a page registered with path="/404", Dash will automatically
# render this page when a URL is visited that doesn't match any other registered page.