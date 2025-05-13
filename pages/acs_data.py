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

FIXED_DISPLAY_COLUMNS = ['id', 'state', 'zipcode', 'year', 'city'] # 这些列总是显示且不可选
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
                dbc.Col(dbc.Label("City(ies):"), width=12, sm=2, className="text-sm-end"),
                dbc.Col(
                    dcc.Dropdown(
                        id='acs-city-filter-dropdown', 
                        multi=True, 
                        searchable=True,
                        placeholder="Select city(ies) (up to 1000 shown)..."),
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
                dbc.Button("Apply Filters & Columns", id="acs-apply-button", color="primary", n_clicks=0, className="w-100"),
                className="d-grid gap-2" # 使按钮占据全部宽度
            )
        ])
    ], className="mb-4")

    tabs_component = dbc.Tabs(
        [
            dbc.Tab(label="Data Table", tab_id="acs-tab-data-table", children=[
                
                dbc.Card(dbc.CardBody([
                    filter_and_column_card,
                    #html.Hr(),
                    html.Div([ # 下载按钮和表格的容器
                        dbc.Button(
                            "Download Selected Data (CSV)", id="acs-download-button",
                            color="success", className="mt-2 mb-3"
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
            dcc.Store(id='applied-filters-store', data={'years': [], 'states': [], 'cities': []}), # 新增Store存储筛选条件
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
    Output('acs-city-filter-dropdown', 'options'),
    [Input('acs-page-tabs', 'active_tab'),
     Input('acs-state-filter-dropdown', 'value')] # 级联：根据选中的州更新城市列表
)
def populate_city_dropdown_options(active_tab, selected_states):
    if active_tab == 'acs-tab-data-table':
        try:
            query = "SELECT DISTINCT city FROM public.acs_data_all WHERE city IS NOT NULL"
            if selected_states: # 如果选择了州，则根据州筛选城市
                # 构建 state IN ('state1', 'state2') 格式的SQL查询条件
                # 注意SQL注入风险，确保 selected_states 中的值是安全的或来自预定义列表
                safe_states_tuple = tuple(str(s).replace("'", "''") for s in selected_states) # 基本的SQL注入防范
                if len(safe_states_tuple) == 1:
                    query += f" AND state = '{safe_states_tuple[0]}'"
                else:
                    query += f" AND state IN {str(safe_states_tuple)}"
            
            # query += " ORDER BY city LIMIT 500;" # 限制城市数量以避免下拉列表过长
            query += " ORDER BY city;"
            
            df_cities = fetch_data(query)
            if df_cities is not None and not df_cities.empty:
                return [{'label': str(c), 'value': str(c)} for c in df_cities['city']]
        except Exception as e:
            print(f"Error populating city filter options: {e}")
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
     State('acs-city-filter-dropdown', 'value')]    # 新增 State
)
def update_stores_on_apply(n_clicks,
                           select_all_cols_checked, individual_cb_ids, individual_cb_values,
                           selected_years, selected_states, selected_cities):
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
        'cities': selected_cities if selected_cities else []
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

    if filters_dict.get('cities'):
        city_list = filters_dict['cities']
        if city_list:
            safe_city_list = [str(c).replace("'", "''") for c in city_list]
            city_tuple_sql = "('" + "', '".join(safe_city_list) + "')"
            conditions.append(f"\"city\" IN {city_tuple_sql}")
            
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
    print(f"DEBUG: Applied filters received by DataTable callback: {current_filters}") # 打印应用的筛选器
    # 构建 WHERE 子句
    where_clause = build_where_clause(applied_filters if applied_filters else {})

    # 1. 获取总行数 (基于筛选条件)
    count_query = f"SELECT COUNT(*) FROM public.acs_data_all WHERE {where_clause};"

    print(f"DEBUG: DataTable COUNT Query SQL: {count_query}") # <--- 打印COUNT查询

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
    print(f"DEBUG: DataTable DATA Query SQL: {data_query}") # <--- 打印数据获取查询
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