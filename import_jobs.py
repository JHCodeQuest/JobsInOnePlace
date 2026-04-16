# import_jobs.py
import re
import sqlite3
from urllib.parse import urlparse, parse_qs

DB = "jobs.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                date_applied TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied',
                job_url TEXT,
                notes TEXT
            )
        """)

def add_job(company, role, date_applied, status="Applied", job_url="", notes=""):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            """
            INSERT INTO jobs (company, role, date_applied, status, job_url, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (company, role, date_applied, status, job_url, notes),
        )

def normalize_indeed_url(url):
    return url.strip()

def extract_id_from_url(url):
    q = parse_qs(urlparse(url).query)
    return q.get("vjk", [None])[0]

def import_job_from_url(url, date_applied, company="", role="", status="Applied", notes=""):
    init_db()
    url = normalize_indeed_url(url)
    if not company:
        company = "Unknown"
    if not role:
        role = "Unknown"
    add_job(company, role, date_applied, status, url, notes)
    return {"company": company, "role": role, "date_applied": date_applied, "status": status, "job_url": url}

if __name__ == "__main__":
    example = import_job_from_url(
        "https://www.indeed.com/viewjob?jk=abc123",
        "2026-04-15",
        company="Acme Ltd",
        role="Admin Assistant"
    )
    print(example)