import requests
import json

try:
    print("Probing http://127.0.0.1:8082/v1/mc/map ...")
    resp = requests.get("http://127.0.0.1:8082/v1/mc/map", timeout=5)
    data = resp.json()
    
    print("\nKeys received:", list(data.keys()))
    
    if "changed" in data:
        print("RESULT: NEW_VERSION_ACTIVE (Good)")
        print(f"Version: {data.get('version')}")
    else:
        print("RESULT: OLD_VERSION_DETECTED (Bad - Restart Required)")

except Exception as e:
    print(f"RESULT: FAILED ({e})")
