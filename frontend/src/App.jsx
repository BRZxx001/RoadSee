import React, { useState, useRef } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import LiveMap from './components/LiveMap';
import Sidebar from './components/Sidebar';
import ReportPanel from './components/ReportPanel';
import RoutePlanner from './components/RoutePlanner';
import Dashboard from './components/Dashboard';
import WeatherFloodPanel from './components/WeatherFloodPanel';

function Navbar() {
  const { view, setView, backendOnline, floodPrediction, isDarkMode, toggleTheme } = useApp();
  const alertLevel = floodPrediction?.summary?.cityAlertLevel || 'GREEN';

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        🛣️ Road<span>See</span>
        <div style={{
          fontSize: '0.62rem', padding: '2px 8px', borderRadius: 20,
          background: backendOnline ? '#16a34a22' : '#fbbf2422',
          color: backendOnline ? '#4ade80' : '#fbbf24',
          border: `1px solid ${backendOnline ? '#4ade8044' : '#fbbf2444'}`,
          fontWeight: 600, letterSpacing: 0.5,
        }}>
          {backendOnline ? '● LIVE' : '● DEMO'}
        </div>
        {alertLevel === 'RED' && (
          <div style={{
            fontSize: '0.62rem', padding: '2px 8px', borderRadius: 20,
            background: '#dc262622', color: '#f87171', border: '1px solid #dc262644',
            fontWeight: 700, animation: 'pulse 1.5s infinite'
          }}>
            ⚠️ FLOOD RED ALERT
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {/* ── Celestial Theme Toggle (Pure Sun / Moon Image Button) ── */}
        <button
          className="theme-switch-btn"
          onClick={toggleTheme}
          title={isDarkMode ? 'Switch to Day Mode (Sun)' : 'Switch to Night Mode (Moon)'}
        >
          <img
            src={isDarkMode ? '/assets/moon_glow.png' : '/assets/sun_drawn.png'}
            alt={isDarkMode ? 'Moon (Dark Mode)' : 'Sun (Light Mode)'}
            className="celestial-avatar"
          />
        </button>

        <div className="navbar-nav">
          <button className={`nav-btn ${view === 'map' ? 'active' : ''}`} onClick={() => setView('map')}>
            🗺️ Live Map
          </button>
          <button className={`nav-btn ${view === 'weather' ? 'active' : ''}`} onClick={() => setView('weather')}>
            🌧️ Flood AI
          </button>
          <button className={`nav-btn ${view === 'report' ? 'active' : ''}`} onClick={() => setView('report')}>
            📸 Report
          </button>
          <button className={`nav-btn ${view === 'route' ? 'active' : ''}`} onClick={() => setView('route')}>
            🧭 Route
          </button>
          <button className={`nav-btn ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
            🏛️ Dashboard
          </button>
        </div>
      </div>
    </nav>
  );
}

function AppContent() {
  const { view, setView } = useApp();
  const [sidebarWidth, setSidebarWidth] = useState(360);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(360);

  const startResizing = (e) => {
    e.preventDefault();
    setIsDragging(true);
    dragStartX.current = e.clientX;
    dragStartWidth.current = sidebarWidth;

    const onMouseMove = (moveEvent) => {
      const delta = moveEvent.clientX - dragStartX.current;
      const newWidth = Math.min(Math.max(dragStartWidth.current + delta, 260), 650);
      setSidebarWidth(newWidth);
    };

    const onMouseUp = () => {
      setIsDragging(false);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  return (
    <>
      <Navbar />
      <div className="app-layout">
        {/* Sidebar — extendable via drag or collapse */}
        <div
          className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}
          style={{ width: isCollapsed ? 0 : `${sidebarWidth}px` }}
        >
          {view === 'map'     && <Sidebar />}
          {view === 'weather' && <WeatherFloodPanel />}
          {view === 'report'  && <ReportPanel />}
          {view === 'route'   && <RoutePlanner />}
          {view === 'dashboard' && (
            <div style={{ padding:20, color:'#64748b', textAlign:'center', paddingTop:40 }}>
              <div style={{ fontSize:'2rem', marginBottom:8 }}>🏛️</div>
              Dashboard is open in fullscreen
            </div>
          )}

          {/* Draggable Resizer Handle on right border */}
          {!isCollapsed && (
            <div
              className={`sidebar-resizer ${isDragging ? 'dragging' : ''}`}
              onMouseDown={startResizing}
              title="Drag to resize sidebar"
            />
          )}
        </div>

        {/* Main Map — always visible */}
        <div className="map-container">
          {/* Toggle pill button to collapse/expand sidebar */}
          <button
            className="sidebar-toggle-pill"
            onClick={() => setIsCollapsed(!isCollapsed)}
            title={isCollapsed ? 'Show Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? '▶ Expand Panel' : '◀ Minimize'}
          </button>

          <LiveMap />

          {/* Floating Action Button */}
          <button className="fab" onClick={() => setView('report')} title="Report a disruption">
            +
          </button>
        </div>
      </div>

      {/* Dashboard Modal */}
      {view === 'dashboard' && <Dashboard onClose={() => setView('map')} />}
    </>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
