import requests

GOOGLE_API_KEY = "AIzaSyADJa3n-ytrIk9TdnJKHyGt-c4rC7nnxI8"  # ← PUT YOUR KEY HERE

# Test with Tallinn address
address = "Pirita tee 13, Tallinn, Estonia"

url = "https://maps.googleapis.com/maps/api/geocode/json"
params = {
    "address": address,
    "key": GOOGLE_API_KEY
}

print(f"Testing Google API with: {address}\n")

try:
    response = requests.get(url, params=params)
    data = response.json()

    print(f"Status: {data['status']}")

    if data['status'] == 'OK':
        loc = data['results'][0]['geometry']['location']
        print(f"✅ SUCCESS!")
        print(f"Coordinates: [{loc['lat']}, {loc['lng']}]")
    else:
        print(f"❌ FAILED: {data.get('error_message', 'Unknown error')}")

except Exception as e:
    print(f"❌ ERROR: {e}")