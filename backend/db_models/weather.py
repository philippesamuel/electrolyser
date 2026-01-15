"""Database models for weather data."""

from datetime import datetime
from sqlmodel import SQLModel, Field
from database import engine


class Weather(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(..., description="Unix timestamp of the weather data")
    temperature_k: float = Field(..., description="Temperature in Kelvin")
    pressure_pa: float = Field(..., description="Pressure in Pascal")
    humidity_percent: float = Field(
        ..., description="Humidity as a percentage (0 to 100)"
    )
    dew_point_k: float = Field(..., description="Dew point in Kelvin")
    wind_speed_m_s: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    wind_gust_m_s: float | None = Field(None, description="Wind gust in m/s")


SQLModel.metadata.create_all(engine)
