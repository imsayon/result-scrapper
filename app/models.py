from pydantic import BaseModel
from typing import Dict, List, Optional

class ScrapeRequest(BaseModel):
    """Request model for starting scraping process"""
    year: str  # e.g., "24" for 2024
    branches: List[str]  # e.g., ["AI", "CS", "IS"]

class ScrapeStatus(BaseModel):
    """Response model for scraping status"""
    is_running: bool
    progress: int
    total: int
    message: str

class SingleUSNRequest(BaseModel):
    """Request model for single USN scraping"""
    usn: str

class ResultFile(BaseModel):
    """Model for result file information"""
    filename: str
    student_name: str
    usn: Optional[str] = None
    branch: str
    size_kb: float
    modified: str

# Available branch codes from your Node.js version
AVAILABLE_BRANCHES = [
    "AE", "AI", "AU", "BT", "CB", "CD", "CG", "CH", "CS", "CV", 
    "CY", "EC", "EE", "EI", "ET", "IC", "IS", "MD", "ME", "RI"
]