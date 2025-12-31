import sys
import os
from dotenv import load_dotenv

load_dotenv("dev.vars")

try:
    import api.python.database as db
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    import api.python.database as db

def activate_hero():
    username = "h4p7o9b7tk@airsworld.net"
    print(f"🦸 Activating Hero Account: {username} ...")
    
    # Force update
    try:
        # Just use bulk read/write logic or custom update
        # Since update_account_status is available:
        db.update_account_status(username, "ACTIVE")
        
        # Also ensure proxy is None (Clean IP) explicitly using bulk add (Upsert)
        # We need password for bulk add, let's just assume it exists or fetch it
        accounts = db.get_all_accounts()
        target = next((a for a in accounts if a['username'] == username), None)
        
        if target:
            target['status'] = "ACTIVE"
            target['proxy'] = None # Ensure NO proxy for local run
            res = db.add_accounts_bulk([target])
            print(f"✅ Account Activated & Proxy Cleared! DB Response: {res}")
        else:
            print("❌ Account not found in DB! Please run seed_accounts.py first.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    activate_hero()
