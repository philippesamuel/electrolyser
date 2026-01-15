from loguru import logger
from prefect import flow, task
from config import settings
from clients.openweather import OpenWeatherClient

from db_models.weather import Weather
from database import create_db_and_tables

from sqlmodel import insert
from prefect_sqlalchemy import SqlAlchemyConnector


def main():
    create_db_and_tables()
    # etl_weather_data()
    etl_weather_data.serve(
        name="etl-weather-data",
        cron=f"*/{settings.WEATHER_UPDATE_INTERVAL_MINUTES} * * * *",  # every N minutes
        # cron=f"*/1 * * * *",  # every 1 minute for testing
    )


@flow
def etl_weather_data() -> None:
    block_name = "database-connector"
    client = OpenWeatherClient()
    weather_data = extract_weather_data(client)  # type: ignore[no-matching-overload]
    transformed_data = transform_weather_data(weather_data)
    load_weather_data(block_name, transformed_data)  # type: ignore[no-matching-overload]


@task
def extract_weather_data(client: OpenWeatherClient) -> Weather:
    api_response = client.fetch_current_weather_sync()
    weather_dict = {
        "timestamp": api_response.dt,
        "temperature_k": api_response.temp_k,
        "pressure_pa": api_response.pressure_hpa * 100,
        "humidity_percent": api_response.humidity,
        "dew_point_k": api_response.dew_point_k,
        "wind_speed_m_s": api_response.wind_speed_m_s,
        "wind_deg": api_response.wind_deg,
        "wind_gust_m_s": api_response.wind_gust_m_s,
    }
    weather_data = Weather.model_validate(weather_dict)
    return weather_data


@task
def transform_weather_data(weather_data: Weather) -> Weather:
    # Placeholder for any transformation logic if needed
    return weather_data


@task
def load_weather_data(block_name: str, weather_data: Weather) -> None:
    logger.info("Loading weather data into the database")
    with SqlAlchemyConnector.load(block_name) as connector:  # type: ignore[invalid-context-manager]
        connector.execute(str(insert(Weather)), parameters=weather_data.model_dump())


if __name__ == "__main__":
    main()
