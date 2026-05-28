import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie
} from 'recharts';
import { AlertCircle, Activity, TrendingUp, CheckCircle, ChevronRight, Server, Lightbulb, Send, User, Bot, Loader } from 'lucide-react';

// ─────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────
function useAPI(url, deps = []) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(url)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
    // eslint-disable-next-line
  }, deps);

  return { data, loading, error };
}

const TOOLTIP_STYLE = {
  backgroundColor: 'var(--bg-panel)',
  borderColor: 'var(--border-color)',
  borderRadius: '8px',
  color: 'var(--text-main)',
};

// Shimmer placeholder
function Shimmer({ height = 40, width = '100%', radius = 8 }) {
  return (
    <div style={{
      height, width, borderRadius: radius,
      background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 1.4s infinite',
    }} />
  );
}

// Simple markdown renderer (bold, lists, headings)
function MarkdownText({ text }) {
  if (!text) return null;
  const lines = text.split('\n');
  return (
    <div style={{ lineHeight: 1.7 }}>
      {lines.map((line, i) => {
        if (line.startsWith('### ')) return <div key={i} style={{ fontWeight: 700, fontSize: '0.95rem', margin: '8px 0 4px', color: 'var(--primary-neon)' }}>{line.slice(4)}</div>;
        if (line.startsWith('## '))  return <div key={i} style={{ fontWeight: 700, fontSize: '1rem',   margin: '8px 0 4px', color: 'var(--text-main)' }}>{line.slice(3)}</div>;
        if (line.startsWith('# '))   return <div key={i} style={{ fontWeight: 700, fontSize: '1.1rem', margin: '8px 0 4px', color: 'var(--text-main)' }}>{line.slice(2)}</div>;
        if (line.startsWith('- **') || line.startsWith('* **') || line.startsWith('- ') || line.startsWith('* ')) {
          const content = line.replace(/^[-*]\s/, '');
          const parts = content.split(/(\*\*.*?\*\*)/g);
          return (
            <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 2 }}>
              <span style={{ color: 'var(--primary-neon)', marginTop: 2 }}>•</span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {parts.map((p, j) => p.startsWith('**') ? <strong key={j} style={{ color: 'var(--text-main)' }}>{p.slice(2, -2)}</strong> : p)}
              </span>
            </div>
          );
        }
        if (line.startsWith('|') && line.includes('|')) {
          if (line.includes('---')) return null;
          const cells = line.split('|').filter(c => c.trim() !== '');
          const isHeader = lines[i - 1]?.includes('---') === false && lines[i + 1]?.includes('---');
          return (
            <div key={i} style={{ display: 'flex', gap: 8, fontSize: '0.8rem', borderBottom: '1px solid var(--border-color)', padding: '4px 0' }}>
              {cells.map((cell, j) => (
                <div key={j} style={{ flex: 1, color: isHeader ? 'var(--text-muted)' : 'var(--text-main)', fontWeight: isHeader ? 600 : 400, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {cell.trim().replace(/\*\*/g, '')}
                </div>
              ))}
            </div>
          );
        }
        if (line.trim() === '') return <div key={i} style={{ height: 6 }} />;
        const parts = line.split(/(\*\*.*?\*\*)/g);
        return (
          <div key={i} style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 2 }}>
            {parts.map((p, j) => p.startsWith('**') ? <strong key={j} style={{ color: 'var(--text-main)' }}>{p.slice(2, -2)}</strong> : p)}
          </div>
        );
      })}
    </div>
  );
}

// Inline mini chart renderer for AI responses
function InlineChart({ config }) {
  if (!config || !config.data || config.data.length === 0) return null;
  const { type, data, xKey, bars, areas, yKey } = config;

  return (
    <div style={{ height: 160, marginTop: 12, borderRadius: 8, overflow: 'hidden' }}>
      <ResponsiveContainer width="100%" height="100%">
        {type === 'bar' ? (
          <BarChart data={data} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
            <XAxis dataKey={xKey} stroke="var(--text-muted)" fontSize={9} tickLine={false} axisLine={false} />
            <YAxis stroke="var(--text-muted)" fontSize={9} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            {(bars || [{ dataKey: yKey || 'value', fill: 'var(--primary-neon)' }]).map((b, i) => (
              <Bar key={i} dataKey={b.dataKey} fill={b.fill} radius={[3, 3, 0, 0]} barSize={14} />
            ))}
          </BarChart>
        ) : type === 'area' ? (
          <AreaChart data={data} margin={{ top: 4, right: 4, left: -28, bottom: 0 }}>
            <defs>
              {(areas || []).map((a, i) => (
                <linearGradient key={i} id={`grad-${i}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={a.stroke} stopOpacity={0.5} />
                  <stop offset="95%" stopColor={a.stroke} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
            <XAxis dataKey={xKey} stroke="var(--text-muted)" fontSize={9} tickLine={false} axisLine={false} />
            <YAxis stroke="var(--text-muted)" fontSize={9} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            {(areas || [{ dataKey: 'value', stroke: 'var(--primary-neon)', fill: 'rgba(88,166,255,0.1)' }]).map((a, i) => (
              <Area key={i} type="monotone" dataKey={a.dataKey} stroke={a.stroke} strokeWidth={2} fill={`url(#grad-${i})`} />
            ))}
          </AreaChart>
        ) : type === 'pie' ? (
          <PieChart>
            <Pie data={data} dataKey={yKey || 'value'} nameKey={xKey} cx="50%" cy="50%" innerRadius={40} outerRadius={65} paddingAngle={3}>
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.color || 'var(--primary-neon)'} />
              ))}
            </Pie>
            <Tooltip contentStyle={TOOLTIP_STYLE} />
          </PieChart>
        ) : null}
      </ResponsiveContainer>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// AI Copilot Chat Panel
