from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import List
import uvicorn
import os
import re
from datetime import datetime
from .scraper import ResultScraper
from .models import ScrapeRequest, ScrapeStatus, ResultFile

app = FastAPI(
    title="DSCE Result Scraper",
    description="Scrapes student results from the DSCE website",
    version="1.0.0"
)

scrape_status = ScrapeStatus(is_running=False, progress=0, total=0, message="Ready")
scraper = ResultScraper()

def update_progress(current: int, total: int, message: str):
    scrape_status.progress = current
    scrape_status.total = total
    scrape_status.message = message

async def run_scraping_task(year: str, branches: list):
    try:
        scrape_status.is_running = True
        scrape_status.message = f"Starting scraping for year 20{year}..."
        scrape_status.progress = 0
        
        await scraper.scrape_all_results(year, branches, update_progress)
        
        scrape_status.message = "Scraping completed!"
    except Exception as e:
        scrape_status.message = f"An error occurred: {e}"
    finally:
        scrape_status.is_running = False

@app.get("/")
async def root():
    return {"message": "DSCE Result Scraper API is running"}

@app.get("/status", response_model=ScrapeStatus)
async def get_status():
    return scrape_status

@app.post("/scrape")
async def start_scraping(request: ScrapeRequest, background_tasks: BackgroundTasks):
    if scrape_status.is_running:
        raise HTTPException(status_code=400, detail="Scraping is already in progress.")

    if not re.match(r'^\d{2}$', request.year):
        raise HTTPException(status_code=422, detail="Invalid year format. Use a 2-digit format, e.g., '23' for 2023.")

    background_tasks.add_task(run_scraping_task, request.year, request.branches)
    return {"message": "Scraping process started in the background."}

@app.post("/scrape-single")
async def scrape_single_usn(usn: str):
    if scrape_status.is_running:
        raise HTTPException(status_code=400, detail="Scraping is already in progress.")
    try:
        file_path = await scraper.scrape_single_result(usn)
        if file_path:
            return {"usn": usn, "status": "success", "file_path": file_path}
        else:
            raise HTTPException(status_code=404, detail=f"Result not found for USN: {usn}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results", response_model=list[ResultFile])
async def list_results():
    all_files = []
    root_dir = "downloads"
    if not os.path.exists(root_dir):
        return []

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.pdf'):
                filepath = os.path.join(dirpath, filename)
                try:
                    name_parts = filename.replace('.pdf', '').split('_')
                    student_name = '_'.join(name_parts[:-1])
                    usn_suffix = name_parts[-1]
                    branch = usn_suffix[:2]

                    all_files.append(ResultFile(
                        filename=filename,
                        student_name=student_name,
                        branch=branch,
                        size_kb=round(os.path.getsize(filepath) / 1024, 2),
                        modified=datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    ))
                except IndexError:
                    continue
    return all_files