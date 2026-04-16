import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

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
    # Convert NaN or None to empty strings for the database
    company = "" if pd.isna(company) else str(company)
    role = "" if pd.isna(role) else str(role)
    date_applied = "" if pd.isna(date_applied) else str(date_applied)
    status = "Applied" if pd.isna(status) else str(status)
    job_url = "" if pd.isna(job_url) else str(job_url)
    notes = "" if pd.isna(notes) else str(notes)

    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO jobs (company, role, date_applied, status, job_url, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (company, role, date_applied, status, job_url, notes)
        )

def delete_job(job_id):
    """Removes a job from the database by ID"""
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))

def fetch_jobs():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, company, role, date_applied, status, job_url, notes FROM jobs ORDER BY id DESC")
        return cursor.fetchall()