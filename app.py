import sys
import os
import requests

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from api.python.get_results import get_results_process
from api.python.manage_accounts import upload_accounts_process, get_account_stats_process
import api.python.database as db

# Load env vars
load_dotenv("dev.vars")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration for GitHub Actions Trigger
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO") # Format: username/repo-name

@app.route('/api/python/run-likes', methods=['POST'])
def run_likes():
    data = request.get_json()
    post_url = data.get('post_url')
    
    if not post_url:
        return jsonify({"error": "post_url is required"}), 400

    # If running locally without GITHUB_REPO configured, warn user
    if not GITHUB_REPO or not GITHUB_TOKEN:
         # Fallback to local run if dev mode (optional, but let's stick to cloud strategy)
         return jsonify({"error": "Server configuration error: GITHUB_REPO or TOKEN missing."}), 500

    # Trigger GitHub Action
    try:
        gh_url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "event_type": "run-likes",
            "client_payload": {
                "post_url": post_url
            }
        }
        
        response = requests.post(gh_url, json=payload, headers=headers)
        
        if response.status_code == 204:
             return jsonify({"message": "✅ Job dispatched to GitHub Actions! Check logs shortly."})
        else:
             return jsonify({"error": f"Failed to trigger GitHub: {response.text}"}), 500
             
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/python/get-results', methods=['GET'])
def get_results():
    # Reads directly from Supabase (shared DB)
    result = get_results_process()
    return jsonify(result)

@app.route('/api/accounts/upload', methods=['POST'])
def upload_accounts():
    result = upload_accounts_process()
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route('/api/accounts/stats', methods=['GET'])
def get_stats():
    result = get_account_stats_process()
    return jsonify(result)

# --- Account Lab Endpoints ---
@app.route('/api/accounts/all', methods=['GET'])
def get_all_accounts_endpoint():
    try:
         accounts = db.get_all_accounts()
         return jsonify(accounts)
    except Exception as e:
         return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/code', methods=['POST'])
def submit_code():
    try:
        data = request.get_json()
        username = data.get('username')
        code = data.get('code')
        if not username or not code:
            return jsonify({"error": "Missing username or code"}), 400
            
        success = db.update_verification_code(username, code)
        if success:
             return jsonify({"message": "✅ Code submitted backend. Engine will pick it up."})
        else:
             return jsonify({"error": "Failed to update DB"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/delete', methods=['POST'])
def delete_account_endpoint():
    try:
        data = request.get_json()
        username = data.get('username')
        if not username:
             return jsonify({"error": "Missing username"}), 400
             
        db.delete_account(username)
        return jsonify({"message": f"Deleted {username}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/check', methods=['POST'])
def check_accounts_endpoint():
    try:
        from api.python.run_likes import start_check_process
        result = start_check_process()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/stop', methods=['POST'])
def stop_check_endpoint():
    try:
        # Get the latest running job and set it to STOPPED
        # This is a simple implementation: stop the latest running job
        # Ideally we pass job_id, but for now we find the active one.
        # But wait, we don't know the job ID easily from frontend unless we track it.
        # Let's just look for any RUNNING job and stop it.
        # Or better: The check process is specific.
        
        # We'll use a new DB function or logic here.
        # Let's start with getting latest job.
        # Simpler: Just update ALL 'RUNNING' jobs to 'STOPPED' 
        # (Since we only run one thing at a time usually)
        
        # But let's be more specific if possible.
        # For now, let's update the latest running job.
        
        # Actually simplest way:
        # Client sends request -> we query Jobs where status=RUNNING -> update to STOPPED.
        url = db._get_url("jobs") + "?status=eq.RUNNING"
        headers = db._get_headers()
        payload = {"status": "STOPPED", "completed_at": db.datetime.utcnow().isoformat()}
        requests.patch(url, headers=headers, json=payload)
        return jsonify({"message": "🛑 Stopping all running jobs..."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Email Generator Endpoint ---
@app.route('/api/utils/generate-email', methods=['POST'])
def generate_email_endpoint():
    try:
        count = request.json.get('count', 1)
        import requests, random, string
        
        BASE_URL = "https://api.mail.tm"
        
        # Get Domain
        r = requests.get(f"{BASE_URL}/domains")
        if r.status_code != 200:
             return jsonify({"error": "Failed to fetch domains"}), 500
        domain = r.json()['hydra:member'][0]['domain']
        
        generated = []
        for _ in range(count):
             username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
             password = "Pass" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
             email = f"{username}@{domain}"
             
             # Create
             payload = {"address": email, "password": password}
             r_cre = requests.post(f"{BASE_URL}/accounts", json=payload)
             if r_cre.status_code == 201:
                 generated.append({"email": email, "password": password})
        
        return jsonify(generated)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5353, debug=True)
