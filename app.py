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

if __name__ == '__main__':
    app.run(port=5353, debug=True)
