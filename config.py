from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENWEATHER_API_URI: str
    OPENWEATHER_API_KEY: SecretStr
    WEATHER_UPDATE_INTERVAL_MINUTES: int = Field(5, ge=2)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
