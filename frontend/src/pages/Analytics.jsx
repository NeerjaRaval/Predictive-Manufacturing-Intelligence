import React, { useState, useEffect } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';
import { Download, RefreshCw } from 'lucide-react';

const TOOLTIP_STYLE = { backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', color: 'var(--text-main)' };
function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

export default function Analytics() {
  const [data, setData]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays]   = useState(30);

  const load = () => {
    setLoading(true);
    fetch(`/api/analytics?days=${days}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { load(); }, [days]);

  return (
    <>
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
      <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h2 style={{ marginBottom: 5 }}>Analytics</h2>
            <p style={{ fontSize: '0.9rem' }}>Deep insights from your local manufacturing CSV data</p>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <select className="input-field" style={{ width: 150, fontSize: '0.85rem' }} value={days} onChange={e => setDays(Number(e.target.value))}>
              <option value={7}>Last 7 Days</option>
              <option value={14}>Last 14 Days</option>
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
            </select>
            <button className="btn btn-secondary" onClick={load}><RefreshCw size={14} /> Refresh</button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid-cols-4">
          {[
            ['OEE', data?.kpis?.oee, '%', 'var(--status-cyan)'],
            ['Availability', data?.kpis?.availability, '%', 'var(--status-good)'],
            ['Performance', data?.kpis?.performance, '%', 'var(--primary-neon)'],
            ['Quality', data?.kpis?.quality, '%', 'var(--status-warning)'],
          ].map(([label, val, unit, color]) => (
            <div key={label} className="card">
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 10 }}>{label}</p>
              {loading ? <Shimmer height={40} /> : (
                <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color }}>
                  {val ?? '--'}<span style={{ fontSize: '1.1rem', color: 'var(--text-muted)' }}>{unit}</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid-cols-2">
          {/* OEE Trend */}
          <div className="card">
            <h3 style={{ marginBottom: '1.25rem' }}>OEE Trend</h3>
            {loading ? <Shimmer height={280} radius={12} /> : (
              <div style={{ height: 280 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data?.oee_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="oeeGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="var(--primary-neon)" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="var(--primary-neon)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} domain={[0, 100]} tickFormatter={v => `${v}%`} />
                    <Tooltip contentStyle={TOOLTIP_STYLE} formatter={v => `${v}%`} />
                    <Area type="monotone" dataKey="value" stroke="var(--primary-neon)" strokeWidth={3} fillOpacity={1} fill="url(#oeeGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Production vs Target */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3>Production vs Target</h3>
              <div style={{ display: 'flex', gap: 12, fontSize: '0.8rem' }}>
                {[['Actual', 'var(--primary-neon)'], ['Target', 'rgba(88,166,255,0.2)']].map(([label, color]) => (
                  <span key={label} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ width: 10, height: 10, borderRadius: '50%', background: color, display: 'inline-block' }} /> {label}
                  </span>
                ))}
              </div>
            </div>
            {loading ? <Shimmer height={280} radius={12} /> : (
              <div style={{ height: 280 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data?.production_vs_target || []} margin={{ top: 10, right: 0, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                    <Tooltip cursor={{ fill: 'var(--bg-hover)' }} contentStyle={TOOLTIP_STYLE} />
                    <Bar dataKey="target" fill="rgba(88,166,255,0.2)" radius={[4, 4, 0, 0]} barSize={18} />
                    <Bar dataKey="actual" fill="var(--primary-neon)" radius={[4, 4, 0, 0]} barSize={18} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid-cols-2">
          {/* Top Bottlenecks */}
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Top Bottleneck Machines</h3>
            {loading ? <Shimmer height={200} /> : (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', borderBottom: '1px solid var(--border-color)' }}>
                    {['Machine', 'Low Efficiency %', 'Defect Rate', 'Error Rate'].map(h => (
                      <th key={h} style={{ padding: '10px 0', fontWeight: 600 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(data?.bottlenecks || []).map((b, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '12px 0', fontWeight: 600, color: 'var(--primary-neon)' }}>{b.machine}</td>
                      <td style={{ padding: '12px 0', color: 'var(--status-critical)', fontWeight: 600 }}>{b.impact}</td>
                      <td style={{ padding: '12px 0', color: 'var(--text-muted)' }}>{b.defect}%</td>
                      <td style={{ padding: '12px 0', color: 'var(--text-muted)' }}>{b.error}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Downtime Reasons */}
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Downtime & Disruption Reasons</h3>
            {loading ? <Shimmer height={200} /> : (
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <div style={{ flex: 1, height: 200 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={data?.downtime_reasons || []} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={4}>
                        {(data?.downtime_reasons || []).map((entry, i) => (
                          <Cell key={i} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={TOOLTIP_STYLE} formatter={v => `${v}%`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {(data?.downtime_reasons || []).map((item, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.82rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: item.color, display: 'inline-block', flexShrink: 0 }} />
                        <span style={{ color: 'var(--text-muted)' }}>{item.name}</span>
                      </div>
                      <span style={{ fontWeight: 600 }}>{item.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
