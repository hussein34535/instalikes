from flask import Flask, request, render_template, redirect, url_for
import json
import os
import subprocess
import sys
from instagrapi import Client
import requests
import re
import time

app = Flask(__name__)

ACCOUNTS_FILE = "accounts.json"

# Ensure accounts.json exists
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump([], f)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        post_url = request.form.get("post_url")
        if post_url:
            # Run the auto-liker logic
            message = run_auto_liker(post_url)
        else:
            message = "Please enter a valid Instagram post/reel URL."
    
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)

    return render_template("index.html", message=message, accounts=accounts)

@app.route("/add_account", methods=["GET", "POST"])
def add_account():
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username and password:
            message = save_account(username, password)
        else:
            message = "Please provide both username and password."

    return render_template("add_account.html", message=message)

def save_account(username, password):
    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)
    
    for acc in accounts:
        if acc["username"] == username:
            return "⚠️ This account already exists."
    
    accounts.append({"username": username, "password": password})
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)
    return "✅ Account added successfully."

def get_yopmail_code(email):
    inbox = email.split('@')[0]
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        msg_list_url = f"https://www.yopmail.com/en/inbox?login={inbox}"
        session.get("https://www.yopmail.com/en/")
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

def run_auto_liker(post_url):
    delay_seconds = 10
    results = []

    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)

    if not accounts:
        return "No accounts found. Please add accounts first."

    for acc in accounts:
        username = acc["username"]
        password = acc["password"]
        cl = Client()

        if username.endswith("@yopmail.com"):
            def code_handler(username, challenge):
                print(f"[{username}] ⏳ Waiting for code from YOPMail...")
                for i in range(6):
                    code = get_yopmail_code(username)
                    if code:
                        print(f"[{username}] 🔐 Got code: {code}")
                        return code
                    print(f"[{username}] ⏳ Retrying to fetch code...")
                    time.sleep(5)
                print(f"[{username}] ❌ Failed to get code after retries.")
                return ""
            cl.challenge_code_handler = code_handler

        try:
            cl.login(username, password)
            results.append(f"[{username}] ✅ Logged in successfully.")

            medi_id = cl.media_pk_from_url(post_url)
            cl.media_like(medi_id)
            results.append(f"[{username}] ❤️ Liked the post successfully.")

        except Exception as e:
            error_str = str(e).lower()
            if "challenge_required" in error_str:
                results.append(f"[{username}] ❌ Challenge required – check if code handler worked.")
            elif "password" in error_str or "credentials" in error_str or "username" in error_str:
                results.append(f"[{username}] ❌ Invalid login credentials.")
            else:
                results.append(f"[{username}] ❌ Error: {e}")

        time.sleep(delay_seconds)
    
    return "<br>".join(results)

if __name__ == "__main__":
    # Install instagrapi if not present
    try:
        import instagrapi
    except ImportError:
        print("📦 Installing missing package: instagrapi")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "instagrapi", "requests", "Flask"])

    app.run(debug=True)
