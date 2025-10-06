from flask import Flask, request, render_template
import json
import os
import threading
import time
import re
import requests
from instagrapi import Client

app = Flask(__name__)

ACCOUNTS_FILE = "accounts.json"
RESULTS_FILE = "results.txt"

# Ensure files exist
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump([], f)
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w") as f:
        f.write("")

# ---------------- ROUTES ---------------- #

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        post_url = request.form.get("post_url")
        if post_url:
            threading.Thread(target=run_auto_liker, args=(post_url,)).start()
            message = "🚀 Auto-liker started in background. Check <a href='/results' target='_blank'>Results</a> soon."
        else:
            message = "⚠️ Please enter a valid Instagram post/reel URL."
    
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
            message = "⚠️ Please provide both username and password."

    return render_template("add_account.html", message=message)

@app.route("/results")
def show_results():
    with open(RESULTS_FILE, "r") as f:
        data = f.read()
    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="5">
        <title>Auto Liker Results</title>
        <style>
            body {{ font-family: monospace; background: #111; color: #0f0; padding: 20px; }}
            pre {{ white-space: pre-wrap; word-break: break-word; }}
        </style>
    </head>
    <body>
        <h2>📊 Auto Liker Logs (refreshes every 5s)</h2>
        <pre>{data}</pre>
        <a href="/" style="color:#0ff;">⬅ Back</a>
    </body>
    </html>
    """

# ---------------- HELPERS ---------------- #

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
        log_line(f"[{email}] ❌ Error while fetching code: {e}")
    return None

def log_line(text):
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)

def run_auto_liker(post_url):
    delay_seconds = 10

    with open(ACCOUNTS_FILE, "r") as f:
        accounts = json.load(f)

    if not accounts:
        log_line("❌ No accounts found. Please add accounts first.")
        return

    log_line("🚀 Starting auto-liker process...")
    log_line(f"🎯 Target: {post_url}")
    log_line("=" * 50)

    for acc in accounts:
        username = acc["username"]
        password = acc["password"]
        cl = Client()

        if username.endswith("@yopmail.com"):
            def code_handler(username, challenge):
                log_line(f"[{username}] ⏳ Waiting for YOPMail code...")
                for i in range(6):
                    code = get_yopmail_code(username)
                    if code:
                        log_line(f"[{username}] 🔐 Got code: {code}")
                        return code
                    time.sleep(5)
                log_line(f"[{username}] ❌ Failed to get code.")
                return ""
            cl.challenge_code_handler = code_handler

        try:
            cl.login(username, password)
            log_line(f"[{username}] ✅ Logged in successfully.")

            medi_id = cl.media_pk_from_url(post_url)
            cl.media_like(medi_id)
            log_line(f"[{username}] ❤️ Liked the post successfully.")

        except Exception as e:
            error_str = str(e).lower()
            if "challenge_required" in error_str:
                log_line(f"[{username}] ⚠️ Challenge required.")
            elif "password" in error_str or "credentials" in error_str or "username" in error_str:
                log_line(f"[{username}] ❌ Invalid credentials.")
            else:
                log_line(f"[{username}] ❌ Error: {e}")

        time.sleep(delay_seconds)

    log_line("✅ Finished all accounts.")
    log_line("=" * 50 + "\n")

if __name__ == "__main__":
    app.run(debug=True)
