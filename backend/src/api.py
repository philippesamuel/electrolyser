from datetime import datetime

from fastapi import FastAPI
from sqlmodel import Session, select
from db_models.weather import Weather
from database import engine


app = FastAPI()


@app.get("/weather/", response_model=list[Weather])
def get_weather_data(
    start_timestamp: datetime | None = None, end_timestamp: datetime | None = None
):
    with Session(engine) as session:
        weather_records = session.exec(
            select(Weather).where(
                (Weather.timestamp >= start_timestamp if start_timestamp else True)
                & (Weather.timestamp <= end_timestamp if end_timestamp else True)
            )
        ).all()
    return weather_records
