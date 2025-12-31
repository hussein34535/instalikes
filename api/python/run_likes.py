import json
import os
import threading
import time
import random
import re
import requests
from instagrapi import Client
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import builtins
import api.python.database as db

# Disable any interactive input prompts globally (non-interactive backend)
builtins.input = lambda *args, **kwargs: ""

def get_yopmail_code(email):
    inbox = email.split('@')[0]
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        session.get("https://www.yopmail.com/en/")
        msg_list_url = f"https://www.yopmail.com/en/inbox?login={inbox}"
        response = session.get(msg_list_url, headers=headers)
        message_ids = re.findall(r'iframe\.php\?id=(.*?)"', response.text)
        if not message_ids:
            return None
        iframe_url = f"https://www.yopmail.com/en/iframe.php?id={message_ids[0]}"
        iframe_response = session.get(iframe_url, headers=headers)
        match = re.search(r"\b\d{6}\b", iframe_response.text)
        if match:
            return match.group()
    except Exception as e:
        print(f"[{email}] ❌ Error while fetching code: {e}")
    return None

def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)

def random_sleep(min_seconds=2, max_seconds=5):
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)

def warmup_actions(cl, username, job_id):
    """Simulate human behavior before the main action."""
    try:
        if random.random() < 0.3: # Only 30% chance to warm up to save time on large batches
             return
             
        action = random.choice(["get_timeline", "get_self_profile"])
        if action == "get_timeline":
            db.log_event(job_id, f"[{username}] 🧘 Warming up: Scrolling timeline...", "INFO")
            cl.get_timeline_feed()
            random_sleep(2, 5)
        elif action == "get_self_profile":
            db.log_event(job_id, f"[{username}] 🧘 Warming up: Checking own profile...", "INFO")
            cl.user_info(cl.user_id)
            random_sleep(2, 5)
    except Exception as e:
        db.log_event(job_id, f"[{username}] ⚠️ Warmup warning: {e}", "WARNING")

def process_account(acc, media_id, job_id):
    username = acc["username"]
    password = acc["password"]
    proxy = acc.get("proxy") 

    cl = Client()
    
    if proxy:
        try:
            cl.set_proxy(proxy)
        except Exception as e:
            db.log_event(job_id, f"[{username}] ❌ Proxy Error: {e}", "ERROR")
            return

    if username.endswith("@yopmail.com"):
        cl.challenge_code_handler = lambda u, c: get_yopmail_code(u)
    else:
        cl.challenge_code_handler = lambda u, c: ""

    session_path = os.path.join(os.path.dirname(__file__), "sessions", f"{sanitize_filename(username)}.json")
    os.makedirs(os.path.dirname(session_path), exist_ok=True)

    try:
        if os.path.exists(session_path):
            cl.load_settings(session_path)
    except Exception:
        pass

    try:
        cl.login(username, password)
        # Update status to ACTIVE if successful
        db.update_account_status(username, 'ACTIVE')
        db.log_event(job_id, f"[{username}] ✅ Login Success", "SUCCESS")
        
        try:
            cl.dump_settings(session_path)
        except Exception:
            pass

        warmup_actions(cl, username, job_id)

        cl.media_like(media_id)
        db.log_event(job_id, f"[{username}] ❤️ LIKED", "SUCCESS")
        
    except Exception as e:
        error_str = str(e).lower()
        if "challenge_required" in error_str:
            db.update_account_status(username, 'CHALLENGE')
            db.log_event(job_id, f"[{username}] ⚠️ Challenge Required", "WARNING")
        elif "password" in error_str or "credentials" in error_str:
            db.update_account_status(username, 'BANNED') # Likely invalid
            db.log_event(job_id, f"[{username}] ❌ Invalid Creds", "ERROR")
        elif "feedback_required" in error_str:
            db.update_account_status(username, 'BANNED')
            db.log_event(job_id, f"[{username}] 🚨 Action Blocked (Proxy/IP Flagged)", "ERROR")
        else:
            db.log_event(job_id, f"[{username}] ❌ Error: {e}", "ERROR")

