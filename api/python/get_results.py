from flask import jsonify
import api.python.database as db

def get_results_process():
    try:
        data = db.get_latest_job_logs()
        return data
    except Exception as e:
        return {"status": "Error fetching results", "logs": [str(e)]}
