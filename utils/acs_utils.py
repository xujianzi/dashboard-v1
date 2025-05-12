import requests
import json
import os
from typing import Dict, List

# 默认设置
ACS_YEAR = 2018
ACS_DATASET = "acs/acs5"
# 在utils目录下创建cache子目录存放缓存文件
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
# 如果缓存目录不存在则创建
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
CACHE_FILE = os.path.join(CACHE_DIR, f"acs5_variables_{ACS_YEAR}_cache.json")

def load_acs_metadata(year: int = ACS_YEAR, dataset: str = ACS_DATASET) -> Dict[str, Dict[str, str]]:
    """
    下载并缓存 ACS 元数据 JSON；首次运行访问网络，后续使用缓存。
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        url = f"https://api.census.gov/data/{year}/{dataset}/variables.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("variables", {})
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return data
        else:
            raise Exception(f"下载 ACS 元数据失败，状态码: {response.status_code}")

def query_acs_code(code: str, metadata: Dict[str, Dict[str, str]]) -> str:
    """
    查询单个变量的描述（concept + label）。
    """
    var = metadata.get(code)
    if var:
        return f"{var.get('concept', '').strip()} - {var.get('label', '').strip()}"
    else:
        return "未找到该代码的描述"

def query_acs_codes(codes: List[str], metadata: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """
    批量查询多个变量代码，返回 {code: description} 字典。
    """
    return {code: query_acs_code(code, metadata) for code in codes}