def run_auto_liker(post_url):
    job_id = db.create_job(post_url)
    db.log_event(job_id, f"🚀 Batch Process for: {post_url}", "INFO")

    # Load accounts from DB
    accounts = db.get_active_accounts(limit=1000)
    
    if not accounts:
        db.log_event(job_id, "❌ No active accounts found in Database. Please upload accounts first.", "ERROR")
        db.update_job_status(job_id, "FAILED")
        return

    # Configuration
    batch_size = int(os.environ.get("BATCH_SIZE", "5")) # Small batch size for safety
    batch_delay = int(os.environ.get("BATCH_DELAY", "10")) # Seconds between batches

    db.log_event(job_id, f"📊 Found {len(accounts)} active accounts. Starting Smart Batching (Size: {batch_size})...", "INFO")

    # Resolve Media ID (using first account's proxy if avail)
    try:
        temp_client = Client()
        if accounts[0].get("proxy"):
            temp_client.set_proxy(accounts[0].get("proxy"))
        media_id = temp_client.media_pk_from_url(post_url)
    except Exception as e:
        db.log_event(job_id, f"❌ Failed to resolve media id: {e}", "ERROR")
        db.update_job_status(job_id, "FAILED")
        return

    # Batch Processing
    total_processed = 0
    
    # Split accounts into chunks
    account_chunks = [accounts[i:i + batch_size] for i in range(0, len(accounts), batch_size)]

    for index, chunk in enumerate(account_chunks):
        db.log_event(job_id, f"🔄 Processing Batch {index + 1}/{len(account_chunks)} ({len(chunk)} accounts)...", "INFO")
        
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(process_account, acc, media_id, job_id) for acc in chunk]
            for _ in as_completed(futures):
                pass
        
        total_processed += len(chunk)
        
        if index < len(account_chunks) - 1:
            wait_time = batch_delay + random.uniform(2, 5) # Add jitter
            db.log_event(job_id, f"⏳ Sleeping {wait_time:.1f}s before next batch...", "INFO")
            time.sleep(wait_time)

    db.log_event(job_id, f"✅ Job Completed. Processed {total_processed} accounts.", "INFO")
    db.update_job_status(job_id, "COMPLETED")

# --- Interactive Challenge Handler ---
def interactive_challenge_handler(username, choice):
    """
    Pauses execution, updates DB to WAITING_FOR_CODE, and polls for code.
    """
    print(f"[{username}] ⚠️ Challenge Requested! Waiting for user code...")
    db.update_account_status(username, "WAITING_FOR_CODE")
    
    # Poll for 5 minutes (300 seconds)
    for _ in range(60): 
        time.sleep(5)
        code = db.get_verification_code(username)
        if code:
            print(f"[{username}] ✅ Code received: {code}")
            return code
            
    print(f"[{username}] ❌ Timeout waiting for code.")
    return None

def run_check_accounts_process():
    """
    Mode: CHECK
    Logins to all accounts to verify status. No Likes.
    """
    job_id = db.create_job("Check Accounts")
    db.log_event(job_id, "🔍 Starting Account Diagnosis...", "INFO")
    
    accounts = db.get_all_accounts(limit=1000) # Get ALL to check everyone
    
    db.log_event(job_id, f"📊 Checking {len(accounts)} accounts...", "INFO")
    
    for acc in accounts:
        # Check for stop signal
        current_status = db.get_job_status(job_id)
        if current_status == 'STOPPED':
            db.log_event(job_id, "🛑 Job stopped by user.", "WARNING")
            break

        username = acc["username"]
        password = acc["password"]
        proxy = acc.get("proxy")
        
        db.log_event(job_id, f"Checking {username}...", "INFO")
        
        cl = Client()
        if proxy:
             try:
                 cl.set_proxy(proxy)
             except:
                 pass
                 
        # Hook the interactive handler
        if username.endswith("@yopmail.com"):
             # Keep auto handler for Yopmail if preferred, or switch to interactive
             cl.challenge_code_handler = interactive_challenge_handler
        else:
             cl.challenge_code_handler = interactive_challenge_handler
             
        try:
            cl.login(username, password)
            db.update_account_status(username, "ACTIVE")
            db.log_event(job_id, f"[{username}] ✅ Healthy", "SUCCESS")
        except Exception as e:
            error_msg = str(e).lower()
            if "challenge_required" in error_msg:
                 db.update_account_status(username, "WAITING_FOR_CODE")
                 db.log_event(job_id, f"[{username}] ⚠️ Needs Code (Check Account Lab)", "WARNING")
            elif "password" in error_msg:
                 db.update_account_status(username, "BANNED")
                 db.log_event(job_id, f"[{username}] ❌ Bad Password", "ERROR")
            else:
                 db.log_event(job_id, f"[{username}] ❌ Error: {e}", "ERROR")
                 
    db.update_job_status(job_id, "COMPLETED")

def run_likes_process(post_url):
    threading.Thread(target=run_auto_liker, args=(post_url,)).start()
    return {"message": "✅ Smart Batch Job started. Monitor progress in Dashboard."}

def start_check_process():
    threading.Thread(target=run_check_accounts_process).start()
    return {"message": "✅ Account Check started. Monitor in Dashboard."}
