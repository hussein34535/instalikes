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
    "lranpbx@telegmail.com", "qhvnh@telegmail.com", "joxnlx@telegmail.com", "dhivk@telegmail.com",
    "nmevfn@telegmail.com", "jnxls@telegmail.com", "nmevfn@telegmail.com", "fzplmcfj@telegmail.com",
    "ancucet@telegmail.com", "sbddsi@telegmail.com", "jrwmuep@telegmail.com", "gacwzrg@telegmail.com",
    "ipukta@telegmail.com", "tnkuzk@telegmail.com", "wlieshc@telegmail.com", "dysasky@telegmail.com",
    "aitspi@telegmail.com", "jqlri@telegmail.com", "iawfyl@telegmail.com", "oacucp@telegmail.com",
    "whdah@telegmail.com", "rnuure@telegmail.com", "zylyzd@telegmail.com", "zthki@telegmail.com",
    "ouzva@telegmail.com", "jcbvn@telegmail.com", "qnjwpd@telegmail.com", "eguour@telegmail.com",
    "anspefss@telegmail.com", "whdah@telegmail.com", "tnkuzk@telegmail.com", "ouzva@telegmail.com",
    "oacucp@telegmail.com", "jnxls@telegmail.com", "mpnjajdx@telegmail.com", "iofxsnau@telegmail.com",
    "piknh@telegmail.com", "svoqxdmi@telegmail.com", "gacwzrg@telegmail.com", "jqlri@telegmail.com",
    "wlieshc@telegmail.com", "dysasky@telegmail.com", "aitspi@telegmail.com", "jrwmuep@telegmail.com",
    "ipukta@telegmail.com", "vinarzpu@telegmail.com", "fyoijttg@telegmail.com", "zhplsxjn@telegmail.com",
    "joxnlx@telegmail.com", "nmevfn@telegmail.com", "sbddsi@telegmail.com", "ancucet@telegmail.com",
    "fzplmcfj@telegmail.com", "iawfyl@telegmail.com", "zylyzd@telegmail.com", "qnjwpd@telegmail.com",
    "rnuure@telegmail.com", "zthki@telegmail.com", "anspefss@telegmail.com", "lranpbx@telegmail.com",
    "piknh@telegmail.com", "jcbvn@telegmail.com", "iofxsnau@telegmail.com", "jrxmz@telegmail.com",
    "mpnjajdx@telegmail.com", "jcbvn@telegmail.com", "gvyvz@telegmail.com", "afsruu@telegmail.com",
    "svoqxdmi@telegmail.com", "eguour@telegmail.com", "ykmiq@telegmail.com", "swolniwn@telegmail.com",
    "svoqxdmi@telegmail.com", "suhraq@telegmail.com", "qkqwa@telegmail.com", "vinarzpu@telegmail.com",
    "jnxls@telegmail.com", "ahbza@telegmail.com", "hgewgs@telegmail.com", "tdechmk@telegmail.com",
    "wzdnjtf@telegmail.com", "zlgbzunx@telegmail.com", "fxaynfk@telegmail.com", "znddrs@telegmail.com",
    "yjeeldpc@telegmail.com", "phjknjy@telegmail.com", "kuaatt@telegmail.com", "xcpwz@telegmail.com",
    "kjwnvs@telegmail.com", "igrzfeg@telegmail.com", "dklccw@telegmail.com", "wgvsjx@telegmail.com",
    "yvdqz@telegmail.com", "iytqzcpx@telegmail.com", "yhsgq@telegmail.com", "rxyjalcl@telegmail.com",
    "wdltpdkg@telegmail.com", "kuqrc@telegmail.com", "vvjqc@telegmail.com", "avozqrv@telegmail.com"
]

PASSWORD = "123123yy"

# Prepare data structure
# Remove duplicates (set) then update
unique_emails = list(set(new_accounts_list))
accounts_data = [{"username": email, "password": PASSWORD} for email in unique_emails]

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

print(f"📦 Preparing to import {len(accounts_data)} new accounts...")
print("ℹ️  Existing accounts will NOT be deleted. New ones will be added.")

stats = db.add_accounts_bulk(accounts_data)
print(f"✅ Done! Added: {stats['added']}, Updated: {stats['updated']}")
