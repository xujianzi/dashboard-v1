# dashboard_project/app.py
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from components.sidebar import create_sidebar
# from utils.db_connector import close_db_resources # Optional: if you want to close DB on exit
# import atexit # Optional

# --- Initialize the Dash App ---
# use_pages=True enables Dash Pages (multi-page app capabilities)
# external_stylesheets apply global styles; BOOTSTRAP theme provides a good starting point.
app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.LUX], # Using LUX theme for a modern look
           suppress_callback_exceptions=True, # Important for multi-page apps with dynamic content
           meta_tags=[ # Responsive meta tag
               {"name": "viewport", "content": "width=device-width, initial-scale=1"}
           ]
          )

# --- Main Application Title ---
# Using dbc.NavbarSimple for a clean and responsive title bar.
app_title = "Comprehensive Data Dashboard"
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("GitHub", href="https://github.com/your-repo", target="_blank")) # Example external link
    ],
    brand=app_title,
    brand_href="/", # Link back to the home page (if you define one) or the first page
    color="primary",
    dark=True,
    className="mb-0 main-app-title", # Added margin bottom 0
    sticky="top", # Make navbar sticky
)

# --- Sidebar ---
# The sidebar is created by the function in components/sidebar.py
sidebar = create_sidebar()

# --- Main Application Layout ---
# This defines the overall structure of your application.
# dbc.Container(fluid=True) allows the content to span the full width.
# dbc.Row and dbc.Col are used for responsive grid layout.
app.layout = dbc.Container(
    [
        navbar, # Application title bar
        sidebar,  # 直接放置侧边栏组件，它会根据自己的style固定定位
        # 主内容区域容器
        html.Div(
            [
                dash.page_container
            ],
            className="content-container" # 可以考虑添加flex-grow-1等，但通常会自动填充
        ),
        # dbc.Row(
        #     [
        #         # Sidebar Column
        #         dbc.Col(
        #             [sidebar],
        #             # width=3, # Example width for larger screens using DBC grid
        #             # For fixed sidebar, direct styling in sidebar.py is used.
        #             # This Col is more of a placeholder if not using fixed styling or to control spacing.
        #             className="d-none d-md-block", # Hide sidebar on small screens, show on medium and up
        #             style={"padding": "0"} # Remove padding if sidebar has its own
        #         ),

        #         # Content Column
        #         dbc.Col(
        #             [
        #                 # dash.page_container is where the content of the currently
        #                 # selected page (from the pages/ directory) will be rendered.
        #                 dash.page_container
        #             ],
        #             # width=9, # Example width for content area
        #             style={"marginLeft": "20rem", "padding": "2rem 1rem"}, # Adjust margin to account for fixed sidebar width
        #             className="content-container flex-grow-1" # Custom class for content styling
        #         )
        #     ],
        #     className="g-0" # No gutters between columns
        # ),
        # Store component for client-side data storage if needed later
        dcc.Store(id='client-side-store'),
    ],
    fluid=True, # Use the full width of the viewport
    className="dbc p-0 m-0" # Ensure container itself has no padding/margin if managing internally
)

# --- For Gunicorn/WSGI deployment ---
# The 'server' variable is what WSGI servers like Gunicorn will look for.
server = app.server

# --- Optional: Register database cleanup function ---
# def on_shutdown():
#     print("Application is shutting down. Closing database resources.")
#     close_db_resources()
# atexit.register(on_shutdown)


if __name__ == '__main__':
    # Runs the Dash development server.
    # debug=True enables hot-reloading and error messages in the browser.
    # Set debug=False in a production environment.
    app.run(debug=True, port=8051)