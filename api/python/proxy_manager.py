import requests
import random
import concurrent.futures
import time

# Sources for free proxies (HTTP, SOCKS4, SOCKS5) - High Anonymity (Elite) Focus
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http,socks4,socks5&timeout=5000&country=all&ssl=all&anonymity=elite",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt"
]

GEONODE_API = "https://proxylist.geonode.com/api/proxy-list?limit=300&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps%2Csocks4%2Csocks5"

def fetch_proxies():
    """Fetches a list of potential proxies from public sources."""
    proxies = set()
    print("🕵️‍♂️ Proxy Hunter: Scouring the web for proxies...")
    
    # 1. Fetch from plain text sources
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                protocol = "http"
                if "socks4" in url: protocol = "socks4"
                elif "socks5" in url: protocol = "socks5"
                
                html_lines = r.text.splitlines()
                for line in html_lines:
                    p = line.strip()
                    if ":" in p and " " not in p:
                        # Format: protocol://ip:port
                        if "://" not in p:
                            proxies.add(f"{protocol}://{p}")
                        else:
                            proxies.add(p)
        except Exception:
            pass

    # 2. Fetch from Geonode (JSON API)
    try:
        r = requests.get(GEONODE_API, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data.get('data', []):
                ip = item.get('ip')
                port = item.get('port')
                protocols = item.get('protocols', [])
                
                if ip and port:
                    # Prefer socks5 > socks4 > http
                    if "socks5" in protocols:
                        proxies.add(f"socks5://{ip}:{port}")
                    elif "socks4" in protocols:
                        proxies.add(f"socks4://{ip}:{port}")
                    else:
                        proxies.add(f"http://{ip}:{port}")
    except Exception as e:
        print(f"⚠️ Geonode fetch error: {e}")
            
    proxy_list = list(proxies)
    print(f"📦 Collected {len(proxy_list)} candidates.")
    random.shuffle(proxy_list)
    return proxy_list

def check_proxy(proxy):
    """Checks if a proxy can connect to Instagram and returns (proxy, latency)."""
    try:
        start_time = time.time()
        # requests support for socks via 'socks5://user:pass@host:port'
        # The proxy string already contains the protocol scheme (http://, socks5://, etc)
        proxies_dict = {"http": proxy, "https": proxy}
        
        # VERY Strict timeout (3s) to filter out slow garbage immediately
        r = requests.get("https://www.instagram.com", 
                         proxies=proxies_dict, 
                         timeout=3)
        if r.status_code == 200:
            latency = time.time() - start_time
            return (proxy, latency)
    except:
        pass
    return None

def get_working_proxy(max_checked=2000):
    """Finds the FASTEST working proxy among candidates."""
    candidates = fetch_proxies()
    candidates = candidates[:max_checked]
    
    print(f"⚡ Deep Scanning top {len(candidates)} candidates (Target: Find 5 good ones)...")
    
    good_proxies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_proxy = {executor.submit(check_proxy, p): p for p in candidates}
        
        # We don't want to wait for ALL 500 if we find good ones early.
        # But we also don't want just the FIRST one (migth be slow).
        # Strategy: Iterate as they complete. Collect up to 5 good ones, then pick winner.
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            if result:
                proxy, latency = result
                print(f"   🟢 Candidate: {proxy} (Latency: {latency:.2f}s)")
                good_proxies.append((proxy, latency))
                
                # Stop if we found 5 usable proxies to choose from
                if len(good_proxies) >= 5:
                    print("✋ Found enough candidates. Stopping search.")
                    break
        
        # If we exhausted the listed futures or broke early, cancel remaining? 
        # ( Python executor context handles shutdown, but pending futures run. It's fine.)
    
    if not good_proxies:
        print("❌ No working proxies found.")
        return []
        
    # Sort by latency (lowest first)
    good_proxies.sort(key=lambda x: x[1])
    
    # Return top 5
    return [p[0] for p in good_proxies[:5]]

if __name__ == "__main__":
    # Test run
    print(get_working_proxy())
