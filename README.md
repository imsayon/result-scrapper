DSCE Result Scraper API
A simple and effective web scraper and API for fetching student results from the DSCE (Dayananda Sagar College of Engineering) results portal. This project is a Python-based backend built with FastAPI, designed to download and organize result PDFs efficiently.

Key Features
Simple & Easy to Understand: Built with standard libraries and a straightforward structure, making it perfect for beginners.

Real-time Status Tracking: A dedicated endpoint (/status) allows you to monitor the progress of a scraping job.

Dynamic Discovery: Intelligently discovers the number of students in a branch by stopping after a set number of consecutive failures.

Organized Downloads: Saves result PDFs in a structured folder hierarchy: downloads/Results_PDF_<YEAR>/<BRANCH>/.

PDF Parsing: Extracts the student's name directly from the PDF content to create user-friendly filenames (e.g., STUDENT_NAME_CS001.pdf).

Interactive API Docs: Automatically generates interactive API documentation with Swagger UI.

Tech Stack
Backend Framework: Python 3 with FastAPI

Web Server: Uvicorn

Data Validation: Pydantic

HTTP Client: Requests

PDF Parsing: PyPDF2

Environment Management: python-dotenv

⚙️ Setup and Installation
1. Prerequisites
Python 3.8+

A Python virtual environment tool (like venv)

2. Clone the Repository
Bash

git clone https://github.com/your-username/result-scraper.git
cd result-scraper
3. Create a Virtual Environment
Bash

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
4. Install Dependencies
Bash

pip install -r requirements.txt
5. Configure Environment Variables
Create a file named .env in the root of the project directory and add the URL for the results portal.

Code snippet

# .env
RESULT_PORTAL_URL="http://14.99.184.178:8080/birt/frameset"
▶ Running the Application
Once the setup is complete, you can start the API server with Uvicorn.

Bash

uvicorn app.main:app --reload
The API will be running and available at http://127.0.0.1:8000.

API Endpoints
You can access the interactive Swagger UI documentation at http://127.0.0.1:8000/docs.

Method	Endpoint	Description
POST	/scrape	Scrapes all results for a given year and branches.
POST	/scrape-single	Scrapes the result for a single USN.
GET	/status	Gets the real-time status of the current scraping job.
GET	/results	Lists all the result PDFs that have been downloaded.

Export to Sheets
Example: Start a Full Scrape
To start scraping all results for the CS and AI branches for the year 2024, send a POST request to /scrape with the following JSON body:

JSON

{
  "year": "24",
  "branches": ["CS", "AI"]
}
The API will wait for the scraping task to complete and then respond. You can monitor its progress in real-time using the /status endpoint.