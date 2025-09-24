# app/scraper.py
import requests
import os
import time
import logging
from io import BytesIO
import PyPDF2
import re
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResultScraper:
    def __init__(self):
        self.base_url = os.getenv("RESULT_PORTAL_URL")
        if not self.base_url:
            raise ValueError("RESULT_PORTAL_URL not found in .env file")

        self.report_params = {
            "__report": "mydsi/exam/Exam_Result_Sheet_dsce.rptdesign",
            "__format": "pdf"
        }
        self.client = requests.Session()
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })
        self.downloads_dir = "downloads"
        os.makedirs(self.downloads_dir, exist_ok=True)

    def generate_usn(self, year, branch, number):
        return f"1DS{year}{branch.upper()}{number:03d}"

    def create_branch_folder(self, year, branch):
        branch_folder = os.path.join(self.downloads_dir, f"Results_PDF_20{year}", branch.upper())
        os.makedirs(branch_folder, exist_ok=True)
        return branch_folder

    def extract_student_name_from_pdf(self, pdf_content):
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            full_text = "".join(page.extract_text() for page in pdf_reader.pages)
            name_match = re.search(r'Name of the Student:\s*([A-Z\s]+)', full_text, re.IGNORECASE)
            if name_match and name_match.group(1).strip():
                return re.sub(r'\s+', ' ', name_match.group(1).strip())
            return None
        except Exception as e:
            logger.error(f"Error extracting name from PDF: {e}")
            return None

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]+', '', name).strip()

    def fetch_single_result(self, usn):
        try:
            params = self.report_params.copy()
            params["USN"] = usn
            response = self.client.get(self.base_url, params=params, timeout=30)
            
            if response.status_code != 200 or 'application/pdf' not in response.headers.get('content-type', ''):
                logger.info(f"No valid PDF found for USN: {usn}")
                return None

            pdf_content = response.content
            student_name = self.extract_student_name_from_pdf(pdf_content)

            if not student_name:
                logger.info(f"No student name found in PDF for USN: {usn}")
                return None

            branch = usn[5:7]
            year = usn[3:5]
            
            return {'usn': usn, 'name': student_name, 'branch': branch, 'pdf_content': pdf_content, 'year': year}
        except Exception as e:
            logger.error(f"Error fetching for USN {usn}: {e}")
            return None

    def save_result_pdf(self, student_info):
        try:
            branch_folder = self.create_branch_folder(student_info['year'], student_info['branch'])
            sanitized_name = self.sanitize_filename(student_info['name'])
            usn_suffix = student_info['usn'][-5:]
            filename = f"{sanitized_name}_{usn_suffix}.pdf"
            filepath = os.path.join(branch_folder, filename)

            if os.path.exists(filepath):
                logger.info(f"File '{filename}' already exists. Skipping.")
                return filepath
            
            with open(filepath, 'wb') as f:
                f.write(student_info['pdf_content'])
            logger.info(f"Result PDF saved as '{filename}'")
            return filepath
        except Exception as e:
            logger.error(f"Error saving PDF for {student_info['usn']}: {e}")
            return None

    def scrape_all_results(self, year, branches, status_callback):
        MAX_CONSECUTIVE_FAILURES = 10
        total_downloads = 0

        for branch in branches:
            logger.info(f"Starting branch: {branch}")
            consecutive_failures = 0
            student_number = 1
            while consecutive_failures < MAX_CONSECUTIVE_FAILURES:
                usn = self.generate_usn(year, branch, student_number)
                status_callback(total_downloads, 0, f"Checking {usn}...")
                
                student_info = self.fetch_single_result(usn)
                if student_info:
                    self.save_result_pdf(student_info)
                    total_downloads += 1
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                
                student_number += 1
                time.sleep(0.1)
    
    def scrape_single_result(self, usn):
        student_info = self.fetch_single_result(usn)
        if not student_info:
            return None
        return self.save_result_pdf(student_info)