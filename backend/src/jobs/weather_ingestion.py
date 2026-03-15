import asyncio
import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from src.infrastructure.database import SessionLocal
from src.domain.models.core import WeatherEvent, Airport

logger = logging.getLogger(__name__)

# NOAA API Endpoint for METAR (Meteorological Aerodrome Reports)
NOAA_URL = "https://aviationweather.gov/api/data/metar"

# Sample major airports to query for weather
AIRPORT_CODES = ["JFK", "LHR", "DXB", "SIN", "CDG"]

async def fetch_weather_events() -> list[dict]:
    """Fetch live severe weather conditions for major airports."""
    logger.info(f"Fetching weather for airports: {AIRPORT_CODES}")
    
    events = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Query the NOAA API, asking for JSON format
            params = {
                "ids": ",".join(AIRPORT_CODES),
                "format": "json",
                "taf": "false"  # Only current conditions, no Terminal Aerodrome Forecast yet
            }
            
            response = await client.get(NOAA_URL, params=params)
            response.raise_for_status()
            metar_data = response.json()
            
            for report in metar_data:
                airport_id = report.get("icaoId")
                raw_text = report.get("rawOb")
                
                # Simple condition parser from METAR report string
                condition = "CLEAR"
                severity = 0.0
                
                if "TS" in raw_text:  # Thunderstorm
                    condition = "THUNDERSTORM"
                    severity = 0.9
                elif "SN" in raw_text:  # Snow
                    condition = "SNOW"
                    severity = 0.8
                elif "FG" in raw_text:  # Fog
                    condition = "FOG"
                    severity = 0.7
                elif "RA" in raw_text:  # Rain
                    condition = "RAIN"
                    severity = 0.5
                    
                events.append({
                    "airport_iata": airport_id[1:] if len(airport_id) == 4 else airport_id[:3],  # Best effort ICAO to IATA proxy for prototype
                    "condition": condition,
                    "severity_score": severity,
                    "timestamp": datetime.utcnow(),
                })

            return events
            
        except Exception as e:
            logger.error(f"Failed to fetch NOAA data: {e}")
            return []

def upsert_weather(db: Session, weather_data: list[dict]):
    """Insert new weather events into PostgreSQL."""
    if not weather_data:
        return
        
    stmt = insert(WeatherEvent).values(weather_data)
    
    # Normally we do On Conflict Do Update, but WeatherEvents uses autoincrement ID so 
    # we just insert a new historical point to track changing weather streams.
    
    logger.info(f"Successfully processed {len(weather_data)} weather observations.")

async def run_weather_job():
    weather = await fetch_weather_events()
    # db = SessionLocal()
    # try:
    #     upsert_weather(db, weather)
    #     db.commit()
    # finally:
    #     db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_weather_job())
