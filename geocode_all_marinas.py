import json
import requests
import time

GOOGLE_API_KEY = "AIzaSyADJa3n-ytrIk9TdnJKHyGt-c4rC7nnxI8"  # ← PUT KEY

# Load marinas
with open('eesti_sadamad.json', 'r', encoding='utf-8') as f:
    marinas = json.load(f)

# Geocode function
def geocode(address):
    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
                           params={"address": address + ", Estonia", "key": GOOGLE_API_KEY})
    data = response.json()
    if data['status'] == 'OK':
        loc = data['results'][0]['geometry']['location']
        return [loc['lat'], loc['lng']]
    return None

# Process all marinas
output = []
for i, marina in enumerate(marinas):
    print(f"{i+1}/{len(marinas)}: {marina['name'][:30]}...", end=" ")

    coords = geocode(marina['address'])

    if coords:
        output.append({
            "publicId": marina['publicId'],
            "name": marina['name'],
            "address": marina['address'],
            "coordinates": coords
        })
        print(f"✓ {coords}")
    else:
        print("✗ FAILED")

    time.sleep(0.1)  # Rate limit

# Save
with open('marina_coordinates.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ Saved {len(output)} marinas to marina_coordinates.json")