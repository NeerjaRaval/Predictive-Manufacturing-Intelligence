import React from 'react';
import { Search, Plus, Filter, MoreHorizontal, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const machineData = [
  { id: 'MCH-001', name: 'CNC Lathe 01', dept: 'Machining', health: 92, status: 'Healthy', updated: '2 min ago' },
  { id: 'MCH-002', name: 'Robotic Arm 02', dept: 'Assembly', health: 78, status: 'Warning', updated: '5 min ago' },
  { id: 'MCH-003', name: 'Conveyor Belt 01', dept: 'Material Handling', health: 99, status: 'Healthy', updated: '1 min ago' },
  { id: 'MCH-004', name: 'Hydraulic Press 01', dept: 'Forming', health: 45, status: 'Critical', updated: '2 min ago' },
  { id: 'MCH-005', name: 'Injection Molding 01', dept: 'Molding', health: 85, status: 'Healthy', updated: '10 min ago' },
  { id: 'MCH-006', name: 'Packaging Machine 01', dept: 'Packaging', health: 62, status: 'Warning', updated: '4 min ago' },
];

export default function Machines() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Header */}
      <div>
        <h2 style={{ marginBottom: '5px' }}>Machines</h2>
        <p style={{ fontSize: '0.9rem' }}>Monitor and manage all machines in real-time</p>
      </div>

      {/* KPI Cards */}
      <div className="grid-cols-4">
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Total Machines</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>128</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-good)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Healthy</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-good)' }}>98</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-warning)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Warning</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-warning)' }}>20</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-critical)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Critical</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-critical)' }}>10</div>
        </div>
      </div>

      {/* Table Container */}
      <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        
        {/* Toolbar */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input type="text" className="input-field" placeholder="Search machines..." style={{ paddingLeft: '35px', width: '250px' }} />
            </div>
            <select className="input-field" style={{ width: '150px' }}>
              <option>All Departments</option>
              <option>Machining</option>
              <option>Assembly</option>
            </select>
            <select className="input-field" style={{ width: '150px' }}>
              <option>All Status</option>
              <option>Healthy</option>
              <option>Warning</option>
              <option>Critical</option>
            </select>
          </div>
          
          <button className="btn btn-primary">
            <Plus size={16} /> Add Machine
          </button>
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)', color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Machine ID</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Machine Name</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Department</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Health Score</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Status</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Last Updated</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {machineData.map((m) => (
                <tr key={m.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.2s' }} className="table-row-hover">
                  <td style={{ padding: '15px', fontWeight: 500 }}>{m.id}</td>
                  <td style={{ padding: '15px' }}>{m.name}</td>
                  <td style={{ padding: '15px', color: 'var(--text-muted)' }}>{m.dept}</td>
                  <td style={{ padding: '15px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ flex: 1, height: '6px', background: 'var(--bg-hover)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${m.health}%`, height: '100%', background: m.status === 'Healthy' ? 'var(--status-good)' : m.status === 'Warning' ? 'var(--status-warning)' : 'var(--status-critical)' }}></div>
                      </div>
                      <span style={{ fontSize: '0.85rem', width: '30px', color: m.status === 'Healthy' ? 'var(--status-good)' : m.status === 'Warning' ? 'var(--status-warning)' : 'var(--status-critical)' }}>{m.health}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '15px' }}>
                    <span className={`tag tag-${m.status === 'Healthy' ? 'good' : m.status === 'Warning' ? 'warning' : 'critical'}`}>
                      {m.status}
                    </span>
                  </td>
                  <td style={{ padding: '15px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{m.updated}</td>
                  <td style={{ padding: '15px', textAlign: 'right' }}>
                    <button style={{ background: 'transparent', border: 'none', color: 'var(--primary-neon)', cursor: 'pointer', fontWeight: 500 }}>View</button>
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
