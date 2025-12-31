import requests
import time
import random
import string
import json
import os

BASE_URL = "https://api.mail.tm"

def get_domain():
    try:
        r = requests.get(f"{BASE_URL}/domains")
        if r.status_code == 200:
            return r.json()['hydra:member'][0]['domain']
    except:
        pass
    return None

def create_account_api(email, password):
    payload = {"address": email, "password": password}
    try:
        r = requests.post(f"{BASE_URL}/accounts", json=payload)
        if r.status_code == 201:
            return True
    except:
        pass
    return False

def generate_emails(count=10):
    print(f"🚀 Starting generation of {count} emails...")
    
    domain = get_domain()
    if not domain:
        print("❌ Could not fetch domain.")
        return

    accounts = []
    
    for i in range(count):
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        password = "Pass" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        email = f"{username}@{domain}"
        
        if create_account_api(email, password):
            print(f"[{i+1}/{count}] ✅ Created: {email}")
            accounts.append({
                "email": email,
                "email_password": password, # Password for the email itself
                "instagram_password": password, # Suggest using same pass for Insta
                "status": "ready_to_register"
            })
        else:
            print(f"[{i+1}/{count}] ❌ Failed to create.")
            
        time.sleep(1) # Prevent rate limits

    # Save to file
    with open("generated_emails.json", "w") as f:
        json.dump(accounts, f, indent=4)
        
    print(f"\n✨ Done! Saved {len(accounts)} emails to 'generated_emails.json'")

if __name__ == "__main__":
    count = int(input("How many emails do you want? ") or "10")
    generate_emails(count)
