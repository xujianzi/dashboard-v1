# dashboard_project/pages/acs_data.py
import dash
from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from utils.db_utils import fetch_data
import math
from dash import dash_table
import json
import os
import plotly.express as px # <--- 新增 Plotly Express
import copy # For deepcopying GeoJSON

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
    "id", "state", "county", "city","zipcode", "year", "pct_less_than_9th_grade", "pct_high_school",
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

FIXED_DISPLAY_COLUMNS = ['id', 'state', 'county', 'city', 'zipcode', 'year'] # 这些列总是显示且不可选
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
# --- 加载 全国 ZCTA GeoJSON 数据 ---
GEOJSON_US_FILE_PATH = os.path.join("data", "zcta_us_simplify.json") # 新的GeoJSON文件路径
geojson_us_data = None # 重命名变量以区分
try:
    with open(GEOJSON_US_FILE_PATH, 'r') as f:
        geojson_us_data = json.load(f)
    print("US ZCTA GeoJSON loaded successfully.")
except FileNotFoundError:
    print(f"ERROR: US ZCTA GeoJSON file not found at '{os.path.abspath(GEOJSON_US_FILE_PATH)}'.")
except json.JSONDecodeError:
    print(f"ERROR: Could not decode US ZCTA GeoJSON file from '{GEOJSON_US_FILE_PATH}'.")




