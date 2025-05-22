# 项目功能

本项目旨在实现以下功能：



## 项目结构：
```txt 
dashboard_project/
├── app.py                 # Main Dash app instantiation and server
├── index.py               # Main layout, URL routing, and core callbacks
├── requirements.txt       # Python dependencies
├── assets/                # For CSS, JS, images (Dash serves these automatically)
│   └── style.css          # Optional custom CSS
├── components/            # Reusable UI components
│   ├── __init__.py
│   └── sidebar.py         # Defines the sidebar layout and navigation
├── pages/                 # Directory for different page modules
│   ├── __init__.py
│   ├── acs_data_page.py
│   ├── covid_stats_page.py
│   └── mobility_patterns_page.py
│   # Add more page_name_page.py files here as needed
└── utils/                 # Utility functions
    ├── __init__.py
    └── db_utils.py        # Placeholder for database connection logic
```

## 1. ACS Code 查询

- **功能描述:** 根据用户提供的美国社区调查 (ACS) 代码，查询并显示该代码所代表的具体含义或变量描述。
- **实现状态:** 已完成
