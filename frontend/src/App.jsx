import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import Machines from './pages/Machines';
import Analytics from './pages/Analytics';
import Predictions from './pages/Predictions';
import Energy from './pages/Energy';
import Alerts from './pages/Alerts';
import Maintenance from './pages/Maintenance';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

// Placeholder components for other pages
const PlaceholderPage = ({ title }) => (
  <div className="animate-fade-in card" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
    <h1 style={{ color: 'var(--primary-neon)', marginBottom: '1rem' }}>{title}</h1>
    <p>This module is currently under construction for the new frontend.</p>
  </div>
);



function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="machines" element={<Machines />} />
          <Route path="predictions" element={<Predictions />} />
          <Route path="maintenance" element={<Maintenance />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="energy" element={<Energy />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
