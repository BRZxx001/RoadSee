import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';

const AppContext = createContext(null);

const API = 'http://localhost:8000';

// ── Seed data shown when backend is offline ──────────────────────
const SEED = {
  constructions: [
    { _id: 'c1', lat: 28.6139, lng: 77.2090, title: 'Metro Line 9 Extension', description: 'Underground metro tunneling work', severity: 'high', agency: 'DMRC', radius: 300, startDate: '2026-10-10', endDate: '2026-12-30', reports: 12 },
    { _id: 'c2', lat: 28.6280, lng: 77.2190, title: 'Water Pipeline Replacement', description: 'DJB replacing 40-year-old mains', severity: 'medium', agency: 'DJB', radius: 150, startDate: '2026-10-14', endDate: '2026-11-15', reports: 5 },
    { _id: 'c3', lat: 28.6050, lng: 77.2250, title: 'Flyover Widening', description: 'PWD widening NH-48 flyover from 4 to 6 lanes', severity: 'high', agency: 'PWD', radius: 400, startDate: '2026-09-01', endDate: '2027-03-31', reports: 28 },
  ],
  potholes: [
    { _id: 'p1', lat: 28.6200, lng: 77.2100, title: 'Severe Pothole', description: 'Large crater, 30cm deep, tyre damage risk', severity: 'severe', reportCount: 7, imageUrl: null },
    { _id: 'p2', lat: 28.6170, lng: 77.2300, title: 'Moderate Pothole', description: 'Road surface crumbling after last rain', severity: 'moderate', reportCount: 3, imageUrl: null },
    { _id: 'p3', lat: 28.6310, lng: 77.2050, title: 'Dangerous Pothole', description: 'Manhole cover collapsed, extremely dangerous', severity: 'dangerous', reportCount: 15, imageUrl: null },
    { _id: 'p4', lat: 28.6090, lng: 77.2180, title: 'Minor Pothole', description: 'Small crack developing', severity: 'minor', reportCount: 1, imageUrl: null },
  ],
  waterlogs: [
    { _id: 'w1', lat: 28.6155, lng: 77.2070, title: 'Flooded Underpass', description: 'ITO underpass — ankle deep water', depth: 'ankle', reportCount: 22 },
    { _id: 'w2', lat: 28.6240, lng: 77.2160, title: 'Waterlogged Junction', description: 'Blocked drain, vehicles risk stalling', depth: 'vehicle_risk', reportCount: 9 },
  ],
  trafficJams: [
    { _id: 't1', lat: 28.6289, lng: 77.2065, title: 'Severe Gridlock (Ashoka Road)', description: 'VIP movement & bottleneck repair', congestion: 'severe', speed_kmh: 6, delay_min: 22, radius: 250 },
    { _id: 't2', lat: 28.5700, lng: 77.2210, title: 'Heavy Traffic (AIIMS / Ring Road)', description: 'Peak hour bottleneck, crawling traffic', congestion: 'heavy', speed_kmh: 12, delay_min: 15, radius: 350 },
    { _id: 't3', lat: 28.6440, lng: 77.2160, title: 'New Delhi Railway Station Jam', description: 'Commercial cabs & autos blocking 3 lanes', congestion: 'heavy', speed_kmh: 10, delay_min: 18, radius: 200 },
    { _id: 't4', lat: 28.5355, lng: 77.2100, title: 'Moderate Congestion (Saket Metro)', description: 'Slow moving traffic near Mall junction', congestion: 'moderate', speed_kmh: 18, delay_min: 8, radius: 180 },
  ],
};

export function AppProvider({ children }) {
  const [view, setView] = useState('map'); // 'map' | 'report' | 'route' | 'dashboard'
  const [constructions, setConstructions] = useState(SEED.constructions);
  const [potholes, setPotholes] = useState(SEED.potholes);
  const [waterlogs, setWaterlogs] = useState(SEED.waterlogs);
  const [trafficJams, setTrafficJams] = useState(SEED.trafficJams);
  const [weather, setWeather] = useState(null);
  const [floodPrediction, setFloodPrediction] = useState(null);
  const [rainScenario, setRainScenario] = useState('heavy');
  const [filters, setFilters] = useState({ construction: true, pothole: true, waterlog: true, predictedFlood: true, traffic: true });
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [activeRoute, setActiveRoute] = useState(null);
  const [selectedRouteType, setSelectedRouteType] = useState('best'); // 'best' | 'normal'
  const [toast, setToast] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const toastTimer = useRef(null);

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  // ── Toast helper ─────────────────────────────────────────────
  const showToast = useCallback((msg, type = 'info') => {
    setToast({ msg, type });
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 3500);
  }, []);

  // ── Fetch all reports & weather from backend ─────────────────
  const fetchAll = useCallback(async () => {
    try {
      const [c, p, w, trf, wea, fld] = await Promise.all([
        axios.get(`${API}/constructions`),
        axios.get(`${API}/potholes`),
        axios.get(`${API}/waterlogs`),
        axios.get(`${API}/traffic`).catch(() => null),
        axios.get(`${API}/weather/current`).catch(() => null),
        axios.get(`${API}/weather/flood-prediction?rain_scenario=${rainScenario}`).catch(() => null),
      ]);
      setConstructions(c.data.length ? c.data : SEED.constructions);
      setPotholes(p.data.length ? p.data : SEED.potholes);
      setWaterlogs(w.data.length ? w.data : SEED.waterlogs);
      if (trf?.data && trf.data.length) setTrafficJams(trf.data);
      if (wea?.data) setWeather(wea.data);
      if (fld?.data) setFloodPrediction(fld.data);
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    }
  }, [rainScenario]);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 15000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const updateRainScenario = async (scen) => {
    setRainScenario(scen);
    try {
      const res = await axios.get(`${API}/weather/flood-prediction?rain_scenario=${scen}`);
      setFloodPrediction(res.data);
      showToast(`Simulation switched to ${res.data.scenarioLabel}`, 'info');
    } catch (err) {
      console.error(err);
    }
  };

  const toggleFilter = (type) =>
    setFilters(f => ({ ...f, [type]: !f[type] }));

  return (
    <AppContext.Provider value={{
      view, setView,
      constructions, setConstructions,
      potholes, setPotholes,
      waterlogs, setWaterlogs,
      trafficJams, setTrafficJams,
      weather, floodPrediction,
      rainScenario, updateRainScenario,
      filters, toggleFilter,
      activeRoute, setActiveRoute,
      selectedRouteType, setSelectedRouteType,
      isDarkMode, toggleTheme,
      showToast, backendOnline,
      fetchAll, API,
    }}>
      {children}
      {toast && (
        <div className={`toast ${toast.type}`}>{toast.msg}</div>
      )}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
