from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
import os

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from pyhd import Chart

app = FastAPI(title="Human Design BodyGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BirthData(BaseModel):
    date: str  # Format: YYYY-MM-DD
    time: str  # Format: HH:MM
    timezone: Optional[str] = None  # Format: +HH:MM or -HH:MM
    zip_code: Optional[str] = None

geolocator = Nominatim(user_agent="bodygraph_app")
tf = TimezoneFinder()

@app.post("/api/calculate")
def calculate_chart(data: BirthData):
    try:
        if data.zip_code:
            # Look up timezone from Zip Code
            location = geolocator.geocode({"postalcode": data.zip_code, "country": "US"})
            if not location:
                raise ValueError("Could not find location for the provided Zip Code.")
            
            tz_name = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            if not tz_name:
                raise ValueError("Could not determine timezone for that location.")
            
            # Combine date and time, apply the timezone, then convert to UTC
            local_dt = datetime.strptime(f"{data.date} {data.time}", "%Y-%m-%d %H:%M")
            local_dt = local_dt.replace(tzinfo=ZoneInfo(tz_name))
            dt = local_dt.astimezone(UTC)
            
        elif data.timezone:
            # Fallback to manual timezone
            dt_str = f"{data.date}T{data.time}:00{data.timezone}"
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo:
                dt = dt.astimezone(UTC)
            else:
                dt = dt.replace(tzinfo=UTC)
        else:
            raise ValueError("You must provide either a Zip Code or a Timezone.")

        # Calculate Human Design Chart
        chart = Chart(dt)
        
        # Manually extract exactly what the frontend needs to bypass pyhd bugs
        chart_data = {
            "profile": chart.profile.full_name,
            "authority": chart.authority.full_name,
            "type": chart.type.full_name,
            "cross": {
                "name": chart.cross.full_name,
                "geometry": chart.geometry.full_name
            } if chart.cross else None,
            "strategy": chart.strategy.full_name,
            "signature": chart.signature.full_name,
            "not_self_theme": chart.not_self_theme.full_name,
            "definitions": chart.definition_type.full_name,
            "centers": [c.full_name for c in chart.centers],
            "channels": [
                {
                    "name": ch.full_name, 
                    "gates": [ch.gates[0].full_name, ch.gates[1].full_name]
                } for ch in chart.channels
            ],
            "variables": {
                "determination": chart.determination.full_name,
                "cognition": chart.cognition.full_name,
                "environment": chart.environment.full_name,
                "perspective": chart.perspective.full_name,
                "motivation": chart.motivation.full_name,
                "sense": chart.sense.full_name
            }
        }
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found. Please create static/index.html"}
