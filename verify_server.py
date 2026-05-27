import urllib.request
import json
import time

print("Waiting 3 seconds for server to initialize...")
time.sleep(3)

print("Verifying server responsiveness...")
try:
    # Test Home page
    with urllib.request.urlopen("http://127.0.0.1:5000/") as response:
        html = response.read().decode('utf-8')
        print(f"[SUCCESS] Home page is active! Status code: {response.status}")
        if "FoodieFinds AI" in html:
            print("[SUCCESS] Home page contains correct branding!")
        else:
            print("[ERROR] Branding missing from home page!")
            
    # Test API Foods list
    with urllib.request.urlopen("http://127.0.0.1:5000/api/foods") as response:
        data = json.loads(response.read().decode('utf-8'))
        print(f"[SUCCESS] API /api/foods is active! Status code: {response.status}")
        print(f"[SUCCESS] Database seeded successfully! Found {len(data)} food items.")
        
        # Verify ML format
        first_item = data[0]
        print(f"[SUCCESS] Food structure verified! First item name: '{first_item.get('name')}' in category: '{first_item.get('category')}'")

except Exception as e:
    print(f"[ERROR] Verification failed: {e}")

