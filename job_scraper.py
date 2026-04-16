# File: job_scraper.py
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, parse_qs
import time
import json
from datetime import datetime
import random

class JobScraper:
    def __init__(self, use_proxies=False):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.use_proxies = use_proxies
        self.proxies = []  # Add your proxies here if needed
        
    def _get_random_headers(self):
        """Return random user agent to avoid detection"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.headers['User-Agent'] = random.choice(user_agents)
        return self.headers
    
    def scrape_indeed_search(self, keywords, location="", max_results=25, days_old=30):
        """
        Scrape job listings from Indeed search results
        
        Note: Scraping Indeed requires careful consideration of their terms of service.
        This is for educational purposes only.
        """
        base_url = "https://www.indeed.com/jobs"
        jobs = []
        
        for start in range(0, max_results, 10):
            params = {
                'q': keywords,
                'l': location,
                'start': start,
                'fromage': days_old,  # Jobs posted in last X days
                'sort': 'date',  # Sort by date
                'limit': 50,
            }
            
            try:
                response = requests.get(
                    base_url, 
                    params=params, 
                    headers=self._get_random_headers(),
                    timeout=15
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_=['job_seen_beacon', 'cardOutline'])
                
                if not job_cards:
                    break  # No more jobs
                
                for card in job_cards:
                    if len(jobs) >= max_results:
                        break
                    
                    job = self._extract_indeed_job(card)
                    if job:
                        jobs.append(job)
                
                # Respectful delay
                time.sleep(random.uniform(1, 3))
                
                # Check if we're at the end
                if not soup.find('a', {'aria-label': 'Next'}):
                    break
                    
            except Exception as e:
                print(f"Error scraping Indeed page {start//10}: {e}")
                break
        
        return jobs
    
    def _extract_indeed_job(self, card):
        """Extract job details from Indeed job card"""
        try:
            # Extract job title
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                return None
            
            title = title_elem.text.strip()
            
            # Extract company
            company_elem = card.find('span', class_='companyName')
            company = company_elem.text.strip() if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('div', class_='companyLocation')
            location = location_elem.text.strip() if location_elem else "Remote"
            
            # Extract job URL
            job_link = card.find('a', class_='jcs-JobTitle')
            if job_link and job_link.get('href'):
                job_url = urljoin('https://www.indeed.com', job_link['href'])
            else:
                job_url = ""
            
            # Extract salary if available
            salary_elem = card.find('div', class_='metadata salary-snippet-container')
            salary = salary_elem.text.strip() if salary_elem else ""
            
            # Extract job snippet/description
            snippet_elem = card.find('div', class_='job-snippet')
            snippet = ' '.join(snippet_elem.stripped_strings) if snippet_elem else ""
            
            # Extract date posted
            date_elem = card.find('span', class_='date')
            date_posted = date_elem.text.strip() if date_elem else "Recently"
            
            # Try to extract job ID from URL
            job_id = ""
            if job_url:
                parsed = urlparse(job_url)
                if parsed.path.startswith('/viewjob'):
                    qs = parse_qs(parsed.query)
                    job_id = qs.get('jk', [''])[0]
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'url': job_url,
                'salary': salary,
                'description': snippet,
                'date_posted': date_posted,
                'job_id': job_id,
                'source': 'Indeed',
                'scraped_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting job details: {e}")
            return None
    
    def scrape_indeed_job_details(self, job_url):
        """
        Scrape detailed information from a specific Indeed job posting
        Note: This is more aggressive scraping and may trigger anti-bot measures
        """
        try:
            response = requests.get(
                job_url, 
                headers=self._get_random_headers(),
                timeout=15
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract full description
            desc_container = soup.find('div', id='jobDescriptionText')
            description = desc_container.get_text(separator='\n', strip=True) if desc_container else ""
            
            # Extract company rating
            rating_elem = soup.find('span', class_='css-1pmc6te')
            rating = rating_elem.text.strip() if rating_elem else ""
            
            # Extract benefits (if available)
            benefits = []
            benefits_elem = soup.find('div', {'data-testid': 'benefits'})
            if benefits_elem:
                benefits = [li.text.strip() for li in benefits_elem.find_all('li')]
            
            return {
                'full_description': description,
                'company_rating': rating,
                'benefits': benefits,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error scraping job details from {job_url}: {e}")
            return {}
    
    def scrape_linkedin_jobs(self, keywords, location="", max_results=25):
        """
        Scrape job listings from LinkedIn
        
        WARNING: LinkedIn has aggressive anti-scraping measures.
        This may require login and may break frequently.
        """
        # LinkedIn scraping is more complex due to login requirements
        # This is a simplified example - you might need to use Selenium or LinkedIn API
        base_url = "https://www.linkedin.com/jobs/search/"
        params = {
            'keywords': keywords,
            'location': location,
            'f_TPR': 'r86400',  # Last 24 hours
            'position': '1',
            'pageNum': '0',
        }
        
        jobs = []
        try:
            response = requests.get(base_url, params=params, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # LinkedIn's HTML structure changes frequently
            # This selector may need adjustment
            job_cards = soup.select('div.base-card')[:max_results]
            
            for card in job_cards:
                try:
                    title_elem = card.select_one('h3.base-search-card__title')
                    company_elem = card.select_one('h4.base-search-card__subtitle')
                    location_elem = card.select_one('span.job-search-card__location')
                    link_elem = card.select_one('a.base-card__full-link')
                    
                    if title_elem and company_elem:
                        job = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip(),
                            'location': location_elem.text.strip() if location_elem else "",
                            'url': link_elem['href'] if link_elem else "",
                            'source': 'LinkedIn',
                            'scraped_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        jobs.append(job)
                except:
                    continue
                    
            time.sleep(2)  # Be respectful
            
        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
            
        return jobs
    
    def scrape_glassdoor_jobs(self, keywords, location="", max_results=25):
        """
        Scrape job listings from Glassdoor
        
        WARNING: Glassdoor has strong anti-scraping measures.
        Consider using their API instead.
        """
        # Glassdoor requires more sophisticated scraping with session handling
        # This is a placeholder - implementation would be complex
        print("Glassdoor scraping not implemented - consider using their API")
        return []
    
    def save_to_csv(self, jobs, filename="scraped_jobs.csv"):
        """Save scraped jobs to CSV file"""
        import pandas as pd
        
        if not jobs:
            print("No jobs to save")
            return False
        
        df = pd.DataFrame(jobs)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Saved {len(jobs)} jobs to {filename}")
        return True
    
    def save_to_database(self, jobs, db_path="jobs.db"):
        """Save scraped jobs directly to the database"""
        import sqlite3
        
        if not jobs:
            print("No jobs to save")
            return 0
        
        saved_count = 0
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()
            
            for job in jobs:
                try:
                    # Check if job already exists (by company, role, and URL)
                    cursor.execute("""
                        SELECT COUNT(*) FROM jobs 
                        WHERE company = ? AND role = ? AND job_url = ?
                    """, (job['company'], job['title'], job['url']))
                    
                    if cursor.fetchone()[0] == 0:
                        # Insert new job
                        cursor.execute("""
                            INSERT INTO jobs (company, role, date_applied, status, job_url, notes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            job['company'],
                            job['title'],
                            datetime.now().strftime('%Y-%m-%d'),
                            'Discovered',  # Set status to 'Discovered' for scraped jobs
                            job['url'],
                            f"Source: {job.get('source', 'Unknown')}\n"
                            f"Location: {job.get('location', '')}\n"
                            f"Salary: {job.get('salary', '')}\n"
                            f"Date Posted: {job.get('date_posted', '')}"
                        ))
                        saved_count += 1
                except Exception as e:
                    print(f"Error saving job {job.get('title', 'Unknown')}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"Successfully saved {saved_count} new jobs to database")
            return saved_count
            
        except Exception as e:
            print(f"Database error: {e}")
            return 0

# Example usage
if __name__ == "__main__":
    scraper = JobScraper()
    
    # Example: Search for Python jobs in London
    print("Searching for jobs on Indeed...")
    jobs = scraper.scrape_indeed_search("Python Developer", "London", max_results=10)
    
    print(f"Found {len(jobs)} jobs")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} at {job['company']} - {job['location']}")
    
    # Save to CSV
    scraper.save_to_csv(jobs, "scraped_jobs.csv")
    
    # Save to database
    saved = scraper.save_to_database(jobs)
    print(f"Saved {saved} jobs to database")
