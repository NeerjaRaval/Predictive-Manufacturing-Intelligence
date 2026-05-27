import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Download } from 'lucide-react';

const oeeData = [
  { name: 'May 14', value: 72 },
  { name: 'May 15', value: 75 },
  { name: 'May 16', value: 74 },
  { name: 'May 17', value: 78 },
  { name: 'May 18', value: 79 },
  { name: 'May 19', value: 76 },
  { name: 'May 20', value: 78.5 },
];

const productionData = [
  { name: 'May 14', actual: 4000, target: 4500 },
  { name: 'May 15', actual: 3000, target: 4000 },
  { name: 'May 16', actual: 2000, target: 3000 },
  { name: 'May 17', actual: 2780, target: 3500 },
  { name: 'May 18', actual: 1890, target: 2000 },
  { name: 'May 19', actual: 2390, target: 2500 },
  { name: 'May 20', actual: 3490, target: 3500 },
];

const downtimeData = [
  { name: 'Equipment Failure', value: 35.6, color: 'var(--status-critical)' },
  { name: 'Setup & Adjustment', value: 25.3, color: 'var(--primary-neon)' },
  { name: 'Maintenance', value: 18.2, color: 'var(--status-warning)' },
  { name: 'Material Shortage', value: 11.5, color: '#bc8cff' },
  { name: 'Others', value: 9.4, color: 'var(--text-muted)' },
];

export default function Analytics() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ marginBottom: '5px' }}>Analytics</h2>
          <p style={{ fontSize: '0.9rem' }}>Deep insights into your manufacturing operations</p>
        </div>
        <div style={{ display: 'flex', gap: '15px' }}>
          <select className="input-field" style={{ width: '150px' }}>
            <option>This Month</option>
            <option>Last Month</option>
            <option>This Year</option>
          </select>
          <button className="btn btn-secondary">
            <Download size={16} /> Export
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-cols-4">
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>OEE</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>78.5<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>%</span></div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Availability</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>82.3<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>%</span></div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Performance</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>76.8<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>%</span></div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Quality</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>96.1<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>%</span></div>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid-cols-2">
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem' }}>OEE Trend</h3>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={oeeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorOee" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary-neon)" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="var(--primary-neon)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} domain={[60, 100]} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                <Area type="monotone" dataKey="value" stroke="var(--primary-neon)" strokeWidth={3} fillOpacity={1} fill="url(#colorOee)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3>Production vs Target</h3>
            <div style={{ display: 'flex', gap: '15px', fontSize: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--primary-neon)' }}></span> Actual</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><span style={{ width: 10, height: 10, borderRadius: '50%', background: 'rgba(88, 166, 255, 0.2)' }}></span> Target</div>
            </div>
          </div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={productionData} margin={{ top: 10, right: 0, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip cursor={{fill: 'var(--bg-hover)'}} contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                <Bar dataKey="target" fill="rgba(88, 166, 255, 0.2)" radius={[4, 4, 0, 0]} barSize={20} />
                <Bar dataKey="actual" fill="var(--primary-neon)" radius={[4, 4, 0, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid-cols-2">
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Top Bottlenecks</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '10px 0', fontWeight: 600 }}>Machine</th>
                <th style={{ padding: '10px 0', fontWeight: 600 }}>Impact</th>
                <th style={{ padding: '10px 0', fontWeight: 600, textAlign: 'right' }}>Duration</th>
              </tr>
            </thead>
            <tbody>
              {[
                { id: 'MCH-004', name: 'Hydraulic Press 01', impact: '23.5%', duration: '4h 32m', color: 'var(--status-critical)' },
                { id: 'MCH-002', name: 'Robotic Arm 02', impact: '18.7%', duration: '3h 15m', color: 'var(--status-warning)' },
                { id: 'MCH-006', name: 'Conveyor Belt 01', impact: '12.3%', duration: '2h 45m', color: 'var(--status-warning)' },
              ].map((m, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '15px 0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: 32, height: 32, borderRadius: '8px', background: m.color, opacity: 0.8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 'bold', fontSize: '0.8rem' }}>M</div>
                      <div>
                        <div style={{ fontWeight: 500 }}>{m.id}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{m.name}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '15px 0' }}>{m.impact}</td>
                  <td style={{ padding: '15px 0', textAlign: 'right', color: 'var(--text-muted)' }}>{m.duration}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Downtime Reasons</h3>
          <div style={{ display: 'flex', height: '200px' }}>
            <div style={{ flex: 1 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={downtimeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {downtimeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '12px' }}>
              {downtimeData.map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: 10, height: 10, borderRadius: '50%', background: item.color }}></span>
                    <span style={{ color: 'var(--text-muted)' }}>{item.name}</span>
                  </div>
                  <span style={{ fontWeight: 600 }}>{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
