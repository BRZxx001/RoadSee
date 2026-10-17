import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useApp } from '../context/AppContext';
import 'leaflet/dist/leaflet.css';

// ── Fix Leaflet default icon path in Vite ────────────────────────
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// ── Custom SVG Icons ─────────────────────────────────────────────
const makeIcon = (color, symbol, size = 36) => L.divIcon({
  className: '',
  html: `<div style="
    width:${size}px; height:${size}px; border-radius:50% 50% 50% 0;
    background:${color}; transform:rotate(-45deg);
    border:3px solid white;
    box-shadow:0 3px 10px rgba(0,0,0,0.35);
    display:flex; align-items:center; justify-content:center;">
    <span style="transform:rotate(45deg);font-size:${size*0.42}px;line-height:1">${symbol}</span>
  </div>`,
  iconSize:   [size, size],
  iconAnchor: [size/2, size],
  popupAnchor:[0, -size],
});

const ICONS = {
  construction_high:   makeIcon('#f59e0b', '🏗️'),
  construction_medium: makeIcon('#fbbf24', '🏗️', 30),
  construction_low:    makeIcon('#fcd34d', '🏗️', 26),
  pothole_dangerous:   makeIcon('#dc2626', '🕳️', 40),
  pothole_severe:      makeIcon('#ef4444', '🕳️'),
  pothole_moderate:    makeIcon('#8b5cf6', '🕳️', 30),
  pothole_minor:       makeIcon('#a78bfa', '🕳️', 26),
  waterlog_avoid:      makeIcon('#1d4ed8', '🌊', 40),
  waterlog_vehicle_risk: makeIcon('#2563eb', '🌊'),
  waterlog_ankle:      makeIcon('#3b82f6', '🌊', 30),
  waterlog_puddles:    makeIcon('#60a5fa', '🌊', 26),
  traffic_severe:      makeIcon('#b91c1c', '🚗', 42),
  traffic_heavy:       makeIcon('#ef4444', '🚗', 36),
  traffic_moderate:    makeIcon('#f97316', '🚗', 30),
};

const getIcon = (type, severity) =>
  ICONS[`${type}_${severity}`] || ICONS[`${type}_moderate`] || ICONS.pothole_moderate;

// ── Severity colour helper ────────────────────────────────────────
const sevColor = {
  dangerous:    '#dc2626', severe:  '#ef4444',
  high:         '#f59e0b', moderate:'#8b5cf6',
  vehicle_risk: '#2563eb', medium:  '#fbbf24',
  ankle:        '#3b82f6', low:     '#86efac',
  minor:        '#a78bfa', puddles: '#60a5fa',
  heavy:        '#ef4444',
};

// ── Popup Card ───────────────────────────────────────────────────
function PopupCard({ type, item }) {
  const typeLabels = { construction: '🏗️ Construction', pothole: '🕳️ Pothole', waterlog: '🌊 Waterlogging', traffic: '🚗 Traffic Jam' };
  const typeColors = { construction: '#f59e0b', pothole: '#8b5cf6', waterlog: '#3b82f6', traffic: '#ef4444' };

  return (
    <div className="map-popup">
      <div className="popup-type" style={{ color: typeColors[type] }}>
        {typeLabels[type]}
      </div>
      <div className="popup-title">{item.title}</div>
      <div className="popup-desc">{item.description}</div>
      <div className="popup-meta">
        {(item.severity || item.depth) && (
          <span className="popup-tag" style={{
            background: sevColor[item.severity || item.depth] + '22',
            color: sevColor[item.severity || item.depth],
            border: `1px solid ${sevColor[item.severity || item.depth]}44`,
          }}>
            {(item.severity || item.depth || '').replace('_', ' ').toUpperCase()}
          </span>
        )}
        {item.agency && (
          <span className="popup-tag" style={{ background:'#f1f5f9', color:'#475569', border:'1px solid #e2e8f0' }}>
            {item.agency}
          </span>
        )}
        {item.reportCount > 0 && (
          <span className="popup-tag" style={{ background:'#fef3c7', color:'#92400e', border:'1px solid #fde68a' }}>
            {item.reportCount} reports
          </span>
        )}
        {item.endDate && (
          <span className="popup-tag" style={{ background:'#ede9fe', color:'#5b21b6', border:'1px solid #ddd6fe' }}>
            Until {item.endDate}
          </span>
        )}
      </div>
    </div>
  );
}

