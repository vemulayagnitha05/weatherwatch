import asyncio
import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException
from sqlalchemy import text, select

from .db import SessionLocal
from .models import City, Reading
from .schemas import CollectRequest


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger("collector")


app = FastAPI(
    title="WeatherWatch Collector",
    version="1.0.4",
    description="REST API and background worker for collecting Open-Meteo data.",
)


COLLECT_INTERVAL = int(os.getenv("COLLECT_INTERVAL_SECONDS", "300"))
TIMEOUT = float(os.getenv("OPEN_METEO_TIMEOUT_SECONDS", "15"))


WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "weatherwatch-collector",
    }


@app.get("/cities")
def cities():
    with SessionLocal() as db:
        return [
            {
                "id": c.id,
                "name": c.name,
                "country": c.country,
            }
            for c in db.scalars(
                select(City)
                .where(City.active.is_(True))
                .order_by(City.name)
            ).all()
        ]


def try_lock(db, city_id: int) -> bool:
    result = db.execute(
        text("SELECT pg_try_advisory_xact_lock(:key)"),
        {"key": city_id},
    )

    return bool(result.scalar())


async def fetch_open_meteo(city: City):
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "timezone": "UTC",
    }

    air_params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "current": "pm10,pm2_5,european_aqi",
        "timezone": "UTC",
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        weather_response, air_response = await asyncio.gather(
            client.get(WEATHER_URL, params=params),
            client.get(AIR_URL, params=air_params),
        )

        weather_response.raise_for_status()
        air_response.raise_for_status()

        return weather_response.json(), air_response.json()


async def collect_city(city_id: int) -> bool:
    with SessionLocal() as db:
        city = db.get(City, city_id)

        if not city or not city.active:
            return False

        if not try_lock(db, city_id):
            logger.info(
                "City %s is already being collected by another replica",
                city.name,
            )
            return False

        try:
            weather, air = await fetch_open_meteo(city)

            current = weather.get("current", {})
            air_current = air.get("current", {})

            observed_at = current.get("time") or air_current.get("time")

            if observed_at:
                observed = datetime.fromisoformat(
                    observed_at.replace("Z", "+00:00")
                )
            else:
                observed = datetime.now(timezone.utc)

            existing = db.scalar(
                select(Reading).where(
                    Reading.city_id == city.id,
                    Reading.observed_at == observed,
                )
            )

            if existing:
                logger.info(
                    "Skipping %s: reading already exists for %s",
                    city.name,
                    observed.isoformat(),
                )
                return False

            reading = Reading(
                city_id=city.id,
                observed_at=observed,
                temperature_c=current.get("temperature_2m"),
                humidity_percent=current.get("relative_humidity_2m"),
                wind_speed_kmh=current.get("wind_speed_10m"),
                weather_code=current.get("weather_code"),
                pm10=air_current.get("pm10"),
                pm25=air_current.get("pm2_5"),
                european_aqi=air_current.get("european_aqi"),
                created_at=datetime.now(timezone.utc),
            )

            db.add(reading)
            db.commit()

            logger.info(
                "Collected %s: %.1f°C, PM2.5=%s, AQI=%s",
                city.name,
                (
                    reading.temperature_c
                    if reading.temperature_c is not None
                    else float("nan")
                ),
                reading.pm25,
                reading.european_aqi,
            )

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Collection failed for %s",
                city.name,
            )

            return False


async def collect_all():
    with SessionLocal() as db:
        ids = [
            c.id
            for c in db.scalars(
                select(City)
                .where(City.active.is_(True))
            ).all()
        ]

    for city_id in ids:
        await collect_city(city_id)


async def worker_loop():
    await asyncio.sleep(10)

    while True:
        try:
            await collect_all()

        except Exception:
            logger.exception("Collector cycle failed")

        await asyncio.sleep(COLLECT_INTERVAL)


@app.on_event("startup")
async def startup():
    asyncio.create_task(worker_loop())


@app.post("/collect")
async def manual_collect(request: CollectRequest):
    if request.city_id is not None:
        with SessionLocal() as db:
            if not db.get(City, request.city_id):
                raise HTTPException(
                    status_code=404,
                    detail="City not found",
                )

        ok = await collect_city(request.city_id)

        return {
            "collected": ok,
            "city_id": request.city_id,
        }

    await collect_all()

    return {
        "status": "collection cycle completed",
    }
