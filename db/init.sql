CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    country VARCHAR(120),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS readings (
    id BIGSERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    observed_at TIMESTAMPTZ NOT NULL,
    temperature_c DOUBLE PRECISION,
    humidity_percent DOUBLE PRECISION,
    wind_speed_kmh DOUBLE PRECISION,
    weather_code INTEGER,
    pm10 DOUBLE PRECISION,
    pm25 DOUBLE PRECISION,
    european_aqi DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_readings_city_observed UNIQUE (city_id, observed_at)
);

CREATE INDEX IF NOT EXISTS idx_readings_city_time
ON readings(city_id, observed_at DESC);

INSERT INTO cities (name, country, latitude, longitude) VALUES
('Hyderabad', 'India', 17.3850, 78.4867),
('Bengaluru', 'India', 12.9716, 77.5946),
('London', 'United Kingdom', 51.5074, -0.1278),
('Tokyo', 'Japan', 35.6762, 139.6503),
('New York', 'United States', 40.7128, -74.0060)
ON CONFLICT (name) DO NOTHING;
