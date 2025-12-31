import requests
import time
import random
import string
import json

BASE_URL = "https://api.mail.tm"

def get_domain():
    r = requests.get(f"{BASE_URL}/domains")
    if r.status_code == 200:
        return r.json()['hydra:member'][0]['domain']
    raise Exception("Could not fetch domains")

def create_account(email, password):
    payload = {"address": email, "password": password}
    r = requests.post(f"{BASE_URL}/accounts", json=payload)
    if r.status_code == 201:
        return True
    return False

def get_token(email, password):
    payload = {"address": email, "password": password}
    r = requests.post(f"{BASE_URL}/token", json=payload)
    if r.status_code == 200:
        return r.json()['token']
    raise Exception("Could not get token")

def get_messages(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/messages", headers=headers)
    if r.status_code == 200:
        return r.json()['hydra:member']
    return []

# --- MAIN ---
try:
    print("🔄 Fetching available domain...")
    domain = get_domain()
    
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    password = "MyStrongPassword123!"
    email = f"{username}@{domain}"
    
    print(f"🛠️ Creating account: {email}")
    if create_account(email, password):
        print("✅ Account created!")
        
        print("🔑 Getting access token...")
        token = get_token(email, password)
        
        print(f"\n📧 YOUR EMAIL: {email}")
        print("⏳ Waiting for emails (Send a test email now!)...")
        
        for i in range(20): # Wait 100 seconds
            print(f"Checking inbox... ({i+1}/20)")
            msgs = get_messages(token)
            if msgs:
                print("\n📬 New Message Received!")
                for msg in msgs:
                    print(f"From: {msg['from']['address']}")
                    print(f"Subject: {msg['subject']}")
                    print(f"Intro: {msg['intro']}")
                    print("-" * 30)
                break
            time.sleep(5)
    else:
        print("❌ Failed to create account.")

except Exception as e:
    print(f"Error: {e}")

print("\n(Demo finished)")
