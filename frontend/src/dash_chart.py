import os
from itertools import compress
from typing import TypedDict

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sqlalchemy import create_engine
import pandas as pd

from loguru import logger


UPDATE_INTERVAL_MS = int(os.getenv("DASH_UPDATE_INTERVAL_MS", 60_000))  
DB_URL = os.getenv("DATABASE_URL")
ENGINE = create_engine(DB_URL)

TABLE_NAME = "v_wind_power"
UPDATE_COLUMN = "updated_at"
X_COLUMN = "timestamp"
Y_TITLES = {
    "temperature_c": "Temperature [°C]",
    "pressure_pa": "Pressure [Pa]",
    "humidity": "Humidity",
    "moist_air_density_kg_m3": "Moist Air Density [kg/m³]",
    "wind_speed_m_s": "Wind Speed [m/s]",
    "turbine_is_on": "Turbine is On",
    "max_specific_wind_power_watts_m2": "Max Specific Wind Power [W/m²]",
    # "temperature_k": "Temperature [K]",
    # "wind_deg": "Wind Direction [deg]",
    # "wind_gust_m_s": "Wind Gust [m/s]",
}
Y_COLUMN_NAMES = list(Y_TITLES.keys())


class WeatherDataStore(TypedDict):
    updated_at: list[str]
    x: list[str]
    y: list[list[float]]


class ExtendDataDict(TypedDict):
    x: list[list[str]]
    y: list[list[float]]


def create_empty_figure() -> go.Figure:
    """Initialize chart layout."""
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
                line_dash="dash",
                marker_symbol="circle",
                # mode="lines",
                # line_dash="solid",
                line_shape="hv",
            ),
            row=i + 1,
            col=1,
        )
        fig.update_yaxes(title_text=Y_TITLES[col], row=i + 1, col=1)
    fig.update_layout(
        # title_text="Live Weather Data",
        # legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center'),
        legend=dict(visible=False),
        template="plotly_white"
    )
    return fig


def fetch_weather_data(min_updated_at: str|None=None) -> pd.DataFrame:
    """Fetches only records that have been updated since 'min_updated_at'.

    If min_updated_at is None, fetches a default window (e.g., last 24h).
    """
    table_name = TABLE_NAME
    cols_to_select = [UPDATE_COLUMN, X_COLUMN] + Y_COLUMN_NAMES

    if min_updated_at is not None:
        where_clause = f"{UPDATE_COLUMN} > '{min_updated_at}'"
        logger.debug(f"Incremental fetch: {where_clause}")
    else:
        logger.info("Initial load: Fetching last 24h of data")
        where_clause = f"{X_COLUMN} >= datetime('now', '-1 day')"

    query = f"""
    SELECT {", ".join(cols_to_select)}
    FROM {table_name}
    WHERE {where_clause}
    ORDER BY {X_COLUMN} ASC
    """
    try:
        logger.debug(f"Executing SQL query:\n{query}")
        df = pd.read_sql_query(query, ENGINE, parse_dates=[X_COLUMN, UPDATE_COLUMN])
    except Exception as e:
        logger.error(f"Database error: {e}")
        return pd.DataFrame(columns=cols_to_select)
    return df.drop_duplicates(subset=[X_COLUMN] + Y_COLUMN_NAMES)


def append_to_store(current_store: WeatherDataStore, new_df: pd.DataFrame) -> WeatherDataStore:
    """Append new DataFrame rows to existing data store."""
    if new_df.empty:
        return current_store
    
    def extend_list(key, values):
        current_store[key].extend(values)

    extend_list("updated_at", new_df[UPDATE_COLUMN].dt.strftime("%Y-%m-%d %H:%M:%S%Z").tolist())
    extend_list("x", new_df[X_COLUMN].dt.strftime("%Y-%m-%d %H:%M:%S%Z").tolist())

    # Append Y columns (list of lists)
    for i, col in enumerate(Y_COLUMN_NAMES):
        current_store["y"][i].extend(new_df[col].tolist())

    return current_store


# --- DASH APP SETUP ---
app = dash.Dash(__name__)

# Initial empty state
initial_store: WeatherDataStore = {
    "id": [],
    "updated_at": [],
    "x": [],
    "y": [[] for _ in Y_COLUMN_NAMES],
}

logger.info("Dash app initialized for live weather monitoring.")

app.layout = html.Div(
    [
        html.H2("Live Weather Monitoring", style={"textAlign": "center"}),
        # The Graph Component
        html.Div(
            dcc.Graph(
                id="live-weather-plot",
                figure=create_empty_figure(),
                style={"height": "160vh"},
            ),
        ),
        dcc.Store(
            id="weather-data-store",
            data=initial_store,
            # data=df_to_weather_data_store(fetch_weather_data(0)),
        ),
        # Interval Component: Fires every 5 minutes (300,000 milliseconds)
        dcc.Interval(
            id="interval-component", 
            interval=UPDATE_INTERVAL_MS, 
            n_intervals=0
            ),
    ]
)


# --- CALLBACK FOR UPDATES ---
@app.callback(
    Output("weather-data-store", "data"),
    [Input("interval-component", "n_intervals")],
    [State("weather-data-store", "data")],
)
def update_weather_data(n, store_data: WeatherDataStore) -> WeatherDataStore:
    logger.debug(f"Updating data at interval {n}")
    last_updated_at = None
    if store_data["updated_at"]:
        last_updated_at = max(store_data["updated_at"])

    new_df = fetch_weather_data(min_updated_at=last_updated_at)

    if new_df.empty:
        logger.debug("No new data found.")
        return store_data

    logger.info(f"Fetched {len(new_df)} new records.")

    updated_data = append_to_store(store_data, new_df)
    return updated_data


@app.callback(
    Output("live-weather-plot", "extendData"),
    [Input("weather-data-store", "data")],
    [State("live-weather-plot", "figure")],
)
def update_graph(store_data: WeatherDataStore, existing_figure) -> ExtendDataDict:
    # or ExtendDataDict, Optional[list[int]] , Optional[int]
    logger.debug("Extending graph data.")
    if not store_data["x"]:
        return dash.no_update

    # Identify timestamps that are new (not already in the graph)
    try:
        existing_timestamps = set(existing_figure["data"][0]["x"])
    except (IndexError, KeyError):
        existing_timestamps = set()
    
    new_indices = [
        i for i, x_val in enumerate(store_data["x"])
        if x_val not in existing_timestamps
    ]

    if not new_indices:
        return dash.no_update
    
    logger.debug(f"Pushing {len(new_indices)} new points to graph.")

    # Extract the data subsets based on the new indices
    new_x = [store_data["x"][i] for i in new_indices]
    new_y = [
        [col_data[i] for i in new_indices] 
        for col_data in store_data["y"]
    ]

    return {
        "x": [new_x for _ in Y_COLUMN_NAMES],
        "y": new_y
    }


# --- RUN SERVER ---
if __name__ == "__main__":
    logger.info("Starting Dash server in debug mode.")
    app.run(debug=True)