// ── Dynamic Map View Controller for Active Route ──────────────────
function MapController({ activeRoute }) {
  const map = useMap();
  useEffect(() => {
    if (activeRoute && activeRoute.fromCoord && activeRoute.toCoord) {
      const bounds = L.latLngBounds([activeRoute.fromCoord, activeRoute.toCoord]);
      map.fitBounds(bounds, { padding: [60, 60], maxZoom: 14 });
    }
  }, [activeRoute, map]);
  return null;
}

// ── Main Map Component ───────────────────────────────────────────
export default function LiveMap() {
  const {
    constructions, potholes, waterlogs, trafficJams, floodPrediction, filters,
    activeRoute, selectedRouteType, setSelectedRouteType, isDarkMode
  } = useApp();
  const center = [28.6139, 77.2090]; // New Delhi

  const startIcon = makeIcon('#16a34a', '🟢', 38);
  const endIcon   = makeIcon('#dc2626', '🏁', 38);

  const bestPath   = activeRoute?.paths?.best;
  const normalPath = activeRoute?.paths?.normal;

  return (
    <MapContainer
      center={center}
      zoom={13}
      className="leaflet-map"
      zoomControl={true}
    >
      <MapController activeRoute={activeRoute} />

      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* ── Active Route Polylines ───────────────────────────── */}
      {normalPath && (
        <Polyline
          positions={normalPath}
          pathOptions={{
            color: '#dc2626',
            weight: selectedRouteType === 'normal' ? 6 : 3.5,
            opacity: selectedRouteType === 'normal' ? 0.9 : 0.4,
            dashArray: '6, 8',
          }}
          eventHandlers={{
            click: () => setSelectedRouteType('normal')
          }}
        >
          <Popup>
            <div className="map-popup">
              <div className="popup-type" style={{ color: '#dc2626' }}>⚠️ NORMAL ROUTE</div>
              <div className="popup-title">High Disruption Path</div>
              <div className="popup-desc">
                {activeRoute.normal.time} mins &bull; {activeRoute.normal.distance} km<br />
                Has {activeRoute.normal.constructions} constructions &amp; {activeRoute.normal.potholes} potholes
              </div>
            </div>
          </Popup>
        </Polyline>
      )}

      {bestPath && (
        <Polyline
          positions={bestPath}
          pathOptions={{
            color: '#16a34a',
            weight: selectedRouteType === 'best' ? 7 : 4,
            opacity: selectedRouteType === 'best' ? 0.95 : 0.45,
            lineCap: 'round',
            lineJoin: 'round',
          }}
          eventHandlers={{
            click: () => setSelectedRouteType('best')
          }}
        >
          <Popup>
            <div className="map-popup">
              <div className="popup-type" style={{ color: '#16a34a' }}>⭐ BEST ROUTE (RECOMMENDED)</div>
              <div className="popup-title">Safe, Clear &amp; Flood-Avoidant</div>
              <div className="popup-desc">
                {activeRoute.clearpath.time} mins &bull; {activeRoute.clearpath.distance} km<br />
                Zero waterlogging, clean road surface!
              </div>
            </div>
          </Popup>
        </Polyline>
      )}

      {/* ── Route Start & End Pin Markers ─────────────────────── */}
      {activeRoute && activeRoute.fromCoord && (
        <Marker position={activeRoute.fromCoord} icon={startIcon}>
          <Popup>
            <div className="map-popup">
              <div className="popup-type" style={{ color: '#16a34a' }}>🟢 START LOCATION</div>
              <div className="popup-title">{activeRoute.from}</div>
            </div>
          </Popup>
        </Marker>
      )}

      {activeRoute && activeRoute.toCoord && (
        <Marker position={activeRoute.toCoord} icon={endIcon}>
          <Popup>
            <div className="map-popup">
              <div className="popup-type" style={{ color: '#dc2626' }}>🏁 DESTINATION</div>
              <div className="popup-title">{activeRoute.to}</div>
            </div>
          </Popup>
        </Marker>
      )}

      {/* ── Construction Zones ──────────────────────────────── */}
      {filters.construction && constructions.map(c => (
        <React.Fragment key={c._id}>
          <Circle
            center={[c.lat, c.lng]}
            radius={c.radius || 200}
            pathOptions={{ color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.12, weight: 2 }}
          />
          <Marker position={[c.lat, c.lng]} icon={getIcon('construction', c.severity)}>
            <Popup><PopupCard type="construction" item={c} /></Popup>
          </Marker>
        </React.Fragment>
      ))}

      {/* ── Potholes ────────────────────────────────────────── */}
      {filters.pothole && potholes.map(p => (
        <Marker key={p._id} position={[p.lat, p.lng]} icon={getIcon('pothole', p.severity)}>
          <Popup><PopupCard type="pothole" item={p} /></Popup>
        </Marker>
      ))}

      {/* ── Crowdsourced Waterlogging ───────────────────────── */}
      {filters.waterlog && waterlogs.map(w => (
        <React.Fragment key={w._id}>
          <Circle
            center={[w.lat, w.lng]}
            radius={100}
            pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.2, weight: 2, dashArray: '6,4' }}
          />
          <Marker position={[w.lat, w.lng]} icon={getIcon('waterlog', w.depth)}>
            <Popup><PopupCard type="waterlog" item={w} /></Popup>
          </Marker>
        </React.Fragment>
      ))}

      {/* ── Live Traffic Congestion Hotspots ──────────────── */}
      {filters.traffic && (trafficJams || []).map(t => {
        const isSevere = t.congestion === 'severe';
        const color = isSevere ? '#b91c1c' : (t.congestion === 'heavy' ? '#ef4444' : '#f97316');
        return (
          <React.Fragment key={t._id}>
            <Circle
              center={[t.lat, t.lng]}
              radius={t.radius || 250}
              pathOptions={{
                color: color,
                fillColor: color,
                fillOpacity: 0.22,
                weight: 2,
                dashArray: '3, 6'
              }}
            />
            <Marker position={[t.lat, t.lng]} icon={getIcon('traffic', t.congestion)}>
              <Popup>
                <div className="map-popup">
                  <div className="popup-type" style={{ color: color }}>
                    🚗 TRAFFIC JAM ({t.congestion.toUpperCase()})
                  </div>
                  <div className="popup-title">{t.title}</div>
                  <div className="popup-desc">{t.description}</div>
                  <div className="popup-meta">
                    <span className="popup-tag" style={{ background: color + '22', color: color, fontWeight: 700 }}>
                      Avg Speed: {t.speed_kmh} km/h
                    </span>
                    <span className="popup-tag" style={{ background: '#fee2e2', color: '#991b1b' }}>
                      +{t.delay_min} min delay
                    </span>
                  </div>
                </div>
              </Popup>
            </Marker>
          </React.Fragment>
        );
      })}

      {/* ── AI Predicted Flood Zones (Weather-driven) ───────── */}
      {filters.predictedFlood && floodPrediction?.zones?.map(fz => {
        const isCritical = fz.riskLevel === 'critical';
        const color = isCritical ? '#dc2626' : (fz.riskLevel === 'high' ? '#ea580c' : '#3b82f6');
        return (
          <React.Fragment key={fz.zoneId}>
            <Circle
              center={[fz.lat, fz.lng]}
              radius={280}
              pathOptions={{
                color: color,
                fillColor: color,
                fillOpacity: isCritical ? 0.25 : 0.15,
                weight: isCritical ? 3 : 2,
                dashArray: isCritical ? '4,4' : undefined,
              }}
            />
            <Marker position={[fz.lat, fz.lng]} icon={makeIcon(color, '⚠️', isCritical ? 42 : 34)}>
              <Popup>
                <div className="map-popup">
                  <div className="popup-type" style={{ color: color }}>
                    🌧️ AI PREDICTED FLOOD ZONE
                  </div>
                  <div className="popup-title">{fz.name}</div>
                  <div className="popup-desc" style={{ marginBottom: 6 }}>
                    {fz.recommendedAction}
                  </div>
                  <div className="popup-meta">
                    <span className="popup-tag" style={{ background: color + '22', color: color, fontWeight: 700 }}>
                      {fz.riskLevel.toUpperCase()} RISK ({fz.riskScore}%)
                    </span>
                    <span className="popup-tag" style={{ background: '#eff6ff', color: '#1d4ed8' }}>
                      Depth: ~{fz.estWaterDepthCm} cm
                    </span>
                    {fz.constructionAmplified && (
                      <span className="popup-tag" style={{ background: '#fffbeb', color: '#b45309' }}>
                        ⚡ Drain blocked by construction
                      </span>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          </React.Fragment>
        );
      })}
    </MapContainer>
  );
}

