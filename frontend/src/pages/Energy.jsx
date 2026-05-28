import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Zap, RefreshCw } from 'lucide-react';

const TOOLTIP_STYLE = { backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', color: 'var(--text-main)' };
function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

export default function Energy() {
  const [data, setData]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays]   = useState(14);

  const load = () => {
    setLoading(true);
    fetch(`/api/energy?days=${days}`)
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
            <h2 style={{ marginBottom: 5 }}>Energy Analytics</h2>
            <p style={{ fontSize: '0.9rem' }}>Power consumption patterns and energy efficiency metrics</p>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <select className="input-field" style={{ width: 150, fontSize: '0.85rem' }} value={days} onChange={e => setDays(Number(e.target.value))}>
              <option value={7}>Last 7 Days</option>
              <option value={14}>Last 14 Days</option>
              <option value={30}>Last 30 Days</option>
            </select>
            <button className="btn btn-secondary" onClick={load}><RefreshCw size={14} /> Refresh</button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid-cols-4">
          {[
            ['Total Power Period', data?.summary?.total_kwh_period, 'kW', 'var(--primary-neon)', <Zap size={20} color="var(--primary-neon)" />],
            ['Average Power', data?.summary?.avg_kw, 'kW', 'var(--status-cyan)', null],
            ['Peak Power', data?.summary?.peak_kw, 'kW', 'var(--status-critical)', null],
            ['Latency-Power Correlation', data?.summary?.latency_power_corr, 'r', 'var(--status-warning)', null],
          ].map(([label, val, unit, color, icon]) => (
            <div key={label} className="card">
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 10 }}>{label}</p>
              {loading ? <Shimmer height={40} /> : (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color }}>
                    {val ?? '--'}<span style={{ fontSize: '1rem', color: 'var(--text-muted)', marginLeft: 4 }}>{unit}</span>
                  </div>
                  {icon}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid-cols-2">
          {/* Power Trend */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3>Power Consumption Trend</h3>
              <div style={{ display: 'flex', gap: 12, fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 10, height: 3, background: 'var(--primary-neon)', display: 'inline-block', borderRadius: 2 }} /> Avg</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 10, height: 3, background: 'var(--status-critical)', display: 'inline-block', borderRadius: 2 }} /> Peak</span>
              </div>
            </div>
            {loading ? <Shimmer height={260} radius={12} /> : (
              <div style={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data?.power_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="avgGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="var(--primary-neon)" stopOpacity={0.7} />
                        <stop offset="95%" stopColor="var(--primary-neon)" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="peakGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="var(--status-critical)" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="var(--status-critical)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={TOOLTIP_STYLE} />
                    <Area type="monotone" dataKey="max_power" stroke="var(--status-critical)" strokeWidth={2} fill="url(#peakGrad)" />
                    <Area type="monotone" dataKey="avg_power" stroke="var(--primary-neon)" strokeWidth={3} fill="url(#avgGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Top Power Consumers */}
          <div className="card">
            <h3 style={{ marginBottom: '1.25rem' }}>Top Power-Consuming Machines</h3>
            {loading ? <Shimmer height={260} radius={12} /> : (
              <div style={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data?.top_machines_power || []} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
                    <XAxis type="number" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis type="category" dataKey="machine" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} width={45} />
                    <Tooltip cursor={{ fill: 'var(--bg-hover)' }} contentStyle={TOOLTIP_STYLE} />
                    <Bar dataKey="avg_power" fill="var(--primary-neon)" radius={[0, 4, 4, 0]} barSize={14} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>

        {/* Energy Efficiency by Mode */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Energy Efficiency by Operation Mode</h3>
          {loading ? <Shimmer height={120} /> : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', borderBottom: '1px solid var(--border-color)' }}>
                    {['Operation Mode', 'Avg Power (kW)', 'Avg Speed (u/h)', 'Efficiency Ratio (units/kW)', 'Rating'].map(h => (
                      <th key={h} style={{ padding: '10px 16px', fontWeight: 600 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(data?.energy_by_mode || []).map((row, i) => {
                    const rating = row.efficiency_ratio > 40 ? 'Excellent' : row.efficiency_ratio > 25 ? 'Good' : row.efficiency_ratio > 15 ? 'Fair' : 'Poor';
                    const ratingClass = rating === 'Excellent' ? 'good' : rating === 'Good' ? 'good' : rating === 'Fair' ? 'warning' : 'critical';
                    return (
                      <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}
                        onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.025)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                        <td style={{ padding: '14px 16px', fontWeight: 600 }}>{row.mode}</td>
                        <td style={{ padding: '14px 16px' }}>{row.avg_power}</td>
                        <td style={{ padding: '14px 16px' }}>{row.avg_speed}</td>
                        <td style={{ padding: '14px 16px', fontWeight: 700, color: 'var(--primary-neon)' }}>{row.efficiency_ratio}</td>
                        <td style={{ padding: '14px 16px' }}><span className={`tag tag-${ratingClass}`}>{rating}</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
