import React, { useState, useEffect } from 'react';
import { FileText, Download, RefreshCw, CheckCircle } from 'lucide-react';

function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

function exportCSV(rows, filename) {
  if (!rows || rows.length === 0) return;
  const keys = Object.keys(rows[0]);
  const csv  = [keys.join(','), ...rows.map(r => keys.map(k => JSON.stringify(r[k] ?? '')).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export default function Reports() {
  const [kpis, setKpis]         = useState(null);
  const [machines, setMachines] = useState([]);
  const [alerts, setAlerts]     = useState([]);
  const [maintenance, setMaint] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [generated, setGenerated] = useState(null);
  const [exporting, setExporting] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [kRes, mRes, aRes, mainRes] = await Promise.all([
        fetch('/api/kpis').then(r => r.json()),
        fetch('/api/machines?limit=100').then(r => r.json()),
        fetch('/api/alerts').then(r => r.json()),
        fetch('/api/maintenance').then(r => r.json()),
      ]);
      setKpis(kRes);
      setMachines(mRes.machines || []);
      setAlerts(aRes.alerts || []);
      setMaint(mainRes.tasks || []);
    } catch { /* silent */ }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const generateReport = () => {
    const now = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    setGenerated({
      date: now,
      summary: {
        oee: kpis?.oee,
        alerts: alerts.length,
        critical_alerts: alerts.filter(a => a.severity === 'Critical').length,
        maintenance_tasks: maintenance.length,
        critical_tasks: maintenance.filter(t => t.priority === 'Critical').length,
        total_machines: machines.length,
        healthy: machines.filter(m => m.status === 'Healthy').length,
        warning: machines.filter(m => m.status === 'Warning').length,
        critical_machines: machines.filter(m => m.status === 'Critical').length,
        efficiency_high: kpis?.efficiency_distribution?.high,
        efficiency_low:  kpis?.efficiency_distribution?.low,
        ai_health: kpis?.ai_health_score,
      }
    });
  };

  const handleExport = async (type) => {
    setExporting(type);
    await new Promise(r => setTimeout(r, 600)); // Simulate processing
    if (type === 'machines')     exportCSV(machines,     `machines_report_${Date.now()}.csv`);
    if (type === 'alerts')       exportCSV(alerts,       `alerts_report_${Date.now()}.csv`);
    if (type === 'maintenance')  exportCSV(maintenance,  `maintenance_report_${Date.now()}.csv`);
    setExporting('');
  };

  const reports = [
    {
      id: 'executive',
      title: 'Executive Summary',
      desc: 'High-level KPI overview with OEE, efficiency distribution, and AI health score.',
      icon: '📊',
      action: generateReport,
    },
    {
      id: 'machines',
      title: 'Machine Telemetry Export',
      desc: `Export all ${machines.length} machines with their average sensor readings to CSV.`,
      icon: '🏭',
      action: () => handleExport('machines'),
    },
    {
      id: 'alerts',
      title: 'Active Alerts Report',
      desc: `Export all ${alerts.length} threshold violations and anomaly alerts to CSV.`,
      icon: '🚨',
      action: () => handleExport('alerts'),
    },
    {
      id: 'maintenance',
      title: 'Maintenance Queue Export',
      desc: `Export all ${maintenance.length} predictive maintenance tasks to CSV.`,
      icon: '🔧',
      action: () => handleExport('maintenance'),
    },
  ];

  return (
    <>
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
      <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h2 style={{ marginBottom: 5 }}>Reports</h2>
            <p style={{ fontSize: '0.9rem' }}>Generate and export reports from your local manufacturing data</p>
          </div>
          <button className="btn btn-secondary" onClick={load}><RefreshCw size={14} /> Reload Data</button>
        </div>

        {/* Report Cards */}
        <div className="grid-cols-2">
          {reports.map(r => (
            <div key={r.id} className="card" style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
              <div style={{ fontSize: '2.5rem', flexShrink: 0 }}>{r.icon}</div>
              <div style={{ flex: 1 }}>
                <h3 style={{ marginBottom: 6, fontSize: '1rem' }}>{r.title}</h3>
                <p style={{ fontSize: '0.85rem', marginBottom: '1rem', lineHeight: 1.5 }}>{r.desc}</p>
                <button className="btn btn-primary" onClick={r.action} disabled={loading || exporting === r.id}
                  style={{ fontSize: '0.8rem', padding: '6px 16px' }}>
                  {exporting === r.id ? '⏳ Exporting...' : r.id === 'executive' ? '📄 Generate Report' : <><Download size={14} /> Export CSV</>}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Generated Executive Summary */}
        {generated && (
          <div className="card" style={{ borderColor: 'rgba(88,166,255,0.4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h3>📊 Executive Summary Report</h3>
                <p style={{ fontSize: '0.8rem' }}>Generated on {generated.date} · Thales Group Manufacturing Intelligence</p>
              </div>
              <CheckCircle size={24} color="var(--status-good)" />
            </div>

            <div className="grid-cols-4" style={{ gap: '1rem' }}>
              {[
                ['OEE',           `${generated.summary.oee}%`,                 'var(--status-cyan)'],
                ['AI Health',     `${generated.summary.ai_health}/100`,         'var(--status-good)'],
                ['Active Alerts', generated.summary.alerts,                     'var(--status-warning)'],
                ['Critical',      generated.summary.critical_alerts,            'var(--status-critical)'],
                ['Total Machines',generated.summary.total_machines,             'var(--text-main)'],
                ['Healthy',       generated.summary.healthy,                    'var(--status-good)'],
                ['At Risk',       generated.summary.warning + generated.summary.critical_machines, 'var(--status-warning)'],
                ['Maint. Tasks',  generated.summary.maintenance_tasks,          'var(--primary-neon)'],
              ].map(([label, val, color]) => (
                <div key={label} style={{ padding: '12px', background: 'var(--bg-hover)', borderRadius: 10 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color }}>{val ?? '--'}</div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: '1.25rem', padding: '1rem', borderRadius: 10, background: 'rgba(88,166,255,0.05)', border: '1px solid rgba(88,166,255,0.15)' }}>
              <div style={{ fontWeight: 600, marginBottom: 8, color: 'var(--primary-neon)', fontSize: '0.9rem' }}>📝 AI-Generated Insights</div>
              <ul style={{ paddingLeft: 20, color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.8 }}>
                <li>Overall Equipment Effectiveness is at <strong style={{ color: 'var(--text-main)' }}>{generated.summary.oee}%</strong> — {generated.summary.oee >= 75 ? 'above industry average.' : 'below target — review bottleneck machines.'}</li>
                <li>High Efficiency classification accounts for <strong style={{ color: 'var(--status-good)' }}>{generated.summary.efficiency_high}%</strong> of all production records. Low Efficiency: <strong style={{ color: 'var(--status-critical)' }}>{generated.summary.efficiency_low}%</strong>.</li>
                <li>There are <strong style={{ color: 'var(--status-critical)' }}>{generated.summary.critical_alerts} Critical</strong> active alerts requiring immediate intervention.</li>
                <li><strong style={{ color: 'var(--status-warning)' }}>{generated.summary.maintenance_tasks}</strong> predictive maintenance tasks are pending ({generated.summary.critical_tasks} Critical priority).</li>
                <li>AI Health Score is <strong style={{ color: 'var(--status-good)' }}>{generated.summary.ai_health}/100</strong> — overall factory health is {generated.summary.ai_health >= 75 ? 'excellent.' : generated.summary.ai_health >= 50 ? 'fair — recommend preventative action.' : 'poor — immediate maintenance required.'}</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
