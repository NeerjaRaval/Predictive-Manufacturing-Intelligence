import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { AlertCircle, Activity, TrendingUp, CheckCircle, ChevronRight, Server, Lightbulb } from 'lucide-react';

const data = [
  { name: 'May 14', value: 4000 },
  { name: 'May 15', value: 3000 },
  { name: 'May 16', value: 2000 },
  { name: 'May 17', value: 2780 },
  { name: 'May 18', value: 1890 },
  { name: 'May 19', value: 2390 },
  { name: 'May 20', value: 3490 },
];

const barData = [
  { name: 'M-01', risk: 80, color: 'var(--status-critical)' },
  { name: 'M-04', risk: 65, color: 'var(--status-warning)' },
  { name: 'M-07', risk: 45, color: 'var(--status-warning)' },
  { name: 'M-10', risk: 30, color: 'var(--primary-neon)' },
  { name: 'M-13', risk: 25, color: 'var(--primary-neon)' },
];

export default function Dashboard() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', gap: '1.5rem' }}>
      {/* Left Column */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* KPI Row */}
        <div className="grid-cols-4">
          <div className="card">
            <h4 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>Overall Equipment Effectiveness</h4>
            <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-cyan)', lineHeight: 1 }}>78<span style={{ fontSize: '1.2rem' }}>%</span></div>
              <span className="tag tag-good">+6.7% vs last 7 days</span>
            </div>
          </div>

          <div className="card">
            <h4 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>Active Alerts</h4>
            <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-critical)', lineHeight: 1 }}>12</div>
              <span className="tag tag-critical" style={{ background: 'transparent', padding: 0 }}>High Priority</span>
            </div>
            <div style={{ color: 'var(--primary-neon)', fontSize: '0.8rem', marginTop: '10px', cursor: 'pointer' }}>View all alerts <ChevronRight size={12} style={{ display: 'inline' }} /></div>
          </div>

          <div className="card">
            <h4 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>Predicted Failures</h4>
            <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-warning)', lineHeight: 1 }}>7</div>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>in next 7 days</span>
            </div>
            <div style={{ color: 'var(--primary-neon)', fontSize: '0.8rem', marginTop: '10px', cursor: 'pointer' }}>View predictions <ChevronRight size={12} style={{ display: 'inline' }} /></div>
          </div>

          <div className="card">
            <h4 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>AI Health Score</h4>
            <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-good)', lineHeight: 1 }}>85<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>/100</span></div>
              <span className="tag tag-good">Excellent</span>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid-cols-3">
          <div className="card" style={{ gridColumn: 'span 2' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3>Production Trend</h3>
              <select className="input-field" style={{ width: '120px', padding: '4px 8px' }}>
                <option>Last 7 Days</option>
                <option>Last 30 Days</option>
              </select>
            </div>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary-neon)" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="var(--primary-neon)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                  <Area type="monotone" dataKey="value" stroke="var(--primary-neon)" strokeWidth={3} fillOpacity={1} fill="url(#colorUv)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3>Failure Prediction</h3>
            <p style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>Risk Score (Next 7 Days)</p>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip cursor={{ fill: 'var(--bg-hover)' }} contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                  <Bar dataKey="risk" radius={[4, 4, 0, 0]}>
                    {barData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid-cols-3">
          <div className="card">
            <h3>Factory Overview</h3>
            <p style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>Digital Twin</p>
            <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed var(--border-color)', borderRadius: '8px', background: 'var(--bg-hover)' }}>
              <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                <Server size={48} style={{ opacity: 0.5, marginBottom: '10px' }} />
                <p>3D Visualization Ready</p>
              </div>
            </div>
          </div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3>Machine Health</h3>
              <div style={{ color: 'var(--text-muted)', cursor: 'pointer' }}>...</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {[{ id: '01', name: 'CNC Lathe', health: 92, status: 'good' }, { id: '02', name: 'Robotic Arm', health: 78, status: 'warning' }, { id: '15', name: 'Conveyor Belt', health: 99, status: 'good' }].map(m => (
                <div key={m.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-hover)', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: 36, height: 36, borderRadius: '8px', background: `var(--status-${m.status})`, opacity: 0.8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 'bold' }}>M</div>
                    <div>
                      <div style={{ fontWeight: 500 }}>Machine {m.id}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{m.name}</div>
                    </div>
                  </div>
                  <div style={{ color: `var(--status-${m.status})`, fontWeight: 'bold' }}>{m.health}%</div>
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3>Maintenance Queue</h3>
              <div style={{ color: 'var(--text-muted)', cursor: 'pointer' }}>...</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div style={{ borderLeft: '3px solid var(--status-critical)', paddingLeft: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 500 }}>Replace Bearing</span>
                  <span className="tag tag-critical">High</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>Machine 12 • Due in 1 day</div>
              </div>
              <div style={{ borderLeft: '3px solid var(--status-warning)', paddingLeft: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 500 }}>Inspect Motor</span>
                  <span className="tag tag-warning">Medium</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>Machine 07 • Due in 3 days</div>
              </div>
              <div style={{ borderLeft: '3px solid var(--status-good)', paddingLeft: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 500 }}>Calibrate Sensor</span>
                  <span className="tag tag-good">Low</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>Machine 03 • Due in 5 days</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column (AI Copilot) */}
      <div className="card" style={{ width: '300px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Lightbulb size={18} color="var(--primary-neon)" /> AI Copilot <span className="tag tag-neutral">BETA</span>
          </h3>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ background: 'var(--bg-hover)', padding: '12px', borderRadius: '12px 12px 12px 0' }}>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-main)' }}>How can I help you today?</p>
          </div>

          <div style={{ background: 'var(--primary-neon)', padding: '12px', borderRadius: '12px 12px 0 12px', alignSelf: 'flex-end', maxWidth: '80%' }}>
            <p style={{ fontSize: '0.9rem', color: '#000', fontWeight: 500 }}>Why is Machine 12 overheating?</p>
          </div>

          <div style={{ background: 'var(--bg-hover)', padding: '12px', borderRadius: '12px 12px 12px 0' }}>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '8px' }}>Here's what I found:</p>
            <ul style={{ fontSize: '0.85rem', color: 'var(--text-muted)', paddingLeft: '20px', marginBottom: '12px' }}>
              <li style={{ marginBottom: '4px' }}>Vibration levels are 42% higher than normal</li>
              <li style={{ marginBottom: '4px' }}>Bearing wear detected</li>
              <li>Coolant flow rate is low</li>
            </ul>
            <div style={{ padding: '10px', background: 'rgba(88, 166, 255, 0.1)', borderRadius: '8px', border: '1px solid rgba(88, 166, 255, 0.2)' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--primary-neon)', marginBottom: '4px' }}>Recommended Action:</div>
              <div style={{ fontSize: '0.85rem' }}>Schedule maintenance and replace bearing.</div>
            </div>
          </div>
        </div>

        <div style={{ position: 'relative' }}>
          <input type="text" className="input-field" placeholder="Ask anything..." style={{ paddingRight: '40px' }} />
          <button className="btn btn-primary" style={{ position: 'absolute', right: '4px', top: '4px', bottom: '4px', padding: '0 8px', borderRadius: '6px' }}>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
