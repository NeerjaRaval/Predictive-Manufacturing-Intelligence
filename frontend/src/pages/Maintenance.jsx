import React, { useState, useEffect } from 'react';
import { RefreshCw, Wrench, CheckCircle, Clock } from 'lucide-react';

function Shimmer({ height = 40, radius = 8 }) {
  return <div style={{ height, borderRadius: radius, background: 'linear-gradient(90deg, var(--bg-hover) 25%, var(--border-color) 50%, var(--bg-hover) 75%)', backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />;
}

const PRIORITY_MAP = {
  Critical: { color: 'var(--status-critical)', tagClass: 'critical', urgency: '🚨 Immediate' },
  High:     { color: 'var(--status-warning)',  tagClass: 'warning',  urgency: '⚠️ Urgent'    },
  Medium:   { color: '#bc8cff',               tagClass: 'neutral',  urgency: '📌 Scheduled'  },
  Low:      { color: 'var(--status-good)',    tagClass: 'good',     urgency: '✅ Routine'    },
};

export default function Maintenance() {
  const [data, setData]         = useState(null);
  const [loading, setLoading]   = useState(true);
  const [completed, setDone]    = useState(new Set());
  const [inProgress, setInProg] = useState(new Set());
  const [priorityFilter, setPri]= useState('');
  const [sort, setSort]         = useState('due_days');

  const load = () => {
    setLoading(true);
    fetch('/api/maintenance')
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const tasks = (data?.tasks || [])
    .filter(t => !completed.has(t.id))
    .filter(t => !priorityFilter || t.priority === priorityFilter)
    .sort((a, b) => {
      if (sort === 'due_days') return a.due_days - b.due_days;
      const po = { Critical: 0, High: 1, Medium: 2, Low: 3 };
      return po[a.priority] - po[b.priority];
    });

  const toggleInProgress = (id) => {
    setInProg(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  return (
    <>
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
      <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h2 style={{ marginBottom: 5 }}>Maintenance Queue</h2>
            <p style={{ fontSize: '0.9rem' }}>AI-predicted maintenance tasks ranked by urgency</p>
          </div>
          <button className="btn btn-secondary" onClick={load}><RefreshCw size={14} /> Refresh</button>
        </div>

        {/* KPI Cards */}
        <div className="grid-cols-4">
          {[
            ['Total Tasks', data?.total, 'var(--text-main)'],
            ['Critical',   data?.critical_count, 'var(--status-critical)'],
            ['High',       data?.high_count,     'var(--status-warning)'],
            ['Completed',  completed.size,        'var(--status-good)'],
          ].map(([label, val, color]) => (
            <div key={label} className="card">
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 10 }}>{label}</p>
              {loading ? <Shimmer height={36} /> : (
                <div style={{ fontSize: '2.2rem', fontWeight: 'bold', color }}>{val ?? 0}</div>
              )}
            </div>
          ))}
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <select className="input-field" style={{ width: 160, fontSize: '0.85rem' }} value={priorityFilter} onChange={e => setPri(e.target.value)}>
            <option value="">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <select className="input-field" style={{ width: 180, fontSize: '0.85rem' }} value={sort} onChange={e => setSort(e.target.value)}>
            <option value="due_days">Sort by Due Date</option>
            <option value="priority">Sort by Priority</option>
          </select>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: 8 }}>{tasks.length} pending tasks</span>
        </div>

        {/* Tasks */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {loading
            ? Array.from({ length: 6 }).map((_, i) => <Shimmer key={i} height={80} />)
            : tasks.length === 0
              ? (
                <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                  <CheckCircle size={40} color="var(--status-good)" style={{ marginBottom: 12 }} />
                  <div style={{ fontWeight: 600, color: 'var(--status-good)' }}>All maintenance tasks completed!</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 6 }}>No pending tasks match your filter.</div>
                </div>
              )
              : tasks.map(task => {
                  const meta = PRIORITY_MAP[task.priority] || PRIORITY_MAP.Low;
                  const isInProg = inProgress.has(task.id);
                  return (
                    <div key={task.id} className="card" style={{
                      borderLeft: `4px solid ${meta.color}`,
                      display: 'flex', alignItems: 'center', gap: '1.5rem',
                      transition: 'all 0.2s',
                      opacity: isInProg ? 0.85 : 1,
                    }}>
                      {/* Left: Task info */}
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                          <span style={{ color: 'var(--primary-neon)', fontWeight: 700, fontSize: '1rem' }}>{task.machine}</span>
                          <span className={`tag tag-${meta.tagClass}`}>{task.priority}</span>
                          {isInProg && <span className="tag tag-neutral">In Progress</span>}
                        </div>
                        <div style={{ fontWeight: 500, marginBottom: 4 }}>{task.task}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {meta.urgency} &nbsp;·&nbsp; Score: <strong style={{ color: 'var(--text-main)' }}>{task.score}</strong>
                          &nbsp;·&nbsp; Task ID: {task.id}
                        </div>
                      </div>

                      {/* Due Days */}
                      <div style={{ textAlign: 'center', minWidth: 80 }}>
                        <Clock size={16} color={meta.color} style={{ marginBottom: 4 }} />
                        <div style={{ fontSize: '1.6rem', fontWeight: 700, color: meta.color, lineHeight: 1 }}>
                          {task.due_days}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {task.due_days === 1 ? 'day left' : 'days left'}
                        </div>
                      </div>

                      {/* Actions */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <button
                          onClick={() => toggleInProgress(task.id)}
                          style={{ padding: '6px 14px', borderRadius: 6, fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer', border: '1px solid var(--border-color)', background: isInProg ? 'rgba(88,166,255,0.15)' : 'var(--bg-hover)', color: isInProg ? 'var(--primary-neon)' : 'var(--text-muted)', transition: 'all 0.2s', whiteSpace: 'nowrap' }}>
                          {isInProg ? '⏸ Pause' : '▶ Start'}
                        </button>
                        <button
                          onClick={() => setDone(prev => new Set([...prev, task.id]))}
                          style={{ padding: '6px 14px', borderRadius: 6, fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer', border: '1px solid var(--status-good)', background: 'rgba(63,185,80,0.1)', color: 'var(--status-good)', transition: 'all 0.2s', whiteSpace: 'nowrap' }}>
                          ✓ Complete
                        </button>
                      </div>
                    </div>
                  );
              })
          }
        </div>
      </div>
    </>
  );
}
