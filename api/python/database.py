import sqlite3
import os
import sys
import time
import json
from datetime import datetime

# Try importing psycopg2 (PostgreSQL adapter)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_type():
    if DATABASE_URL and PSYCOPG2_AVAILABLE:
        return "POSTGRES"
    return "SQLITE"

def get_db_connection():
    db_type = get_db_type()
    if db_type == "POSTGRES":
        try:
            # Parse URL
            from urllib.parse import urlparse
            import socket
            
            url = urlparse(DATABASE_URL)
            hostname = url.hostname
            
            # FORCE IPv4 Resolution
            # AF_INET ensures we ONLY get IPv4 addresses
            print(f"Resolving {hostname} (IPv4)...")
            infos = socket.getaddrinfo(hostname, 5432, family=socket.AF_INET, proto=socket.IPPROTO_TCP)
            
            if not infos:
                raise Exception("No IPv4 address found!")
                
            ipv4_ip = infos[0][4][0]
            print(f"Resolved to: {ipv4_ip}")
            
            # Connect using the IP ADDRESS directly
            conn = psycopg2.connect(
                host=ipv4_ip,
                user=url.username,
                password=url.password,
                port=url.port,
                dbname=url.path[1:],
                sslmode='require'
            )
            return conn
        except Exception as e:
            print(f"IPv4 Connection Error: {e}")
            # Last resort fallback
            conn = psycopg2.connect(DATABASE_URL)
            return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def get_placeholder():
    """Returns '?' for SQLite and '%s' for Postgres"""
    return "%s" if get_db_type() == "POSTGRES" else "?"

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    db_type = get_db_type()
    
    # DataType Adjustments
    serial_type = "SERIAL" if db_type == "POSTGRES" else "INTEGER"
    pk_def = "PRIMARY KEY" if db_type == "POSTGRES" else "PRIMARY KEY AUTOINCREMENT"
    
    # Jobs table
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS jobs (
            id {serial_type} {pk_def},
            target_url TEXT NOT NULL,
            status TEXT DEFAULT 'RUNNING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')

    # Logs table
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS logs (
            id {serial_type} {pk_def},
            job_id INTEGER,
            level TEXT DEFAULT 'INFO',
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Note: Foreign key constraints syntax differs slightly or requires enabling in SQLite, 
    # keeping it simple/loose for compatibility here.
    
    # Accounts table
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS accounts (
            id {serial_type} {pk_def},
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            proxy TEXT,
            status TEXT DEFAULT 'ACTIVE',
            last_used TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# --- Job/Log Functions ---

def create_job(target_url):
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    p = get_placeholder()
    
    query = f'INSERT INTO jobs (target_url, status) VALUES ({p}, {p})'
    if get_db_type() == "POSTGRES":
        query += " RETURNING id"
        c.execute(query, (target_url, 'RUNNING'))
        job_id = c.fetchone()[0]
    else:
        c.execute(query, (target_url, 'RUNNING'))
        job_id = c.lastrowid
        
    conn.commit()
    conn.close()
    return job_id

def update_job_status(job_id, status):
    conn = get_db_connection()
    c = conn.cursor()
    p = get_placeholder()
    
    if status in ['COMPLETED', 'FAILED']:
        c.execute(f'UPDATE jobs SET status = {p}, completed_at = CURRENT_TIMESTAMP WHERE id = {p}', (status, job_id))
    else:
        c.execute(f'UPDATE jobs SET status = {p} WHERE id = {p}', (status, job_id))
    conn.commit()
    conn.close()

def log_event(job_id, message, level='INFO'):
    conn = get_db_connection()
    c = conn.cursor()
    p = get_placeholder()
    
    c.execute(f'INSERT INTO logs (job_id, message, level) VALUES ({p}, {p}, {p})', (job_id, message, level))
    conn.commit()
    conn.close()
    # Print for server logs
    print(f"[{level}] {message}")

def get_latest_job_logs(limit=50):
    init_db()
    conn = get_db_connection()
    
    # Handle cursor type for dictionary access
    if get_db_type() == "POSTGRES":
        c = conn.cursor(cursor_factory=RealDictCursor)
    else:
        c = conn.cursor()
        
    c.execute('SELECT * FROM jobs ORDER BY id DESC LIMIT 1')
    job = c.fetchone()
    
    if not job:
        conn.close()
        return {"status": "No jobs run yet.", "logs": [], "job": None}
    
    job_id = job['id']
    job_status = job['status']
    target_url = job['target_url']
    
    p = get_placeholder()
    c.execute(f'SELECT * FROM logs WHERE job_id = {p} ORDER BY id ASC', (job_id,))
    logs = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return {
        "job_id": job_id,
        "status": job_status,
        "target": target_url,
        "logs": [f"[{l['timestamp']}] [{l['level']}] {l['message']}" for l in logs]
    }

# --- Account Functions ---

def add_accounts_bulk(accounts_list):
    """
    accounts_list: list of dicts {username, password, proxy (optional)}
    """
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    p = get_placeholder()
    
    added_count = 0
    updated_count = 0
    
    for acc in accounts_list:
        try:
            c.execute(f"SELECT id FROM accounts WHERE username = {p}", (acc['username'],))
            existing = c.fetchone()
            
            proxy = acc.get('proxy', None)
            
            if existing:
                c.execute(f"UPDATE accounts SET password = {p}, proxy = {p}, status = 'ACTIVE' WHERE username = {p}", 
                          (acc['password'], proxy, acc['username']))
                updated_count += 1
            else:
                c.execute(f"INSERT INTO accounts (username, password, proxy) VALUES ({p}, {p}, {p})", 
                          (acc['username'], acc['password'], proxy))
                added_count += 1
        except Exception as e:
            print(f"Error adding account {acc.get('username')}: {e}")
            
    conn.commit()
    conn.close()
    return {"added": added_count, "updated": updated_count}

def get_active_accounts(limit=1000):
    init_db()
    conn = get_db_connection()
    if get_db_type() == "POSTGRES":
        c = conn.cursor(cursor_factory=RealDictCursor)
    else:
        c = conn.cursor()
        
    p = get_placeholder()
    c.execute(f"SELECT * FROM accounts WHERE status = 'ACTIVE' LIMIT {p}", (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def update_account_status(username, status):
    conn = get_db_connection()
    c = conn.cursor()
    p = get_placeholder()
    c.execute(f"UPDATE accounts SET status = {p}, last_used = CURRENT_TIMESTAMP WHERE username = {p}", (status, username))
    conn.commit()
    conn.close()

def get_account_stats():
    init_db()
    conn = get_db_connection()
    if get_db_type() == "POSTGRES":
        c = conn.cursor(cursor_factory=RealDictCursor)
    else:
        c = conn.cursor()
        
    c.execute("SELECT COUNT(*) as total FROM accounts")
    total = c.fetchone()['total']
    
    c.execute("SELECT COUNT(*) as active FROM accounts WHERE status = 'ACTIVE'")
    active = c.fetchone()['active']
    
    c.execute("SELECT COUNT(*) as banned FROM accounts WHERE status = 'BANNED' OR status = 'CHALLENGE'")
    banned = c.fetchone()['banned']
    
    conn.close()
    return {"total": total, "active": active, "banned": banned}
