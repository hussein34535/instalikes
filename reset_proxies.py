import sys
import os
from dotenv import load_dotenv

# Load Env Vars
load_dotenv("dev.vars")

# Import Modules
try:
    import api.python.database as db
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    import api.python.database as db

def clear_proxies():
    print("🧹 Cleaning up proxies to use LOCAL IP...")
    
    # 1. Get Accounts
    accounts = db.get_all_accounts(limit=1000)
    print(f"📊 Found {len(accounts)} accounts.")
    
    # 2. Update each to have proxy=None
    count = 0
    for acc in accounts:
        username = acc['username']
        if acc.get('proxy'): # Only update if it has a proxy
            print(f"   🛁 Stripping proxy from {username}...")
            # We use the bulk add logic or raw update. 
            # Since database.py doesn't have a specific "update_proxy" function exposed easily aside from bulk add,
            # we will re-add it with proxy=None.
            
            # Construct the update payload
            clean_acc = {
                "username": username,
                "password": acc['password'],
                "proxy": None, # Force clear
                "status": "ACTIVE" # Reset status to try again
            }
            
            db.add_accounts_bulk([clean_acc])
            count += 1
            
    print(f"✅ Cleared proxies from {count} accounts.")
    print("🚀 Now these accounts will use your Home IP (Clean) when running local_worker.py")

if __name__ == "__main__":
    clear_proxies()
