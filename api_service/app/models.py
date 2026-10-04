from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    country: Mapped[str | None] = mapped_column(String(120))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class Reading(Base):
    __tablename__ = "readings"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temperature_c: Mapped[float | None] = mapped_column(Float)
    humidity_percent: Mapped[float | None] = mapped_column(Float)
    wind_speed_kmh: Mapped[float | None] = mapped_column(Float)
    weather_code: Mapped[int | None] = mapped_column(Integer)
    pm10: Mapped[float | None] = mapped_column(Float)
    pm25: Mapped[float | None] = mapped_column(Float)
    european_aqi: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint("city_id", "observed_at", name="uq_readings_city_observed"),)
