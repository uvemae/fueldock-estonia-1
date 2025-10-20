import json
import random

# Load marina coordinates
with open('marina_coordinates.json', 'r', encoding='utf-8') as f:
    marina_coords = {m['publicId']: m['coordinates'] for m in json.load(f)}

with open('eesti_sadamad.json', 'r', encoding='utf-8') as f:
    all_marinas = json.load(f)

# 49 real fuel stations
real_fuel_stations = {
    151: "Olerex", 1401: "Olerex", 326: "Alexela", 250: "Other", 207: "Other",
    348: "Other", 201: "Alexela", 370: "Other", 313: "Other", 390: "Other",
    302: "Other", 347: "Other", 357: "Other", 371: "Alexela", 374: "Other",
    1403: "Other", 373: "Other", 382: "Other", 1600: "Olerex", 318: "Other",
    6600: "Other", 1907: "Alexela", 51: "Other", 1452: "Other", 324: "Alexela",
    368: "Other", 168: "Other", 330: "Other", 154: "Other", 344: "Alexela",
    2101: "Other", 402: "Olerex", 360: "Other", 389: "Other", 804: "Other",
    1201: "Other", 2115: "Other", 452: "Other", 3934: "Other", 1210: "Olerex",
    163: "Alexela", 1207: "Alexela", 2266: "Other", 450: "Olerex", 332: "Other",
    2114: "Other", 376: "Other", 1966: "Other", 404: "Other"
}

stations = []
used_ids = set()

# 1. Real fuel stations
for pub_id, station_type in real_fuel_stations.items():
    marina = next((m for m in all_marinas if m['publicId'] == pub_id), None)
    if marina and pub_id in marina_coords:
        used_ids.add(pub_id)
        stations.append({
            "id": f"station-{pub_id}",
            "name": marina['name'],
            "location": marina['address'].split(',')[0],
            "coordinates": marina_coords[pub_id],
            "hasStation": True,
            "stationType": station_type,
            "fuelLevel": random.randint(0, 100),
            "capacity": random.choice([3000, 5000, 8000]),
            "fuels": {"diesel": {"available": True, "price": 1.54},
                     "e95": {"available": True, "price": 1.69},
                     "e98": {"available": True, "price": 1.79}},
            "payment": ["card", "qr", "app"] if station_type == "Alexela" else ["card", "qr"],
            "hours": "24/7"
        })

# 2. 100 FuelDock
remaining = [m for m in all_marinas if m['publicId'] not in used_ids]
random.shuffle(remaining)
for marina in remaining[:100]:
    if marina['publicId'] in marina_coords:
        used_ids.add(marina['publicId'])
        stations.append({
            "id": f"fueldock-{marina['publicId']}",
            "name": marina['name'],
            "location": marina['address'].split(',')[0],
            "coordinates": marina_coords[marina['publicId']],
            "hasStation": True,
            "stationType": "FuelDock",
            "fuelLevel": random.randint(0, 100),
            "capacity": random.choice([3000, 5000]),
            "fuels": {"diesel": {"available": True, "price": 1.54},
                     "e98": {"available": True, "price": 1.79}},
            "payment": ["card", "qr"],
            "hours": "24/7"
        })

# 3. No fuel
for marina in all_marinas:
    if marina['publicId'] not in used_ids and marina['publicId'] in marina_coords:
        stations.append({
            "id": f"no-fuel-{marina['publicId']}",
            "name": marina['name'],
            "location": marina['address'].split(',')[0],
            "coordinates": marina_coords[marina['publicId']],
            "hasStation": False
        })

# Save
with open('src/data/stations.json', 'w', encoding='utf-8') as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

print(f"✅ Created {len(stations)} marinas with REAL coordinates!")
print(f"   • {sum(1 for s in stations if s.get('stationType') == 'Alexela')} Alexela")
print(f"   • {sum(1 for s in stations if s.get('stationType') == 'Olerex')} Olerex")
print(f"   • {sum(1 for s in stations if s.get('stationType') == 'FuelDock')} FuelDock")
print(f"   • {sum(1 for s in stations if s.get('stationType') == 'Other')} Other")
print(f"   • {sum(1 for s in stations if not s.get('hasStation'))} No fuel")