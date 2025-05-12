from dash import html, dcc, Output, Input, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash # For dash.exceptions.PreventUpdate

from app import app
from components import sidebar
import inspect # 导入 inspect 模块

print(f"导入的 sidebar 模块来自: {sidebar.__file__}") # 打印 sidebar.py 的实际文件路径
print("sidebar 模块包含的属性:")
for name, obj in inspect.getmembers(sidebar): # 使用 inspect 获取更详细信息
    if inspect.isfunction(obj) or inspect.isclass(obj): # 只打印函数和类
        print(f"  {name}")
from pages import acs_data, covid_stat, mobility_patterns

# --- Application Header Children ---
# This function now returns the *children* for the AppShell's header area
def create_app_header_children():
    return dmc.Group(
        justify="space-between", #
        align="center",
        style={"height": "100%", "paddingLeft": "1rem", "paddingRight": "1rem"}, # Ensure content uses full header height
        children=[
            dmc.Title("My Data Dashboard", order=1, c="blue.7"),
            # You could add other header elements here, e.g., a theme switcher
            # dmc.ActionIcon(DashIconify(icon="radix-icons:moon"), variant="default", id="theme-switcher")
        ]
    )

# --- Main Application Layout using AppShell ---
app.layout = dmc.MantineProvider(
    theme={
        "fontFamily": "'Inter', sans-serif",
        "primaryColor": "indigo", # Choose your primary color
        "components": {
            "Button": {"styles": {"root": {"fontWeight": 400}}},
            "Alert": {"styles": {"title": {"fontWeight": 500}}},
            "Title": {"styles": {"root": {"fontFamily": "'Greycliff CF', sans-serif"}}},
        },
    },
    inherit=True, # Inherit system theme (light/dark mode) if browser supports it
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=[
        dcc.Location(id="url", refresh=False),
        html.Div( # Container for notifications
            id="notifications-container",
            style={
                "position": "fixed", "top": "80px", "right": "10px",
                "zIndex": 2000, "width": "auto", "maxWidth": "400px"
            }
        ),
        dmc.AppShell(
            padding="md", # Padding for the main content area
            fixed=True,   # Header and Navbar will be fixed
            zIndex=100,
            header=create_app_header_children(), # Pass children for the header
            headerHeight=70,                      # Specify header height
            navbar=sidebar.create_sidebar_children(), # Pass children for the navbar (from sidebar.py)
            navbarWidth=300,                     # Specify navbar width
            styles={
                "main": { # Styles for the main content area that holds `page-content`
                    "paddingTop": "var(--app-shell-header-height, 70px)",
                    "paddingLeft": "var(--app-shell-navbar-width, 300px)",
                    "minHeight": "calc(100vh - var(--app-shell-header-height, 0px))",
                    # Example: "backgroundColor": dmc.theme.DEFAULT_COLORS["gray"][0],
                }
            },
            children=[
                # The dmc.Container for page content goes here
                dmc.Container(
                    id="page-content",
                    fluid=True,
                    pt="xl", # Adjust padding as needed within the main area
                )
            ]
        )
    ]
)

# --- Callback to Update Page Content Based on URL ---
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/acs-data" or pathname == "/":
        return acs_data.layout()
    elif pathname == "/covid-19-stats":
        return covid_stat.layout()
    elif pathname == "/mobility-patterns":
        return mobility_patterns.layout()
    else:
        return dmc.Center(
            style={"height": "calc(100vh - 200px)"}, # Adjust height to be visible
            children=[
                dmc.Stack([
                    dmc.Title("404 - Page Not Found", order=1, color="red"),
                    dmc.Text(f"The path '{pathname}' was not recognised."),
                    dmc.Anchor("Go back to Home", href="/"),
                ])
            ]
        )

# --- 回调：根据 URL 更新侧边栏 NavLinks 的激活状态 ---
@app.callback(
    # 输出目标是每个 NavLink 的 'active' 属性
    [Output(f"navlink{link['href'].replace('/', '_').replace('-', '_')}", "active") for link in sidebar.NAV_LINKS],
    [Input("url", "pathname")],
    # prevent_initial_call=False # 通常希望在页面加载时就设置活动链接，因此设为 False
)
def update_navlink_active_state(pathname): # 函数名可以更新
    return [pathname == link["href"] for link in sidebar.NAV_LINKS]


# Example for triggering notifications (ensure button exists in one of your page layouts)
# @app.callback(
#     Output("notifications-container", "children"),
#     Input("some-button-id-to-trigger-notification", "n_clicks"),
#     State("notifications-container", "children"),
#     prevent_initial_call=True,
# )
# def show_notification_callback(n_clicks, existing_notifications):
#     if not n_clicks:
#         raise dash.exceptions.PreventUpdate
#     notifications = existing_notifications if isinstance(existing_notifications, list) else []
#     new_notif = dmc.Notification(...) # Define your dmc.Notification here
#     return notifications + [new_notif]

if __name__ == '__main__':
    app.run(debug=True, port=8050)