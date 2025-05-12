import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json
from sqlalchemy import create_engine
from pathlib import Path

# === 加载数据 ===
db_url = "postgresql+psycopg2://postgres:wym45123@localhost:5432/dashboard"
engine = create_engine(db_url)
df = pd.read_sql("SELECT * FROM acs_data", engine)
df["zipcode"] = df["zipcode"].astype(str)

# 当前文件所在目录（无论你从哪里运行）
base_path = Path(__file__).resolve().parent
geojson_path = base_path.parent / "data" / "zcta_ca_simplify.json"
# === 加载 GeoJSON ===
with open(geojson_path, "r") as f:
    geojson = json.load(f)

# === 获取所有数值变量列 ===
exclude_cols = ['zipcode', 'state', 'lat', 'lng', 'geom', 'id', 'year']
numeric_cols = [col for col in df.select_dtypes(include='number').columns if col not in exclude_cols]
default_var = numeric_cols[0]

# === 创建 Dash App ===
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H3("📍 ZIP Code Choropleth Map (ACS Variables)"),

    html.Div([
        html.Label("选择变量以显示："),
        dcc.Dropdown(
            id="variable-dropdown",
            options=[{"label": col.replace("_", " ").title(), "value": col} for col in numeric_cols],
            value=default_var,
            clearable=False,
            style={"width": "400px"}
        )
    ]),

    dcc.Graph(id="choropleth-map", style={"height": "700px"})
])

# === 回调更新地图 ===
@app.callback(
    Output("choropleth-map", "figure"),
    Input("variable-dropdown", "value")
)
def update_map(selected_variable):
    vmin = df[selected_variable].quantile(0.01)
    vmax = df[selected_variable].quantile(0.99)

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE20",
        color=selected_variable,
        color_continuous_scale="Viridis",
        range_color=(vmin, vmax),
        mapbox_style="carto-positron",
        zoom=6,
        center={"lat": 36.5, "lon": -119.5},
        opacity=0.6
    )

    fig.update_layout(
        margin={"r": 0, "t": 20, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title=selected_variable.replace("_", " ").title(),
            tickformat=".1f",
            len=0.75,
            thickness=15
        )
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
