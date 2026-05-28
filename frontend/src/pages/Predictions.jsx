import React, { useState, useEffect } from 'react';
import { TrendingUp, Download, RefreshCw } from 'lucide-react';

function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

export default function Predictions() {
  const [predictions, setPredictions] = useState([]);
  const [summary, setSummary]         = useState({});
  const [loading, setLoading]         = useState(true);
  const [search, setSearch]           = useState('');
  const [riskFilter, setRisk]         = useState('');
  const [model, setModel]             = useState('random_forest');

  // Predict form state
  const [form, setForm]               = useState({
    Temperature_C: '', Vibration_Hz: '', Power_Consumption_kW: '',
    Network_Latency_ms: '', 'Packet_Loss_%': '', 'Quality_Control_Defect_Rate_%': '',
    Production_Speed_units_per_hr: '', Predictive_Maintenance_Score: '', 'Error_Rate_%': ''
  });
  const [predResult, setPredResult]   = useState(null);
  const [predLoading, setPredLoading] = useState(false);

  const loadFromAPI = async () => {
    setLoading(true);
    try {
      const [machRes, maintRes] = await Promise.all([
        fetch('/api/machines?limit=50').then(r => r.json()),
        fetch('/api/maintenance').then(r => r.json()),
      ]);

      const machines = machRes.machines || [];
      const tasks    = maintRes.tasks   || [];

      // Build a prediction-like row from machine stats + maintenance queue
      const rows = machines.map((m, i) => {
        const task = tasks.find(t => t.machine === m.id);
        const risk = m.status === 'Critical' ? 'High' : m.status === 'Warning' ? 'Medium' : 'Low';
        return {
          id:         `PRD-${String(i + 1).padStart(3, '0')}`,
          machine:    m.id,
          type:       task?.task || deriveFailureType(m),
          risk,
          rul:        task ? `${task.due_days} days` : '> 30 days',
          conf:       `${Math.min(99, Math.round(50 + m.health / 2))}%`,
          efficiency: m.dominant_efficiency,
          status:     m.status === 'Healthy' ? 'Nominal' : 'Active',
        };
      });

      setSummary({
        total: rows.length,
        high:   rows.filter(r => r.risk === 'High').length,
        medium: rows.filter(r => r.risk === 'Medium').length,
        low:    rows.filter(r => r.risk === 'Low').length,
        nominal: rows.filter(r => r.status === 'Nominal').length,
      });
      setPredictions(rows);
    } catch { /* silent */ }
    setLoading(false);
  };

  function deriveFailureType(m) {
    if (m.avg_temperature > 78) return 'Thermal Overload';
    if (m.avg_vibration > 5.5)  return 'Bearing Wear / Vibration';
    if (m.avg_packet_loss > 1)  return '6G Network Disruption';
    if (m.avg_maint_score < 0.4) return 'Component Wear';
    return 'Sensor Drift';
  }

  useEffect(() => { loadFromAPI(); }, []);

  const filtered = predictions.filter(p => {
    const matchSearch = !search || p.machine.toLowerCase().includes(search.toLowerCase()) || p.type.toLowerCase().includes(search.toLowerCase());
    const matchRisk   = !riskFilter || p.risk === riskFilter;
    return matchSearch && matchRisk;
  });

  const riskColor = (r) => r === 'High' ? 'var(--status-critical)' : r === 'Medium' ? 'var(--status-warning)' : 'var(--status-good)';

  const runPredict = async () => {
    const features = {};
    Object.entries(form).forEach(([k, v]) => { features[k] = parseFloat(v) || 0; });
    setPredLoading(true);
    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features, model_name: model }),
      });
      const d = await res.json();
      setPredResult(d);
    } catch (e) {
      setPredResult({ error: 'Prediction failed. Make sure the backend is running.' });
    }
    setPredLoading(false);
  };

  const fillRandom = () => {
    setForm({
      Temperature_C: (55 + Math.random() * 40).toFixed(1),
      Vibration_Hz: (2 + Math.random() * 7).toFixed(2),
      Power_Consumption_kW: (5 + Math.random() * 20).toFixed(2),
      Network_Latency_ms: (5 + Math.random() * 20).toFixed(1),
      'Packet_Loss_%': (Math.random() * 3).toFixed(2),
      'Quality_Control_Defect_Rate_%': (Math.random() * 15).toFixed(2),
      Production_Speed_units_per_hr: (300 + Math.random() * 400).toFixed(1),
      Predictive_Maintenance_Score: Math.random().toFixed(3),
      'Error_Rate_%': (Math.random() * 15).toFixed(2),
    });
    setPredResult(null);
  };

  return (
    <>
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
      <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h2 style={{ marginBottom: 5 }}>Predictions</h2>
            <p style={{ fontSize: '0.9rem' }}>AI-powered failure forecasts from your local manufacturing telemetry</p>
          </div>
          <button className="btn btn-secondary" onClick={loadFromAPI}><RefreshCw size={14} /> Refresh</button>
        </div>

        {/* KPI Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1.5rem' }}>
          {[
            ['Total Predictions', summary.total, 'var(--text-main)'],
            ['High Risk',   summary.high,   'var(--status-critical)'],
            ['Medium Risk', summary.medium, 'var(--status-warning)'],
            ['Low Risk',    summary.low,    'var(--status-good)'],
            ['Nominal',     summary.nominal,'var(--text-muted)'],
          ].map(([label, val, color]) => (
            <div key={label} className="card">
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 10 }}>{label}</p>
              {loading ? <Shimmer height={36} /> : (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <div style={{ fontSize: '2.2rem', fontWeight: 'bold', color }}>{val ?? '--'}</div>
                  <TrendingUp size={20} color={color} style={{ opacity: 0.7 }} />
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
          {/* Predictions Table */}
          <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden' }}>
            {/* Toolbar */}
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', gap: 12 }}>
              <div style={{ display: 'flex', gap: 12 }}>
                <input type="text" className="input-field" placeholder="Search machine or failure..." value={search} onChange={e => setSearch(e.target.value)} style={{ width: 220, fontSize: '0.85rem' }} />
                <select className="input-field" style={{ width: 140, fontSize: '0.85rem' }} value={riskFilter} onChange={e => setRisk(e.target.value)}>
                  <option value="">All Risk Levels</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', alignSelf: 'center' }}>{filtered.length} predictions</span>
            </div>

            <div style={{ overflowX: 'auto', maxHeight: 400, overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead style={{ position: 'sticky', top: 0, zIndex: 1 }}>
                  <tr style={{ background: 'var(--bg-panel)', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                    {['ID', 'Machine', 'Failure Type', 'Risk Level', 'RUL', 'Confidence', 'Efficiency', 'Status'].map(h => (
                      <th key={h} style={{ padding: '12px 16px', fontWeight: 600, borderBottom: '1px solid var(--border-color)', whiteSpace: 'nowrap' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {loading
                    ? Array.from({ length: 6 }).map((_, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                          {Array.from({ length: 8 }).map((_, j) => <td key={j} style={{ padding: '12px 16px' }}><Shimmer height={14} /></td>)}
                        </tr>
                      ))
                    : filtered.map(p => (
                        <tr key={p.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.15s' }}
                          onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.025)'}
                          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                          <td style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>{p.id}</td>
                          <td style={{ padding: '12px 16px', color: 'var(--primary-neon)', fontWeight: 600 }}>{p.machine}</td>
                          <td style={{ padding: '12px 16px', fontSize: '0.85rem' }}>{p.type}</td>
                          <td style={{ padding: '12px 16px' }}>
                            <span style={{ color: riskColor(p.risk), fontWeight: 700 }}>{p.risk}</span>
                          </td>
                          <td style={{ padding: '12px 16px', fontSize: '0.85rem' }}>{p.rul}</td>
                          <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--status-good)' }}>{p.conf}</td>
                          <td style={{ padding: '12px 16px' }}>
                            <span style={{ color: p.efficiency === 'High' ? 'var(--status-good)' : p.efficiency === 'Medium' ? 'var(--status-warning)' : 'var(--status-critical)', fontSize: '0.85rem' }}>{p.efficiency}</span>
                          </td>
                          <td style={{ padding: '12px 16px' }}>
                            <span className={`tag tag-${p.status === 'Nominal' ? 'good' : 'warning'}`}>{p.status}</span>
                          </td>
                        </tr>
                      ))
                  }
                </tbody>
              </table>
            </div>
          </div>

          {/* Live Prediction Panel */}
          <div className="card" style={{ width: 300, flexShrink: 0 }}>
            <h3 style={{ marginBottom: '0.25rem' }}>Live ML Prediction</h3>
            <p style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>Enter telemetry values to run the model</p>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Model</label>
              <select className="input-field" value={model} onChange={e => setModel(e.target.value)} style={{ fontSize: '0.85rem' }}>
                <option value="random_forest">Random Forest</option>
                <option value="xgboost">XGBoost</option>
                <option value="logistic_regression">Logistic Regression</option>
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: '1rem' }}>
              {Object.keys(form).map(k => (
                <div key={k}>
                  <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>
                    {k.replace(/_/g, ' ').replace(/%/, ' (%)')}
                  </label>
                  <input type="number" step="any" className="input-field" value={form[k]} onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))} style={{ fontSize: '0.8rem', padding: '6px 10px' }} />
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: 8, marginBottom: '1rem' }}>
              <button className="btn btn-secondary" onClick={fillRandom} style={{ flex: 1, fontSize: '0.8rem' }}>Random</button>
              <button className="btn btn-primary" onClick={runPredict} disabled={predLoading} style={{ flex: 1, fontSize: '0.8rem' }}>
                {predLoading ? 'Running...' : 'Predict'}
              </button>
            </div>

            {predResult && !predResult.error && (
              <div style={{ padding: '1rem', borderRadius: 10, background: 'var(--bg-main)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 6 }}>MODEL OUTPUT · {predResult.model_used}</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: predResult.prediction === 'High' ? 'var(--status-good)' : predResult.prediction === 'Medium' ? 'var(--status-warning)' : 'var(--status-critical)' }}>
                  {predResult.prediction}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 10 }}>
                  Confidence: <strong style={{ color: 'var(--text-main)' }}>{(predResult.confidence * 100).toFixed(1)}%</strong>
                </div>
                {predResult.probabilities && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {Object.entries(predResult.probabilities).map(([k, v]) => (
                      <div key={k}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 3 }}>
                          <span style={{ color: k === 'High' ? 'var(--status-good)' : k === 'Medium' ? 'var(--status-warning)' : 'var(--status-critical)' }}>{k}</span>
                          <span style={{ color: 'var(--text-muted)' }}>{(v * 100).toFixed(1)}%</span>
                        </div>
                        <div style={{ height: 4, background: 'var(--bg-hover)', borderRadius: 2 }}>
                          <div style={{ width: `${v * 100}%`, height: '100%', background: k === 'High' ? 'var(--status-good)' : k === 'Medium' ? 'var(--status-warning)' : 'var(--status-critical)', borderRadius: 2, transition: 'width 0.5s ease' }} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            {predResult?.error && (
              <div style={{ padding: '10px 12px', borderRadius: 8, background: 'rgba(248,81,73,0.1)', border: '1px solid rgba(248,81,73,0.3)', color: 'var(--status-critical)', fontSize: '0.8rem' }}>
                {predResult.error}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
