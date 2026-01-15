from typing import TypedDict
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import pandas as pd

from itertools import compress

from loguru import logger


class WeatherDataStore(TypedDict):
    id: list[int]
    x: list[float]
    y: list[list[float]]


class ExtendDataDict(TypedDict):
    x: list[list[float]]
    y: list[list[float]]


DB_URL = "sqlite+pysqlite:///../backend/database.db"
ENGINE = create_engine(DB_URL)

X_COLUMN = "timestamp"
Y_COLUMN_NAMES = [
    "temperature_k",
    "pressure_pa",
    "humidity_percent",
    "wind_speed_m_s",
    # "wind_deg",
    # "wind_gust_m_s"
]
Y_TITLES = {
    "temperature_k": "Temperature [K]",
    "pressure_pa": "Pressure [Pa]",
    "humidity_percent": "Humidity [%]",
    "wind_speed_m_s": "Wind Speed [m/s]",
    "wind_deg": "Wind Direction [deg]",
    "wind_gust_m_s": "Wind Gust [m/s]",
}


def create_empty_figure() -> go.Figure:
    fig = make_subplots(
        rows=len(Y_COLUMN_NAMES), cols=1, shared_xaxes=True, vertical_spacing=0.05
    )
    for i, col in enumerate(Y_COLUMN_NAMES):
        fig.add_trace(
            go.Scatter(
                x=[],
                y=[],
                name=Y_TITLES[col],
                mode="lines+markers",
            ),
            row=i + 1,
            col=1,
        )
        fig.update_yaxes(title_text=Y_TITLES[col], row=i + 1, col=1)
    fig.update_layout(
        # title_text="Live Weather Data",
        # legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center'),
        template="plotly_white"
    )
    return fig


def fetch_weather_data(start_id: int = 0) -> pd.DataFrame:
    table_name = "weather"
    x_column = "timestamp"
    y_columns = Y_COLUMN_NAMES
    x_min = "datetime('now', '-1 day')"  # last 1 day
    _query = f"""
    SELECT
        id,
        {x_column},
        {", ".join(y_columns)}
    FROM {table_name}
    WHERE 
        ({x_column} >= {x_min})
        AND (id > {start_id})
    ORDER BY {x_column} ASC
    """
    df = pd.read_sql_query(_query, ENGINE, parse_dates=[x_column])
    return df.drop_duplicates(subset=[x_column] + y_columns)


def df_to_weather_data_store(df: pd.DataFrame) -> WeatherDataStore:
    return {
        "id": df["id"].tolist(),
        "x": df[X_COLUMN].tolist(),
        "y": [df[col].tolist() for col in Y_COLUMN_NAMES],
    }


# --- 2. DASH APP SETUP ---
app = dash.Dash(__name__)
logger.info("Dash app initialized for live weather monitoring.")

app.layout = html.Div(
    [
        html.H2("Live Weather Monitoring", style={"textAlign": "center"}),
        # The Graph Component
        html.Div(
            dcc.Graph(
                id="live-weather-plot",
                figure=create_empty_figure(),
                style={"height": "80vh"},
            ),
        ),
        dcc.Store(
            id="weather-data-store",
            data=df_to_weather_data_store(fetch_weather_data(0)),
        ),
        # Interval Component: Fires every 5 minutes (300,000 milliseconds)
        dcc.Interval(id="interval-component", interval=60_000, n_intervals=0),
    ]
)


# --- 3. CALLBACK FOR UPDATES ---
@app.callback(
    Output("weather-data-store", "data"),
    [Input("interval-component", "n_intervals")],
    [State("weather-data-store", "data")],
)
def update_weather_data(n, store_data) -> WeatherDataStore:
    logger.debug(f"Updating data at interval {n}")
    # Connect to DB and fetch data
    # We use a context manager to ensure the connection closes cleanly
    try:
        # Querying all data. For very large datasets, consider LIMIT or a time window (WHERE timestamp > X)

        df = fetch_weather_data(0)
        logger.info(f"Fetched {len(df)} weather records from database.")
    except Exception as e:
        logger.error(f"Database error: {e}")
        return store_data  # return existing data on error

    return df_to_weather_data_store(df)


@app.callback(
    Output("live-weather-plot", "extendData"),
    [Input("weather-data-store", "data")],
    [State("live-weather-plot", "figure")],
)
def update_graph(
    store_data, existing_figure
) -> tuple[ExtendDataDict, list[int] | None, int | None]:
    logger.debug("Extending graph data.")

    # Identify timestamps that are new (not already in the graph)
    existing_timestamps = set(existing_figure["data"][0]["x"])
    is_new_timestamp = [x not in existing_timestamps for x in store_data["x"]]

    # Extract only new data points
    new_x_values = list(compress(store_data["x"], is_new_timestamp))
    new_y_values = [list(compress(y, is_new_timestamp)) for y in store_data["y"]]

    extend_data: ExtendDataDict = {
        "x": [new_x_values for _ in Y_COLUMN_NAMES],
        "y": new_y_values,
    }
    return extend_data  # No need to update layout


# --- 4. RUN SERVER ---
if __name__ == "__main__":
    logger.info("Starting Dash server in debug mode.")
    app.run(debug=True)
