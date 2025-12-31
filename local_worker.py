import time
import sys
import os
from dotenv import load_dotenv

# Load Env Vars
load_dotenv("dev.vars")

# Import Modules
try:
    import api.python.database as db
    from api.python.run_likes import run_auto_liker
except ImportError:
    # Handle direct execution paths
    sys.path.append(os.path.dirname(__file__))
    import api.python.database as db
    from api.python.run_likes import run_auto_liker

def main():
    print("👷 Starting Local Worker... (Waiting for jobs from Website)")
    print(f"🔗 Connected to Supabase: {os.environ.get('SUPABASE_URL')}")
    print("---------------------------------------------------------")
    
    while True:
        try:
            # Poll for Pending Jobs
            jobs = db.get_pending_jobs()
            
            if jobs:
                print(f"⚡ Found {len(jobs)} pending job(s)!")
                
                for job in jobs:
                    job_id = job['id']
                    target_url = job['target_url']
                    
                    print(f"▶️ Picking up Job #{job_id}: {target_url}")
                    
                    # Update status to claiming/running
                    db.update_job_status(job_id, "RUNNING")
                    
                    # Execute
                    try:
                        run_auto_liker(target_url, job_id=job_id)
                        print(f"✅ Job #{job_id} Finished.")
                    except Exception as e:
                        print(f"❌ Job #{job_id} Failed: {e}")
                        db.update_job_status(job_id, "FAILED")
                        db.log_event(job_id, f"Worker Error: {str(e)}", "ERROR")
            
            else:
                # No jobs, pulse check
                # print(".", end="", flush=True) 
                # Reduced noise
                pass
                
        except Exception as e:
            print(f"\n⚠️ Worker Loop Error: {e}")
            
        # Sleep before next poll
        time.sleep(5)

if __name__ == "__main__":
    main()
