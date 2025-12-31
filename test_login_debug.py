import sys
import os
from dotenv import load_dotenv
from instagrapi import Client

# Load environment variables
load_dotenv("dev.vars")

def test_login(username, password, proxy=None):
    print(f"🕵️ Testing login for: {username}")
    print(f"🔑 Password: {password}")
    print(f"🌐 Proxy: {proxy or 'None (WARNING: Might get banned)'}")
    
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)
    
    try:
        print("⏳ Attempting login...")
        cl.login(username, password)
        print("✅ LOGIN SUCCESS! The account is valid and working.")
        info = cl.account_info()
        print(f"ℹ️  Account ID: {info.pk}")
    except Exception as e:
        print(f"❌ LOGIN FAILED: {e}")
        print("\nPossible causes:")
        print("1. Password is truly wrong (Typo during registration?)")
        print("2. Account is suspended (Check email for 'We suspended your account')")
        print("3. Proxy is dead/blocked.")

if __name__ == "__main__":
    user = "h4p7o9b7tk@airsworld.net"
    pw = "PasseumnmEkY"
    
    print(f"🔄 Starting Proxy Hunter Test for: {user}...")

    # 1. Import Proxy Manager
    try:
        from api.python.proxy_manager import get_working_proxy
    except ImportError:
        # Fallback if running from root without package context
        sys.path.append(os.path.join(os.path.dirname(__file__), "api", "python"))
        from proxy_manager import get_working_proxy

    # New Proxies from User
    proxies = [
        "http://ivkgcgdd:gkzg2d1l13fd@142.111.48.253:7030",
        "http://ivkgcgdd:gkzg2d1l13fd@23.95.150.145:6114",
        "http://ivkgcgdd:gkzg2d1l13fd@198.23.239.134:6540",
        "http://ivkgcgdd:gkzg2d1l13fd@107.172.163.27:6543",
        "http://ivkgcgdd:gkzg2d1l13fd@198.105.121.200:6462",
        "http://ivkgcgdd:gkzg2d1l13fd@64.137.96.74:6641",
        "http://ivkgcgdd:gkzg2d1l13fd@84.247.60.125:6095",
        "http://ivkgcgdd:gkzg2d1l13fd@216.10.27.159:6837",
        "http://ivkgcgdd:gkzg2d1l13fd@23.26.71.145:5628",
        "http://ivkgcgdd:gkzg2d1l13fd@23.27.208.120:5830"
    ]

    print(f"\n✨ Testing {len(proxies)} NEW User Proxies...")
    
    # 0. Sanity Check: Test Local IP First
    print(f"\n--- Attempt 0 (Control Test: Local IP) ---")
    try:
        cl_local = Client()
        cl_local.login(user, pw)
        print("✅✅ CONFIRMED: Account is ALIVE and works with Local IP.")
        print("⚠️ If proxies fail below, it means Instagram is 'Lying' to these proxies (Shadow Ban).")
    except Exception as e:
        print(f"❌ FAIL (Local IP): {e}")
        if "not find an account" in str(e) or "suspended" in str(e):
            print("🚨 CRITICAL: The account seems to be BANNED/DELETED. Proxies are innocent.")
            sys.exit(1)
        
    for i, proxy in enumerate(proxies):
        print(f"\n🔸 Testing Proxy {i+1}: {proxy}")
        print(f"⏳ Attempting login...")
        try:
            cl = Client()
            cl.set_proxy(proxy)
            cl.login(user, pw)
            print("✅✅ SUCCESS! This proxy WORKS!")
            print(f"working_proxy = '{proxy}'")
            break
        except Exception as e:
            print(f"❌ Failed: {e}")
