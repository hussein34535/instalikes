import json
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv("dev.vars")

import api.python.database as db

# Top-level list of new accounts
new_accounts_list = [
    "h4p7o9b7tk@airsworld.net:PasseumnmEkY",
]

# Prepare data structure
accounts_data = []

# Remove duplicates (set) - cautious with objects, so we process list
processed_emails = set()

for item in new_accounts_list:
    item = item.strip()
    if not item: continue
    
    # Check for email:password format
    if ":" in item:
        parts = item.split(":")
        email = parts[0].strip()
        pwd = parts[1].strip()
    else:
        print(f"⚠️ Skipping '{item}': No password provided (Format: email:password)")
        continue
        
    if email in processed_emails:
        continue
        
    processed_emails.add(email)
    accounts_data.append({"username": email, "password": pwd})

# US Proxies provided by user

# US Proxies provided by user
proxies_list = [
    "http://setohkmm:viuevel3xkqt@142.111.48.253:7030",
    "http://setohkmm:viuevel3xkqt@23.95.150.145:6114",
    "http://setohkmm:viuevel3xkqt@198.23.239.134:6540",
    "http://setohkmm:viuevel3xkqt@107.172.163.27:6543",
    "http://setohkmm:viuevel3xkqt@216.10.27.159:6837",
    "http://setohkmm:viuevel3xkqt@23.26.71.145:5628",
    "http://setohkmm:viuevel3xkqt@23.27.208.120:5830"
]

# Assign proxies round-robin
for i, acc in enumerate(accounts_data):
    acc["proxy"] = proxies_list[i % len(proxies_list)]

# --- EXECUTION ---

# WARNING: Only set this to True if you want to wipe everything!
DELETE_ALL_FIRST = True

if DELETE_ALL_FIRST:
    print("🗑️  Deleting ALL accounts from Database as requested...")
    # There is no direct "delete_all" in `database.py`, but we can fetch all and delete one by one
    # OR better: implement `delete_all_accounts()` in `database.py` or just loop here.
    # Since we want to be safe, let's fetch and delete.
    all_accs = db.get_all_accounts(limit=1000)
    for acc in all_accs:
        db.delete_account(acc['username'])
        print(f"   - Deleted {acc['username']}")
    print("✨ Database Cleared.")

print(f"📦 Preparing to import {len(accounts_data)} new accounts...")

if accounts_data:
    stats = db.add_accounts_bulk(accounts_data)
    print(f"✅ Import Result: Added {stats.get('added', 0)}, Updated {stats.get('updated', 0)}")
    if stats.get('error'):
        print(f"❌ Error: {stats['error']}")
else:
    print("⚠️ No accounts to import.")

print("🚀 Done.")
