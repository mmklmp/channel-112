from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, UTC
import os

from pyhd import Chart

app = FastAPI(title="Human Design BodyGraph API")

# Add CORS middleware to allow requests from any origin (useful during dev)
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
    timezone: str  # Format: +HH:MM or -HH:MM or Z

@app.post("/api/calculate")
def calculate_chart(data: BirthData):
    try:
        # Construct ISO datetime string
        dt_str = f"{data.date}T{data.time}:00{data.timezone}"
        
        # Parse datetime
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo:
            dt = dt.astimezone(UTC)
        else:
            dt = dt.replace(tzinfo=UTC)
            
        # Calculate Human Design Chart
        chart = Chart(dt)
        
        # Return serialized chart data
        return chart.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Mount static files for the frontend UI
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
