import React, { useState, useEffect } from 'react';
import { RefreshCw, Save, CheckCircle } from 'lucide-react';

function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [form, setForm]         = useState(null);
  const [loading, setLoading]   = useState(true);
  const [saving, setSaving]     = useState(false);
  const [saved, setSaved]       = useState(false);

  const load = () => {
    setLoading(true);
    fetch('/api/settings')
      .then(r => r.json())
      .then(d => {
        setSettings(d);
        setForm({ active_model: d.active_model, thresholds: { ...d.thresholds } });
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
      load();
    } catch { /* silent */ }
    setSaving(false);
  };

  const setThreshold = (key, val) => {
    setForm(f => ({ ...f, thresholds: { ...f.thresholds, [key]: parseFloat(val) } }));
  };

  const THRESHOLD_CONFIG = [
    { key: 'temperature_warning',       label: '🌡️ Temperature Warning',       unit: '°C', min: 50, max: 100, step: 0.5, desc: 'Triggers Warning alert when machine temperature exceeds this value.' },
    { key: 'temperature_critical',      label: '🌡️ Temperature Critical',      unit: '°C', min: 60, max: 120, step: 0.5, desc: 'Triggers Critical alert. Risk of thermal damage.' },
    { key: 'vibration_warning',         label: '📳 Vibration Warning',         unit: 'Hz', min: 2,  max: 10, step: 0.1, desc: 'Elevated vibration may indicate bearing wear.' },
    { key: 'vibration_critical',        label: '📳 Vibration Critical',        unit: 'Hz', min: 3,  max: 15, step: 0.1, desc: 'Critical vibration levels risk structural damage.' },
    { key: 'latency_warning',           label: '📡 Network Latency Warning',   unit: 'ms', min: 5,  max: 30, step: 0.5, desc: 'Increased 6G latency affects real-time monitoring.' },
    { key: 'latency_critical',          label: '📡 Network Latency Critical',  unit: 'ms', min: 10, max: 50, step: 0.5, desc: 'Severe latency may cause missed sensor readings.' },
    { key: 'packet_loss_warning',       label: '📶 Packet Loss Warning',       unit: '%',  min: 0,  max: 5,  step: 0.1, desc: 'Data loss in 6G communication network.' },
    { key: 'packet_loss_critical',      label: '📶 Packet Loss Critical',      unit: '%',  min: 0,  max: 10, step: 0.1, desc: 'High packet loss indicates serious network disruption.' },
    { key: 'defect_rate_warning',       label: '⚙️ QC Defect Rate Warning',   unit: '%',  min: 0,  max: 20, step: 0.5, desc: 'Quality control defect rate above this triggers a warning.' },
    { key: 'defect_rate_critical',      label: '⚙️ QC Defect Rate Critical',  unit: '%',  min: 0,  max: 40, step: 0.5, desc: 'Critical defect level requiring production halt review.' },
    { key: 'maintenance_score_critical',label: '🔧 Maintenance Score (Critical)', unit: '',min: 0,  max: 1,  step: 0.01, desc: 'Machines with scores below this are queued for maintenance. Lower = worse.' },
  ];

  const MODEL_INFO = {
    random_forest:       { label: 'Random Forest',       icon: '🌲', desc: 'Ensemble of decision trees. High accuracy, handles feature interactions well. Best for this dataset.' },
    xgboost:             { label: 'XGBoost',             icon: '⚡', desc: 'Gradient boosting algorithm. Fast, memory-efficient, excellent with tabular data and imbalanced classes.' },
    logistic_regression: { label: 'Logistic Regression', icon: '📈', desc: 'Linear classification. Simple, fast, interpretable. Best used as a baseline comparison.' },
  };

  return (
    <>
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
      <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h2 style={{ marginBottom: 5 }}>Settings</h2>
            <p style={{ fontSize: '0.9rem' }}>Configure the active ML model and alert detection thresholds</p>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            {saved && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--status-good)', fontSize: '0.85rem' }}>
                <CheckCircle size={16} /> Saved successfully
              </div>
            )}
            <button className="btn btn-secondary" onClick={load}><RefreshCw size={14} /></button>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving || loading} style={{ minWidth: 120 }}>
              <Save size={14} /> {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>

        {/* Model Selection */}
        <div className="card">
          <h3 style={{ marginBottom: '0.5rem' }}>🤖 Active ML Model</h3>
          <p style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>Select which trained model to use for real-time efficiency predictions.</p>
          {loading ? <Shimmer height={100} /> : (
            <div className="grid-cols-3">
              {Object.entries(MODEL_INFO).map(([key, info]) => {
                const isActive = form?.active_model === key;
                return (
                  <div key={key} onClick={() => setForm(f => ({ ...f, active_model: key }))}
                    style={{
                      padding: '1.25rem', borderRadius: 12, cursor: 'pointer',
                      border: `2px solid ${isActive ? 'var(--primary-neon)' : 'var(--border-color)'}`,
                      background: isActive ? 'rgba(88,166,255,0.07)' : 'var(--bg-hover)',
                      transition: 'all 0.2s',
                    }}>
                    <div style={{ fontSize: '1.8rem', marginBottom: 8 }}>{info.icon}</div>
                    <div style={{ fontWeight: 600, marginBottom: 4, color: isActive ? 'var(--primary-neon)' : 'var(--text-main)' }}>{info.label}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{info.desc}</div>
                    {isActive && (
                      <div style={{ marginTop: 10 }}>
                        <span className="tag tag-good" style={{ fontSize: '0.65rem' }}>ACTIVE</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Alert Thresholds */}
        <div className="card">
          <h3 style={{ marginBottom: '0.5rem' }}>⚡ Alert Detection Thresholds</h3>
          <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>
            Adjust the sensor limits that trigger Warning and Critical alerts across all 50 machines.
            Changes take effect immediately after saving.
          </p>
          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {Array.from({ length: 5 }).map((_, i) => <Shimmer key={i} height={70} />)}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {THRESHOLD_CONFIG.map(({ key, label, unit, min, max, step, desc }) => {
                const val = form?.thresholds?.[key] ?? 0;
                const pct = Math.min(100, Math.max(0, ((val - min) / (max - min)) * 100));
                const isWarning = key.includes('warning') || key.includes('score');
                return (
                  <div key={key} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', alignItems: 'center', padding: '1rem', background: 'var(--bg-hover)', borderRadius: 10 }}>
                    <div>
                      <div style={{ fontWeight: 500, marginBottom: 4, fontSize: '0.9rem' }}>{label}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{desc}</div>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{min}{unit}</span>
                        <span style={{ fontWeight: 700, fontSize: '1rem', color: isWarning ? 'var(--status-warning)' : 'var(--status-critical)' }}>
                          {val}{unit}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{max}{unit}</span>
                      </div>
                      <input type="range" min={min} max={max} step={step} value={val}
                        onChange={e => setThreshold(key, e.target.value)}
                        style={{ width: '100%', accentColor: isWarning ? 'var(--status-warning)' : 'var(--status-critical)', cursor: 'pointer' }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Dataset Info */}
        <div className="card" style={{ borderColor: 'rgba(88,166,255,0.2)' }}>
          <h3 style={{ marginBottom: '0.75rem' }}>📁 Dataset Information</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
            {[
              ['Source', 'Thales_Group_Manufacturing.csv'],
              ['Machines', '50 unique Machine IDs (1–50)'],
              ['Features', '14 columns (sensor + network + quality)'],
              ['Efficiency Classes', 'High / Medium / Low'],
              ['Date Range', 'January 2025+'],
              ['AI Model Location', '/models/ (local, no cloud)'],
            ].map(([k, v]) => (
              <div key={k} style={{ padding: '8px 16px', borderRadius: 8, background: 'var(--bg-hover)', border: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>{k}: </span>
                <span style={{ color: 'var(--primary-neon)', fontWeight: 600 }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
