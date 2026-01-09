"""Client for OpenWeather API."""

from datetime import datetime
import httpx
from hishel.httpx import AsyncCacheClient
from pydantic import BaseModel, Field

from config import settings

OPENWEATHER_API_URI = settings.OPENWEATHER_API_URI
OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY
LATITUDE, LONGITUDE = 52.5200, 13.4050
TTL_SECONDS = settings.WEATHER_UPDATE_INTERVAL_MINUTES * 60

class OpenWeatherResponse(BaseModel):
    dt: datetime = Field(..., description="Unix timestamp")
    temp: float = Field(..., description="Temperature in Kelvin")
    pressure: float = Field(..., description="Pressure in hPa")
    humidity: float = Field(..., description="Humidity as a percentage (0 to 100)")
    dew_point: float = Field(..., description="Dew point in Kelvin")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    wind_gust: float = Field(None, description="Wind gust in m/s")

class OpenWeatherClient:
    def __init__(self, api_key: str = OPENWEATHER_API_KEY.get_secret_value(), api_uri: str = OPENWEATHER_API_URI):
        self.api_key = api_key
        self.api_uri = api_uri
    
    
    async def fetch_current_weather(self, lat: float = LATITUDE, lon: float = LONGITUDE) -> OpenWeatherResponse:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "standard",
        }
        async with AsyncCacheClient() as client:
            response = await client.get(
                self.api_uri, 
                params=params, 
                extensions={"hishel_ttl": TTL_SECONDS}
                )
            response.raise_for_status()
            data = response.json()
            return OpenWeatherResponse(**data["current"])
