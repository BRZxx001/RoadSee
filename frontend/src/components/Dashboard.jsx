import React from 'react';
import { useApp } from '../context/AppContext';

const SEV_SCORE = { dangerous: 100, severe: 75, high: 80, vehicle_risk: 70, moderate: 50, medium: 50, ankle: 40, minor: 20, low: 20, puddles: 10 };
const TRAFFIC   = { dangerous: 5000, severe: 3500, high: 3000, vehicle_risk: 3000, moderate: 2000, medium: 2500, ankle: 2000, minor: 500, low: 1000, puddles: 500 };

function priorityScore(item) {
  const sev = SEV_SCORE[item.severity || item.depth || 'moderate'] || 50;
  const trf = TRAFFIC[item.severity || item.depth || 'moderate'] || 1000;
  const rep = (item.reportCount || item.reports || 1);
  return Math.round(sev * 0.5 + (trf / 100) * 0.3 + rep * 2);
}

export default function Dashboard({ onClose }) {
  const { constructions, potholes, waterlogs } = useApp();

  const allItems = [
    ...potholes.map(p => ({ ...p, type: 'pothole',      icon: '🕳️', typeLabel: 'Pothole' })),
    ...waterlogs.map(w => ({ ...w, type: 'waterlog',     icon: '🌊', typeLabel: 'Waterlogging' })),
    ...constructions.map(c => ({ ...c, type: 'construction', icon: '🏗️', typeLabel: 'Construction' })),
  ].map(item => ({ ...item, score: priorityScore(item) }))
   .sort((a, b) => b.score - a.score);

  const typeColors = { pothole:'#8b5cf6', waterlog:'#3b82f6', construction:'#f59e0b' };

  // Overlap detection: constructions within 500m of each other
  const overlaps = [];
  for (let i = 0; i < constructions.length; i++) {
    for (let j = i+1; j < constructions.length; j++) {
      const dlat = (constructions[i].lat - constructions[j].lat) * 111000;
      const dlng = (constructions[i].lng - constructions[j].lng) * 111000 * Math.cos(constructions[i].lat * Math.PI/180);
      const dist = Math.sqrt(dlat*dlat + dlng*dlng);
      if (dist < 500) overlaps.push({ a: constructions[i], b: constructions[j], dist: Math.round(dist) });
    }
  }

  const stats = [
    { label:'Total Disruptions', value: constructions.length + potholes.length + waterlogs.length, color:'#1e3a5f' },
    { label:'Dangerous Potholes', value: potholes.filter(p => p.severity === 'dangerous').length, color:'#dc2626' },
    { label:'High-Risk Waterlog', value: waterlogs.filter(w => ['avoid','vehicle_risk'].includes(w.depth)).length, color:'#2563eb' },
    { label:'Agency Conflicts', value: overlaps.length, color:'#f59e0b' },
  ];

  return (
    <div className="dashboard-overlay" onClick={onClose}>
      <div className="dashboard-modal" onClick={e => e.stopPropagation()}>

        <div className="dashboard-header">
          <div>
            <div className="dashboard-title">🏛️ City Authority Dashboard</div>
            <div style={{ fontSize:'0.78rem', color:'#64748b' }}>
              Real-time disruption intelligence & priority management
            </div>
          </div>
          <button className="btn btn-outline" style={{ width:'auto', padding:'8px 14px' }} onClick={onClose}>
            ✕ Close
          </button>
        </div>

        {/* ── Stats ────────────────────────────────────────────── */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:24 }}>
          {stats.map(s => (
            <div key={s.label} className="stat-card" style={{ border:`2px solid ${s.color}22` }}>
              <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {/* ── Agency Overlap Alerts ─────────────────────────────── */}
        {overlaps.length > 0 && (
          <div style={{ marginBottom:24 }}>
            <h3 style={{ fontSize:'0.95rem', fontWeight:800, color:'#92400e', marginBottom:10 }}>
              ⚠️ Agency Overlap Conflicts
            </h3>
            <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
              {overlaps.map((o, i) => (
                <div key={i} style={{
                  padding:'12px 14px', borderRadius:10,
                  background:'#fffbeb', border:'1.5px solid #fde68a',
                }}>
                  <div style={{ fontWeight:700, fontSize:'0.85rem', color:'#92400e', marginBottom:4 }}>
                    🏗️ {o.a.title} &amp; {o.b.title}
                  </div>
                  <div style={{ fontSize:'0.75rem', color:'#78350f' }}>
                    Only {o.dist}m apart — {o.a.agency} &amp; {o.b.agency} should coordinate digging schedule
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Priority Fix Queue ────────────────────────────────── */}
        <div>
          <h3 style={{ fontSize:'0.95rem', fontWeight:800, color:'#1e3a5f', marginBottom:10 }}>
            📋 Priority Fix Queue
          </h3>
          <div className="priority-queue">
            {allItems.map((item, idx) => {
              const rank = idx < 3 ? 'high' : idx < 6 ? 'medium' : 'low';
              return (
                <div key={item._id} className="priority-item">
                  <div className={`priority-rank ${rank}`}>{idx + 1}</div>
                  <div style={{
                    width:32, height:32, borderRadius:8,
                    background: typeColors[item.type] + '22',
                    display:'flex', alignItems:'center', justifyContent:'center',
                    fontSize:'1.1rem', flexShrink:0,
                  }}>
                    {item.icon}
                  </div>
                  <div className="priority-info">
                    <div className="priority-name">{item.title}</div>
                    <div className="priority-meta">
                      {item.typeLabel} &bull; {item.severity || item.depth || ''} &bull; {item.reportCount || item.reports || 0} reports
                      {item.agency ? ` · ${item.agency}` : ''}
                    </div>
                  </div>
                  <div className="priority-score">{item.score}pts</div>
                </div>
              );
            })}
          </div>
        </div>

        <div style={{ marginTop:16, padding:'12px 14px', borderRadius:10, background:'#f8fafc', border:'1px solid #e2e8f0' }}>
          <div style={{ fontSize:'0.75rem', color:'#64748b', lineHeight:1.6 }}>
            <strong>Priority Score Formula:</strong> Severity (50%) + Traffic Volume (30%) + Report Count (20%)<br/>
            Items with score &gt; 80 should be actioned within 24 hours.
          </div>
        </div>
      </div>
    </div>
  );
}
