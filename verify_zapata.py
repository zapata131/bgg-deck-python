from app.services.bgg import fetch_collection
import json

username = "zapata131"
print(f"Fetching collection for {username}...")
data = fetch_collection(username)

if data:
    if 'status' in data and data['status'] == 202:
        print("Request queued by BGG (202 Accepted). Try again later.")
    else:
        items = data.get('items', {}).get('item', [])
        if isinstance(items, dict):
            items = [items]
        print(f"Successfully fetched {len(items)} items.")
        # print(json.dumps(items[0], indent=2)) # Print first item for inspection
else:
    print("Failed to fetch collection.")
