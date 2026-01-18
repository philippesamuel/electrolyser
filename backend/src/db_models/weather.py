"""Database models for weather data."""

from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import func, event, DDL
from sqlalchemy.schema import FetchedValue
from database import engine


class Weather(SQLModel, table=True):
    __tablename__ = "weather"

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        ..., unique=True, description="Unix timestamp of the weather data"
    )
    temperature_k: float = Field(..., description="Temperature in Kelvin")
    pressure_pa: float = Field(..., description="Pressure in Pascal")
    humidity_percent: float = Field(
        ..., description="Humidity as a percentage (0 to 100)"
    )
    dew_point_k: float = Field(..., description="Dew point in Kelvin")
    wind_speed_m_s: float = Field(..., description="Wind speed in m/s")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    wind_gust_m_s: float | None = Field(None, description="Wind gust in m/s")

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Record creation timestamp",
        sa_column_kwargs={"server_default": func.now()},
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Record last update timestamp",
        sa_column_kwargs={
            "server_default": func.now(),
            "server_onupdate": FetchedValue(),
        },
    )


# Create triggers based on database type
dialect = engine.dialect.name

if dialect == "sqlite":
    sqlite_trigger = DDL("""
        CREATE TRIGGER IF NOT EXISTS weather_update_timestamp 
        AFTER UPDATE ON weather
        FOR EACH ROW
        BEGIN
            UPDATE weather SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)
    event.listen(Weather.__table__, "after_create", sqlite_trigger)

elif dialect == "postgresql":
    pg_trigger = DDL("""
        CREATE OR REPLACE FUNCTION update_weather_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS weather_update_timestamp ON weather;
        CREATE TRIGGER weather_update_timestamp
        BEFORE UPDATE ON weather
        FOR EACH ROW
        EXECUTE FUNCTION update_weather_timestamp();
    """)
    event.listen(Weather.__table__, "after_create", pg_trigger)


SQLModel.metadata.create_all(engine)
