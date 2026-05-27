import React from 'react';
import { Settings as SettingsIcon, Users, Server, Activity, Bell, Wrench, Link as LinkIcon, Sliders, User, Lock, Key, List } from 'lucide-react';

export default function Settings() {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ marginBottom: '5px' }}>Settings</h2>
          <p style={{ fontSize: '0.9rem' }}>Configure system settings and preferences</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1.5rem' }}>
        
        {/* Sidebar Navigation */}
        <div className="card" style={{ width: '250px', padding: '1rem' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '10px', padding: '0 10px' }}>
            Profile & Preferences
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <button className="btn btn-secondary" style={{ justifyContent: 'flex-start', border: 'none', background: 'rgba(88, 166, 255, 0.1)', color: 'var(--primary-neon)' }}>
              <User size={18} /> Profile Information
            </button>
            <button className="btn btn-secondary" style={{ justifyContent: 'flex-start', border: 'none', color: 'var(--text-main)' }}>
              <Sliders size={18} /> Preferences
            </button>
            <button className="btn btn-secondary" style={{ justifyContent: 'flex-start', border: 'none', color: 'var(--text-main)' }}>
              <Lock size={18} /> Security
            </button>
            <button className="btn btn-secondary" style={{ justifyContent: 'flex-start', border: 'none', color: 'var(--text-main)' }}>
              <Key size={18} /> API Keys
            </button>
            <button className="btn btn-secondary" style={{ justifyContent: 'flex-start', border: 'none', color: 'var(--text-main)' }}>
              <List size={18} /> Activity Log
            </button>
          </div>
        </div>

        {/* Main Settings Area */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Profile Form */}
          <div className="card">
            <h3 style={{ marginBottom: '1.5rem' }}>Profile Information</h3>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '2rem' }}>
              <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'var(--bg-hover)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '2px solid var(--border-color)' }}>
                <User size={40} color="var(--text-muted)" />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>Admin User</div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>admin@pmi.com</div>
              </div>
            </div>

            <div className="grid-cols-2" style={{ marginBottom: '1.5rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Full Name *</label>
                <input type="text" className="input-field" defaultValue="Admin User" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Role</label>
                <input type="text" className="input-field" defaultValue="Administrator" disabled style={{ opacity: 0.7 }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Email *</label>
                <input type="email" className="input-field" defaultValue="admin@pmi.com" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Phone</label>
                <input type="text" className="input-field" defaultValue="+91 98765 43210" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Department</label>
                <input type="text" className="input-field" defaultValue="Information Technology" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Location</label>
                <input type="text" className="input-field" defaultValue="Chennai, India" />
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-primary">Save Changes</button>
            </div>
          </div>

          {/* System Settings Grid */}
          <h3 style={{ marginTop: '1rem' }}>System Administration</h3>
          <div className="grid-cols-3">
            {[
              { icon: <SettingsIcon size={24} />, title: 'General Settings', desc: 'System configuration and preferences' },
              { icon: <Users size={24} />, title: 'User Management', desc: 'Manage users and roles' },
              { icon: <Server size={24} />, title: 'Machine Management', desc: 'Add, edit and configure machines' },
              { icon: <Activity size={24} />, title: 'Sensors & Data', desc: 'Configure sensors and data collection' },
              { icon: <Bell size={24} />, title: 'Alert Settings', desc: 'Configure alert rules and notifications' },
              { icon: <Wrench size={24} />, title: 'Maintenance Settings', desc: 'Maintenance schedules and rules' },
              { icon: <LinkIcon size={24} />, title: 'Integration', desc: 'Third-party integrations' },
              { icon: <Sliders size={24} />, title: 'System Configuration', desc: 'Advanced system settings' },
            ].map((s, i) => (
              <div key={i} className="card" style={{ display: 'flex', alignItems: 'flex-start', gap: '15px', cursor: 'pointer' }}>
                <div style={{ color: 'var(--primary-neon)' }}>{s.icon}</div>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '5px' }}>{s.title}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>

        </div>
      </div>
    </div>
  );
}
