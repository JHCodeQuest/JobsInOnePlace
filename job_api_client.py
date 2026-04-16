# Create a new file: job_api_client.py
import requests
from datetime import datetime
import json

class JobAPIClient:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {}
        self.sources = {
            'reed': self.fetch_reed_jobs,
            'adzuna': self.fetch_adzuna_jobs,
        }
    
    def fetch_reed_jobs(self, keywords, location="", max_results=25):
        """Fetch jobs from Reed API (requires API key)"""
        api_key = self.api_keys.get('reed', '')
        if not api_key:
            return []
        
        url = "https://www.reed.co.uk/api/1.0/search"
        params = {
            'keywords': keywords,
            'location': location,
            'resultsToTake': min(max_results, 100)
        }
        
        try:
            response = requests.get(
                url, 
                params=params, 
                auth=(api_key, ''),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for result in data.get('results', [])[:max_results]:
                    job = {
                        'company': result.get('employerName', ''),
                        'role': result.get('jobTitle', ''),
                        'date_applied': datetime.now().strftime('%Y-%m-%d'),
                        'status': 'Applied',
                        'job_url': result.get('jobUrl', ''),
                        'notes': f"Source: Reed\nLocation: {result.get('locationName', '')}\nSalary: {result.get('minimumSalary', '')}"
                    }
                    jobs.append(job)
                return jobs
        except Exception as e:
            print(f"Error fetching Reed jobs: {e}")
        
        return []
    
    def fetch_adzuna_jobs(self, keywords, location="GB", max_results=25):
        """Fetch jobs from Adzuna API (requires API keys)"""
        app_id = self.api_keys.get('adzuna_app_id', '')
        app_key = self.api_keys.get('adzuna_app_key', '')
        
        if not app_id or not app_key:
            return []
        
        url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'what': keywords,
            'max_days_old': 30,
            'results_per_page': min(max_results, 50)
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for result in data.get('results', [])[:max_results]:
                    job = {
                        'company': result.get('company', {}).get('display_name', ''),
                        'role': result.get('title', ''),
                        'date_applied': datetime.now().strftime('%Y-%m-%d'),
                        'status': 'Applied',
                        'job_url': result.get('redirect_url', ''),
                        'notes': f"Source: Adzuna\nLocation: {result.get('location', {}).get('display_name', '')}\nSalary: {result.get('salary_min', '')}"
                    }
                    jobs.append(job)
                return jobs
        except Exception as e:
            print(f"Error fetching Adzuna jobs: {e}")
        
        return []
    
    def search_jobs(self, source, keywords, location="", max_results=25):
        """Search jobs from a specific source"""
        if source in self.sources:
            return self.sources[source](keywords, location, max_results)
        return []
