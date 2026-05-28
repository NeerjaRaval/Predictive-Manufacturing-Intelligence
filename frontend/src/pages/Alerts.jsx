import React, { useState, useEffect } from 'react';
import { RefreshCw, Bell, Thermometer, Activity, Wifi, AlertTriangle } from 'lucide-react';

function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

const CATEGORY_ICON = {
  Thermal:    <Thermometer size={16} />,
  Mechanical: <Activity size={16} />,
  Network:    <Wifi size={16} />,
  Quality:    <AlertTriangle size={16} />,
};

export default function Alerts() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter]   = useState('');
  const [catFilter, setCat]   = useState('');
  const [acknowledged, setAck] = useState(new Set());

  const load = () => {
    setLoading(true);
    fetch('/api/alerts')
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const allAlerts = data?.alerts || [];
  const filtered  = allAlerts.filter(a => {
    if (acknowledged.has(a.id)) return false;
    const matchSev = !filter   || a.severity.toLowerCase() === filter.toLowerCase();
    const matchCat = !catFilter || a.category === catFilter;
    return matchSev && matchCat;
  });

  const categories = [...new Set(allAlerts.map(a => a.category))];

  return (
    <>
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}} @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}`}</style>
      <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h2 style={{ marginBottom: 5 }}>Active Alerts</h2>
            <p style={{ fontSize: '0.9rem' }}>Threshold-based anomaly detection across all 50 machines</p>
          </div>
          <button className="btn btn-secondary" onClick={load}><RefreshCw size={14} /> Refresh</button>
        </div>

        {/* KPI Cards */}
        <div className="grid-cols-4">
          {[
            ['Total Alerts', data?.total, 'var(--text-main)'],
            ['Critical', data?.critical_count, 'var(--status-critical)'],
            ['Warning',  data?.warning_count,  'var(--status-warning)'],
            ['Acknowledged', acknowledged.size, 'var(--status-good)'],
          ].map(([label, val, color]) => (
            <div key={label} className="card">
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 10 }}>{label}</p>
              {loading ? <Shimmer height={36} /> : (
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ fontSize: '2.2rem', fontWeight: 'bold', color }}>{val ?? 0}</div>
                  {label === 'Critical' && (val ?? 0) > 0 && (
                    <Bell size={20} color="var(--status-critical)" style={{ animation: 'pulse 1.5s infinite' }} />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Thresholds Reference Card */}
        {data?.thresholds && (
          <div className="card" style={{ padding: '1rem 1.5rem' }}>
            <h4 style={{ marginBottom: '0.75rem', fontSize: '0.9rem' }}>Active Threshold Configuration</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
              {[
                ['🌡️ Temp Warning', `>${data.thresholds.temperature_warning}°C`],
                ['🌡️ Temp Critical', `>${data.thresholds.temperature_critical}°C`],
                ['📳 Vibration Warn', `>${data.thresholds.vibration_warning} Hz`],
                ['📳 Vibration Crit', `>${data.thresholds.vibration_critical} Hz`],
                ['📡 Latency Warn', `>${data.thresholds.latency_warning} ms`],
                ['📡 Latency Crit', `>${data.thresholds.latency_critical} ms`],
                ['📶 Packet Loss', `>${data.thresholds.packet_loss_warning}%`],
                ['🔧 Maint. Score', `<${data.thresholds.maintenance_score_critical}`],
              ].map(([label, val]) => (
                <div key={label} style={{ padding: '6px 12px', borderRadius: 8, background: 'var(--bg-hover)', border: '1px solid var(--border-color)', fontSize: '0.78rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{label}: </span>
                  <span style={{ color: 'var(--primary-neon)', fontWeight: 600 }}>{val}</span>
                </div>
              ))}
              <div style={{ marginLeft: 'auto', alignSelf: 'center' }}>
                <a href="/settings" style={{ fontSize: '0.8rem', color: 'var(--primary-neon)', textDecoration: 'none' }}>Edit thresholds →</a>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: 12, alignItems: 'center' }}>
            <select className="input-field" style={{ width: 150, fontSize: '0.85rem' }} value={filter} onChange={e => setFilter(e.target.value)}>
              <option value="">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="Warning">Warning</option>
            </select>
            <select className="input-field" style={{ width: 160, fontSize: '0.85rem' }} value={catFilter} onChange={e => setCat(e.target.value)}>
              <option value="">All Categories</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
              {filtered.length} active · {acknowledged.size} acknowledged
            </span>
          </div>

          {/* Alerts List */}
          <div style={{ maxHeight: 520, overflowY: 'auto' }}>
            {loading ? (
              <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: 12 }}>
                {Array.from({ length: 8 }).map((_, i) => <Shimmer key={i} height={70} />)}
              </div>
            ) : filtered.length === 0 ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--status-good)' }}>
                <Bell size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
                <div style={{ fontWeight: 600 }}>No active alerts</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>All machines are within normal operating thresholds.</div>
              </div>
            ) : (
              filtered.map(alert => (
                <div key={alert.id} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-color)', transition: 'background 0.15s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>

                  {/* Severity Indicator */}
                  <div style={{
                    width: 4, height: 48, borderRadius: 2, flexShrink: 0,
                    background: alert.severity === 'Critical' ? 'var(--status-critical)' : 'var(--status-warning)',
                    ...(alert.severity === 'Critical' ? { animation: 'pulse 1.5s infinite' } : {})
                  }} />

                  {/* Category Icon */}
                  <div style={{
                    width: 40, height: 40, borderRadius: 10, flexShrink: 0,
                    background: alert.severity === 'Critical' ? 'rgba(248,81,73,0.15)' : 'rgba(210,153,34,0.15)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: alert.severity === 'Critical' ? 'var(--status-critical)' : 'var(--status-warning)'
                  }}>
                    {CATEGORY_ICON[alert.category] || <Bell size={16} />}
                  </div>

                  {/* Content */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 3 }}>
                      <span style={{ fontWeight: 600, color: 'var(--primary-neon)' }}>{alert.machine}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{alert.category}</span>
                      <span className={`tag tag-${alert.tag}`}>{alert.severity}</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {alert.message}
                    </div>
                  </div>

                  {/* Date & Action */}
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8 }}>{alert.date}</div>
                    <button
                      onClick={() => setAck(prev => new Set([...prev, alert.id]))}
                      style={{ fontSize: '0.75rem', padding: '4px 10px', borderRadius: 6, background: 'var(--bg-hover)', border: '1px solid var(--border-color)', color: 'var(--text-muted)', cursor: 'pointer', transition: 'all 0.2s' }}
                      onMouseEnter={e => { e.target.style.background = 'var(--status-good)'; e.target.style.color = '#000'; e.target.style.borderColor = 'var(--status-good)'; }}
                      onMouseLeave={e => { e.target.style.background = 'var(--bg-hover)'; e.target.style.color = 'var(--text-muted)'; e.target.style.borderColor = 'var(--border-color)'; }}>
                      Acknowledge
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
