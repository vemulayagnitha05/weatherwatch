from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    country: str | None
    latitude: float
    longitude: float

class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    city_id: int
    observed_at: datetime
    temperature_c: float | None
    humidity_percent: float | None
    wind_speed_kmh: float | None
    weather_code: int | None
    pm10: float | None
    pm25: float | None
    european_aqi: float | None
