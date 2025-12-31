from flask import jsonify, request
import api.python.database as db
import re

def parse_txt_accounts(text_content):
    """
    Parses accounts from text line by line.
    Formats: 
    user:pass
    user:pass:proxy
    """
    accounts = []
    lines = text_content.splitlines()
    for line in lines:
        line = line.strip()
        if not line: 
            continue
            
        parts = line.split(':')
        if len(parts) >= 2:
            acc = {
                "username": parts[0].strip(),
                "password": parts[1].strip()
            }
            # Handle proxy if present (naive parsing, assumes remainder is proxy)
            # Better format: user:pass:ip:port:user:pass (too complex for simple split)
            # We assume user:pass:proxy_string if 3 parts
            if len(parts) > 2:
                # Reconstruct proxy part
                acc["proxy"] = ":".join(parts[2:]).strip()
                # If proxy doesn't start with http, add it
                if acc["proxy"] and not acc["proxy"].startswith("http"):
                    acc["proxy"] = f"http://{acc['proxy']}"
            
            accounts.append(acc)
    return accounts

def upload_accounts_process():
    try:
        data = request.get_json()
        print(data)
        raw_text = data.get('text', '')
        
        if not raw_text:
            return {"error": "No text provided"}, 400
            
        accounts_list = parse_txt_accounts(raw_text)
        
        if not accounts_list:
             return {"error": "No valid accounts found in text"}, 400
             
        stats = db.add_accounts_bulk(accounts_list)
        return {"message": "Success", "details": stats}
        
    except Exception as e:
        return {"error": str(e)}, 500

def get_account_stats_process():
    return db.get_account_stats()
