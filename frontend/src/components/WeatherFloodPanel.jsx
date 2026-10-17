import React from 'react';
import { useApp } from '../context/AppContext';

export default function WeatherFloodPanel() {
  const { weather, floodPrediction, rainScenario, updateRainScenario, setView } = useApp();

  const scenarios = [
    { id: 'dry',        label: '☀️ Clear Sky',       desc: '0 mm/hr' },
    { id: 'moderate',   label: '🌧️ Moderate Rain',   desc: '12 mm/hr' },
    { id: 'heavy',      label: '⛈️ Heavy Downpour',   desc: '38.5 mm/hr' },
    { id: 'cloudburst', label: '🌊 Cloudburst Flood', desc: '75 mm/hr' },
  ];

  const riskBadgeStyle = {
    critical: { bg: '#fee2e2', color: '#991b1b', border: '#f87171' },
    high:     { bg: '#ffedd5', color: '#9a3412', border: '#fb923c' },
    moderate: { bg: '#fef3c7', color: '#92400e', border: '#fde68a' },
    low:      { bg: '#dcfce7', color: '#166534', border: '#86efac' },
  };

  return (
    <div style={{ padding: 16 }}>
      {/* ── Header ────────────────────────────────────────────── */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
        <div>
          <h2 style={{ fontSize:'1.1rem', fontWeight:800, color:'#1e3a5f' }}>Weather &amp; Flood AI</h2>
          <p style={{ fontSize:'0.75rem', color:'#64748b' }}>Rainfall vs drainage physics model</p>
        </div>
        <button className="btn btn-outline" style={{ width:'auto', padding:'6px 12px' }} onClick={() => setView('map')}>
          ← Back
        </button>
      </div>

      {/* ── Live Weather Stats ─────────────────────────────────── */}
      {weather && (
        <div style={{
          background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)',
          borderRadius: 12, padding: 14, color: 'white', marginBottom: 14,
          boxShadow: '0 4px 15px rgba(37,99,235,0.2)'
        }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
            <div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800 }}>{weather.city}</div>
              <div style={{ fontSize: '0.75rem', opacity: 0.85 }}>{weather.description}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{weather.temp}°C</div>
              <div style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.2)', padding:'2px 6px', borderRadius: 10 }}>
                {weather.source}
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginTop: 12, paddingTop: 10, borderTop: '1px solid rgba(255,255,255,0.15)' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.95rem', fontWeight: 700 }}>{weather.rain_mm_hr} mm</div>
              <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>Rain / hr</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.95rem', fontWeight: 700 }}>{weather.humidity}%</div>
              <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>Humidity</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.95rem', fontWeight: 700 }}>{weather.wind_speed_kmh} km/h</div>
              <div style={{ fontSize: '0.65rem', opacity: 0.8 }}>Wind</div>
            </div>
          </div>
        </div>
      )}

      {/* ── Weather Intensity Scenario Selector ─────────────────── */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1e3a5f', textTransform: 'uppercase', marginBottom: 8 }}>
          🎮 Simulate Rainfall Scenario
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
          {scenarios.map(s => (
            <div
              key={s.id}
              onClick={() => updateRainScenario(s.id)}
              style={{
                padding: '8px 10px',
                borderRadius: 8,
                cursor: 'pointer',
                border: `2px solid ${rainScenario === s.id ? '#2563eb' : '#e2e8f0'}`,
                background: rainScenario === s.id ? '#eff6ff' : 'white',
                transition: 'all 0.15s',
              }}
            >
              <div style={{ fontSize: '0.78rem', fontWeight: 700, color: rainScenario === s.id ? '#1d4ed8' : '#1e293b' }}>
                {s.label}
              </div>
              <div style={{ fontSize: '0.68rem', color: '#64748b' }}>{s.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Flood Prediction Summary ────────────────────────────── */}
      {floodPrediction && (
        <div>
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '10px 12px', borderRadius: 8, marginBottom: 12,
            background: floodPrediction.summary.cityAlertLevel === 'RED' ? '#fee2e2' : '#fef3c7',
            border: `1.5px solid ${floodPrediction.summary.cityAlertLevel === 'RED' ? '#f87171' : '#fde68a'}`,
          }}>
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 800, color: floodPrediction.summary.cityAlertLevel === 'RED' ? '#991b1b' : '#92400e' }}>
                🚨 City Alert: {floodPrediction.summary.cityAlertLevel}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#64748b' }}>
                {floodPrediction.summary.criticalZones} critical / {floodPrediction.summary.highRiskZones} high risk zones
              </div>
            </div>
            <button className="btn btn-primary" style={{ width: 'auto', padding: '6px 10px', fontSize: '0.75rem' }} onClick={() => setView('route')}>
              🧭 Avoid Floods
            </button>
          </div>

          {/* ── Predicted Zones List ─────────────────────────────── */}
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1e3a5f', textTransform: 'uppercase', marginBottom: 8 }}>
            Predicted Flood Hotspots
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {floodPrediction.zones.map(z => {
              const badge = riskBadgeStyle[z.riskLevel] || riskBadgeStyle.moderate;
              return (
                <div key={z.zoneId} style={{
                  padding: 10, borderRadius: 10,
                  border: `1.5px solid ${badge.border}`,
                  background: 'white',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.82rem', color: '#1e293b' }}>
                      🌊 {z.name}
                    </div>
                    <span style={{
                      fontSize: '0.65rem', fontWeight: 800, padding: '2px 6px', borderRadius: 12,
                      background: badge.bg, color: badge.color, border: `1px solid ${badge.border}`
                    }}>
                      {z.riskLevel.toUpperCase()} ({z.riskScore}%)
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: 10, fontSize: '0.72rem', color: '#64748b', marginBottom: 4 }}>
                    <span>🌊 Est Depth: <strong>{z.estWaterDepthCm} cm</strong></span>
                    <span>📍 Elev: {z.elevationM}m</span>
                    <span>⚠️ Past: {z.historicalIncidents}x</span>
                  </div>

                  {z.constructionAmplified && (
                    <div style={{
                      fontSize: '0.68rem', padding: '3px 6px', borderRadius: 4,
                      background: '#fffbeb', color: '#b45309', border: '1px solid #fde68a',
                      marginBottom: 4, fontWeight: 600
                    }}>
                      ⚡ Chain Reaction: Active construction blocking nearby drains!
                    </div>
                  )}

                  <div style={{ fontSize: '0.7rem', color: '#475569', fontStyle: 'italic' }}>
                    {z.recommendedAction}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
