import React from 'react';
import { Search, CheckCircle2 } from 'lucide-react';

const alertData = [
  { id: 'ALT-001', machine: 'MCH-004', type: 'Temperature', priority: 'Critical', msg: 'Hydraulic oil temperature high', time: '10:30 AM', status: 'New' },
  { id: 'ALT-002', machine: 'MCH-002', type: 'Vibration', priority: 'High', msg: 'Abnormal vibration detected', time: '09:15 AM', status: 'New' },
  { id: 'ALT-003', machine: 'MCH-012', type: 'Pressure', priority: 'Medium', msg: 'Air pressure below threshold', time: '08:45 AM', status: 'Acknowledged' },
  { id: 'ALT-004', machine: 'MCH-005', type: 'Current', priority: 'High', msg: 'Motor current above normal', time: '08:20 AM', status: 'New' },
  { id: 'ALT-005', machine: 'MCH-001', type: 'Temperature', priority: 'Low', msg: 'Spindle temperature elevated', time: '07:50 AM', status: 'Acknowledged' },
  { id: 'ALT-006', machine: 'MCH-007', type: 'Sensor', priority: 'Low', msg: 'Sensor reading unstable', time: '06:30 AM', status: 'Acknowledged' },
  { id: 'ALT-007', machine: 'MCH-003', type: 'Speed', priority: 'Low', msg: 'Speed variation detected', time: '06:10 AM', status: 'New' },
];

export default function Alerts() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ marginBottom: '5px' }}>Alerts</h2>
          <p style={{ fontSize: '0.9rem' }}>Real-time alerts and notifications</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-cols-4" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Total Alerts</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>45</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-critical)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Critical</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-critical)' }}>8</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-warning)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>High</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-warning)' }}>15</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--primary-neon)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Medium</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary-neon)' }}>14</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-good)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Low</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-good)' }}>8</div>
        </div>
      </div>

      {/* Table Container */}
      <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        
        {/* Toolbar */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input type="text" className="input-field" placeholder="Search alerts..." style={{ paddingLeft: '35px', width: '220px' }} />
            </div>
            <select className="input-field" style={{ width: '130px' }}><option>All Status</option></select>
            <select className="input-field" style={{ width: '130px' }}><option>All Priorities</option></select>
            <select className="input-field" style={{ width: '130px' }}><option>Today</option></select>
          </div>
          
          <button className="btn btn-secondary">
            <CheckCircle2 size={16} /> Mark All Read
          </button>
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)', color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Alert ID</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Machine</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Alert Type</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Priority</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Message</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Time</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {alertData.map((a) => (
                <tr key={a.id} style={{ borderBottom: '1px solid var(--border-color)' }} className="table-row-hover">
                  <td style={{ padding: '15px', fontWeight: 500, color: 'var(--text-muted)' }}>{a.id}</td>
                  <td style={{ padding: '15px', color: 'var(--primary-neon)', fontWeight: 500 }}>{a.machine}</td>
                  <td style={{ padding: '15px' }}>{a.type}</td>
                  <td style={{ padding: '15px' }}>
                    <span style={{ color: a.priority === 'Critical' ? 'var(--status-critical)' : a.priority === 'High' ? 'var(--status-warning)' : a.priority === 'Medium' ? 'var(--primary-neon)' : 'var(--status-good)', fontWeight: 600 }}>
                      {a.priority}
                    </span>
                  </td>
                  <td style={{ padding: '15px' }}>{a.msg}</td>
                  <td style={{ padding: '15px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{a.time}</td>
                  <td style={{ padding: '15px' }}>
                    <span className={`tag ${a.status === 'New' ? 'tag-critical' : 'tag-neutral'}`} style={a.status === 'New' ? { background: 'var(--status-critical)', color: '#000', border: 'none' } : {}}>
                      {a.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
        .table-row-hover:hover { background-color: rgba(255,255,255,0.02); }
      `}} />
    </div>
  );
}
