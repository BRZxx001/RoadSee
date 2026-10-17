# RoadSee 🛣️

> **AI-Powered Urban Mobility, Multi-Modal Disruption Navigation & Disaster Resilience Engine**

RoadSee is a unified smart city mobility platform that dynamically solves the challenges of uncoordinated roadworks, undetected dangerous potholes, monsoon waterlogging, and sudden traffic gridlocks.

---

## 🌟 Key Features

1. **Dynamic "Best Route" Planning**:
   - Avoids floods, dangerous potholes, unannounced road digs, and severe traffic jams.
   - Shows real-time comparative time saved inline (e.g. `60 min (saves 26 min)`).
   - Powered by a high-performance C++ Dijkstra algorithm (< 2ms execution time).

2. **Predictive Urban Flood Inundation Engine**:
   - Simulates rainfall scenarios (*Dry, Moderate, Heavy, Cloudburst*).
   - Predicts street-level flood depth based on rainfall rate, land elevation, and drain blockage.

3. **AI Pothole Severity Classifier**:
   - Automated 4-tier damage classification (*Minor, Moderate, Severe, Dangerous*).
   - Real-time computer vision scoring for municipal priority dispatch.

4. **Live Disruption & Traffic Sensing**:
   - Models congestion nodes and delay metrics across OpenStreetMap (OSM) segments.
   - Tracks 5 live disruption vectors simultaneously.

5. **Celestial Day / Night Mode**:
   - Interactive theme switch powered by custom Sun ☀️ and Moon 🌙 visual icons.
   - 100% free dark neon OpenStreetMap cartography requiring zero external API keys.

6. **City Authority Command Console**:
   - Municipal repair queue prioritized by composite severity index.
   - Cross-agency excavation overlap detector (PWD, Telecom, Water Board).

---

## 🏗️ Architecture & Tech Stack

- **Frontend**: React 18, Vite, Leaflet.js, OpenStreetMap, CSS3 Variables.
- **Backend**: FastAPI (Python 3.11), Uvicorn ASGI.
- **Routing Engine**: C++17 (compiled Dijkstra with dynamic risk penalty weights).
- **Vision Pipeline**: PyTorch / OpenCV pothole geometry analysis.

---

## 🚀 Quick Start Guide

### 1. Start Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📄 Presentation & Pitch Masterfile
A complete slide-by-slide presentation blueprint, technical architecture breakdown, and Q&A defense document is available in `RoadSee_Complete_Project_Presentation_Masterfile.docx`.
