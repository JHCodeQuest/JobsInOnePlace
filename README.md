# JobsInOnePlace

A desktop job-application tracker: scrape and import job listings, record what
you've applied for, and generate reports — all kept in one place instead of
spread across job boards and spreadsheets.

## What's in it

| File | Purpose |
| --- | --- |
| `app.py` | Application entry point |
| `jobgui.py` | Desktop UI |
| `jobapps.py` | Application records and state |
| `job_scraper.py` | Scrapes listings from job sites |
| `job_api_client.py` | Pulls listings from job APIs |
| `import_jobs.py` | Bulk import from CSV (`jobs1.csv` is sample data) |
| `job_report.py` | Reporting over your applications |
| `viewer_export.py` | Export for viewing/sharing |

## Stack

Python · see `requirements.txt`

## Running it

```bash
pip install -r requirements.txt
python app.py
```

### Building a standalone executable

The project is set up for PyInstaller:

```bash
pyinstaller JobTracker.spec
```

Build output (`build/`, `dist/`) is gitignored.

## Status

Working personal tool.