// ─────────────────────────────────────────────────────────────
const STARTER_PROMPTS = [
  'Find temperature anomalies',
  'Show Machine 12 telemetry',
  'Correlations in the data',
  'Which machine has highest power?',
];

function AICopilotPanel() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: "Hello! I'm your **AI Copilot** — running 100% locally on your CSV data.\n\nAsk me anything about your manufacturing operations, machine health, or sensor correlations!",
      chart: null,
    }
  ]);
  const [input, setInput]   = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const sendQuery = useCallback(async (query) => {
    if (!query.trim() || loading) return;
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/copilot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'ai',
        text: data.text || 'I could not analyze that query.',
        chart: data.chart || null,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'ai',
        text: '⚠️ Could not reach the AI backend. Make sure the FastAPI server is running.',
        chart: null,
      }]);
    } finally {
      setLoading(false);
    }
  }, [loading]);

  const handleKey = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQuery(input); } };

  return (
    <div className="card" style={{ width: 320, display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
        <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.95rem' }}>
          <Lightbulb size={16} color="var(--primary-neon)" />
          AI Copilot
          <span className="tag tag-good" style={{ fontSize: '0.65rem' }}>LOCAL</span>
        </h3>
      </div>

      {/* Starter chips */}
      {messages.length === 1 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: '0.75rem' }}>
          {STARTER_PROMPTS.map(p => (
            <button key={p} onClick={() => sendQuery(p)}
              style={{ fontSize: '0.72rem', padding: '4px 10px', borderRadius: 20, background: 'rgba(88,166,255,0.1)', border: '1px solid rgba(88,166,255,0.25)', color: 'var(--primary-neon)', cursor: 'pointer', transition: 'all 0.2s' }}>
              {p}
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 12, minHeight: 0, maxHeight: 480 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {msg.role === 'ai' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                <div style={{ width: 22, height: 22, borderRadius: '50%', background: 'rgba(88,166,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Bot size={12} color="var(--primary-neon)" />
                </div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>AI Copilot</span>
              </div>
            )}
            <div style={{
              maxWidth: '90%',
              padding: '10px 12px',
              borderRadius: msg.role === 'user' ? '12px 12px 0 12px' : '0 12px 12px 12px',
              background: msg.role === 'user' ? 'var(--primary-neon)' : 'var(--bg-hover)',
              color: msg.role === 'user' ? '#000' : 'var(--text-main)',
              fontSize: '0.85rem',
              fontWeight: msg.role === 'user' ? 500 : 400,
            }}>
              {msg.role === 'user' ? msg.text : <MarkdownText text={msg.text} />}
              {msg.chart && <InlineChart config={msg.chart} />}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 12px', background: 'var(--bg-hover)', borderRadius: '0 12px 12px 12px', width: 'fit-content' }}>
            <Loader size={14} color="var(--primary-neon)" style={{ animation: 'spin 1s linear infinite' }} />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Analyzing CSV data...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{ position: 'relative', flexShrink: 0 }}>
        <input
          type="text"
          className="input-field"
          placeholder="Ask anything about your data..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          style={{ paddingRight: 44, fontSize: '0.85rem' }}
        />
        <button
          onClick={() => sendQuery(input)}
          disabled={loading || !input.trim()}
          style={{
            position: 'absolute', right: 4, top: 4, bottom: 4,
            padding: '0 10px', borderRadius: 6,
            background: input.trim() && !loading ? 'var(--primary-neon)' : 'var(--bg-hover)',
            border: 'none', cursor: input.trim() ? 'pointer' : 'default',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transition: 'all 0.2s',
          }}>
          <Send size={14} color={input.trim() && !loading ? '#000' : 'var(--text-muted)'} />
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Main Dashboard Component
// ─────────────────────────────────────────────────────────────
export default function Dashboard() {
  const { data: kpis, loading: kpiLoading }     = useAPI('/api/kpis');
  const { data: charts, loading: chartLoading } = useAPI('/api/charts/production?days=7');
  const { data: machines }                       = useAPI('/api/machines?limit=3');
  const { data: maintenance }                    = useAPI('/api/maintenance');

  const prodData     = charts?.production_trend || [];
  const failureData  = charts?.failure_risk     || [];
  const maintTasks   = maintenance?.tasks?.slice(0, 3) || [];
  const machineList  = machines?.machines?.slice(0, 3) || [];

  const healthBg = (status) =>
    status === 'Healthy' ? 'var(--status-good)' :
    status === 'Warning' ? 'var(--status-warning)' : 'var(--status-critical)';

  const priorityClass = (p) =>
    p === 'Critical' ? 'critical' : p === 'High' ? 'warning' : 'good';

  return (
    <>
      <style>{`
        @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes pulse   { 0%,100%{opacity:1} 50%{opacity:0.5} }
      `}</style>

      <div className="animate-fade-in" style={{ display: 'flex', gap: '1.5rem' }}>
        {/* Left Column */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.5rem', minWidth: 0 }}>

          {/* ── KPI Row ── */}
          <div className="grid-cols-4">
            {/* OEE */}
            <div className="card">
              <h4 style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>Overall Equipment Effectiveness</h4>
              {kpiLoading ? <Shimmer height={40} /> : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 10 }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-cyan)', lineHeight: 1 }}>
                    {kpis?.oee ?? '--'}<span style={{ fontSize: '1.1rem' }}>%</span>
                  </div>
                  {kpis?.oee_delta !== undefined && (
                    <span className={`tag tag-${kpis.oee_delta >= 0 ? 'good' : 'critical'}`}>
                      {kpis.oee_delta >= 0 ? '+' : ''}{kpis.oee_delta}% vs last 7d
                    </span>
                  )}
                </div>
              )}
              {!kpiLoading && kpis && (
                <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
                  {['high','medium','low'].map(k => (
                    <div key={k} style={{ flex: kpis.efficiency_distribution[k], height: 4, borderRadius: 2,
                      background: k === 'high' ? 'var(--status-good)' : k === 'medium' ? 'var(--status-warning)' : 'var(--status-critical)'
                    }} title={`${k}: ${kpis.efficiency_distribution[k]}%`} />
                  ))}
                </div>
              )}
            </div>

            {/* Active Alerts */}
            <div className="card">
              <h4 style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>Active Alerts</h4>
              {kpiLoading ? <Shimmer height={40} /> : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 10 }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-critical)', lineHeight: 1 }}>
                    {kpis?.active_alerts ?? '--'}
                  </div>
                  <span className="tag tag-critical" style={{ background: 'transparent', padding: 0 }}>Threshold Violations</span>
                </div>
              )}
              <div style={{ color: 'var(--primary-neon)', fontSize: '0.8rem', marginTop: 10, cursor: 'pointer' }}>
                View all alerts <ChevronRight size={12} style={{ display: 'inline' }} />
              </div>
            </div>

            {/* Predicted Failures */}
            <div className="card">
              <h4 style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>Predicted Failures</h4>
              {kpiLoading ? <Shimmer height={40} /> : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 10 }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-warning)', lineHeight: 1 }}>
                    {kpis?.predicted_failures ?? '--'}
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>maintenance needed</span>
                </div>
              )}
              <div style={{ color: 'var(--primary-neon)', fontSize: '0.8rem', marginTop: 10, cursor: 'pointer' }}>
                View predictions <ChevronRight size={12} style={{ display: 'inline' }} />
              </div>
            </div>

            {/* AI Health Score */}
            <div className="card">
              <h4 style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>AI Health Score</h4>
              {kpiLoading ? <Shimmer height={40} /> : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 10 }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--status-good)', lineHeight: 1 }}>
                    {kpis?.ai_health_score ?? '--'}
                    <span style={{ fontSize: '1.1rem', color: 'var(--text-muted)' }}>/100</span>
                  </div>
                  <span className={`tag tag-${(kpis?.ai_health_score ?? 0) >= 75 ? 'good' : (kpis?.ai_health_score ?? 0) >= 50 ? 'warning' : 'critical'}`}>
                    {(kpis?.ai_health_score ?? 0) >= 75 ? 'Excellent' : (kpis?.ai_health_score ?? 0) >= 50 ? 'Fair' : 'Poor'}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* ── Charts Row ── */}
          <div className="grid-cols-3">
            {/* Production Trend */}
            <div className="card" style={{ gridColumn: 'span 2' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3>Production Trend</h3>
                <div style={{ display: 'flex', gap: 12, fontSize: '0.8rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ width: 10, height: 3, borderRadius: 2, background: 'var(--primary-neon)', display: 'inline-block' }} /> Actual
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <span style={{ width: 10, height: 3, borderRadius: 2, background: 'var(--border-color)', display: 'inline-block' }} /> Target
                  </span>
                </div>
              </div>
              {chartLoading ? <Shimmer height={240} radius={12} /> : (
                <div style={{ height: 240 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={prodData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%"  stopColor="var(--primary-neon)" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="var(--primary-neon)" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Area type="monotone" dataKey="target" stroke="var(--border-color)" strokeWidth={2} strokeDasharray="5 5" fill="none" />
                      <Area type="monotone" dataKey="actual" stroke="var(--primary-neon)" strokeWidth={3} fillOpacity={1} fill="url(#colorActual)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Failure Risk Bar */}
            <div className="card">
              <h3>Failure Risk</h3>
              <p style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>Top 5 At-Risk Machines</p>
              {chartLoading ? <Shimmer height={240} radius={12} /> : (
                <div style={{ height: 240 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={failureData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                      <Tooltip cursor={{ fill: 'var(--bg-hover)' }} contentStyle={TOOLTIP_STYLE} />
                      <Bar dataKey="risk" radius={[4, 4, 0, 0]}>
                        {failureData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>

          {/* ── Bottom Row ── */}
          <div className="grid-cols-3">
            {/* Machine Health */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h3>Machine Health</h3>
                <div style={{ fontSize: '0.75rem', color: 'var(--primary-neon)', cursor: 'pointer' }}>View All</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {kpiLoading ? [1,2,3].map(i => <Shimmer key={i} height={50} />) :
                  machineList.length > 0 ? machineList.map(m => (
                    <div key={m.machine_id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px', background: 'var(--bg-hover)', borderRadius: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{ width: 36, height: 36, borderRadius: 8, background: healthBg(m.status), opacity: 0.85, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 700, fontSize: '0.75rem' }}>
                          {m.id}
                        </div>
                        <div>
                          <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{m.id}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{m.operation_mode} · {m.dominant_efficiency} Eff.</div>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ color: healthBg(m.status), fontWeight: 700 }}>{m.health}%</div>
                        <span className={`tag tag-${m.status === 'Healthy' ? 'good' : m.status === 'Warning' ? 'warning' : 'critical'}`} style={{ fontSize: '0.65rem' }}>
                          {m.status}
                        </span>
                      </div>
                    </div>
                  )) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: 20 }}>No machine data available</div>
                  )
                }
              </div>
            </div>

            {/* Maintenance Queue */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h3>Maintenance Queue</h3>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{maintenance?.total ?? '--'} tasks</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {kpiLoading ? [1,2,3].map(i => <Shimmer key={i} height={52} />) :
                  maintTasks.length > 0 ? maintTasks.map(t => (
                    <div key={t.id} style={{ borderLeft: `3px solid var(--status-${priorityClass(t.priority)})`, paddingLeft: 12 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 500, fontSize: '0.9rem' }}>{t.task}</span>
                        <span className={`tag tag-${priorityClass(t.priority)}`}>{t.priority}</span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                        {t.machine} · Due in {t.due_days} day{t.due_days !== 1 ? 's' : ''}
                      </div>
                    </div>
                  )) : (
                    <div style={{ color: 'var(--status-good)', fontSize: '0.85rem', textAlign: 'center', padding: 20 }}>✅ All machines nominal</div>
                  )
                }
              </div>
            </div>

            {/* Efficiency Distribution */}
            <div className="card">
              <h3 style={{ marginBottom: '0.75rem' }}>Efficiency Distribution</h3>
              <p style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>Across all machines & records</p>
              {kpiLoading ? <Shimmer height={160} /> : kpis && (
                <>
                  <div style={{ height: 140 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'High',   value: kpis.efficiency_distribution.high,   color: 'var(--status-good)' },
                            { name: 'Medium', value: kpis.efficiency_distribution.medium, color: 'var(--status-warning)' },
                            { name: 'Low',    value: kpis.efficiency_distribution.low,    color: 'var(--status-critical)' },
                          ]}
                          dataKey="value"
                          cx="50%" cy="50%"
                          innerRadius={40} outerRadius={62}
                          paddingAngle={4}
                        >
                          {['var(--status-good)', 'var(--status-warning)', 'var(--status-critical)'].map((c, i) => (
                            <Cell key={i} fill={c} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => `${v}%`} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: 8 }}>
                    {[['High', 'good'], ['Medium', 'warning'], ['Low', 'critical']].map(([label, cls]) => (
                      <div key={label} style={{ textAlign: 'center' }}>
                        <div style={{ fontWeight: 700, color: `var(--status-${cls})`, fontSize: '1.1rem' }}>
                          {kpis.efficiency_distribution[label.toLowerCase()]}%
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: AI Copilot */}
        <AICopilotPanel />
      </div>
    </>
  );
}
