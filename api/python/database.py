import os
import requests
import json
import time
from datetime import datetime

# --- Configuration ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# For local testing fallback (local dev) if vars are missing
if not SUPABASE_URL:
    print("[WARNING] SUPABASE_URL not set!")
if not SUPABASE_KEY:
    print("[WARNING] SUPABASE_KEY not set!")

def _get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"  # Default prefer
    }

def _get_url(table):
    # Remove trailing slash from URL if present
    base = SUPABASE_URL.rstrip('/')
    return f"{base}/rest/v1/{table}"

# --- Tables ---
# jobs, logs, accounts

def init_db():
    # REST API cannot create tables on the fly.
    # User must run the SQL schema in Dashboard.
    pass

# --- Job/Log Functions ---

def create_job(target_url):
    url = _get_url("jobs")
    headers = _get_headers()
    
    payload = {
        "target_url": target_url,
        "status": "RUNNING"
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        if data and len(data) > 0:
            return data[0]['id']
        return None
    except Exception as e:
        print(f"Error creating job: {e}")
        return None

def update_job_status(job_id, status):
    url = _get_url("jobs") + f"?id=eq.{job_id}"
    headers = _get_headers()
    
    payload = {"status": status}
    if status in ['COMPLETED', 'FAILED', 'STOPPED']:
        payload['completed_at'] = datetime.utcnow().isoformat()
        
    try:
        r = requests.patch(url, headers=headers, json=payload)
        r.raise_for_status()
    except Exception as e:
        print(f"Error updating job {job_id}: {e}")

def get_job_status(job_id):
    url = _get_url("jobs") + f"?select=status&id=eq.{job_id}"
    headers = _get_headers()
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if data:
                return data[0]['status']
    except:
        pass
    return None

def log_event(job_id, message, level='INFO'):
    url = _get_url("logs")
    headers = _get_headers()
    
    payload = {
        "job_id": job_id,
        "message": message,
        "level": level
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        # We don't necessarily need to raise here to avoid crashing the bot on log failure
        if r.status_code >= 400:
             print(f"Failed to log: {r.text}")
    except Exception as e:
        print(f"Error logging event: {e}")
    
    # Print for server logs
    print(f"[{level}] {message}")

def get_latest_job_logs(limit=50):
    headers = _get_headers()
    
    # 1. Get latest job
    try:
        job_url = _get_url("jobs") + "?select=*&order=id.desc&limit=1"
        r = requests.get(job_url, headers=headers)
        r.raise_for_status()
        jobs = r.json()
        
        if not jobs:
            return {"status": "No jobs run yet.", "logs": [], "job": None}
            
        job = jobs[0]
        job_id = job['id']
        
        # 2. Get logs for this job
        logs_url = _get_url("logs") + f"?select=*&job_id=eq.{job_id}&order=id.asc"
        r_logs = requests.get(logs_url, headers=headers)
        r_logs.raise_for_status()
        logs_data = r_logs.json()
        
        return {
            "job_id": job_id,
            "status": job['status'],
            "target": job['target_url'],
            "logs": [f"[{l['timestamp']}] [{l['level']}] {l['message']}" for l in logs_data]
        }
        
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return {"status": "Error", "logs": [str(e)], "job": None}

# --- Account Functions ---

def add_accounts_bulk(accounts_list):
    """
    accounts_list: list of dicts {username, password, proxy (optional)}
    """
    try:
        url = _get_url("accounts") + "?on_conflict=username"
        headers = _get_headers()
        # Merge duplicates (Upsert)
        headers["Prefer"] = "resolution=merge-duplicates, return=representation"
    except Exception as e:
        print(f"Error preparing request: {e}")
        return {"added": 0, "updated": 0, "error": str(e)}
    
    # Add default status if missing
    payloads = []
    for acc in accounts_list:
        item = {
            "username": acc['username'],
            "password": acc['password'],
            "proxy": acc.get('proxy'),
            "status": "ACTIVE"
        }
        payloads.append(item)
        
    if not payloads:
        return {"added": 0, "updated": 0}

    try:
        r = requests.post(url, headers=headers, json=payloads)
        r.raise_for_status()
        data = r.json()
        # Count is tricky with upsert in one go via REST.
        # But we know how many we sent. REST returns the rows processed (inserted or updated).
        # We can just say "Processed X accounts".
        return {"added": len(data), "updated": 0} # Simplified stats for REST
    except Exception as e:
        print(f"Error adding accounts: {e}")
        return {"added": 0, "updated": 0, "error": str(e)}

def get_active_accounts(limit=1000):
    url = _get_url("accounts") + f"?select=*&status=eq.ACTIVE&limit={limit}"
    headers = _get_headers()
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return []

def get_all_accounts(limit=1000):
    try:
        url = _get_url("accounts") + f"?select=*&limit={limit}&order=id.desc"
        headers = _get_headers()
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return []

def update_account_status(username, status):
    url = _get_url("accounts") + f"?username=eq.{username}"
    headers = _get_headers()
    
    payload = {
        "status": status,
        "last_used": datetime.utcnow().isoformat()
    }
    
    try:
        requests.patch(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Error updating account {username}: {e}")

def update_verification_code(username, code):
    # Propagate errors to app.py for better user feedback
    url = _get_url("accounts") + f"?username=eq.{username}"
    headers = _get_headers()
    
    payload = {
        "verification_code": code,
    }

    r = requests.patch(url, headers=headers, json=payload)
    r.raise_for_status()
    return True

def get_verification_code(username):
    url = _get_url("accounts") + f"?select=verification_code&username=eq.{username}"
    headers = _get_headers()
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        if data:
            return data[0].get('verification_code')
        return None
    except Exception as e:
        print(f"Error getting code for {username}: {e}")
        return None

def delete_account(username):
    try:
        url = _get_url("accounts") + f"?username=eq.{username}"
        headers = _get_headers()
        requests.delete(url, headers=headers)
        return True
    except Exception as e:
        print(f"Error deleting account {username}: {e}")
        return False

def get_account_stats():
    # Use HEAD requests with Count header for efficiency
    base_url = _get_url("accounts")
    headers = _get_headers()
    headers['Prefer'] = 'count=exact'
    
    def get_count(query_param=""):
        try:
            url = base_url + query_param
            r = requests.head(url, headers=headers)
            # Count returned in Content-Range: 0-24/25 -> Total 25
            # Or simplified: if we query for range 0-0, content-range format is '0-0/Total'
            cr = r.headers.get("Content-Range")
            if cr:
                return int(cr.split('/')[-1])
            return 0
        except:
            return 0

    total = get_count("?select=id&limit=1")
    active = get_count("?select=id&status=eq.ACTIVE&limit=1")
    banned = get_count("?select=id&status=in.(BANNED,CHALLENGE)&limit=1")
    
    return {"total": total, "active": active, "banned": banned}
