import React, { useState, useEffect } from 'react';
import { Search, Plus, Filter, ChevronLeft, ChevronRight, RefreshCw, X } from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

const TOOLTIP_STYLE = { backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', color: 'var(--text-main)' };

function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

function HealthBar({ value, status }) {
  const color = status === 'Healthy' ? 'var(--status-good)' : status === 'Warning' ? 'var(--status-warning)' : 'var(--status-critical)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{ flex: 1, height: 6, background: 'var(--bg-hover)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${value}%`, height: '100%', background: color, transition: 'width 0.6s ease', borderRadius: 3 }} />
      </div>
      <span style={{ fontSize: '0.85rem', width: 34, color, fontWeight: 600 }}>{value}%</span>
    </div>
  );
}

// ── Machine Detail Drawer ────────────────────────────────────
function MachineDrawer({ machine, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!machine) return;
    setLoading(true);
    fetch(`/api/machines/${machine.machine_id}?days=30`)
      .then(r => r.json())
      .then(d => { setDetail(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [machine]);

  if (!machine) return null;

  const statusColor = machine.status === 'Healthy' ? 'var(--status-good)' : machine.status === 'Warning' ? 'var(--status-warning)' : 'var(--status-critical)';

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex' }}>
      {/* Backdrop */}
      <div onClick={onClose} style={{ flex: 1, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }} />
      {/* Panel */}
      <div style={{ width: 420, background: 'var(--bg-panel)', borderLeft: '1px solid var(--border-color)', overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', animation: 'slideIn 0.25s ease' }}>
        <style>{`@keyframes slideIn{from{transform:translateX(100%)}to{transform:translateX(0)}} @keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ margin: 0 }}>{machine.id}</h2>
            <span className={`tag tag-${machine.status === 'Healthy' ? 'good' : machine.status === 'Warning' ? 'warning' : 'critical'}`}>{machine.status}</span>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 4 }}><X size={20} /></button>
        </div>

        {/* Quick Stats */}
        <div className="grid-cols-2" style={{ gap: '0.75rem' }}>
          {[
            ['Health Score',    `${machine.health}%`,                  statusColor],
            ['Efficiency',      machine.dominant_efficiency,             machine.dominant_efficiency === 'High' ? 'var(--status-good)' : machine.dominant_efficiency === 'Medium' ? 'var(--status-warning)' : 'var(--status-critical)'],
            ['Temperature',     `${machine.avg_temperature}°C`,         machine.avg_temperature > 80 ? 'var(--status-critical)' : 'var(--text-main)'],
            ['Vibration',       `${machine.avg_vibration} Hz`,          machine.avg_vibration > 6 ? 'var(--status-warning)' : 'var(--text-main)'],
            ['Power',           `${machine.avg_power} kW`,              'var(--text-main)'],
            ['Latency',         `${machine.avg_latency} ms`,            machine.avg_latency > 15 ? 'var(--status-warning)' : 'var(--text-main)'],
            ['Packet Loss',     `${machine.avg_packet_loss}%`,          machine.avg_packet_loss > 1 ? 'var(--status-warning)' : 'var(--text-main)'],
            ['Maint. Score',    machine.avg_maint_score,                machine.avg_maint_score < 0.4 ? 'var(--status-critical)' : 'var(--status-good)'],
          ].map(([label, val, color]) => (
            <div key={label} style={{ background: 'var(--bg-hover)', padding: '10px 12px', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
              <div style={{ fontWeight: 700, color }}>{val}</div>
            </div>
          ))}
        </div>

        {/* Efficiency Breakdown */}
        {!loading && detail?.efficiency_breakdown && (
          <div>
            <h4 style={{ marginBottom: '0.75rem', fontSize: '0.9rem' }}>Efficiency Status Distribution</h4>
            {[['High', 'good'], ['Medium', 'warning'], ['Low', 'critical']].map(([k, cls]) => (
              <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <div style={{ width: 50, fontSize: '0.8rem', color: 'var(--text-muted)' }}>{k}</div>
                <div style={{ flex: 1, height: 8, background: 'var(--bg-main)', borderRadius: 4, overflow: 'hidden' }}>
                  <div style={{ width: `${detail.efficiency_breakdown[k.toLowerCase()]}%`, height: '100%', background: `var(--status-${cls})`, borderRadius: 4 }} />
                </div>
                <div style={{ width: 36, fontSize: '0.8rem', fontWeight: 600, textAlign: 'right', color: `var(--status-${cls})` }}>
                  {detail.efficiency_breakdown[k.toLowerCase()]}%
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 30-day Trend Chart */}
        <div>
          <h4 style={{ marginBottom: '0.75rem', fontSize: '0.9rem' }}>30-Day Telemetry Trend</h4>
          {loading ? <Shimmer height={200} /> : (
            <div style={{ height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={detail?.trend || []} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
                  <defs>
                    <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--status-critical)" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="var(--status-critical)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="vibGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--primary-neon)" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="var(--primary-neon)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Area type="monotone" dataKey="temperature" stroke="var(--status-critical)" strokeWidth={2} fill="url(#tempGrad)" />
                  <Area type="monotone" dataKey="vibration"   stroke="var(--primary-neon)"   strokeWidth={2} fill="url(#vibGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
          <div style={{ display: 'flex', gap: 16, marginTop: 6, fontSize: '0.75rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 10, height: 3, background: 'var(--status-critical)', display: 'inline-block', borderRadius: 2 }} /> Temperature</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span style={{ width: 10, height: 3, background: 'var(--primary-neon)', display: 'inline-block', borderRadius: 2 }} /> Vibration</span>
          </div>
        </div>

        {detail && (
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: 12 }}>
            <strong>{detail.total_records}</strong> records from {detail.date_range?.from} to {detail.date_range?.to}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main Machines Component ─────────────────────────────────
export default function Machines() {
  const [machines, setMachines]     = useState([]);
  const [summary, setSummary]       = useState({});
  const [loading, setLoading]       = useState(true);
  const [search, setSearch]         = useState('');
  const [statusFilter, setStatus]   = useState('');
  const [page, setPage]             = useState(0);
  const [total, setTotal]           = useState(0);
  const [selected, setSelected]     = useState(null);
  const LIMIT = 15;

  const loadMachines = () => {
    setLoading(true);
    const params = new URLSearchParams({ limit: LIMIT, offset: page * LIMIT });
    if (search)  params.set('search', search);
    if (statusFilter) params.set('status', statusFilter);

    fetch(`/api/machines?${params}`)
      .then(r => r.json())
      .then(d => {
        setMachines(d.machines || []);
        setTotal(d.total || 0);
        setSummary({ healthy: d.healthy_count, warning: d.warning_count, critical: d.critical_count });
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => { loadMachines(); }, [search, statusFilter, page]);

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <>
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
      {selected && <MachineDrawer machine={selected} onClose={() => setSelected(null)} />}

      <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h2 style={{ marginBottom: 5 }}>Machines</h2>
            <p style={{ fontSize: '0.9rem' }}>Monitor all {total} industrial machines in real-time</p>
          </div>
          <button className="btn btn-secondary" onClick={loadMachines} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>

        {/* KPI Cards */}
        <div className="grid-cols-4">
          <div className="card">
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 10 }}>Total Machines</p>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{loading ? '--' : total}</div>
          </div>
          <div className="card" style={{ borderBottom: '3px solid var(--status-good)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 10 }}>Healthy</p>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-good)' }}>{loading ? '--' : summary.healthy ?? 0}</div>
          </div>
          <div className="card" style={{ borderBottom: '3px solid var(--status-warning)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 10 }}>Warning</p>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-warning)' }}>{loading ? '--' : summary.warning ?? 0}</div>
          </div>
          <div className="card" style={{ borderBottom: '3px solid var(--status-critical)' }}>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 10 }}>Critical</p>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-critical)' }}>{loading ? '--' : summary.critical ?? 0}</div>
          </div>
        </div>

        {/* Table Card */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {/* Toolbar */}
          <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
            <div style={{ display: 'flex', gap: 12, flex: 1 }}>
              <div style={{ position: 'relative', flex: 1, maxWidth: 280 }}>
                <Search size={15} style={{ position: 'absolute', left: 10, top: 11, color: 'var(--text-muted)' }} />
                <input type="text" className="input-field" placeholder="Search by machine ID..." value={search} onChange={e => { setSearch(e.target.value); setPage(0); }} style={{ paddingLeft: 34, fontSize: '0.85rem' }} />
              </div>
              <select className="input-field" style={{ width: 150, fontSize: '0.85rem' }} value={statusFilter} onChange={e => { setStatus(e.target.value); setPage(0); }}>
                <option value="">All Status</option>
                <option value="Healthy">Healthy</option>
                <option value="Warning">Warning</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
              {total > 0 ? `${page * LIMIT + 1}–${Math.min((page + 1) * LIMIT, total)} of ${total}` : ''}
            </div>
          </div>

          {/* Table */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.02)', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
                  {['Machine ID','Mode','Health Score','Status','Avg Temp','Avg Vibration','Efficiency','Error Rate','Action'].map(h => (
                    <th key={h} style={{ padding: '12px 16px', fontWeight: 600, borderBottom: '1px solid var(--border-color)', whiteSpace: 'nowrap' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: 8 }).map((_, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        {Array.from({ length: 9 }).map((_, j) => (
                          <td key={j} style={{ padding: '14px 16px' }}><Shimmer height={16} /></td>
                        ))}
                      </tr>
                    ))
                  : machines.map(m => (
                      <tr key={m.machine_id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.15s', cursor: 'pointer' }}
                        onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.025)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                        <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--primary-neon)' }}>{m.id}</td>
                        <td style={{ padding: '14px 16px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{m.operation_mode}</td>
                        <td style={{ padding: '14px 16px', minWidth: 160 }}><HealthBar value={m.health} status={m.status} /></td>
                        <td style={{ padding: '14px 16px' }}>
                          <span className={`tag tag-${m.status === 'Healthy' ? 'good' : m.status === 'Warning' ? 'warning' : 'critical'}`}>{m.status}</span>
                        </td>
                        <td style={{ padding: '14px 16px', color: m.avg_temperature > 80 ? 'var(--status-critical)' : 'var(--text-main)', fontSize: '0.9rem' }}>{m.avg_temperature}°C</td>
                        <td style={{ padding: '14px 16px', color: m.avg_vibration > 6 ? 'var(--status-warning)' : 'var(--text-main)', fontSize: '0.9rem' }}>{m.avg_vibration} Hz</td>
                        <td style={{ padding: '14px 16px' }}>
                          <span style={{ color: m.dominant_efficiency === 'High' ? 'var(--status-good)' : m.dominant_efficiency === 'Medium' ? 'var(--status-warning)' : 'var(--status-critical)', fontWeight: 600, fontSize: '0.85rem' }}>
                            {m.dominant_efficiency}
                          </span>
                        </td>
                        <td style={{ padding: '14px 16px', fontSize: '0.9rem', color: m.avg_error_rate > 5 ? 'var(--status-warning)' : 'var(--text-muted)' }}>{m.avg_error_rate}%</td>
                        <td style={{ padding: '14px 16px' }}>
                          <button onClick={() => setSelected(m)} style={{ background: 'rgba(88,166,255,0.1)', border: '1px solid rgba(88,166,255,0.25)', color: 'var(--primary-neon)', cursor: 'pointer', padding: '4px 12px', borderRadius: 6, fontSize: '0.8rem', fontWeight: 500 }}>
                            View
                          </button>
                        </td>
                      </tr>
                    ))
                }
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 12, padding: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <button className="btn btn-secondary" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} style={{ padding: '6px 12px' }}>
                <ChevronLeft size={16} />
              </button>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Page {page + 1} / {totalPages}</span>
              <button className="btn btn-secondary" onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} style={{ padding: '6px 12px' }}>
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
