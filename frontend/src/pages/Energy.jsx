import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Download } from 'lucide-react';

const energyData = [
  { name: 'May 14', value: 1200 },
  { name: 'May 15', value: 1350 },
  { name: 'May 16', value: 1100 },
  { name: 'May 17', value: 1400 },
  { name: 'May 18', value: 1250 },
  { name: 'May 19', value: 1380 },
  { name: 'May 20', value: 1450 },
];

const deptData = [
  { name: 'Machining', value: 35.2, color: 'var(--primary-neon)' },
  { name: 'Assembly', value: 25.4, color: 'var(--status-warning)' },
  { name: 'Forming', value: 20.2, color: 'var(--status-critical)' },
  { name: 'Molding', value: 12.8, color: '#bc8cff' },
  { name: 'Others', value: 6.4, color: 'var(--text-muted)' },
];

export default function Energy() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ marginBottom: '5px' }}>Energy Management</h2>
          <p style={{ fontSize: '0.9rem' }}>Monitor and optimize energy consumption</p>
        </div>
        <div style={{ display: 'flex', gap: '15px' }}>
          <select className="input-field" style={{ width: '150px' }}>
            <option>This Month</option>
            <option>Last Month</option>
          </select>
          <button className="btn btn-secondary">
            <Download size={16} /> Export
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-cols-4">
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Total Consumption</p>
          <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>12,456<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}> kWh</span></div>
            <span style={{ color: 'var(--status-critical)', fontSize: '0.85rem', marginBottom: '8px' }}>+4.2% vs last month</span>
          </div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Cost</p>
          <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>$2,345</div>
            <span style={{ color: 'var(--status-critical)', fontSize: '0.85rem', marginBottom: '8px' }}>+12.8% vs last month</span>
          </div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>CO2 Emissions</p>
          <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>8.7<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}> tCO2</span></div>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '8px' }}>-0.5% vs last month</span>
          </div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Efficiency</p>
          <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>85.2<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>%</span></div>
            <span style={{ color: 'var(--status-good)', fontSize: '0.85rem', marginBottom: '8px' }}>+3.2% vs last month</span>
          </div>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid-cols-2">
        <div className="card">
          <h3 style={{ marginBottom: '1.5rem' }}>Energy Consumption Trend (kWh)</h3>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={energyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorEnergy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary-neon)" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="var(--primary-neon)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                <Area type="monotone" dataKey="value" stroke="var(--primary-neon)" strokeWidth={3} fillOpacity={1} fill="url(#colorEnergy)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1.5rem' }}>Energy by Department</h3>
          <div style={{ display: 'flex', height: '300px' }}>
            <div style={{ flex: 1, position: 'relative' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={deptData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {deptData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)' }} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>12,456</div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Total kWh</div>
              </div>
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '15px' }}>
              {deptData.map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: 12, height: 12, borderRadius: '2px', background: item.color }}></span>
                    <span style={{ color: 'var(--text-main)' }}>{item.name}</span>
                  </div>
                  <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="card">
        <h3 style={{ marginBottom: '1.5rem' }}>Top Energy Consumers</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '10px 0', fontWeight: 600 }}>Department</th>
              <th style={{ padding: '10px 0', fontWeight: 600 }}>Consumption (kWh)</th>
              <th style={{ padding: '10px 0', fontWeight: 600 }}>Percentage</th>
            </tr>
          </thead>
          <tbody>
            {[
              { dept: 'Machining', val: '4,384', pct: 35.2 },
              { dept: 'Assembly', val: '3,164', pct: 25.4 },
              { dept: 'Forming', val: '2,516', pct: 20.2 },
              { dept: 'Molding', val: '1,594', pct: 12.8 },
              { dept: 'Others', val: '798', pct: 6.4 },
            ].map((d, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '15px 0', fontWeight: 500 }}>{d.dept}</td>
                <td style={{ padding: '15px 0', color: 'var(--text-muted)' }}>{d.val}</td>
                <td style={{ padding: '15px 0', width: '50%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                    <div style={{ flex: 1, height: '8px', background: 'var(--bg-hover)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${d.pct}%`, height: '100%', background: 'var(--primary-neon)' }}></div>
                    </div>
                    <span style={{ fontSize: '0.85rem', width: '40px', textAlign: 'right' }}>{d.pct}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
