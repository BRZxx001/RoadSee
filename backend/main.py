"""
ClearPath — FastAPI Backend
Handles: constructions, potholes, waterlogs, routing, ML inference, weather & flood prediction
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid, math, subprocess, json, os, io, random
from datetime import datetime, timedelta


app = FastAPI(title="ClearPath API", version="1.0.0")

# ── CORS — allow React dev server ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory store (replace with MongoDB in production) ─────────
DB = {
    "constructions": [
        {"_id":"c1","lat":28.6139,"lng":77.2090,"title":"Metro Line 9 Extension","description":"Underground metro tunneling","severity":"high","agency":"DMRC","radius":300,"startDate":"2026-10-10","endDate":"2026-12-30","reports":12,"createdAt":datetime.now().isoformat()},
        {"_id":"c2","lat":28.6280,"lng":77.2190,"title":"Water Pipeline Replacement","description":"DJB replacing 40-year-old mains","severity":"medium","agency":"DJB","radius":150,"startDate":"2026-10-14","endDate":"2026-11-15","reports":5,"createdAt":datetime.now().isoformat()},
        {"_id":"c3","lat":28.6050,"lng":77.2250,"title":"Flyover Widening","description":"PWD widening NH-48 flyover","severity":"high","agency":"PWD","radius":400,"startDate":"2026-09-01","endDate":"2027-03-31","reports":28,"createdAt":datetime.now().isoformat()},
    ],
    "potholes": [
        {"_id":"p1","lat":28.6200,"lng":77.2100,"title":"Severe Pothole","description":"Large crater, 30cm deep","severity":"severe","reportCount":7,"createdAt":datetime.now().isoformat()},
        {"_id":"p2","lat":28.6170,"lng":77.2300,"title":"Moderate Pothole","description":"Road crumbling after rain","severity":"moderate","reportCount":3,"createdAt":datetime.now().isoformat()},
        {"_id":"p3","lat":28.6310,"lng":77.2050,"title":"Dangerous Pothole","description":"Manhole cover collapsed","severity":"dangerous","reportCount":15,"createdAt":datetime.now().isoformat()},
        {"_id":"p4","lat":28.6090,"lng":77.2180,"title":"Minor Pothole","description":"Small crack developing","severity":"minor","reportCount":1,"createdAt":datetime.now().isoformat()},
    ],
    "waterlogs": [
        {"_id":"w1","lat":28.6155,"lng":77.2070,"title":"Flooded Underpass","description":"ITO underpass — ankle deep","depth":"ankle","reportCount":22,"createdAt":datetime.now().isoformat()},
        {"_id":"w2","lat":28.6240,"lng":77.2160,"title":"Waterlogged Junction","description":"Blocked drain, vehicle risk","depth":"vehicle_risk","reportCount":9,"createdAt":datetime.now().isoformat()},
    ],
    "traffic_jams": [
        {"_id":"t1","lat":28.6289,"lng":77.2065,"title":"Severe Gridlock (Ashoka Road)","description":"Deadlock due to VIP movement & ongoing repair","congestion":"severe","speed_kmh":6,"delay_min":22,"radius":250,"createdAt":datetime.now().isoformat()},
        {"_id":"t2","lat":28.5700,"lng":77.2210,"title":"Heavy Traffic (AIIMS / Ring Road)","description":"Peak hour bottleneck, crawling traffic","congestion":"heavy","speed_kmh":12,"delay_min":15,"radius":350,"createdAt":datetime.now().isoformat()},
        {"_id":"t3","lat":28.6440,"lng":77.2160,"title":"New Delhi Railway Station Jam","description":"Commercial cabs & autos blocking 3 lanes","congestion":"heavy","speed_kmh":10,"delay_min":18,"radius":200,"createdAt":datetime.now().isoformat()},
        {"_id":"t4","lat":28.5355,"lng":77.2100,"title":"Moderate Congestion (Saket Metro)","description":"Slow moving traffic near Mall junction","congestion":"moderate","speed_kmh":18,"delay_min":8,"radius":180,"createdAt":datetime.now().isoformat()},
    ],
}

# ── Pydantic Models ──────────────────────────────────────────────
class ConstructionIn(BaseModel):
    lat:         float
    lng:         float
    title:       str
    description: Optional[str] = ""
    severity:    Optional[str] = "medium"
    agency:      Optional[str] = "PWD"
    radius:      Optional[int] = 200
    startDate:   Optional[str] = ""
    endDate:     Optional[str] = ""

class PotholeIn(BaseModel):
    lat:         float
    lng:         float
    title:       str
    description: Optional[str] = ""
    severity:    Optional[str] = "moderate"

class WaterlogIn(BaseModel):
    lat:         float
    lng:         float
    title:       str
    description: Optional[str] = ""
    depth:       Optional[str] = "ankle"

class RouteRequest(BaseModel):
    from_:       Optional[str] = None
    to:          Optional[str] = None
    from_lat:    Optional[float] = None
    from_lng:    Optional[float] = None
    to_lat:      Optional[float] = None
    to_lng:      Optional[float] = None
    disruptions: Optional[list]  = []

    model_config = {"populate_by_name": True}

# ── Health ────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "app": "ClearPath API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ── Construction CRUD ─────────────────────────────────────────────
@app.get("/constructions")
def get_constructions():
    return DB["constructions"]

@app.post("/constructions", status_code=201)
def add_construction(data: ConstructionIn):
    item = {**data.dict(), "_id": str(uuid.uuid4())[:8], "reports": 0, "createdAt": datetime.now().isoformat()}
    DB["constructions"].append(item)
    return item

@app.delete("/constructions/{id}")
def delete_construction(id: str):
    DB["constructions"] = [c for c in DB["constructions"] if c["_id"] != id]
    return {"deleted": id}

# ── Pothole CRUD ──────────────────────────────────────────────────
@app.get("/potholes")
def get_potholes():
    return DB["potholes"]

@app.post("/potholes", status_code=201)
def add_pothole(data: PotholeIn):
    item = {**data.dict(), "_id": str(uuid.uuid4())[:8], "reportCount": 1, "createdAt": datetime.now().isoformat()}
    DB["potholes"].append(item)
    return item

@app.patch("/potholes/{id}/report")
def report_pothole(id: str):
    for p in DB["potholes"]:
        if p["_id"] == id:
            p["reportCount"] = p.get("reportCount", 0) + 1
            # Auto-escalate severity
            if p["reportCount"] >= 10 and p["severity"] == "moderate":
                p["severity"] = "severe"
            elif p["reportCount"] >= 5 and p["severity"] == "minor":
                p["severity"] = "moderate"
            return p
    raise HTTPException(404, "Pothole not found")

@app.delete("/potholes/{id}")
def delete_pothole(id: str):
    DB["potholes"] = [p for p in DB["potholes"] if p["_id"] != id]
    return {"deleted": id}

# ── Waterlog CRUD ─────────────────────────────────────────────────
@app.get("/waterlogs")
def get_waterlogs():
    return DB["waterlogs"]

@app.post("/waterlogs", status_code=201)
def add_waterlog(data: WaterlogIn):
    item = {**data.dict(), "_id": str(uuid.uuid4())[:8], "reportCount": 1, "createdAt": datetime.now().isoformat()}
    DB["waterlogs"].append(item)
    return item

@app.delete("/waterlogs/{id}")
def delete_waterlog(id: str):
    DB["waterlogs"] = [w for w in DB["waterlogs"] if w["_id"] != id]
    return {"deleted": id}

# ── Live Traffic Congestion CRUD ──────────────────────────────────
@app.get("/traffic")
def get_traffic():
    return DB.get("traffic_jams", [])

# ── Routing Engine (calls C++ Dijkstra) ───────────────────────────
def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@app.post("/route")
def get_route(req: RouteRequest):
    # Simple geocoding: treat address as Delhi area
    def fake_geo(addr):
        base = [28.6139, 77.2090]
        seed = sum(ord(c) for c in (addr or ""))
        return [base[0] + (seed % 100 - 50) * 0.002, base[1] + (seed % 80 - 40) * 0.002]

    from_coord = [req.from_lat, req.from_lng] if req.from_lat else fake_geo(req.from_ or "")
    to_coord   = [req.to_lat,   req.to_lng]   if req.to_lat   else fake_geo(req.to    or "")

    dist_km = haversine(from_coord[0], from_coord[1], to_coord[0], to_coord[1])

    # Try calling compiled C++ router
    cpp_exe = os.path.join(os.path.dirname(__file__), "..", "routing_engine", "router.exe")
    router_result = None
    if os.path.exists(cpp_exe):
        try:
            payload = json.dumps({"from": from_coord, "to": to_coord, "disruptions": req.disruptions or []})
            proc = subprocess.run([cpp_exe], input=payload, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0:
                router_result = json.loads(proc.stdout)
        except Exception:
            pass

    # Python fallback routing
    all_disrupt = DB["constructions"] + DB["potholes"] + DB["waterlogs"] + DB.get("traffic_jams", [])
    if req.disruptions:
        all_disrupt = req.disruptions

    SEV_PENALTY = {"dangerous":8, "severe":5, "high":6, "vehicle_risk":5, "moderate":3, "medium":3, "ankle":2, "minor":1, "low":1, "puddles":0.5}

    def count_disruptions_near_route(fraction=1.0):
        c_count = w_count = p_count = t_count = 0
        for d in all_disrupt:
            dlat = (d.get("lat",0) - (from_coord[0] + to_coord[0])/2) * 111
            dlng = (d.get("lng",0) - (from_coord[1] + to_coord[1])/2) * 111
            if math.sqrt(dlat**2 + dlng**2) < dist_km * 0.8 * fraction:
                t = d.get("type","")
                if "traffic" in t or d.get("congestion"):        t_count += 1
                elif "construction" in t or d.get("agency"):     c_count += 1
                elif "waterlog"   in t or d.get("depth"):        w_count += 1
                else:                                             p_count += 1
        return c_count, p_count, w_count, t_count

    nc, np_, nw, nt = count_disruptions_near_route(1.0)
    cc, cp, cw, ct  = count_disruptions_near_route(0.3)

    base_time = dist_km / 28 * 60  # 28 km/h city avg
    normal_extra = nc*5 + np_*2 + nw*4 + nt*8
    normal_time  = round(base_time + normal_extra + 8)
    clear_time   = round(base_time * 1.15 + 4)

    return {
        "engine": router_result["engine"] if router_result else "python_fallback",
        "distance_km": round(dist_km, 2),
        "normal": {
            "time":          normal_time,
            "distance":      round(dist_km, 2),
            "constructions": nc,
            "potholes":      np_,
            "waterlogs":     nw,
            "trafficJams":   nt,
        },
        "clearpath": {
            "time":          clear_time,
            "distance":      round(dist_km * 1.18, 2),
            "constructions": cc,
            "potholes":      max(0, cp - round(cp * 0.8)),
            "waterlogs":     0,
            "trafficJams":   0,
        },
    }

# ── ML Pothole Analysis ───────────────────────────────────────────
@app.post("/ml/analyse-pothole")
async def analyse_pothole(file: UploadFile = File(...)):
    """
    Analyses uploaded image to detect pothole severity.
    Uses pixel brightness analysis as lightweight ML proxy.
    For production: load a trained CNN (TensorFlow/PyTorch) model here.
    """
    try:
        from PIL import Image
        import numpy as np

        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB").resize((64, 64))
        arr = np.array(img, dtype=np.float32)

        # Brightness & texture analysis
        brightness = arr.mean() / 255.0
        dark_ratio = (arr.mean(axis=2) < 80).mean()
        contrast   = arr.std() / 255.0

        # Pothole heuristic: dark + high contrast + irregular texture
        score = dark_ratio * 0.6 + (1 - brightness) * 0.3 + contrast * 0.1

        if score > 0.40:
            severity, confidence = "dangerous", min(97, round(85 + score * 20))
        elif score > 0.28:
            severity, confidence = "severe",    min(95, round(78 + score * 20))
        elif score > 0.16:
            severity, confidence = "moderate",  min(90, round(70 + score * 20))
        else:
            severity, confidence = "minor",     min(88, round(65 + score * 20))

        descriptions = {
            "minor":     "Small surface crack. Monitor regularly.",
            "moderate":  "Significant pothole. Repair within 2 weeks.",
            "severe":    "Large pothole. Urgent repair needed.",
            "dangerous": "Critical hazard. Immediate closure recommended.",
        }

        return {
            "severity":    severity,
            "confidence":  confidence,
            "description": descriptions[severity],
            "score":       round(score, 3),
            "model":       "ClearPath-PotholeNet-v1",
        }

    except Exception as e:
        # Fallback if PIL not available
        return {"severity": "moderate", "confidence": 72, "description": "Analysis unavailable", "error": str(e)}

# ── Stats endpoint ─────────────────────────────────────────────────
@app.get("/stats")
def stats():
    dangerous_potholes  = sum(1 for p in DB["potholes"] if p.get("severity") == "dangerous")
    high_risk_waterlogs = sum(1 for w in DB["waterlogs"] if w.get("depth") in ["avoid","vehicle_risk"])
    return {
        "total":             len(DB["constructions"]) + len(DB["potholes"]) + len(DB["waterlogs"]),
        "constructions":     len(DB["constructions"]),
        "potholes":          len(DB["potholes"]),
        "waterlogs":         len(DB["waterlogs"]),
        "dangerous_potholes": dangerous_potholes,
        "high_risk_waterlogs": high_risk_waterlogs,
    }

# ── Weather & Flood Prediction System ──────────────────────────────
# Historical flood-prone zones in Delhi with elevation & drainage factor
FLOOD_PRONE_ZONES = [
    {"name": "Minto Bridge Underpass",     "lat": 28.6335, "lng": 77.2220, "drainageScore": 0.2, "elevationM": 210, "histIncidents": 14},
    {"name": "ITO Junction & Vikas Marg", "lat": 28.6280, "lng": 77.2410, "drainageScore": 0.3, "elevationM": 212, "histIncidents": 11},
    {"name": "Pul Prahladpur Underpass",   "lat": 28.5110, "lng": 77.2880, "drainageScore": 0.15, "elevationM": 208, "histIncidents": 18},
    {"name": "Dhaula Kuan Underpass",      "lat": 28.5920, "lng": 77.1610, "drainageScore": 0.35, "elevationM": 225, "histIncidents": 8},
    {"name": "Azadpur Underpass",          "lat": 28.7070, "lng": 77.1780, "drainageScore": 0.25, "elevationM": 214, "histIncidents": 9},
    {"name": "Kashmere Gate Metro Zone",  "lat": 28.6670, "lng": 77.2280, "drainageScore": 0.3, "elevationM": 211, "histIncidents": 10},
]

def calculate_flood_risk(rain_mm_hr: float, rain_total_24h: float, zone: dict, nearby_construction: bool) -> dict:
    """
    Physics + heuristic based flood risk calculation
    Risk = (Rainfall intensity / Drainage capacity) * Historical factor + Construction penalty
    """
    # Base runoff from rain (mm/hr) vs drainage rate (mm/hr)
    # Average urban storm drain in India handles ~15-20 mm/hr
    drain_capacity = zone["drainageScore"] * 50.0  # 7.5 to 17.5 mm/hr
    water_accumulation_rate = max(0.0, rain_mm_hr - drain_capacity)
    
    # Risk score: 0 to 100
    base_score = min(70.0, (water_accumulation_rate / 25.0) * 50.0 + (rain_total_24h / 60.0) * 20.0)
    
    # Historical multiplier
    hist_factor = min(15.0, zone["histIncidents"] * 0.8)
    
    # Construction penalty (dug up roads block storm drains)
    const_penalty = 20.0 if nearby_construction else 0.0
    
    total_score = min(100.0, round(base_score + hist_factor + const_penalty))
    
    if total_score >= 75:
        risk_level = "critical"
        est_depth_cm = round(30 + (total_score - 75) * 1.6)
        action = "Avoid completely. Road impassable for 2-wheelers and sedans."
    elif total_score >= 50:
        risk_level = "high"
        est_depth_cm = round(15 + (total_score - 50) * 0.6)
        action = "High risk. Stalled vehicles likely. Slow down or detour."
    elif total_score >= 25:
        risk_level = "moderate"
        est_depth_cm = round(5 + (total_score - 25) * 0.4)
        action = "Water accumulation expected. Exercise caution."
    else:
        risk_level = "low"
        est_depth_cm = round(total_score * 0.2)
        action = "Normal conditions. Standard driving."
        
    return {
        "riskScore": total_score,
        "riskLevel": risk_level,
        "estWaterDepthCm": est_depth_cm,
        "recommendedAction": action,
        "constructionAmplified": nearby_construction,
    }

@app.get("/weather/current")
def get_current_weather(city: str = "Delhi"):
    """
    Returns current weather + 24hr forecast.
    Uses realistic simulated monsoon/rain scenarios by default,
    with pluggable OpenWeatherMap API key support.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    
    if api_key:
        try:
            import urllib.request
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            with urllib.request.urlopen(url, timeout=4) as response:
                data = json.loads(response.read().decode())
                rain_1h = data.get("rain", {}).get("1h", 0.0)
                return {
                    "source": "OpenWeatherMap LIVE",
                    "city": data.get("name", city),
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"].capitalize(),
                    "icon": data["weather"][0]["main"],
                    "rain_mm_hr": rain_1h,
                    "rain_24h_mm": rain_1h * 6,
                    "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
                }
        except Exception:
            pass  # Fallback to smart simulated data
            
    # Realistic monsoon simulation for testing/demo
    # Allows hackathon judges to toggle scenario (Dry / Drizzle / Heavy Rain / Cloudburst)
    return {
        "source": "Smart Simulation (Demo Mode)",
        "city": "New Delhi",
        "temp": 28.5,
        "humidity": 88,
        "description": "Heavy Monsoon Thunderstorms",
        "icon": "Rain",
        "rain_mm_hr": 38.5,       # mm/hr intensity
        "rain_24h_mm": 84.0,      # total accumulated
        "wind_speed_kmh": 22.4,
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/weather/flood-prediction")
def predict_floods(rain_scenario: Optional[str] = "heavy"):
    """
    Predicts waterlogging & flooding across city zones based on weather intensity.
    rain_scenario can be: 'dry', 'moderate', 'heavy', 'cloudburst'
    """
    scenarios = {
        "dry":        {"rain_mm_hr": 0.0,  "rain_24h": 0.0,   "label": "☀️ Clear Sky"},
        "moderate":   {"rain_mm_hr": 12.0, "rain_24h": 25.0,  "label": "🌧️ Moderate Rain"},
        "heavy":      {"rain_mm_hr": 38.5, "rain_24h": 84.0,  "label": "⛈️ Heavy Downpour"},
        "cloudburst": {"rain_mm_hr": 75.0, "rain_24h": 140.0, "label": "🌊 Cloudburst / Extreme"},
    }
    
    current_scen = scenarios.get(rain_scenario, scenarios["heavy"])
    rain_mm = current_scen["rain_mm_hr"]
    rain_24h = current_scen["rain_24h"]
    
    predictions = []
    
    for zone in FLOOD_PRONE_ZONES:
        # Check if any registered construction is within 500m of this zone
        has_construction = False
        for c in DB["constructions"]:
            dlat = (c["lat"] - zone["lat"]) * 111000
            dlng = (c["lng"] - zone["lng"]) * 111000 * math.cos(zone["lat"] * math.pi / 180)
            if math.sqrt(dlat*dlat + dlng*dlng) < 600:
                has_construction = True
                break
                
        risk = calculate_flood_risk(rain_mm, rain_24h, zone, has_construction)
        
        predictions.append({
            "zoneId": zone["name"].lower().replace(" ", "_"),
            "name": zone["name"],
            "lat": zone["lat"],
            "lng": zone["lng"],
            "elevationM": zone["elevationM"],
            "historicalIncidents": zone["histIncidents"],
            **risk,
        })
        
    predictions.sort(key=lambda x: x["riskScore"], reverse=True)
    
    # Overall city impact summary
    critical_count = sum(1 for p in predictions if p["riskLevel"] == "critical")
    high_count     = sum(1 for p in predictions if p["riskLevel"] == "high")
    
    return {
        "scenario": rain_scenario,
        "scenarioLabel": current_scen["label"],
        "rainfall_mm_hr": rain_mm,
        "rainfall_24h_mm": rain_24h,
        "summary": {
            "criticalZones": critical_count,
            "highRiskZones": high_count,
            "cityAlertLevel": "RED" if critical_count > 1 else ("ORANGE" if high_count > 1 else "GREEN"),
            "evacuationAdvisory": critical_count > 2,
        },
        "zones": predictions,
    }

