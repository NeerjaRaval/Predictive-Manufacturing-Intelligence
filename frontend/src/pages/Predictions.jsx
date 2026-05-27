import React from 'react';
import { Search, Download, TrendingUp } from 'lucide-react';

const predictionData = [
  { id: 'PRD-001', machine: 'MCH-004', type: 'Hydraulic Leakage', risk: 'High', rul: '2 days', conf: '92%', date: 'May 20, 08:15 AM', status: 'Active' },
  { id: 'PRD-002', machine: 'MCH-002', type: 'Motor Overheating', risk: 'High', rul: '5 days', conf: '88%', date: 'May 20, 09:30 AM', status: 'Active' },
  { id: 'PRD-003', machine: 'MCH-006', type: 'Bearing Wear', risk: 'Medium', rul: '8 days', conf: '76%', date: 'May 19, 14:45 PM', status: 'Active' },
  { id: 'PRD-004', machine: 'MCH-012', type: 'Belt Misalignment', risk: 'Medium', rul: '9 days', conf: '72%', date: 'May 18, 10:20 AM', status: 'Active' },
  { id: 'PRD-005', machine: 'MCH-007', type: 'Spindle Vibration', risk: 'Medium', rul: '11 days', conf: '65%', date: 'May 18, 11:10 AM', status: 'Active' },
  { id: 'PRD-006', machine: 'MCH-001', type: 'Sensor Drift', risk: 'Low', rul: '15 days', conf: '58%', date: 'May 17, 09:00 AM', status: 'Resolved' },
  { id: 'PRD-007', machine: 'MCH-003', type: 'Gear Wear', risk: 'Low', rul: '18 days', conf: '54%', date: 'May 16, 16:30 PM', status: 'Active' },
];

export default function Predictions() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ marginBottom: '5px' }}>Predictions</h2>
          <p style={{ fontSize: '0.9rem' }}>AI-powered failure predictions and insights</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-cols-4" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Total Predictions</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>56</div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>High Risk</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-critical)' }}>12</div>
            <TrendingUp size={24} color="var(--status-critical)" />
          </div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Medium Risk</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-warning)' }}>28</div>
            <TrendingUp size={24} color="var(--status-warning)" />
          </div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Low Risk</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-good)' }}>16</div>
            <TrendingUp size={24} color="var(--status-good)" style={{ transform: 'scaleY(-1)' }} />
          </div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Resolved</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>38</div>
        </div>
      </div>

      {/* Table Container */}
      <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        
        {/* Toolbar */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input type="text" className="input-field" placeholder="Search predictions..." style={{ paddingLeft: '35px', width: '220px' }} />
            </div>
            <select className="input-field" style={{ width: '130px' }}><option>All Types</option></select>
            <select className="input-field" style={{ width: '130px' }}><option>All Machines</option></select>
            <select className="input-field" style={{ width: '130px' }}><option>All Risk Levels</option></select>
            <select className="input-field" style={{ width: '160px' }}><option>May 13 - May 20, 2024</option></select>
          </div>
          
          <button className="btn btn-secondary">
            <Download size={16} /> Export
          </button>
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)', color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Prediction ID</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Machine</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Failure Type</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Risk Level</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>RUL (Remaining)</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Confidence</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Predicted On</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {predictionData.map((p) => (
                <tr key={p.id} style={{ borderBottom: '1px solid var(--border-color)' }} className="table-row-hover">
                  <td style={{ padding: '15px', fontWeight: 500, color: 'var(--text-muted)' }}>{p.id}</td>
                  <td style={{ padding: '15px', color: 'var(--primary-neon)', fontWeight: 500 }}>{p.machine}</td>
                  <td style={{ padding: '15px' }}>{p.type}</td>
                  <td style={{ padding: '15px' }}>
                    <span style={{ color: p.risk === 'High' ? 'var(--status-critical)' : p.risk === 'Medium' ? 'var(--status-warning)' : 'var(--status-good)', fontWeight: 600 }}>
                      {p.risk}
                    </span>
                  </td>
                  <td style={{ padding: '15px' }}>{p.rul}</td>
                  <td style={{ padding: '15px' }}>{p.conf}</td>
                  <td style={{ padding: '15px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{p.date}</td>
                  <td style={{ padding: '15px' }}>
                    <span className={`tag tag-${p.status === 'Active' ? 'good' : 'neutral'}`}>
                      {p.status}
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