def layout():
    # --- 列选择卡片 ---
    filter_and_column_card  = dbc.Card([
        dbc.CardHeader("Data Filters & Column Selection"),
        dbc.CardBody([
            # --- 新增筛选器 ---
            dbc.Label("Filter Data By:", className="fw-bold"),
            dbc.Row([
                dbc.Col(dbc.Label("Year(s):"), width=12, sm=2, className="text-sm-end"),
                dbc.Col(
                    dcc.Dropdown(
                        id='acs-year-filter-dropdown',
                        options=[{'label': str(y), 'value': y} for y in range(2016, 2023 + 1)], # 2016 到 2023
                        multi=True,
                        placeholder="Select year(s)..."
                    ),
                    sm=10
                )
            ], className="mb-2 align-items-center"),
            dbc.Row([
                dbc.Col(dbc.Label("State(s):"), width=12, sm=2, className="text-sm-end"),
                dbc.Col(
                    dcc.Dropdown(id='acs-state-filter-dropdown', multi=True, placeholder="Select state(s)..."),
                    sm=10
                )
            ], className="mb-2 align-items-center"),
            dbc.Row([
                dbc.Col(dbc.Label("County(ies):"), width=12, sm=2, className="text-sm-end"),
                dbc.Col(
                    dcc.Dropdown(
                        id='acs-county-filter-dropdown', 
                        multi=True, 
                        searchable=True,
                        placeholder="Select county(ies)..."),
                        sm=10
                )
            ], className="mb-3 align-items-center"),
            html.Hr(),

            # --- 列选择 (与之前类似) ---
            dbc.Label("Select Columns for Table:", className="fw-bold"),
            dbc.Row([
                dbc.Col(
                    dbc.Checkbox(id="acs-select-all-columns-checkbox", label="Select All Displayable Variables", value=True),
                    width=12, className="mb-2"
                ),
            ]),
            dbc.DropdownMenu(
                label="Choose Variables from List...",
                id="acs-column-select-dropdown", # 这个ID似乎没在回调中使用，主要是视觉容器
                color="light", className="mb-3 d-block",
                children=[
                    html.Div(
                        id="acs-individual-column-checkboxes-container", # 复选框会在这里生成
                        style={"padding": "1rem", "maxHeight": "250px", "overflowY": "auto", "minWidth": "300px"}
                    )
                ],
            ),
            html.Div(
                # dbc.Button("Apply Filters & Columns", id="acs-apply-button", color="primary", n_clicks=0, className="w-100"),
                dbc.Button("Apply Filters & Columns", id="acs-apply-button", n_clicks=0, className="custom-gradient-button w-100"),
                className="d-grid gap-2" # 使按钮占据全部宽度
            )
        ])
    ], className="mb-4")

    # --- New Filter Card for Map Tab ---
    map_filters_card = dbc.Card([
        dbc.CardHeader("Configure Map View"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Year:", html_for="map-year-dropdown"),
                    dcc.Dropdown(id='map-year-dropdown', clearable=False, placeholder="Select Year") # Options populated by callback
                ], md=6, lg=3, className="mb-2 mb-lg-0"),
                dbc.Col([
                    dbc.Label("Variable:", html_for="acs-map-variable-dropdown"),
                    dcc.Dropdown(
                        id='acs-map-variable-dropdown', # Existing ID
                        options=MAP_VARIABLE_OPTIONS,
                        value=DEFAULT_MAP_VARIABLE,
                        clearable=False
                    )
                ], md=6, lg=3, className="mb-2 mb-lg-0"),
                dbc.Col([
                    dbc.Label("State(s):", html_for="map-state-dropdown"),
                    dcc.Dropdown(id='map-state-dropdown', multi=True, placeholder="Select State(s)") # Options populated
                ], md=6, lg=3, className="mb-2 mb-lg-0"),
                dbc.Col([
                    dbc.Label("County(ies):", html_for="map-county-dropdown"),
                    dcc.Dropdown(id='map-county-dropdown', multi=True, placeholder="Select County(ies)") # Options populated (cascading)
                ], md=6, lg=3, className="mb-2 mb-lg-0"),
            ], className="mb-3 align-items-end"), # align-items-end for button
            dbc.Button("Update Map & Stats", id="map-update-button", className="custom-gradient-button w-100", )
        ])
    ], className="mb-3")

    tabs_component = dbc.Tabs(
        [
            dbc.Tab(label="Data Table", tab_id="acs-tab-data-table", children=[
                
                dbc.Card(dbc.CardBody([
                    filter_and_column_card,
                    #html.Hr(),
                    html.Div([ # 下载按钮和表格的容器
                        # dbc.Button(
                        #     "Download Selected Data (CSV)", id="acs-download-button",
                        #     color="success", className="mt-2 mb-3"
                        # ),
                        dbc.Button(
                            "Download Selected Data (CSV)", id="acs-download-button",
                             className="custom-gradient-button mt-2 mb-3"
                        ),
                        dcc.Download(id="acs-download-dataframe"),
                        dbc.Spinner(
                            html.Div( # DataTable 的包裹 Div
                                dash_table.DataTable(
                                    id='acs-datatable',
                                    # columns, data 等将由回调填充
                                    page_action='custom', page_current=0, page_size=PAGE_SIZE_DT,
                                    sort_action='custom', sort_mode='multi', sort_by=[],
                                    style_table={'overflowX': 'auto'},
                                    style_cell={
                                        'minWidth': '100px', 'width': '150px', 'maxWidth': '180px',
                                        'overflow': 'hidden', 'textOverflow': 'ellipsis',
                                        'textAlign': 'left', 'padding': '5px'
                                    },
                                    style_header={
                                        'backgroundColor': 'rgb(230, 230, 230)',
                                        'fontWeight': 'bold', 'border': '1px solid grey'
                                    },
                                    style_data={'border': '1px solid grey'},
                                ),
                            ) # DataTable 包裹 Div 不需要 className="mt-0" 了，由父级控制
                        )
                    ])
                ]))
            ]),
            # dbc.Tab(label="Map Visualization", tab_id="acs-tab-map-viz", children=[
            #     dbc.Card(dbc.CardBody([
            #         # --- 新增：变量选择下拉菜单 ---
            #         dbc.Row([
            #             dbc.Col(dbc.Label("Select Variable:", html_for="acs-map-variable-dropdown"), width="auto", className="me-2 align-self-center"),
            #             dbc.Col(
            #                 dcc.Dropdown(
            #                     id='acs-map-variable-dropdown',
            #                     options=MAP_VARIABLE_OPTIONS,
            #                     value=DEFAULT_MAP_VARIABLE,
            #                     clearable=False,
            #                     # style={'width': '100%'} # dcc.Dropdown 默认为块级，宽度由Col控制
            #                 ),
            #                 sm=12, md=8, lg=6, xl=4 # 控制下拉菜单的响应式宽度
            #             ),

            #         ], className="mb-3", align="center"), # mb-3 在下拉菜单和地图之间创建一些间距

            #         dbc.Spinner(html.Div(id='acs-map-container')), # Plotly Graph 将加载到这里

            #         html.Hr(className="my-4"), # 在地图和新表格之间添加一个分隔线

            #         # --- 新增：显示数据分布的卡片和表格 ---
            #         dbc.Card([
            #             dbc.CardHeader(id='map-data-table-header', className="fw-bold"), # 表格标题将动态更新
            #             dbc.CardBody(
            #                 dbc.Spinner(
            #                     html.Div(
            #                         id='map-variable-data-table-container',
            #                         # 为表格内容区域设置最大高度和滚动条
            #                         style={"maxHeight": "450px", "overflowY": "auto"}
            #                     )
            #                 )
            #             )
            #         ], className="mt-3") # 卡片顶部加一些外边距
            #     ]))
            # ]),
            dbc.Tab(label="Map Visualization", tab_id="acs-tab-map-viz", children=[
                dbc.Card(dbc.CardBody([
                    map_filters_card, # Add the new filter card here
                    dbc.Spinner(html.Div(id='acs-map-container')), # Map Graph
                    html.Hr(className="my-4"),
                    dbc.Card([ # Card for statistics
                        dbc.CardHeader(id='map-stats-header', className="fw-bold"),
                        dbc.CardBody(dbc.Spinner(html.Div(id='map-stats-plots-container')))
                    ], className="mt-3")
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
            # applied-filters-store 的初始值需要更新，将 'cities' 键改为 'counties'
            dcc.Store(id='applied-filters-store', data={'years': [], 'states': [], 'counties': []}),
            dcc.Store(id='map-applied-filters-store', data={
                'year': None, # Or latest year by default
                'states': [],
                'counties': [],
                'variable': DEFAULT_MAP_VARIABLE
            }),
            tabs_component
        ],
        fluid=True,
    )
# # 定义要显示的列和它们的顺序 (与下载功能中的列保持一致或按需选择)
# DISPLAY_COLUMNS = [
#     "id", "state", "zipcode", "year", "population", "median_income",
#     "pct_bachelor", "pct_below_poverty", "pct_unemployed", "per_capita_income"
# ]
# 增回调函数来填充筛选器选项
@callback(
    Output('acs-state-filter-dropdown', 'options'),
    Input('acs-page-tabs', 'active_tab') # 确保仅在相关标签页加载时触发
)
def populate_state_dropdown_options(active_tab):
    if active_tab == 'acs-tab-data-table':
        try:
            # 改用新的表名 acs_data_all
            df_states = fetch_data("SELECT DISTINCT state FROM public.acs_data_all WHERE state IS NOT NULL ORDER BY state;")
            if df_states is not None and not df_states.empty:
                return [{'label': str(s), 'value': str(s)} for s in df_states['state']]
        except Exception as e:
            print(f"Error populating state filter options: {e}")
    return []

@callback(
    Output('acs-county-filter-dropdown', 'options'), # Output ID 修改
    [Input('acs-page-tabs', 'active_tab'),
     Input('acs-state-filter-dropdown', 'value')] # 仍然可以根据州级联筛选县
)
def populate_county_dropdown_options(active_tab, selected_states): # 函数名修改
    if active_tab == 'acs-tab-data-table':
        try:
            # 查询 county 列，表名为 acs_data_all
            query = "SELECT DISTINCT county FROM public.acs_data_all WHERE county IS NOT NULL"
            if selected_states:
                safe_states_tuple = tuple(str(s).replace("'", "''") for s in selected_states)
                if len(safe_states_tuple) == 1:
                    query += f" AND state = '{safe_states_tuple[0]}'"
                else:
                    query += f" AND state IN {str(safe_states_tuple)}"

            query += " ORDER BY county LIMIT 1000;" # 限制数量，或者您可以移除LIMIT

            df_counties = fetch_data(query) # 修改变量名
            if df_counties is not None and not df_counties.empty:
                return [{'label': str(c), 'value': str(c)} for c in df_counties['county']]
        except Exception as e:
            print(f"Error populating county filter options: {e}") # 修改错误信息
    return []

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

# 回调2: "修改“应用”按钮的回调函数, 此回调现在将同时处理筛选器和列选择。
@callback(
    [Output('acs-selected-columns-store', 'data'),  # 存储选中的列
     Output('applied-filters-store', 'data')],      # 存储应用的筛选器
    [Input('acs-apply-button', 'n_clicks')],        # ID 已更改
    [State('acs-select-all-columns-checkbox', 'value'),
     State({'type': 'acs-dynamic-column-checkbox', 'index': dash.ALL}, 'id'),
     State({'type': 'acs-dynamic-column-checkbox', 'index': dash.ALL}, 'value'),
     State('acs-year-filter-dropdown', 'value'),    # 新增 State
     State('acs-state-filter-dropdown', 'value'),   # 新增 State
     State('acs-county-filter-dropdown', 'value')]    # 新增 State
)
def update_stores_on_apply(n_clicks,
                           select_all_cols_checked, individual_cb_ids, individual_cb_values,
                           selected_years, selected_states, selected_counties):
    if not n_clicks or n_clicks == 0:
        return dash.no_update, dash.no_update

    # --- 处理列选择 (与之前的 update_selected_columns_store 逻辑相同) ---
    selected_cols_final = list(FIXED_DISPLAY_COLUMNS)
    if select_all_cols_checked:
        selected_cols_final.extend(POSSIBLE_SELECTABLE_COLUMNS)
    else:
        if individual_cb_ids and individual_cb_values:
            for i, cb_id_dict in enumerate(individual_cb_ids):
                column_name = cb_id_dict['index']
                if individual_cb_values[i] and column_name not in selected_cols_final:
                    selected_cols_final.append(column_name)
    # 去重
    final_columns_for_store = list(dict.fromkeys(selected_cols_final))


    # --- 处理筛选条件 ---
    filters_data = {
        'years': selected_years if selected_years else [], #确保是列表
        'states': selected_states if selected_states else [],
        'counties': selected_counties if selected_counties else [] # 键名和变量名修改
    }

    return final_columns_for_store, filters_data

# --- 辅助函数：构建WHERE子句 ---
def build_where_clause(filters_dict):
    conditions = ["1=1"] # 始终为真，方便后续AND连接
    # params = {} # 如果使用参数化查询

    if filters_dict.get('years'):
        year_list = filters_dict['years']
        if year_list:
            year_tuple = tuple(map(int, year_list)) # 年份是整数
            if len(year_tuple) == 1:
                conditions.append(f"\"year\" = {year_tuple[0]}")
            else:
                conditions.append(f"\"year\" IN {year_tuple}")
    
    if filters_dict.get('states'):
        state_list = filters_dict['states']
        if state_list:
            # 对字符串列表进行处理以适配SQL IN子句，并做基本SQL注入防范
            safe_state_list = [str(s).replace("'", "''") for s in state_list]
            state_tuple_sql = "('" + "', '".join(safe_state_list) + "')"
            conditions.append(f"\"state\" IN {state_tuple_sql}")

    # --- 将 City 筛选逻辑修改为 County ---
    if filters_dict.get('counties'): # 键名修改
        county_list = filters_dict['counties'] # 变量名修改
        if county_list:
            safe_county_list = [str(c).replace("'", "''") for c in county_list] # 变量名修改
            county_tuple_sql = "('" + "', '".join(safe_county_list) + "')" # 变量名修改
            conditions.append(f"\"county\" IN {county_tuple_sql}") # SQL列名修改
            
    return " AND ".join(conditions)

# 回调3: 更新 DataTable (监听列选择、分页、排序、标签页激活)
# --- 更新 DataTable 的回调 ---
@callback(
    [Output('acs-datatable', 'data'),
     Output('acs-datatable', 'page_count'),
     Output('acs-datatable', 'columns')],
    [Input('acs-page-tabs', 'active_tab'),
     Input('acs-datatable', 'page_current'),
     Input('acs-datatable', 'page_size'),
     Input('acs-datatable', 'sort_by'),
     Input('acs-selected-columns-store', 'data'), # 列选择
     Input('applied-filters-store', 'data')]      # 新增：筛选条件
)
def update_datatable_data(active_tab_id, page_current, page_size, sort_by, 
                          selected_columns_from_store, applied_filters):
    # ... (selected_columns 和 datatable_columns 的处理与之前类似) ...
    selected_columns = selected_columns_from_store if selected_columns_from_store else DEFAULT_SELECTED_COLUMNS
    datatable_columns = [{"name": col.replace("pct_", "% ").replace("_", " ").title(), "id": col} for col in selected_columns]

    if active_tab_id != "acs-tab-data-table":
        return [], 1, datatable_columns

    current_filters = applied_filters if applied_filters else {}
    # print(f"DEBUG: Applied filters received by DataTable callback: {current_filters}") # 打印应用的筛选器
    # 构建 WHERE 子句
    where_clause = build_where_clause(applied_filters if applied_filters else {})

    # 1. 获取总行数 (基于筛选条件)
    count_query = f"SELECT COUNT(*) FROM public.acs_data_all WHERE {where_clause};"

    # print(f"DEBUG: DataTable COUNT Query SQL: {count_query}") # <--- 打印COUNT查询

    df_count = fetch_data(count_query)
    # ... (处理 df_count 为空或 total_rows 为0的情况，与之前类似) ...
    total_rows = df_count.iloc[0,0] if df_count is not None and not df_count.empty else 0
    if total_rows == 0:
        return [], 1, datatable_columns

    page_count = math.ceil(total_rows / page_size) if page_size > 0 else 1
    page_current = max(0, min(page_current, page_count - 1 if page_count > 0 else 0))
    offset = page_current * page_size

    # 2. 构建数据查询SQL (包括排序、分页和筛选)
    order_by_clause = "ORDER BY \"year\" DESC, \"state\" ASC, \"zipcode\" ASC" # 默认
    if sort_by: # 处理排序
        orders = [f'"{s_col["column_id"]}" {"DESC" if s_col["direction"] == "desc" else "ASC"}' 
                  for s_col in sort_by if s_col["column_id"] in selected_columns]
        if orders: order_by_clause = "ORDER BY " + ", ".join(orders)
    
    safe_selected_columns_sql = ", ".join([f'"{col}"' for col in selected_columns])
    if not safe_selected_columns_sql: safe_selected_columns_sql = ", ".join([f'"{col}"' for col in FIXED_DISPLAY_COLUMNS])

    data_query = f"""
        SELECT {safe_selected_columns_sql}
        FROM public.acs_data_all
        WHERE {where_clause}
        {order_by_clause}
        LIMIT {page_size} OFFSET {offset};
    """
    # print(f"DEBUG: DataTable DATA Query SQL: {data_query}") # <--- 打印数据获取查询
    df_page_data = fetch_data(data_query)
    # ... (处理 df_page_data 和返回 data_for_datatable, page_count, datatable_columns) ...
    data_for_datatable = df_page_data.to_dict('records') if df_page_data is not None and not df_page_data.empty else []
    return data_for_datatable, page_count, datatable_columns

# 回调4: 下载数据 (监听下载按钮和选择的列)
# --- 下载数据的回调 ---
@callback(
    Output("acs-download-dataframe", "data"),
    [Input("acs-download-button", "n_clicks")],
    [State("acs-selected-columns-store", "data"),
     State("applied-filters-store", "data")], # 新增 State
    prevent_initial_call=True,
)
def download_acs_dataset(n_clicks, selected_columns_for_download, applied_filters_for_download):
    if not n_clicks: return dash.no_update

    columns_to_download = selected_columns_for_download if selected_columns_for_download else DEFAULT_SELECTED_COLUMNS
    safe_columns_sql = ", ".join([f'"{col}"' for col in columns_to_download])
    if not safe_columns_sql: return dash.no_update

    where_clause_download = build_where_clause(applied_filters_for_download if applied_filters_for_download else {})

    query_all_data = f"""
        SELECT {safe_columns_sql}
        FROM public.acs_data_all
        WHERE {where_clause_download}
        ORDER BY "year" DESC, "state" ASC, "zipcode" ASC;
    """
    df_all_data = fetch_data(query_all_data)
    # ... (处理 df_all_data 为空的情况) ...
    if df_all_data is None or df_all_data.empty:
        print("Download: No data to download.")
        return dash.no_update # 或者可以下载一个空文件或提示信息

    return dcc.send_data_frame(df_all_data.to_csv, f"acs_filtered_data.csv", index=False)

# Populate Year dropdown for Map
@callback(
    [Output('map-year-dropdown', 'options'),
     Output('map-year-dropdown', 'value')],
    [Input('acs-page-tabs', 'active_tab')] # Trigger when map tab might become visible
)
def populate_map_year_dropdown(active_tab):
    if active_tab == "acs-tab-map-viz": # Only populate if relevant tab is active or about to be
        try:
            # Fetch distinct years from the new table
            df_years = fetch_data("SELECT DISTINCT year FROM public.acs_data_all ORDER BY year DESC;")
            if df_years is not None and not df_years.empty:
                years = df_years['year'].tolist()
                options = [{'label': str(y), 'value': y} for y in years]
                default_year = years[0] if years else None # Default to latest year
                return options, default_year
        except Exception as e:
            print(f"Error populating map year filter: {e}")
    return [], None

# Populate State dropdown for Map (similar to data table state dropdown but new ID)
@callback(
    Output('map-state-dropdown', 'options'),
    [Input('acs-page-tabs', 'active_tab')]
)
def populate_map_state_dropdown(active_tab):
    if active_tab == "acs-tab-map-viz":
        try:
            df_states = fetch_data("SELECT DISTINCT state FROM public.acs_data_all WHERE state IS NOT NULL ORDER BY state;")
            if df_states is not None and not df_states.empty:
                return [{'label': str(s), 'value': str(s)} for s in df_states['state']]
        except Exception as e:
            print(f"Error populating map state filter: {e}")
    return []

# Populate County dropdown for Map (cascading based on selected states)
@callback(
    [Output('map-county-dropdown', 'options'),
     Output('map-county-dropdown', 'value')], # Reset value when states change
    [Input('map-state-dropdown', 'value')],
    [State('acs-page-tabs', 'active_tab')]
)
def populate_map_county_dropdown(selected_states, active_tab):
    if active_tab != "acs-tab-map-viz" or not selected_states:
        return [], [] # No states selected, or tab not active, so no county options / clear selection

    try:
        # Ensure selected_states is a list of strings, suitable for SQL IN clause
        safe_states_sql_tuple = "('" + "', '".join([str(s).replace("'", "''") for s in selected_states]) + "')"
        query = f"SELECT DISTINCT county FROM public.acs_data_all WHERE county IS NOT NULL AND state IN {safe_states_sql_tuple} ORDER BY county LIMIT 1000;"
        
        df_counties = fetch_data(query)
        if df_counties is not None and not df_counties.empty:
            options = [{'label': str(c), 'value': str(c)} for c in df_counties['county']]
            return options, [] # Return options and reset selected counties
    except Exception as e:
        print(f"Error populating map county filter: {e}")
    return [], []

# This callback will read all map filter values and store them.
@callback(
    Output('map-applied-filters-store', 'data'),
    [Input('map-update-button', 'n_clicks')],
    [State('map-year-dropdown', 'value'),
     State('acs-map-variable-dropdown', 'value'), # Existing variable dropdown
     State('map-state-dropdown', 'value'),
     State('map-county-dropdown', 'value')],
    prevent_initial_call=True # Only run on button click
)
def store_map_filters_on_apply(n_clicks, year, variable, states, counties):
    if not n_clicks:
        return dash.no_update

    filters = {
        'year': year,
        'variable': variable,
        'states': states if states else [],
        'counties': counties if counties else []
    }
    return filters


# 计算 center zoom level
def calculate_map_view_from_geojson(geojson_features):
    """
    根据 GeoJSON feature 列表计算地图的中心点和合适的缩放级别。
    """
    if not geojson_features: # 如果没有地理特征，返回美国大陆的默认视图
        return {"lat": 39.8283, "lon": -98.5795}, 3

    all_lons = []
    all_lats = []

    def extract_coords_from_geometry(geometry):
        geom_type = geometry['type']
        coords = geometry['coordinates']
        if geom_type == 'Polygon':
            # coords 是环的列表，第一个环是外环
            for lon, lat in coords[0]:
                all_lons.append(lon)
                all_lats.append(lat)
        elif geom_type == 'MultiPolygon':
            # coords 是多边形列表，每个多边形又包含环的列表
            for polygon in coords:
                if polygon and polygon[0]: # 确保多边形和外环存在
                    for lon, lat in polygon[0]:
                        all_lons.append(lon)
                        all_lats.append(lat)
        # 可以根据需要添加对 Point, LineString 等其他几何类型的处理

    for feature in geojson_features:
        if 'geometry' in feature and feature['geometry']:
            extract_coords_from_geometry(feature['geometry'])
    
    if not all_lons or not all_lats: # 如果无法提取任何坐标
        return {"lat": 39.8283, "lon": -98.5795}, 3

    min_lon, max_lon = min(all_lons), max(all_lons)
    min_lat, max_lat = min(all_lats), max(all_lats)

    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2
    map_center = {"lat": center_lat, "lon": center_lon}

    # --- 估算缩放级别 (这是一个启发式方法，可能需要调整) ---
    delta_lon = max_lon - min_lon
    delta_lat = max_lat - min_lat

    # 如果边界框非常小（例如单个点或非常小的区域），设置一个较高的默认缩放级别
    if delta_lon < 0.001 and delta_lat < 0.001: # 阈值可以调整
        map_zoom = 12
    else:
        # 根据边界框的最大跨度（经度或纬度）估算
        # Mapbox的缩放级别大致遵循：zoom N 覆盖的世界宽度约为 360 / (2^N) 度
        # 反过来，zoom ≈ log2(360 / span_degrees) - C (C是一个调整常数)
        # 一个更简单的经验公式：
        max_span = max(delta_lon, delta_lat)
        if max_span <= 0: # 理论上不应发生，除非只有一个点且delta计算为0
            map_zoom = 12
        else:
            # 这个常数9需要根据您的数据和期望的“紧凑度”进行调整
            # 值越大，对于给定的span，地图会越放大
            map_zoom = math.floor(9 - math.log2(max_span))
            map_zoom = max(0, min(map_zoom, 18)) # 将缩放级别限制在合理范围内 (0-22)
    
    # print(f"Calculated View: Center={map_center}, Zoom={map_zoom}, SpanLon={delta_lon}, SpanLat={delta_lat}")
    return map_center, map_zoom

# 回调5: 更新地图 (监听标签页激活)
@callback(
    [Output('acs-map-container', 'children'),
     Output('map-stats-plots-container', 'children'),
     Output('map-stats-header', 'children')],
    [Input('acs-page-tabs', 'active_tab'),
     Input('map-applied-filters-store', 'data')] # 监听存储的筛选条件
)
def render_map_and_stats(active_tab_id, applied_filters):
    ctx = dash.callback_context
    triggered_input_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if active_tab_id != "acs-tab-map-viz":
        return dash.no_update, dash.no_update, dash.no_update

    # 初始提示信息
    map_placeholder = html.Div([
        html.P("Please select Year and Variable, then optionally State(s) and County(ies)."),
        html.P("Click 'Update Map & Stats' to view the visualization.")
    ], className="text-center p-4 text-muted mt-4")
    stats_placeholder = html.P("Statistics will appear here once the map is updated.", className="text-center text-muted p-3")
    default_stats_header = "Variable Statistics"

    # 检查 applied_filters 是否已由按钮有效填充
    # 如果是首次加载标签页，且 store 内容是初始默认值，则显示提示
    if not applied_filters or not applied_filters.get('year') or not applied_filters.get('variable'):
        # 如果触发的不是 store 的更新（例如，是标签页切换），并且基本筛选不全
        if triggered_input_id != 'map-applied-filters-store':
            return map_placeholder, stats_placeholder, default_stats_header
        # 如果是 store 更新了，但年份或变量仍然缺失（理论上按钮回调会保证它们有值）
        elif not applied_filters.get('year') or not applied_filters.get('variable'):
             return (dbc.Alert("Year and Variable selections are required. Please make your selections and click 'Update Map & Stats'.", color="warning", className="m-4"),
                    stats_placeholder, default_stats_header)


    selected_year = applied_filters.get('year')
    selected_variable = applied_filters.get('variable')
    selected_states = applied_filters.get('states', [])   # 默认为空列表
    selected_counties = applied_filters.get('counties', []) # 默认为空列表

    # 再次确认核心筛选条件是否存在
    if not selected_year or not selected_variable:
        # 这个情况理论上会被上面的逻辑捕获，但作为双重保险
        return map_placeholder, stats_placeholder, default_stats_header


    # --- Mapbox Token 和 GeoJSON 检查 (保持不变) ---
    mapbox_access_token = os.getenv("MAPBOX_ACCESS_TOKEN")
    # mapbox_access_token = "pk.YOURTOKEN" # for local testing
    if not mapbox_access_token or mapbox_access_token == "pk.YOURTOKEN": # 请替换占位符
        alert_msg = dbc.Alert([html.H5("Mapbox Access Token缺失", className="alert-heading"), html.P(["无法加载地图..."])], color="danger", className="m-4")
        return alert_msg, stats_placeholder, default_stats_header
    if geojson_us_data is None:
        alert_msg = dbc.Alert("US GeoJSON data failed to load.", color="danger", className="m-4")
        return alert_msg, stats_placeholder, default_stats_header

    # --- 构建动态SQL的WHERE子句 ---
    # 确保 selected_variable 是有效的，并且在SQL中安全使用
    if selected_variable not in POSSIBLE_SELECTABLE_COLUMNS: # (确保POSSIBLE_SELECTABLE_COLUMNS已正确定义)
        return dbc.Alert(f"Invalid variable selected: {selected_variable}", color="danger"), stats_placeholder, default_stats_header
    
    safe_sql_variable_name = f'"{selected_variable}"'
    where_conditions = [f"\"year\" = {int(selected_year)}", f"{safe_sql_variable_name} IS NOT NULL"]

    if selected_states: # 只有当用户选择了州时，才添加州筛选
        safe_states_sql = "('" + "', '".join([str(s).replace("'", "''") for s in selected_states]) + "')"
        where_conditions.append(f"\"state\" IN {safe_states_sql}")
        
        if selected_counties: # 只有当用户选择了州 *并且* 选择了县时，才添加县筛选
            safe_counties_sql = "('" + "', '".join([str(c).replace("'", "''") for c in selected_counties]) + "')"
            where_conditions.append(f"\"county\" IN {safe_counties_sql}")
    
    where_clause_sql = " AND ".join(where_conditions)

    # 获取数据
    query = f"""
        SELECT zipcode, {safe_sql_variable_name} AS "value_to_map"
        FROM public.acs_data_all  -- 确保表名是 acs_data_all
        WHERE {where_clause_sql};
    """
    df_map_data = fetch_data(query)

    selected_variable_label = next((opt['label'] for opt in MAP_VARIABLE_OPTIONS if opt['value'] == selected_variable), selected_variable.replace('_',' ').title())
    current_stats_header = f"Statistics for: {selected_variable_label} ({selected_year})"
    if selected_states:
        current_stats_header += f" in State(s): {', '.join(selected_states)}"
    if selected_counties:
         current_stats_header += f", County(ies): {', '.join(selected_counties)}"


    if df_map_data is None or df_map_data.empty:
        msg = f"No data found for '{selected_variable_label}' with the current filters (Year: {selected_year}"
        if selected_states: msg += f", States: {', '.join(selected_states)}"
        if selected_counties: msg += f", Counties: {', '.join(selected_counties)}"
        msg += ")."
        return dbc.Alert(msg, color="warning"), html.P(msg, className="text-center text-muted p-3"), current_stats_header
    
    # --- 数据准备和GeoJSON过滤 (与之前类似) ---
    df_map_data['zipcode'] = df_map_data['zipcode'].astype(str)
    df_map_data['value_to_map'] = pd.to_numeric(df_map_data['value_to_map'], errors='coerce')
    df_map_data.dropna(subset=['value_to_map'], inplace=True)

    if df_map_data.empty: # 清理后再次检查
        msg = f"No valid (numeric) data for '{selected_variable_label}' after cleaning for year {selected_year} and other filters."
        return dbc.Alert(msg, color="warning"), html.P(msg, className="text-center text-muted p-3"), current_stats_header
        
    filtered_geojson_features = []
    zctas_in_data = set(df_map_data['zipcode'])
    if geojson_us_data and 'features' in geojson_us_data:
        for feature in geojson_us_data['features']:
            if str(feature['properties'].get('ZCTA5CE20')) in zctas_in_data:
                filtered_geojson_features.append(feature)
    
    current_display_geojson = {"type": "FeatureCollection", "features": filtered_geojson_features}

    if not filtered_geojson_features:
        return dbc.Alert("No geographical ZCTA shapes match the filtered data. Ensure GeoJSON 'ZCTA5CE20' property aligns with 'zipcode' data.", color="info"), \
               html.P("No shapes to display.", className="text-center text-muted p-3"), current_stats_header

    # --- 创建Choropleth Mapbox图形 ---
    # ... (与您之前创建 fig_map 的代码一致, 使用 current_display_geojson, df_map_data)
    # ... (hover_data_format_str 逻辑)
    hover_data_format_str = ':.1f'
    if "pct_" in selected_variable: hover_data_format_str = ':.1f}%'
    elif "income" in selected_variable or "median_income" in selected_variable: hover_data_format_str = '$,.0f'
    elif selected_variable in ["population", "year"]: hover_data_format_str = ',.0f'

    # --- 计算地图的中心点和缩放级别 ---
    map_center_calc, map_zoom_calc = calculate_map_view_from_geojson(current_display_geojson.get("features", []))


    map_graph_component = html.Div("Error creating map.")
    try:
        fig_map = px.choropleth_mapbox(
            df_map_data, geojson=current_display_geojson, locations='zipcode',
            featureidkey='properties.ZCTA5CE20', color='value_to_map',
            color_continuous_scale="YlOrRd",
            mapbox_style="light",
            # 当显示全国数据时，移除固定的 center 和 zoom，让 mapbox_autofitbounds 工作
            # center 和 zoom 可以在没有州选择时设为美国中心，或完全依赖 autofit
            # zoom= (3.5 if not selected_states else 5.5), 
            # center= ({"lat": 39.8283, "lon": -98.5795} if not selected_states else None), # None 会让autofit生效
            opacity=0.7,
            labels={'value_to_map': selected_variable_label},
            hover_name='zipcode',
            hover_data={'value_to_map': hover_data_format_str, 'zipcode': False}
        )
        fig_map.update_layout(
            margin={"r":5,"t":5,"l":5,"b":5},
            mapbox_accesstoken=mapbox_access_token,
            mapbox={
                'center': map_center_calc, # 美国中心点
                'zoom': map_zoom_calc # 概览缩放级别
            },
            # mapbox_autofitbounds="locations", # 关键：让地图自动适应有数据的位置
            coloraxis_colorbar_title_text=selected_variable_label
        )
        map_graph_component = dcc.Graph(figure=fig_map, style={'width': '100%', 'height': '65vh'})
    except Exception as e:
        map_graph_component = dbc.Alert(f"Error creating map: {str(e)}", color="danger")
        return map_graph_component, stats_placeholder, current_stats_header
        
    # --- 创建统计图 (与之前一致, 使用筛选后的 df_map_data) ---
    stats_plots_component = html.Div("Error generating stats or no data for stats.")
    if not df_map_data.empty: # 确保有数据来绘制统计图
        try:
            fig_hist = px.histogram(df_map_data, x="value_to_map", labels={'value_to_map': ''}, nbins=30, marginal="rug")
            fig_hist.update_layout(title_text="Distribution (Histogram)", title_x=0.5, title_font_size=15, margin=dict(t=40, b=20, l=20, r=20), bargap=0.1, yaxis_title="Frequency")
            
            fig_box = px.box(df_map_data, y="value_to_map", points="outliers", notched=True, labels={'value_to_map': ''})
            fig_box.update_layout(title_text="Distribution (Box Plot)", title_x=0.5, title_font_size=15, margin=dict(t=40, b=20, l=20, r=20))
            
            stats_plots_component = dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_hist, config={'displayModeBar': False}), md=6),
                dbc.Col(dcc.Graph(figure=fig_box, config={'displayModeBar': False}), md=6)
            ])
        except Exception as e:
            stats_plots_component = dbc.Alert(f"Error generating statistics plots: {str(e)}", color="warning")

    return map_graph_component, stats_plots_component, current_stats_header