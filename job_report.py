import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os

# Database and Email Configuration
DB_PATH = "jobs.db"
MY_EMAIL = "jkhassan95@gmail.com"  # Your email from context
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD') # Use a Google App Password



def get_weekly_stats():
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Total jobs applied this week
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE date_applied >= ?", (one_week_ago,))
        total_weekly = cursor.fetchone()[0]
        
        # Overall success rate stats
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_all_time = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Offer'")
        total_offers = cursor.fetchone()[0]
        
        success_rate = (total_offers / total_all_time * 100) if total_all_time > 0 else 0
        
    return total_weekly, total_all_time, success_rate

def send_email(weekly, total, rate):
    # check if the password was actually found
    if not EMAIL_PASSWORD:
        print("Error: EMAIL_PASSWORD environment variable not found.")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Weekly Job Tracker Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = MY_EMAIL
    msg['To'] = MY_EMAIL

    # HTML Dashboard Layout
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2c3e50;">Weekly Job Application Dashboard</h2>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6;">
            <p><strong>Jobs Applied This Week:</strong> <span style="font-size: 1.2em; color: #2980b9;">{weekly}</span></p>
            <p><strong>Total Applications:</strong> {total}</p>
            <hr>
            <p><strong>Current Success Rate:</strong> <span style="font-size: 1.5em; color: #27ae60;">{rate:.1f}%</span></p>
        </div>
        <p style="font-size: 0.8em; color: #7f8c8d; margin-top: 20px;">
            This is an automated report from your JobTrackerApp.
        </p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_EMAIL, EMAIL_PASSWORD)
            server.sendmail(MY_EMAIL, MY_EMAIL, msg.as_string())
        print("Report sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    w, t, r = get_weekly_stats()
    send_email(w, t, r)