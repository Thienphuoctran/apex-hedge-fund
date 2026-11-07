import urllib.request
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://www.tiktok.com/@tranphuoc262'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fetched {len(html)} chars from {url}")
        
        # Save raw html
        with open('data/tiktok_profile_raw.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        m1 = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html)
        if m1:
            print("Found __UNIVERSAL_DATA_FOR_REHYDRATION__!")
            data = json.loads(m1.group(1))
            default_scope = data.get('__DEFAULT_SCOPE__', {})
            user_detail = default_scope.get('webapp.user-detail', {})
            user_info = user_detail.get('userInfo', {})
            user = user_info.get('user', {})
            stats = user_info.get('stats', {})
            print(f"User: {user.get('nickname')} (@{user.get('uniqueId')})")
            print(f"Stats: Follower: {stats.get('followerCount')}, Following: {stats.get('followingCount')}, Heart: {stats.get('heartCount')}")
            
            # Check item list or liked items if included
            item_list = user_detail.get('itemList', [])
            print(f"ItemList in hydration: {len(item_list)}")
            
            # Print structure
            print("webapp.user-detail keys:", list(user_detail.keys()))
        else:
            print("Not found rehydration script")
except Exception as e:
    print("Error fetching profile:", e)
