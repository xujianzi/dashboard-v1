# dashboard_project/components/sidebar.py
import dash
import dash_bootstrap_components as dbc
from dash import html

def get_sort_key(page_dict):
    """
    Provides a sort key for pages.
    Sorts by 'order' if present and numeric. Pages without a valid numeric 'order'
    (e.g., missing, None, or non-numeric) are placed after those with valid orders.
    Secondary sort is by 'name'.
    """
    order = page_dict.get('order')
    # Fallback for name to ensure it's a string, useful if a page somehow lacks a name
    name = page_dict.get('name', str(page_dict.get('module', 'Unnamed Page')))

    if isinstance(order, (int, float)):
        # Valid numeric order found
        return (order, name)
    else:
        # Order is None, not a number, or missing.
        # Use float('inf') to place these items last when sorting.
        return (float('inf'), name)

def create_sidebar():
    """
    Creates the sidebar navigation for the Dash application.
    Dynamically generates NavLinks from dash.page_registry for registered pages.
    Filters out specific pages like 404 and sorts pages based on 'order' then 'name'.

    Returns:
        html.Div: A Dash HTML Div component containing the sidebar.
    """
    sidebar_style = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "20rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
        "overflow-y": "auto"
    }

    nav_links = []
    if dash.page_registry:
        # Sort all registered pages using the robust key
        # dash.page_registry.values() gives a list of page definition dicts
        sorted_page_items = sorted(dash.page_registry.values(), key=get_sort_key)

        for page in sorted_page_items:
            # Exclude specific pages (e.g., 404) from the navigation sidebar
            if page.get("path") == "/404":
                continue  # Skip this page

            page_name = page.get("name")
            # 'relative_path' is what Dash uses for hrefs in multi-page apps
            page_href = page.get("relative_path")

            if page_name and page_href:
                nav_links.append(
                    dbc.NavLink(
                        page_name,
                        href=page_href,
                        active="exact",  # Highlights the link for an exact path match
                        className="mb-1" # Margin bottom for spacing
                    )
                )
            else:
                # Optional: Log a warning if a page is missing necessary attributes
                print(
                    f"Warning: Page with module '{page.get('module', 'Unknown')}' "
                    f"(path: '{page.get('path', 'Unknown')}') is missing 'name' or 'relative_path' "
                    "and will not be added to the sidebar."
                )

    sidebar_content = html.Div(
        [
            html.H4("Navigation", className="display-6 text-center mb-4"),
            html.Hr(),
            dbc.Nav(
                nav_links,
                vertical=True,
                pills=True,
                className="flex-grow-1"
            ),
        ],
        className="sidebar d-flex flex-column"
    )

    return html.Div(
        sidebar_content, 
        style=sidebar_style, 
        id="sidebar",
        className="d-none d-md-block" # 响应式类名直接加在这里
        )