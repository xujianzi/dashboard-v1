# dashboard_project/pages/acs_data.py
import dash
from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from utils.db_utils import fetch_data
import math
from dash import dash_table
import json
import dash_leaflet as dl
import dash_leaflet.express as dlx # For categorical_colorbar and potentially assign
import os
import plotly.express as px # <--- 新增 Plotly Express

# --- Register Page ---
dash.register_page(
    __name__,
    path='/acs-data',
    name='ACS Data',
    title='ACS Data Analysis',
    description='American Community Survey Data Visualization.',
    order=1
)

# --- Page Specific Layout ---
# dashboard_project/pages/acs_data.py

# --- 列定义 ---
ALL_COLUMNS_FROM_SCHEMA = [
    "id", "state", "zipcode", "year", "pct_less_than_9th_grade", "pct_high_school",
    "pct_bachelor", "pct_master", "pct_high_school_or_higher", "pct_english_speaker",
    "pct_spanish_speaker", "pct_asian_speaker", "pct_lep", "pct_white", "pct_black",
    "pct_asian", "pct_non_white", "pct_hispanic", "pct_non_hispanic_white",
    "pct_non_hispanic_black", "pct_non_hispanic_asian", "pct_minority_population",
    "pct_infant_toddler", "pct_school_age_children", "pct_young_adults",
    "pct_working_age_adults", "pct_middle_aged_adults", "pct_senior", "pct_adults",
    "pct_children", "pct_male", "pct_female", "pct_below_poverty", "pct_unemployed",
    "pct_employed", "pct_unisured", "pct_isured", "pct_disability", "per_capita_income",
    "median_income", "population", "pct_receive_public_assistance", "pct_house_with_children",
    "pct_single_parent_households", "pct_female_headed_households", "pct_foreign_born",
    "pct_multi_unit_structures", "pct_without_plumbing", "pct_overcrowded_housing",
    "pct_renter_occupied", "pct_households_without_a_vehicle",
    "pct_with_access_to_a_vehicle", "commute_time", "pct_work_at_home",
    "pct_professinal", "pct_service", "lat", "lng", "geom"
] # 从您的建表语句中获取

FIXED_DISPLAY_COLUMNS = ['id', 'state', 'zipcode', 'year'] # 这些列总是显示且不可选
EXCLUDED_COLUMNS = ['geom', "lat", "lng"] # 这些列不参与选择和显示

# 计算可选列 (从所有列中排除固定列和特定排除列)
POSSIBLE_SELECTABLE_COLUMNS = sorted([
    col for col in ALL_COLUMNS_FROM_SCHEMA
    if col not in FIXED_DISPLAY_COLUMNS and col not in EXCLUDED_COLUMNS
])

# 初始状态下，“All”被选中，所以默认选中的列是固定列+所有可选列
DEFAULT_SELECTED_COLUMNS = FIXED_DISPLAY_COLUMNS + POSSIBLE_SELECTABLE_COLUMNS

PAGE_SIZE_DT = 15 # 为DataTable定义页面大小

# --- 地图tab的布局和准备 ---
# --- 为地图变量下拉菜单准备选项 ---
MAP_VARIABLE_OPTIONS = []
if 'POSSIBLE_SELECTABLE_COLUMNS' in globals() and POSSIBLE_SELECTABLE_COLUMNS: # 确保变量已定义且不为空
    MAP_VARIABLE_OPTIONS = [
        {"label": col.replace("pct_", "% ").replace("_", " ").title(), "value": col}
        for col in POSSIBLE_SELECTABLE_COLUMNS
    ]
    # 设置一个默认显示的地图变量，例如 'commute_time'
    DEFAULT_MAP_VARIABLE = 'commute_time' if 'commute_time' in POSSIBLE_SELECTABLE_COLUMNS else POSSIBLE_SELECTABLE_COLUMNS[0]
else: # Fallback if POSSIBLE_SELECTABLE_COLUMNS is not defined or empty
    DEFAULT_MAP_VARIABLE = 'commute_time' # Or some other sensible default or None
    MAP_VARIABLE_OPTIONS.append({'label': 'Commute Time (Default)', 'value': 'commute_time'})


