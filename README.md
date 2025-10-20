# ⛽ FuelDock Estonia

Portable fuel station locator for Estonian marinas. MVP prototype for startup business class presentation.

## 🚀 Live Demo

**[https://uvemae.github.io/fueldock-estonia-1/](https://uvemae.github.io/fueldock-estonia-1/)**

## 📋 Features

- 🗺️ Interactive map of 252 Estonian marinas
- ⛽ 149 fuel stations (Alexela, Olerex, FuelDock)
- 🔍 Search by marina name/location
- 💳 Payment flow mockup (QR/Card)
- 📊 Transaction history
- 📱 PWA - works on mobile

## 🛠️ Tech Stack

- Vue 3 + Vite
- Tailwind CSS
- Leaflet.js (maps)
- Google Maps Geocoding API

## 💡 Business Model

**B2B2C:**
- Gas companies (Alexela/Olerex) provide fuel
- Municipalities rent dock space
- Boat owners get convenient 24/7 refueling

**Problem:** Only 8 marinas have fuel stations, but Estonia has 250+ marinas.

## 🚀 Local Setup
```bash
npm install
npm run dev
```

## 📦 Build
```bash
npm run build
```

## 📄 Data

- `eesti_sadamad.json` - 252 Estonian marinas
- `marina_coordinates.json` - Google-geocoded locations
- `src/data/stations.json` - Generated fuel station data

## 👤 Author

**Uve Ellermäe**  
TalTech Business IT Student  
[LinkedIn](https://linkedin.com/in/uve-mae) | [GitHub](https://github.com/uvemae)

---

**MVP Prototype** - October 2025