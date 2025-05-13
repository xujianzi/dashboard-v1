import os
import re
import json
import pandas as pd
from census import Census
from geoalchemy2 import WKTElement
from sqlalchemy import create_engine
from sqlalchemy.types import Float, Integer, Text
from geoalchemy2 import Geometry
from us import states 
from dotenv import load_dotenv 

# ========== 参数配置 ==========
load_dotenv()
API_KEY = os.getenv("ACS_API_KEY")
YEAR = 2018
STATE_FIPS = '06'  # California
EXCEL_PATH = "H:/GoogleDrive/Dissertation/dissertation-local/dissertation-Paper-#3/acs_data_version#2.xlsx"
JSON_PATH = "../data/acs_variable_definitions.json"
ZIP_LATLON_PATH = "../data/us_zip_lat_lon.csv"


# ========== 函数定义 ==========

def load_definition_table(json_path: str, excel_path: str) -> pd.DataFrame:
    """加载变量定义表，优先读取 JSON 缓存，否则从 Excel 导入并保存 JSON。"""
    if os.path.exists(json_path):
        print(f"🔁 读取缓存 JSON 文件: {json_path}")
        return pd.read_json(json_path)
    else:
        print(f"📥 读取 Excel 文件: {excel_path}")
        df_def = pd.read_excel(excel_path)
        df_def = df_def.dropna(subset=['Code'])
        df_def.to_json(json_path, orient="records", indent=2)
        print(f"✅ 已缓存为 JSON 文件: {json_path}")
    return df_def


def extract_variable_codes(code_series: pd.Series) -> list:
    """提取公式或代码中的所有原始 ACS 变量名。"""
    all_vars = set()
    for formula in code_series.dropna():
        found = re.findall(r'[BC]\d{5}_\d+E', formula)
        all_vars.update(found)
    print(f"🔁 提取公式或代码中的所有原始 ACS 变量名")
    return sorted(all_vars)

def enrich_with_zip_info(df: pd.DataFrame, zip_info_path: str) -> pd.DataFrame:
    """
    清洗 df，并根据 zip_info CSV 添加 city 和 state 信息。
    步骤：
    1. 重命名 'zip code tabulation area' 为 'zipcode'
    2. 如果 'state' 列存在，则删除
    3. 根据 zipcode 合并 zip_info 中的 city 和 state
    """
    # 重命名字段
    if 'zip code tabulation area' in df.columns:
        df = df.rename(columns={'zip code tabulation area': 'zipcode'})

    # 删除已有 state 列
    if 'state' in df.columns:
        df = df.drop(columns=['state'])

    # 加载 ZIP -> city/state 映射表
    zip_info = pd.read_csv(zip_info_path)
    zip_info.columns = zip_info.columns.str.lower()
    
    if not {'zip', 'county', 'city', 'state'}.issubset(zip_info.columns):
        raise ValueError("ZIP 映射表必须包含 'zip', 'city', 'state' 字段")

    zip_info['zip'] = zip_info['zip'].astype(str)
    df['zipcode'] = df['zipcode'].astype(str)

    # 合并
    df = df.merge(zip_info[['zip', 'county', 'city', 'state']], left_on='zipcode', right_on='zip', how='left')
    df.drop(columns=['zip'], inplace=True)

    return df



def download_acs_data(api_key: str, year: int, state_fips: str, var_codes: list) -> pd.DataFrame:
    """使用 Census API 下载指定变量的 ACS 数据(ZIP 级别)。"""
    c = Census(api_key)
    data = c.acs5.state_zipcode(
        fields=var_codes,
        state_fips=state_fips,
        zcta='*',
        year=year
    )
    df = pd.DataFrame(data)
    for var in var_codes:
        df[var] = pd.to_numeric(df[var], errors='coerce')

    return df

def download_acs_data_old(api_key: str, year: int, var_codes: list) -> pd.DataFrame:
    """
    下载全美所有州的 ACS ZIP 级别数据，并合并为一个 DataFrame。

    参数：
        api_key: Census API Key
        year: 年份（例如 2018, 2019）
        var_codes: 要请求的 ACS 变量代码列表

    返回：
        包含全美 ZIP 数据的 Pandas DataFrame
    """
    c = Census(api_key)
    all_dfs = []

    # 排除阿拉斯加、夏威夷、华盛顿特区、海外领地等
    excluded = {"AK", "HI", "DC", "PR", "VI", "GU", "MP", "AS"}

    # 获取大陆州的 State 对象列表
    continental_states = [s for s in states.STATES if s.abbr not in excluded]

    for state in states.STATES:
        state_fips = state.fips
        try:
            print(f"⬇ 正在下载 {state.name} ({state_fips}) 的数据...")
            data = c.acs5.state_zipcode(
                fields=var_codes,
                state_fips=state_fips,
                zcta='*',
                year=year
            )
            df = pd.DataFrame(data)
            for var in var_codes:
                df[var] = pd.to_numeric(df[var], errors='coerce')
            all_dfs.append(df)
        except Exception as e:
            print(f"❌ 无法下载 {state.name}（{state_fips}）: {e}")
            continue

    # 合并所有州的数据
    if all_dfs:
        df_all = pd.concat(all_dfs, ignore_index=True)
        return df_all
    else:
        print("⚠️ 未能成功下载任何州的数据。")
        return pd.DataFrame()


