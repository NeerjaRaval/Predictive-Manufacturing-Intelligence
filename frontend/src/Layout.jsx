import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Server, Lightbulb, Wrench, 
  BarChart3, Zap, Bell, FileText, Settings,
  Search, User, Menu
} from 'lucide-react';

export default function Layout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Machines', path: '/machines', icon: <Server size={20} /> },
    { name: 'Predictions', path: '/predictions', icon: <Lightbulb size={20} /> },
    { name: 'Maintenance', path: '/maintenance', icon: <Wrench size={20} /> },
    { name: 'Analytics', path: '/analytics', icon: <BarChart3 size={20} /> },
    { name: 'Energy', path: '/energy', icon: <Zap size={20} /> },
    { name: 'Alerts', path: '/alerts', icon: <Bell size={20} /> },
    { name: 'Reports', path: '/reports', icon: <FileText size={20} /> },
    { name: 'Settings', path: '/settings', icon: <Settings size={20} /> },
  ];

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className={`sidebar ${isSidebarOpen ? '' : 'collapsed'}`}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '2rem', padding: '0 10px' }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'var(--primary-neon)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 'bold' }}>
            PMI
          </div>
          {isSidebarOpen && <span style={{ fontWeight: 600, fontSize: '1.1rem', whiteSpace: 'nowrap', overflow: 'hidden' }}>Intelligence</span>}
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <NavLink 
                to={item.path} 
                key={item.name}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  color: isActive ? 'var(--primary-neon)' : 'var(--text-muted)',
                  backgroundColor: isActive ? 'rgba(88, 166, 255, 0.1)' : 'transparent',
                  transition: 'all 0.2s'
                }}
              >
                {item.icon}
                {isSidebarOpen && <span style={{ fontWeight: isActive ? 600 : 400 }}>{item.name}</span>}
              </NavLink>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Topbar */}
        <header className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <button 
              className="btn-secondary" 
              style={{ border: 'none', padding: '5px' }}
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <Menu size={24} />
            </button>
            <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>
              {navItems.find(n => n.path === location.pathname)?.name || 'Dashboard'}
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
              <input 
                type="text" 
                className="input-field" 
                placeholder="Search anything..." 
                style={{ paddingLeft: '35px', width: '250px', borderRadius: '20px' }}
              />
            </div>
            
            <button className="btn btn-primary" style={{ borderRadius: '20px' }}>
              <Lightbulb size={16} /> Ask AI Copilot
            </button>
            
            <button className="btn-secondary" style={{ border: 'none', position: 'relative' }}>
              <Bell size={20} />
              <span style={{ position: 'absolute', top: -2, right: -2, width: 8, height: 8, background: 'var(--status-critical)', borderRadius: '50%' }}></span>
            </button>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <User size={20} />
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>Admin</div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
