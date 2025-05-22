# Comprehensive Data Dashboard

## Introduction

This project is a multi-page Dash dashboard designed for visualizing and interacting with various datasets. It provides analytical tools and visualizations for American Community Survey (ACS) data, COVID-19 statistics, and mobility patterns.

## Key Features

This dashboard offers a range of features to explore and analyze different datasets:

*   **Multi-Page Application**: Uses Dash Pages for a clean, organized, and navigable multi-page structure.
*   **Interactive Data Tables**: Most datasets can be viewed in interactive tables with sorting and pagination.
*   **Dynamic Visualizations**: Utilizes Plotly and Mapbox for creating insightful charts and maps.
*   **Filtering Capabilities**: Allows users to filter data based on various parameters like year, state, county, etc.

### 1. ACS Data Analysis (`pages/acs_data.py`)

The American Community Survey (ACS) page provides tools to explore socio-economic data across the United States:

*   **Comprehensive Data Table**: Display ACS data with the ability to:
    *   Filter by year(s), state(s), and county(ies).
    *   Dynamically select specific columns/variables for display.
    *   Download the selected data as a CSV file.
*   **Map Visualization**:
    *   Choropleth maps displaying selected ACS variables across U.S. ZCTAs (Zip Code Tabulation Areas).
    *   Filters for year, variable, state(s), and county(ies) to customize the map view.
    *   Interactive hover-over data for specific ZCTAs.
    *   Basic statistical plots (histogram, box plot) for the displayed variable on the map.
*   **Trend Analysis**:
    *   Line charts showing the trend of up to three selected ACS variables over different years.
    *   Filters for variable(s), state(s), and county(ies) to refine the trend analysis.

### 2. COVID-19 Statistics (`pages/covid_stat.py`)

This section is dedicated to visualizing COVID-19 related data:

*   **Data Table**: Displays COVID-19 case data. (Currently shows a limited sample).
*   **Map Visualization**: (Placeholder) Intended for geographical visualization of COVID-19 statistics.
*   **Trend Analysis**: (Placeholder) Intended for analyzing trends in COVID-19 data over time.

### 3. Mobility Patterns (`pages/mobility_patterns.py`)

This section focuses on the analysis of mobility data:

*   **Data Table**: (Placeholder/Incomplete) Intended for displaying mobility datasets.
*   **Map Visualization**: (Placeholder) Intended for visualizing mobility patterns geographically.
*   **Trend Analysis**: (Placeholder) Intended for understanding changes in mobility patterns over time.

## Project Structure

The project is organized into the following directories and key files:

```
.
├── app.py                 # Main Dash application setup and layout
├── requirements.txt       # Python dependencies for the project
├── README.md              # This file
├── assets/                # Directory for static assets (CSS, images)
│   └── custom_styles.css  # Custom CSS styles for the application
├── components/            # Reusable Dash components
│   └── sidebar.py         # Defines the navigation sidebar
├── data/                  # (Assumed) Directory for local data files like GeoJSON
│   └── zcta_us_simplify.json # GeoJSON for US ZCTA boundaries (used in ACS map)
├── pages/                 # Contains modules for each page of the dashboard
│   ├── acs_data.py        # Logic and layout for the ACS data page
│   ├── covid_stat.py      # Logic and layout for the COVID-19 statistics page
│   ├── mobility_patterns.py # Logic and layout for the mobility patterns page
│   └── ...                # Other page files
├── tests/                 # Contains tests for the application (structure may vary)
└── utils/                 # Utility functions and modules
    ├── acs_utils.py       # Utility functions specific to ACS data
    ├── db_utils.py        # Utilities for database connections and data fetching
    └── ...                # Other utility files
```

## Technical Stack

This project is built using the following main technologies:

*   **Dash**: Main framework for building the web application.
*   **Plotly**: For creating interactive charts and visualizations.
*   **Pandas**: For data manipulation and analysis.
*   **Dash Bootstrap Components**: For layout and styling using Bootstrap themes.
*   **Python**: Backend programming language.
*   **PostgreSQL (assumed)**: Database for storing and querying data (based on `db_utils.py` and query syntax).
*   **Mapbox**: Used for rendering map visualizations (specifically in the ACS data page).

## Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd <repository_directory_name>
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Make sure you have Python 3.x installed. Install the required packages using:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Mapbox Access Token:**
    The ACS data map visualization requires a Mapbox access token.
    *   Obtain a free token from [Mapbox](https://www.mapbox.com/).
    *   Set it as an environment variable named `MAPBOX_ACCESS_TOKEN`. You can do this by adding the following line to a `.env` file in the project root (ensure `.env` is in your `.gitignore`):
        ```
        MAPBOX_ACCESS_TOKEN='your_actual_mapbox_token'
        ```
        Alternatively, you can set it directly in your shell:
        ```bash
        export MAPBOX_ACCESS_TOKEN='your_actual_mapbox_token' # Linux/macOS
        # set MAPBOX_ACCESS_TOKEN=your_actual_mapbox_token    # Windows (cmd)
        # $env:MAPBOX_ACCESS_TOKEN="your_actual_mapbox_token" # Windows (PowerShell)
        ```

5.  **Database Setup:**
    The application fetches data from a database (likely PostgreSQL, based on `utils/db_utils.py` and SQL queries like `public.acs_data_all`).
    *   Ensure you have a running PostgreSQL instance.
    *   You will need to create the necessary database, tables (e.g., `acs_data_all`, `covid_cases_table`, `mobility_data_table`), and load the data.
    *   The database connection parameters (hostname, port, username, password, database name) are managed in `utils/db_utils.py`. You may need to modify this file or use environment variables if it's configured to read them, to match your database setup.
    *   The project also requires a GeoJSON file for ZCTA boundaries (`data/zcta_us_simplify.json`). Make sure this file is present in the specified path if you are using local GeoJSON data for maps.

    *(Note: Specific schema details and data loading scripts are not provided in this README and would need to be part of your database setup process.)*

## Running the Application

Once the setup is complete:

1.  Ensure your virtual environment is activated and all dependencies are installed.
2.  Make sure your database is running and accessible, and the `MAPBOX_ACCESS_TOKEN` environment variable is set.
3.  Run the Dash application using:
    ```bash
    python app.py
    ```
4.  Open your web browser and navigate to `http://127.0.0.1:8051` (or the address shown in your terminal).

## Contributing

Contributions to this project are welcome! If you would like to contribute, please consider the following:

*   Fork the repository.
*   Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
*   Make your changes and commit them with clear and descriptive messages.
*   Push your changes to your fork.
*   Submit a pull request to the main repository.

Please ensure your code adheres to any existing coding standards and include tests for new features if applicable.

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 The Comprehensive Data Dashboard Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