# --- Load GeoJSON Data ---
# Construct the absolute path to the GeoJSON file
# Assumes 'data' folder is in the same directory as 'app.py' (project root)
# If pages/acs_data.py is in a subdirectory, adjust path accordingly.
# For robustness, let's assume app.py is in the parent directory of pages/
# and data/ is at the same level as app.py.
# A simpler way if running from project root: GEOJSON_PATH = "data/zcta_ca_simplify.json"

# Assuming the script is run from the project root (where app.py is)
GEOJSON_FILE_PATH = os.path.join("data", "zcta_ca_simplify.json")
geojson_data_ca_zcta = None
try:
    with open(GEOJSON_FILE_PATH, 'r') as f:
        geojson_data_ca_zcta = json.load(f)
    # print("GeoJSON loaded successfully.")
except FileNotFoundError:
    print(f"ERROR: GeoJSON file not found at '{os.path.abspath(GEOJSON_FILE_PATH)}'. Please check the path.")
except json.JSONDecodeError:
    print(f"ERROR: Could not decode GeoJSON file from '{GEOJSON_FILE_PATH}'. Check file content.")




def layout():
    # --- 列选择卡片 ---
    column_selection_card = dbc.Card([
        dbc.CardHeader("Select Data Columns"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dbc.Checkbox(
                        id="acs-select-all-columns-checkbox",
                        label="Select All",
                        value=True # 默认全选
                    ),
                    width=12, # 让它占据整行，或 "auto"
                    className="mb-2 fw-bold" # 加粗并添加底部边距
                ),
            ]),
            html.Hr(), # 分隔线
            dbc.Label("Choose ACS Variables:"),
            dbc.DropdownMenu(
                label="Select Columns from List...",
                id="acs-column-select-dropdown",
                color="light", # 下拉按钮的颜色
                className="mb-3 d-block", # d-block使其占据全部可用宽度
                children=[
                    # 这个html.Div将作为下拉菜单的内容区域，并容纳动态生成的复选框网格
                    # 为其添加内边距和滚动条
                    html.Div(
                        id="acs-individual-column-checkboxes-container", # ID保持，但现在它在Dropdown内
                        style={"padding": "1rem", "maxHeight": "300px", "overflowY": "auto", "minWidth": "350px"}
                    )
                ],
                # direction="down", # 默认向下
            ),
            dbc.Button("Apply Column Selection", id="acs-apply-columns-button", color="primary", n_clicks=0)
        ])
    ], className="mb-4")

    # map_selection_card = dbc.Card(
    #     dbc.CardBody([
    #         dbc.Row([
    #             dbc.Col(dbc.Label("Select Variable to Display on Map:"), width="auto", className="me-2"),
    #             dbc.Col(
    #                 dcc.Dropdown(
    #                     id='acs-map-variable-dropdown',
    #                     options=MAP_VARIABLE_OPTIONS,
    #                     value=DEFAULT_MAP_VARIABLE, # 默认选中的变量
    #                     clearable=False,
    #                     style={'width': '100%'}
    #                 ),
    #                 md=6, # 下拉菜单占据的宽度
    #                 lg=4
    #             ),
    #         ], align="center", className="mb-0") # 移除了mb-3，让卡片更紧凑
    #     ]),
    #     className="mb-3" # 变量选择卡片底部的边距
    # ),
    # --- 标签页定义 (内容包裹在Card中，与之前一致) ---
    tabs_component = dbc.Tabs(
        [
            dbc.Tab(label="Data Table", tab_id="acs-tab-data-table", children=[
                
                dbc.Card(dbc.CardBody([
                    column_selection_card,
                    html.Hr(),
                    html.Div([
                        dbc.Button(
                            "Download Selected Data (CSV)",
                            id="acs-download-button",
                            color="success",
                            className="mt-2 mb-3"
                        ),
                        dcc.Download(id="acs-download-dataframe"),
                        dbc.Spinner(
                            html.Div( # 用于包裹 DataTable 的 Div
                                dash_table.DataTable(
                                    id='acs-datatable',
                                    columns=[{"name": col.replace("pct_", "% ").replace("_", " ").title(), "id": col} for col in DEFAULT_SELECTED_COLUMNS],
                                    data=[],
                                    page_action='custom',
                                    page_current=0,
                                    page_size=PAGE_SIZE_DT,
                                    sort_action='custom',
                                    sort_mode='multi',
                                    sort_by=[],
                                    style_table={'overflowX': 'auto'},
                                    style_cell={
                                        'minWidth': '100px', 'width': '150px', 'maxWidth': '180px',
                                        'overflow': 'hidden',
                                        'textOverflow': 'ellipsis',
                                        'textAlign': 'left', 'padding': '5px'
                                    },
                                    style_header={
                                        'backgroundColor': 'rgb(230, 230, 230)',
                                        'fontWeight': 'bold', 'border': '1px solid grey'
                                    },
                                    style_data={'border': '1px solid grey'},
                                ),
                                className="mt-0"
                            )
                        )
                    ])
                ]))
            ]),
            dbc.Tab(label="Map Visualization", tab_id="acs-tab-map-viz", children=[
                # dbc.Card(dbc.CardBody([ # 确保内容用Card包裹
                #     map_selection_card,
                #     html.Hr(),
                #     dbc.Spinner(html.Div(id='acs-map-container')) # Plotly Graph 将加载到这里
                # ]))
                dbc.Card(dbc.CardBody([
                    # --- 新增：变量选择下拉菜单 ---
                    dbc.Row([
                        dbc.Col(dbc.Label("Select Variable:", html_for="acs-map-variable-dropdown"), width="auto", className="me-2 align-self-center"),
                        dbc.Col(
                            dcc.Dropdown(
                                id='acs-map-variable-dropdown',
                                options=MAP_VARIABLE_OPTIONS,
                                value=DEFAULT_MAP_VARIABLE,
                                clearable=False,
                                # style={'width': '100%'} # dcc.Dropdown 默认为块级，宽度由Col控制
                            ),
                            sm=12, md=8, lg=6, xl=4 # 控制下拉菜单的响应式宽度
                        ),

                    ], className="mb-3", align="center"), # mb-3 在下拉菜单和地图之间创建一些间距

                    dbc.Spinner(html.Div(id='acs-map-container')), # Plotly Graph 将加载到这里

                    html.Hr(className="my-4"), # 在地图和新表格之间添加一个分隔线

                    # --- 新增：显示数据分布的卡片和表格 ---
                    dbc.Card([
                        dbc.CardHeader(id='map-data-table-header', className="fw-bold"), # 表格标题将动态更新
                        dbc.CardBody(
                            dbc.Spinner(
                                html.Div(
                                    id='map-variable-data-table-container',
                                    # 为表格内容区域设置最大高度和滚动条
                                    style={"maxHeight": "450px", "overflowY": "auto"}
                                )
                            )
                        )
                    ], className="mt-3") # 卡片顶部加一些外边距
                ]))
            ]),
            dbc.Tab(label="Trend Analysis", tab_id="acs-tab-trend-analysis", children=[
                dbc.Card(dbc.CardBody([
                     html.P("Trend analysis placeholder. Implement charts here.")
                ]))
            ]),
        ],
        id="acs-page-tabs",
        active_tab="acs-tab-data-table",
        className="mb-3"
    )

    return dbc.Container(
        [
            dcc.Store(id='acs-selected-columns-store', data=DEFAULT_SELECTED_COLUMNS),
            # column_selection_card,
            tabs_component
        ],
        fluid=True,
    )
