import sys
import os
# 这会把父目录（即 your_project/）加入模块查找路径，解决导入问题。
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import load_acs_metadata, query_acs_code, query_acs_codes

def main():
    metadata = load_acs_metadata()

    # 单个查询
    print(query_acs_code("B01001_001E", metadata))

    # 批量查询
    codes = [
    "B15003_001E",  # Total population 25 years and over
    "B15003_017E",  # High school graduate (includes equivalency)
    "B15003_018E",  # Some college, less than 1 year
    "B15003_019E",  # Some college, 1 or more years, no degree
    "B15003_020E",  # Associate's degree
    "B15003_021E",  # Associate's degree
    "B15003_022E",  # Bachelor's degree
    "B15003_023E",  # Master's degree
    "B15003_024E",  # Professional school degree
    "B15003_025E",   # Doctorate degree
]
    results = query_acs_codes(codes, metadata)

    for code, desc in results.items():
        print(f"{code}: {desc}")

if __name__ == "__main__":
    main()