def calculate_custom_variables(df_raw: pd.DataFrame, df_def: pd.DataFrame) -> pd.DataFrame:
    """根据自定义公式计算衍生变量。"""
    def get_vars_from_formula(formula):
        return re.findall(r'[BC]\d{5}_\d+E', formula)

    def safe_eval_formula(df, formula, var_name):
        needed_vars = get_vars_from_formula(formula)
        missing = [v for v in needed_vars if v not in df.columns]
        if missing:
            print(f"⚠️ 跳过 {var_name}，缺失变量: {missing}")
            return None
        try:
            return df.eval(formula)
        except Exception as e:
            print(f"❌ 错误公式 {var_name}: {e}")
            return None

    df = df_raw.copy()
    for _, row in df_def.iterrows():
        var_name = row['Definition']
        formula = row['Code']
        result = safe_eval_formula(df, formula, var_name)
        if result is not None:
            df[var_name] = result
    print(f"🔁 根据自定义公式计算衍生变量")
    return df


def clean_and_rename_columns(df: pd.DataFrame, df_def: pd.DataFrame) -> pd.DataFrame:
    """重命名列并标准化字段格式。"""
    geo_cols = ['state', 'county', 'city', 'zipcode']
    custom_vars = df_def['Definition'].tolist()
    df = df[geo_cols + custom_vars]
    # df = df.rename(columns={'zip code tabulation area': 'zipcode'})
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace('%', 'pct', regex=False)
        .str.replace(' ', '_')
        .str.replace('-', '_')
    )
    print(f"🔁 重命名列并标准化字段格式")
    return df


def attach_zip_latlon_geom(df: pd.DataFrame, zip_latlon_csv_path: str) -> pd.DataFrame:
    """合并 ZIP 经纬度坐标，并创建 PostGIS 兼容的 geom 列。"""
    zip_coords = pd.read_csv(zip_latlon_csv_path)
    zip_coords.columns = zip_coords.columns.str.lower()

    if not {'zip', 'lat', 'lng'}.issubset(zip_coords.columns):
        raise ValueError("CSV 文件必须包含 'zip', 'lat', 'lng' 列")

    zip_coords['zip'] = zip_coords['zip'].astype(str)
    df['zipcode'] = df['zipcode'].astype(str)

    df = df.merge(zip_coords[['zip', 'lat', 'lng']], left_on='zipcode', right_on='zip', how='left')
    df.drop(columns=['zip'], inplace=True)

    df['geom'] = df.apply(
        lambda row: WKTElement(f"POINT({row['lng']} {row['lat']})", srid=4326)
        if pd.notnull(row['lat']) and pd.notnull(row['lng']) else None,
        axis=1
    )
    return df

def write_df_to_postgres(df, table_name, db_url):
    """
    将 DataFrame 写入 PostgreSQL 表（支持 PostGIS geom 列）

    参数:
        df: 包含数据的 DataFrame，必须包含 'geom' 列（GeoAlchemy WKTElement 类型）
        table_name: 目标表名，例如 'acs_data'
        db_url: SQLAlchemy 格式的连接字符串，例如 'postgresql+psycopg2://user:pwd@localhost:5432/db'
    """
    engine = create_engine(db_url)

    # 字段类型映射（可以根据实际数据再细化）
    dtype = {
        'zipcode': Text(),
        'state': Text(),
        'county': Text(),
        'city': Text(),
        'year': Integer(),
        'population': Integer(),
        'median_income': Float(),
        'per_capita_income': Float(),
        'geom': Geometry('POINT', srid=4326)
    }

    # 自动识别其余列为 Float 类型
    for col in df.columns:
        if col not in dtype and col not in ['geom']:
            dtype[col] = Float()

    # 写入数据库
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False,
        dtype=dtype,
        method='multi'
    )

    print(f"✅ 数据已成功写入 PostgreSQL 表 `{table_name}`")


# ========== 主流程 ==========
def main(year = 2016):
    # 1. 加载变量定义
    df_def = load_definition_table(JSON_PATH, EXCEL_PATH)

    # 2. 提取原始变量代码
    var_codes = extract_variable_codes(df_def['Code'])

    # 3. 下载原始 ACS 数据
    if year >= 2020:
        df_raw = download_acs_data(API_KEY, year, STATE_FIPS, var_codes)
    else:
        df_raw = download_acs_data_old(API_KEY, year, var_codes)

    df_enriched = enrich_with_zip_info(df_raw, "../data/us_zip_lat_lon.csv")
    # 4. 计算自定义指标
    df_final = calculate_custom_variables(df_enriched, df_def)
    # 5. 重命名、清洗列
    df_cleaned = clean_and_rename_columns(df_final, df_def)

    # 6. 附加经纬度与空间字段
    df_with_geom = attach_zip_latlon_geom(df_cleaned, ZIP_LATLON_PATH)

    # 7. 添加年份信息
    df_with_geom['year'] = year

    # 8. 保存结果
    db_url = "postgresql+psycopg2://postgres:wym45123@localhost:5432/dashboard"
    write_df_to_postgres(df_with_geom, table_name="acs_data_all", db_url=db_url)


if __name__ == "__main__":
    main()