# # 定义要显示的列和它们的顺序 (与下载功能中的列保持一致或按需选择)
# DISPLAY_COLUMNS = [
#     "id", "state", "zipcode", "year", "population", "median_income",
#     "pct_bachelor", "pct_below_poverty", "pct_unemployed", "per_capita_income"
# ]

@callback(
    Output('acs-individual-column-checkboxes-container', 'children'),
    [Input('acs-select-all-columns-checkbox', 'value')]
)
def generate_column_checkboxes_in_dropdown(select_all_checked):
    if select_all_checked is None: # 初始回调时可能为None
        is_checked_and_disabled = True # 假设初始 "Select All" 为 true
    else:
        is_checked_and_disabled = select_all_checked

    checkbox_rows = []
    current_row_cols = []
    # 目标是每行大约3-4个复选框，可以根据屏幕大小调整 Col 的 width/md/lg 属性
    # 例如，md=4 表示在中等屏幕上一行最多3个 (12/4=3)
    # lg=3 表示在较大屏幕上一行最多4个 (12/3=4)
    # sm=6 表示在较小屏幕上一行最多2个 (12/6=2)
    # 您可以根据 POSSIBLE_SELECTABLE_COLUMNS 的数量和期望的显示效果调整
    cols_per_row_md = 3 # 在中等屏幕上，每行3个Col

    for i, col_name in enumerate(POSSIBLE_SELECTABLE_COLUMNS):
        pretty_label = col_name.replace("pct_", "% ").replace("_", " ").title()
        checkbox = dbc.Checkbox(
            id={'type': 'acs-dynamic-column-checkbox', 'index': col_name},
            label=pretty_label,
            value=is_checked_and_disabled, # 如果"All"选中，则此复选框也选中
            disabled=is_checked_and_disabled, # 如果"All"选中，则禁用此复选框
        )
        # 将每个复选框包裹在dbc.Col中，以实现栅格布局
        current_row_cols.append(dbc.Col(checkbox, md=12 // cols_per_row_md, className="mb-2"))

        if len(current_row_cols) == cols_per_row_md or (i == len(POSSIBLE_SELECTABLE_COLUMNS) - 1):
            checkbox_rows.append(dbc.Row(current_row_cols))
            current_row_cols = []

    return checkbox_rows

# 回调2: "Apply Column Selection" 按钮点击事件
@callback(
    Output('acs-selected-columns-store', 'data'),
    [Input('acs-apply-columns-button', 'n_clicks')],
    [State('acs-select-all-columns-checkbox', 'value'),
     State({'type': 'acs-dynamic-column-checkbox', 'index': dash.ALL}, 'id'), # 获取所有动态复选框的ID
     State({'type': 'acs-dynamic-column-checkbox', 'index': dash.ALL}, 'value')], # 获取所有动态复选框的value
    prevent_initial_call=True # 只有点击按钮时才执行
)
def update_selected_columns_store(n_clicks, select_all_checked, individual_cb_ids, individual_cb_values):
    if not n_clicks or n_clicks == 0:
        return dash.no_update

    selected_cols_final = list(FIXED_DISPLAY_COLUMNS) # 始终包含固定列

    if select_all_checked:
        selected_cols_final.extend(POSSIBLE_SELECTABLE_COLUMNS)
    else:
        # 遍历所有动态生成的复选框的状态
        if individual_cb_ids and individual_cb_values: # 确保列表不为空
            for i, cb_id_dict in enumerate(individual_cb_ids):
                column_name = cb_id_dict['index']
                if individual_cb_values[i]: # 如果该复选框被选中
                    if column_name not in selected_cols_final:
                        selected_cols_final.append(column_name)

    # 去重并保持顺序 (主要是为了POSSIBLE_SELECTABLE_COLUMNS部分)
    seen = set(FIXED_DISPLAY_COLUMNS)
    unique_selectable = []
    if select_all_checked:
        for col in POSSIBLE_SELECTABLE_COLUMNS:
            if col not in seen:
                unique_selectable.append(col)
                seen.add(col)
    else:
        if individual_cb_values and individual_cb_ids:
             for i, cb_id_dict in enumerate(individual_cb_ids):
                column_name = cb_id_dict['index']
                if individual_cb_values[i]:
                     if column_name not in seen:
                        unique_selectable.append(column_name)
                        seen.add(column_name)

    return FIXED_DISPLAY_COLUMNS + unique_selectable


# 回调3: 更新 DataTable (监听列选择、分页、排序、标签页激活)
@callback(
    [Output('acs-datatable', 'data'),
     Output('acs-datatable', 'page_count'),
     Output('acs-datatable', 'columns')],
    [Input('acs-page-tabs', 'active_tab'), # 当Data Table标签页被激活时
     Input('acs-datatable', 'page_current'),
     Input('acs-datatable', 'page_size'),
     Input('acs-datatable', 'sort_by'),
     Input('acs-selected-columns-store', 'data')] # 当选择的列更新时
)
def update_datatable_data(active_tab_id, page_current, page_size, sort_by, selected_columns_from_store):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # 设定一个默认的列列表，以防 selected_columns_from_store 为空或 None
    # （例如，在应用刚加载，"Apply"按钮还未被点击，且Store未被正确初始化时）
    selected_columns = selected_columns_from_store
    if not selected_columns:
        selected_columns = DEFAULT_SELECTED_COLUMNS # 使用默认的全选列

    # 定义DataTable的列结构
    datatable_columns = [{"name": col.replace("pct_", "% ").replace("_", " ").title(), "id": col} for col in selected_columns]

    if active_tab_id != "acs-tab-data-table":
        return [], 1, datatable_columns # 返回空数据和默认分页，但保持列结构

    # 1. 获取总行数
    # TODO: 如果未来加入基于列内容的筛选，这里的COUNT(*)也需要相应调整
    count_query = "SELECT COUNT(*) FROM public.acs_data;"
    df_count = fetch_data(count_query)

    if df_count is None or df_count.empty:
        return [], 1, datatable_columns
    total_rows = df_count.iloc[0,0]

    if total_rows == 0:
        return [], 1, datatable_columns

    page_count = math.ceil(total_rows / page_size) if page_size > 0 else 1

    # 确保 page_current 在有效范围内
    page_current = max(0, min(page_current, page_count -1 if page_count > 0 else 0) )


    # 2. 构建数据查询SQL (包括排序和分页)
    offset = page_current * page_size

    order_by_clause = "ORDER BY \"year\" DESC, \"state\" ASC, \"zipcode\" ASC" # 默认排序，注意列名加引号
    if sort_by:
        orders = []
        for s_col in sort_by:
            col_name = s_col['column_id']
            direction = "DESC" if s_col['direction'] == 'desc' else "ASC"
            if col_name in selected_columns: # 确保只按选中的列排序
                orders.append(f'"{col_name}" {direction}') # 给列名加引号以防关键字或特殊字符
        if orders:
            order_by_clause = "ORDER BY " + ", ".join(orders)

    # 确保选中的列名在SQL中是安全的 (例如，通过加引号)
    safe_selected_columns_sql = ", ".join([f'"{col}"' for col in selected_columns])
    if not safe_selected_columns_sql: # 如果没有可选列（不应该发生，因为有固定列）
        safe_selected_columns_sql = ", ".join([f'"{col}"' for col in FIXED_DISPLAY_COLUMNS])


    data_query = f"""
        SELECT {safe_selected_columns_sql}
        FROM public.acs_data
        {order_by_clause}
        LIMIT {page_size} OFFSET {offset};
    """
    df_page_data = fetch_data(data_query)

    data_for_datatable = []
    if df_page_data is not None and not df_page_data.empty:
        data_for_datatable = df_page_data.to_dict('records')
    elif total_rows > 0 : # 有数据但是当前页没取到（例如页码超出），返回空，让用户知道
        pass # data_for_datatable 已经是 []

    return data_for_datatable, page_count, datatable_columns


# 回调4: 下载数据 (监听下载按钮和选择的列)
@callback(
    Output("acs-download-dataframe", "data"),
    [Input("acs-download-button", "n_clicks")],
    [State("acs-selected-columns-store", "data")], # 使用 State 获取当前选中的列
    prevent_initial_call=True,
)
def download_acs_dataset(n_clicks, selected_columns_for_download):
    if not n_clicks:
        return dash.no_update

    columns_to_download = selected_columns_for_download
    if not columns_to_download: # 如果store为空，则下载所有默认列
        columns_to_download = DEFAULT_SELECTED_COLUMNS

    safe_columns_for_download_sql = ", ".join([f'"{col}"' for col in columns_to_download])
    if not safe_columns_for_download_sql:
        return dash.no_update # 不下载空数据

    query_all_acs_data = f"""
        SELECT {safe_columns_for_download_sql}
        FROM public.acs_data
        ORDER BY "year" DESC, "state" ASC, "zipcode" ASC;
    """
    df_all_acs = fetch_data(query_all_acs_data)

    if df_all_acs is None or df_all_acs.empty:
        print("Download request: No data to download or error fetching data.")
        # 可以考虑给用户一个提示，例如通过 dbc.Alert
        return dash.no_update

    return dcc.send_data_frame(df_all_acs.to_csv, f"acs_data_selected_columns.csv", index=False)


# 回调5: 更新地图 (监听标签页激活)

@callback(
    [Output('acs-map-container', 'children'),           # 地图组件
     Output('map-variable-data-table-container', 'children'), # 新：统计图组件
     Output('map-data-table-header', 'children')],      # 新：统计卡片的标题
    [Input('acs-page-tabs', 'active_tab'),
     Input('acs-map-variable-dropdown', 'value')]
)
def render_map_visualization_tab(active_tab_id, selected_variable):
    if active_tab_id != "acs-tab-map-viz":
        return dash.no_update, dash.no_update, dash.no_update

    # --- 默认返回值 ---
    empty_map_return = dbc.Alert("Map could not be generated.", color="info", className="m-4")
    empty_stats_return = html.Div("No data available for statistical plots.", className="text-center text-muted p-3")
    default_stats_header = "Variable Statistics"

    if not selected_variable: # 处理 selected_variable 可能为空的情况
        selected_variable = DEFAULT_MAP_VARIABLE # 假定 DEFAULT_MAP_VARIABLE 已定义
    if not selected_variable or selected_variable not in POSSIBLE_SELECTABLE_COLUMNS:
        alert_msg = dbc.Alert(f"Invalid map variable '{selected_variable}' selected.", color="danger")
        return alert_msg, empty_stats_return, default_stats_header
    
    # --- Mapbox Token, GeoJSON 加载, 数据获取和准备 (与您之前的代码一致) ---
    mapbox_access_token = os.getenv("MAPBOX_ACCESS_TOKEN")
    # mapbox_access_token = "pk.YOURTOKEN" # 本地测试
    if not mapbox_access_token or mapbox_access_token == "pk.YOURTOKEN": # 请替换
        alert_msg = dbc.Alert(
            [html.H5("Mapbox Access Token缺失", className="alert-heading"), html.P(["无法加载地图..."])],
            color="danger", className="m-4"
        )
        return alert_msg, empty_stats_return, default_stats_header

    if geojson_data_ca_zcta is None: # 假定 geojson_data_ca_zcta 在全局加载
        alert_msg = dbc.Alert("GeoJSON map data failed to load.", color="danger", className="m-4")
        return alert_msg, empty_stats_return, default_stats_header

    safe_sql_variable_name = f'"{selected_variable}"'
    query = f"""
        WITH LatestYearData AS (
            SELECT zipcode, {safe_sql_variable_name} AS "value_to_map", state,
                   ROW_NUMBER() OVER(PARTITION BY zipcode ORDER BY year DESC) as rn
            FROM public.acs_data
            WHERE {safe_sql_variable_name} IS NOT NULL AND state = '6'
        )
        SELECT zipcode, "value_to_map" FROM LatestYearData WHERE rn = 1;
    """
    df_map_data = fetch_data(query)

    selected_variable_label = selected_variable.replace('_',' ').title()
    if 'MAP_VARIABLE_OPTIONS' in globals(): # 确保 MAP_VARIABLE_OPTIONS 已定义
        for opt in MAP_VARIABLE_OPTIONS:
            if opt['value'] == selected_variable:
                selected_variable_label = opt['label']
                break
    
    stats_header_text = f"Statistics for: {selected_variable_label}" # 动态统计卡片标题

    if df_map_data is None or df_map_data.empty:
        alert_msg = dbc.Alert(f"No data found for '{selected_variable_label}' to display.", color="warning", className="m-4")
        return alert_msg, empty_stats_return, stats_header_text

    df_map_data['zipcode'] = df_map_data['zipcode'].astype(str)
    df_map_data['value_to_map'] = pd.to_numeric(df_map_data['value_to_map'], errors='coerce')
    df_map_data.dropna(subset=['value_to_map'], inplace=True)

    if df_map_data.empty:
        alert_msg = dbc.Alert(f"No valid data for '{selected_variable_label}' after cleaning.", color="warning", className="m-4")
        return alert_msg, empty_stats_return, stats_header_text

    # --- 创建Choropleth Mapbox图形 (与您之前的代码一致) ---
    map_graph_component = empty_map_return # Default
    try:
        hover_data_format_str = ':.1f'
        if "pct_" in selected_variable: hover_data_format_str = ':.1f}%'
        elif "income" in selected_variable or "median_income" in selected_variable: hover_data_format_str = '$,.0f'
        elif selected_variable in ["population", "year"]: hover_data_format_str = ',.0f'

        fig_map = px.choropleth_mapbox(
            df_map_data, geojson=geojson_data_ca_zcta, locations='zipcode',
            featureidkey='properties.ZCTA5CE20', color='value_to_map',
            color_continuous_scale="YlOrRd", mapbox_style="light",
            zoom=5.2, center={"lat": 37.2, "lon": -119.5}, opacity=0.7,
            labels={'value_to_map': selected_variable_label},
            hover_name='zipcode',
            hover_data={'value_to_map': hover_data_format_str, 'zipcode': False}
        )
        fig_map.update_layout(
            margin={"r":5,"t":5,"l":5,"b":5}, mapbox_accesstoken=mapbox_access_token,
            coloraxis_colorbar_title_text=selected_variable_label
        )
        map_graph_component = dcc.Graph(figure=fig_map, style={'width': '100%', 'height': '70vh'})
    except Exception as e:
        print(f"Error creating choropleth_mapbox for variable {selected_variable}: {e}")
        map_graph_component = dbc.Alert(f"Error creating map: {str(e)}", color="danger")
        # 如果地图创建失败，也返回空的统计图和对应的标题
        return map_graph_component, empty_stats_return, stats_header_text

    # --- 创建统计图 ---
    stats_plots_component = empty_stats_return # Default
    if not df_map_data.empty: # 再次确认，因为dropna可能使其变空
        try:
            # 1. 直方图 (Histogram)
            fig_hist = px.histogram(
                df_map_data,
                x="value_to_map",
                labels={'value_to_map': ''}, # X轴标签可以留空或设为变量名
                nbins=30, # 可根据数据调整
                marginal="rug" # 可选，在边缘显示数据点
            )
            fig_hist.update_layout(
                title_text=f"Distribution (Histogram)", title_x=0.5, title_font_size=15,
                margin=dict(t=40, b=20, l=20, r=20), # 紧凑边距
                bargap=0.1,
                yaxis_title="Frequency"
            )

            # 2. 箱线图 (Box Plot)
            fig_box = px.box(
                df_map_data,
                y="value_to_map",
                points="outliers", # "all", False, "outliers"
                notched=True, # 可选
                labels={'value_to_map': ''} # Y轴标签可以留空
            )
            fig_box.update_layout(
                title_text=f"Distribution (Box Plot)", title_x=0.5, title_font_size=15,
                margin=dict(t=40, b=20, l=20, r=20) # 紧凑边距
            )

            stats_plots_component = dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_hist, config={'displayModeBar': False}), md=6),
                dbc.Col(dcc.Graph(figure=fig_box, config={'displayModeBar': False}), md=6)
            ])
        except Exception as e:
            print(f"Error creating statistical plots for {selected_variable}: {e}")
            stats_plots_component = dbc.Alert(f"Error generating statistics plots: {str(e)}", color="warning")

    return map_graph_component, stats_plots_component, stats_header_text