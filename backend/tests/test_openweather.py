from clients.openweather import OpenWeatherClient
from db_models.weather import Weather
from config import settings


# TEST_API_KEY = settings.OPENWEATHER_API_KEY.get_secret_value()
TEST_API_KEY = "TEST_API_KEY"


# call fetch_current_weather_sync
def test_fetch_current_weather_sync():
    client = OpenWeatherClient(
        api_key=TEST_API_KEY, api_uri=settings.OPENWEATHER_API_URI
    )
    response = client.fetch_current_weather_sync()
    _ = Weather(
        timestamp=response.dt,
        temperature_k=response.temp_k,
        pressure_pa=response.pressure_hpa * 100,
        humidity_percent=response.humidity,
        dew_point_k=response.dew_point_k,
        wind_speed_m_s=response.wind_speed_m_s,
        wind_deg=response.wind_deg,
        wind_gust_m_s=response.wind_gust_m_s,
    )


if __name__ == "__main__":
    test_fetch_current_weather_sync()
