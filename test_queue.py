import sys
import os
from dotenv import load_dotenv
import time

# Load Env Vars
load_dotenv("dev.vars")

# Import Modules
try:
    import api.python.database as db
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    import api.python.database as db

def add_test_job():
    print("🧪 Simulating a Job Request from the Website...")
    
    # Use a safe, public post (Instagram generic) or just a placeholder to test connection
    # This won't actually succeed in 'liking' if the URL is bad, but it proves the worker picks it up.
    test_url = "https://www.instagram.com/p/C-TestLink123/" 
    
    job_id = db.create_job(test_url, status="PENDING")
    
    if job_id:
        print(f"✅ Job Added to Queue! (ID: {job_id})")
        print("👀 NOW WATCH YOUR 'Start_Bot' WINDOW...")
        print("   It should say: '▶️ Picking up Job...' in a few seconds.")
    else:
        print("❌ Failed to add job to Supabase. Check internet/keys.")

if __name__ == "__main__":
    add_test_job()
