import React from 'react';
import { Search, Plus, Wrench } from 'lucide-react';

const maintenanceData = [
  { id: 'WO-001', machine: 'MCH-004', type: 'Preventive', priority: 'High', status: 'In Progress', assigned: 'Ramesh K.', due: 'May 21, 2024' },
  { id: 'WO-002', machine: 'MCH-002', type: 'Preventive', priority: 'Medium', status: 'Open', assigned: 'Suresh P.', due: 'May 22, 2024' },
  { id: 'WO-003', machine: 'MCH-012', type: 'Corrective', priority: 'High', status: 'Open', assigned: 'Arjun M.', due: 'May 20, 2024' },
  { id: 'WO-004', machine: 'MCH-005', type: 'Predictive', priority: 'Medium', status: 'Open', assigned: 'Karthik S.', due: 'May 23, 2024' },
  { id: 'WO-005', machine: 'MCH-001', type: 'Corrective', priority: 'Low', status: 'In Progress', assigned: 'Vijay R.', due: 'May 21, 2024' },
  { id: 'WO-006', machine: 'MCH-007', type: 'Predictive', priority: 'Low', status: 'Scheduled', assigned: 'Manoj T.', due: 'May 25, 2024' },
  { id: 'WO-007', machine: 'MCH-003', type: 'Preventive', priority: 'Low', status: 'Scheduled', assigned: 'David R.', due: 'May 26, 2024' },
];

export default function Maintenance() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ marginBottom: '5px' }}>Maintenance</h2>
          <p style={{ fontSize: '0.9rem' }}>Manage maintenance schedules and work orders</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-cols-4" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Open Work Orders</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>32</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--primary-neon)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>In Progress</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary-neon)' }}>12</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-good)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Completed</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-good)' }}>108</div>
        </div>
        <div className="card" style={{ borderBottom: '3px solid var(--status-warning)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Scheduled</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-warning)' }}>7</div>
        </div>
        <div className="card">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '10px' }}>Total</p>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>24</div>
        </div>
      </div>

      {/* Table Container */}
      <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        
        {/* Toolbar */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input type="text" className="input-field" placeholder="Search work orders..." style={{ paddingLeft: '35px', width: '220px' }} />
            </div>
            <select className="input-field" style={{ width: '130px' }}><option>All Types</option></select>
            <select className="input-field" style={{ width: '130px' }}><option>All Priorities</option></select>
            <select className="input-field" style={{ width: '130px' }}><option>This Month</option></select>
          </div>
          
          <button className="btn btn-primary">
            <Plus size={16} /> New Work Order
          </button>
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.02)', color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Work Order ID</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Machine</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Type</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Priority</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Status</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Assigned To</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)' }}>Due Date</th>
                <th style={{ padding: '15px', fontWeight: 600, borderBottom: '1px solid var(--border-color)', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {maintenanceData.map((m) => (
                <tr key={m.id} style={{ borderBottom: '1px solid var(--border-color)' }} className="table-row-hover">
                  <td style={{ padding: '15px', fontWeight: 500, color: 'var(--text-muted)' }}>{m.id}</td>
                  <td style={{ padding: '15px', color: 'var(--primary-neon)', fontWeight: 500 }}>{m.machine}</td>
                  <td style={{ padding: '15px' }}>{m.type}</td>
                  <td style={{ padding: '15px' }}>
                    <span style={{ color: m.priority === 'High' ? 'var(--status-critical)' : m.priority === 'Medium' ? 'var(--status-warning)' : 'var(--status-good)', fontWeight: 600 }}>
                      {m.priority}
                    </span>
                  </td>
                  <td style={{ padding: '15px' }}>
                    <span style={{ color: m.status === 'In Progress' ? 'var(--primary-neon)' : m.status === 'Open' ? 'var(--status-critical)' : m.status === 'Scheduled' ? 'var(--status-warning)' : 'var(--status-good)' }}>
                      {m.status}
                    </span>
                  </td>
                  <td style={{ padding: '15px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'var(--bg-hover)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem' }}>
                        {m.assigned.charAt(0)}
                      </div>
                      {m.assigned}
                    </div>
                  </td>
                  <td style={{ padding: '15px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{m.due}</td>
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
