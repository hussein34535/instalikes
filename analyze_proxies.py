import requests

def analyze_proxy(proxy_url):
    print(f"\n🔍 Analyzing Proxy: {proxy_url.split('@')[1]} ...")
    
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    try:
        # 1. Check IP and ISP
        r = requests.get("http://ip-api.com/json", proxies=proxies, timeout=10)
        data = r.json()
        
        if data['status'] == 'fail':
            print("❌ Proxy failed connection test.")
            return

        print(f"   ✅ IP: {data['query']}")
        print(f"   🌍 Country: {data['country']}")
        print(f"   🏢 ISP: {data['isp']}")
        print(f"   🏢 Org: {data['org']}")
        
        # Heuristic for Datacenter
        dc_keywords = ['hosting', 'datacenter', 'cloud', 'vps', 'digitalocean', 'google', 'amazon', 'microsoft', 'hetzner', 'ovh', 'linode']
        isp_lower = data['isp'].lower()
        org_lower = data['org'].lower()
        
        is_dc = any(k in isp_lower for k in dc_keywords) or any(k in org_lower for k in dc_keywords)
        
        if is_dc:
            print("   ⚠️  TYPE: DATACENTER / HOSTING DETECTED")
            print("   🚨 RESULT: Instagram BLOCKS this type automatically.")
        else:
            print("   ✅ TYPE: Looks like Residential/Business.")
            print("   ✨ RESULT: Should work (unless blacklisted specifically).")
            
    except Exception as e:
        print(f"❌ Error analyzing proxy: {e}")

if __name__ == "__main__":
    proxies = [
        "http://ivkgcgdd:gkzg2d1l13fd@142.111.48.253:7030",
        "http://ivkgcgdd:gkzg2d1l13fd@23.95.150.145:6114"
    ]
    
    print("🔬 Forensic Proxy Analysis")
    for p in proxies:
        analyze_proxy(p)
