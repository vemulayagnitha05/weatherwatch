from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from .db import get_db
from .models import City, Reading
from .schemas import CityOut, ReadingOut

app = FastAPI(
    title="WeatherWatch API",
    version="1.0.2",
    description="REST API for current and historical weather and air-quality readings.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "weatherwatch-api"}

@app.get("/api/cities", response_model=list[CityOut])
def list_cities(db: Session = Depends(get_db)):
    return db.scalars(select(City).where(City.active.is_(True)).order_by(City.name)).all()

@app.get("/api/weather/{city_name}", response_model=ReadingOut)
def current_weather(city_name: str, db: Session = Depends(get_db)):
    city = db.scalar(select(City).where(City.name.ilike(city_name), City.active.is_(True)))
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    reading = db.scalar(
        select(Reading)
        .where(Reading.city_id == city.id)
        .order_by(desc(Reading.observed_at))
        .limit(1)
    )
    if not reading:
        raise HTTPException(status_code=404, detail="No reading available yet")
    return reading

@app.get("/api/weather/{city_name}/history", response_model=list[ReadingOut])
def weather_history(
    city_name: str,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    city = db.scalar(select(City).where(City.name.ilike(city_name), City.active.is_(True)))
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    return db.scalars(
        select(Reading)
        .where(Reading.city_id == city.id, Reading.observed_at >= since)
        .order_by(Reading.observed_at)
    ).all()

STATIC_DIR = Path(__file__).resolve().parents[1] / "frontend"

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/app.js", include_in_schema=False)
def javascript():
    return FileResponse(STATIC_DIR / "app.js", media_type="application/javascript")

@app.get("/styles.css", include_in_schema=False)
def stylesheet():
    return FileResponse(STATIC_DIR / "styles.css", media_type="text/css")
