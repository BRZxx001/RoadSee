import React from 'react';
import { useApp } from '../context/AppContext';

export default function Sidebar() {
  const { constructions, potholes, waterlogs, trafficJams, floodPrediction, filters, toggleFilter, setView } = useApp();

  const trfList = trafficJams || [];
  const stats = [
    { label: 'Live Traffic',     count: trfList.length,                 type: 'traffic',        color: '#ef4444', icon: '🚗' },
    { label: 'Construction',    count: constructions.length,           type: 'construction',   color: '#f59e0b', icon: '🏗️' },
    { label: 'Potholes',        count: potholes.length,                type: 'pothole',        color: '#8b5cf6', icon: '🕳️' },
    { label: 'Waterlogging',    count: waterlogs.length,               type: 'waterlog',       color: '#3b82f6', icon: '🌊' },
    { label: 'Predicted Floods',count: floodPrediction?.summary?.criticalZones || 0, type: 'predictedFlood', color: '#dc2626', icon: '🌧️' },
  ];

  const totalDisruptions = constructions.length + potholes.length + waterlogs.length + trfList.length;

  // Most urgent items (top 4)
  const urgent = [
    ...trfList.filter(t => t.congestion === 'severe' || t.congestion === 'heavy').map(t => ({ ...t, type: 'traffic' })),
    ...potholes.filter(p => p.severity === 'dangerous' || p.severity === 'severe').map(p => ({ ...p, type: 'pothole' })),
    ...constructions.filter(c => c.severity === 'high').map(c => ({ ...c, type: 'construction' })),
    ...waterlogs.filter(w => w.depth === 'avoid' || w.depth === 'vehicle_risk').map(w => ({ ...w, type: 'waterlog' })),
  ].slice(0, 4);

  const typeColor = { construction: '#f59e0b', pothole: '#8b5cf6', waterlog: '#3b82f6', traffic: '#ef4444' };
  const typeLabel = { construction: '🏗️', pothole: '🕳️', waterlog: '🌊', traffic: '🚗' };

  return (
    <aside className="sidebar">

      {/* ── Stats ───────────────────────────────────────────── */}
      <div className="sidebar-section">
        <div className="sidebar-title">Live Disruptions</div>
        <div style={{ textAlign:'center', marginBottom: 12 }}>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#dc2626', lineHeight: 1 }}>
            {totalDisruptions}
          </div>
          <div className="stat-label">active disruptions in your city</div>
        </div>
        <div className="stats-grid">
          {stats.map(s => (
            <div className="stat-card" key={s.type}>
              <div className="stat-value" style={{ color: s.color }}>{s.icon} {s.count}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#16a34a' }}>
              {potholes.filter(p => p.severity === 'dangerous').length}
            </div>
            <div className="stat-label">Dangerous Potholes</div>
          </div>
        </div>
      </div>

      {/* ── Filters ─────────────────────────────────────────── */}
      <div className="sidebar-section">
        <div className="sidebar-title">Map Filters</div>
        <div className="filter-group">
          {stats.map(s => (
            <div
              key={s.type}
              className={`filter-toggle ${s.type} ${filters[s.type] ? 'active' : ''}`}
              onClick={() => toggleFilter(s.type)}
            >
              <div className="filter-label">
                <div className="filter-dot" style={{ background: filters[s.type] ? s.color : '#64748b' }} />
                {s.icon} {s.label}
              </div>
              <span className={`filter-count ${s.type}`} style={{ opacity: filters[s.type] ? 1 : 0.4 }}>
                {s.count}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Urgent Alerts ────────────────────────────────────── */}
      {urgent.length > 0 && (
        <div className="sidebar-section">
          <div className="sidebar-title">🚨 Urgent Alerts</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {urgent.map(item => (
              <div key={item._id} style={{
                padding: '10px 12px',
                borderRadius: 10,
                border: `1.5px solid ${typeColor[item.type]}55`,
                background: typeColor[item.type] + '18',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
                  <span>{typeLabel[item.type]}</span>
                  <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>{item.title}</span>
                </div>
                <div className="stat-label" style={{ fontSize: '0.75rem' }}>{item.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Quick Actions ─────────────────────────────────────── */}
      <div className="sidebar-section">
        <div className="sidebar-title">Quick Actions</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <button className="btn btn-danger" onClick={() => setView('report')}>
            📸 Report a Disruption
          </button>
          <button className="btn btn-primary" onClick={() => setView('route')}>
            🗺️ Plan Best Route
          </button>
          <button className="btn btn-outline" onClick={() => setView('dashboard')}>
            🏛️ City Authority Dashboard
          </button>
        </div>
      </div>

      {/* ── Legend ────────────────────────────────────────────── */}
      <div className="sidebar-section">
        <div className="sidebar-title">Severity Legend</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {[
            ['#dc2626', 'Dangerous / Avoid Completely'],
            ['#ef4444', 'Severe / Vehicle Risk'],
            ['#f59e0b', 'Moderate / High Impact'],
            ['#8b5cf6', 'Minor / Low Impact'],
          ].map(([c, l]) => (
            <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.78rem' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: c, flexShrink: 0 }} />
              <span className="stat-label" style={{ fontSize: '0.78rem' }}>{l}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
