from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import json
import os
from pathlib import Path

app = FastAPI(title="Labor Force Survey Dashboard", 
              description="Dashboard for TVET and Employment Analysis")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/tables")
async def get_tables():
    """Get all table data as JSON"""
    tables = {}
    
    # Load table data
    table_files = [
        "table2_employment_by_tvet",
        "table2_employment_by_tvet_rowpct", 
        "table3_education_by_tvet",
        "table3_education_by_tvet_rowpct",
        "table4a_employment_by_gender",
        "table4a_employment_by_gender_rowpct",
        "table4b_employment_by_location",
        "table4b_employment_by_location_rowpct"
    ]
    
    for table_name in table_files:
        if os.path.exists(f"{table_name}.json"):
            with open(f"{table_name}.json", 'r') as f:
                tables[table_name] = json.load(f)
    
    return tables

@app.get("/api/summary")
async def get_summary():
    """Get summary statistics"""
    summary = {
        "total_observations": 3858,
        "key_findings": {
            "employment_by_tvet": {
                "chi_square": 10.11,
                "p_value": 0.0015,
                "significance": "**"
            },
            "education_by_tvet": {
                "chi_square": 3027.71,
                "p_value": 0.0000,
                "significance": "***"
            },
            "employment_by_gender": {
                "chi_square": 522.83,
                "p_value": 0.0000,
                "significance": "***"
            },
            "employment_by_location": {
                "chi_square": 115.65,
                "p_value": 0.0000,
                "significance": "***"
            }
        }
    }
    return summary

@app.get("/images/{image_name}")
async def get_image(image_name: str):
    """Serve image files"""
    image_path = f"{image_name}"
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return {"error": "Image not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 