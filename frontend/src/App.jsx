import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertCircle,
  ArrowRight,
  Check,
  ChevronDown,
  CircleDot,
  ClipboardList,
  FlaskConical,
  LayoutDashboard,
  MapPin,
  Plus,
  RefreshCw,
  Search,
  Wrench,
  X,
} from 'lucide-react'

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`)
  }
  return response.status === 204 ? null : response.json()
}

const statusRank = { offline: 0, attention: 1, operational: 2 }
const statusLabel = { offline: 'Out of service', attention: 'Needs attention', operational: 'Operational' }
const incidentLabel = { open: 'Open', in_progress: 'In progress', resolved: 'Resolved' }

function formattedDate(value) {
  return new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short' }).format(new Date(value))
}

function Sidebar({ active, onNavigate, summary }) {
  const links = [
    ['overview', LayoutDashboard, 'Overview'],
    ['equipment', FlaskConical, 'Equipment'],
    ['incidents', ClipboardList, 'Incidents'],
  ]
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark"><Activity size={23} strokeWidth={2.4} /></span>
        <span className="brand-name">Lab<span>Pulse</span><small>OPERATIONS</small></span>
      </div>
      <div className="sidebar-label">WORKSPACE</div>
      <nav className="side-nav" aria-label="Main navigation">
        {links.map(([key, Icon, label]) => (
          <button key={key} type="button" className={`nav-item ${active === key ? 'active' : ''}`} onClick={() => onNavigate(key)} aria-current={active === key ? 'page' : undefined}>
            <Icon size={18} /> <span>{label}</span>
            {key === 'incidents' && summary?.open_incidents > 0 && <em>{summary.open_incidents}</em>}
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="footer-icon"><Wrench size={18} /></div>
        <div><strong>Built for the bench</strong><span>Campus lab operations</span></div>
      </div>
    </aside>
  )
}

function StatusPill({ status, kind = 'equipment' }) {
  const label = kind === 'equipment' ? statusLabel[status] : incidentLabel[status]
  return <span className={`status-pill ${status}`}><span className="status-dot" />{label || status}</span>
}

function EquipmentTile({ item, incidentCount, onClick }) {
  return (
    <button type="button" className={`equipment-tile ${item.status}`} onClick={onClick} aria-label={`View incidents for ${item.name}, ${statusLabel[item.status]}`}>
      <span className="tile-top"><span className="asset-code">{item.code}</span><ArrowRight size={16} /></span>
      <span className="tile-name">{item.name}</span>
      <span className="tile-room"><MapPin size={13} />{item.room}</span>
      <span className="tile-bottom"><StatusPill status={item.status} /><span>{incidentCount} active {incidentCount === 1 ? 'report' : 'reports'}</span></span>
    </button>
  )
}

function IncidentRows({ rows, equipmentById, onStatus }) {
  if (rows.length === 0) {
    return <div className="empty-state"><Check size={24} /><strong>Nothing in this view</strong><span>Try another filter or report a new incident.</span></div>
  }
  return (
    <div className="table-scroll">
      <table className="incident-table">
        <thead><tr><th>Incident</th><th>Equipment / room</th><th>Priority</th><th>Status</th><th>Reported</th><th><span className="sr-only">Action</span></th></tr></thead>
        <tbody>
          {rows.map((item) => {
            const equipment = equipmentById[item.equipment_id]
            return <tr key={item.id}>
              <td><span className="incident-title">{item.title}</span><span className="incident-id">INC-{String(item.id).padStart(3, '0')} · {item.reported_by}</span></td>
              <td><span className="cell-strong">{equipment?.name || 'Unknown equipment'}</span><span className="cell-sub">{equipment?.room || 'Room unavailable'}</span></td>
              <td><span className={`severity ${item.severity}`}>{item.severity}</span></td>
              <td><StatusPill status={item.status} kind="incident" /></td>
              <td className="date-cell">{formattedDate(item.created_at)}</td>
              <td>{item.status === 'resolved' ? <span className="resolved-check"><Check size={17} /></span> : <button className="row-action" type="button" onClick={() => onStatus(item.id, item.status === 'open' ? 'in_progress' : 'resolved')} title={item.status === 'open' ? 'Start work' : 'Resolve incident'}>{item.status === 'open' ? 'Start' : 'Resolve'}<ArrowRight size={14} /></button>}</td>
            </tr>
          })}
        </tbody>
      </table>
    </div>
  )
}

function Modal({ kind, equipment, onClose, onSubmit, saving }) {
  useEffect(() => {
    const onKey = (event) => { if (event.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const incident = kind === 'incident'
  function handleSubmit(event) {
    event.preventDefault()
    const data = Object.fromEntries(new FormData(event.currentTarget).entries())
    if (incident) data.equipment_id = Number(data.equipment_id)
    onSubmit(data)
  }

  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
    <section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal-top"><div><span className="eyebrow">LABPULSE / NEW RECORD</span><h2 id="modal-title">{incident ? 'Report an incident' : 'Add equipment'}</h2></div><button type="button" className="icon-button" onClick={onClose} aria-label="Close dialog"><X size={20} /></button></div>
      <p className="modal-intro">{incident ? 'Record what happened so the next person at this bench has the context they need.' : 'Give the instrument a clear code and location so reports can point to the right bench.'}</p>
      <form onSubmit={handleSubmit} className="record-form">
        {incident ? <>
          <label>Equipment<select name="equipment_id" required defaultValue=""><option value="" disabled>Choose an instrument</option>{equipment.map((item) => <option value={item.id} key={item.id}>{item.code} · {item.name}</option>)}</select></label>
          <label>What happened?<input name="title" required minLength="4" maxLength="160" placeholder="e.g. Channel B shows no signal" autoFocus /></label>
          <label>Details<textarea name="detail" rows="3" maxLength="2000" placeholder="What did you observe? What have you tried?" /></label>
          <div className="form-row"><label>Priority<select name="severity" defaultValue="medium"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></label><label>Reported by<input name="reported_by" required maxLength="80" placeholder="Your name" /></label></div>
        </> : <>
          <div className="form-row"><label>Equipment code<input name="code" required minLength="2" maxLength="32" pattern="[A-Za-z0-9-]+" placeholder="ECE-OSC-04" autoFocus /></label><label>Room<input name="room" required minLength="2" maxLength="60" placeholder="Electronics Lab 2" /></label></div>
          <label>Equipment name<input name="name" required minLength="2" maxLength="120" placeholder="Digital oscilloscope" /></label>
          <label>Category<input name="category" required minLength="2" maxLength="60" placeholder="Measurement" /></label>
        </>}
        <div className="form-actions"><button type="button" className="button ghost" onClick={onClose}>Cancel</button><button type="submit" className="button primary" disabled={saving}>{saving ? 'Saving…' : incident ? 'Report incident' : 'Add equipment'}<ArrowRight size={16} /></button></div>
      </form>
    </section>
  </div>
}

export default function App() {
  const [view, setView] = useState('overview')
  const [equipment, setEquipment] = useState([])
  const [incidents, setIncidents] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [modal, setModal] = useState(null)
  const [saving, setSaving] = useState(false)
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('active')
  const [equipmentFilter, setEquipmentFilter] = useState(null)

  const refresh = useCallback(async () => {
    try {
      const [nextEquipment, nextIncidents, nextSummary] = await Promise.all([
        request('/api/equipment'), request('/api/incidents'), request('/api/summary'),
      ])
      setEquipment(nextEquipment)
      setIncidents(nextIncidents)
      setSummary(nextSummary)
      setError('')
    } catch (caught) { setError(caught.message) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { refresh() }, [refresh])
  useEffect(() => { if (!notice) return; const timer = setTimeout(() => setNotice(''), 4200); return () => clearTimeout(timer) }, [notice])

  const equipmentById = useMemo(() => Object.fromEntries(equipment.map((item) => [item.id, item])), [equipment])
  const activeIncidents = useMemo(() => incidents.filter((item) => item.status !== 'resolved'), [incidents])
  const orderedEquipment = useMemo(() => [...equipment].sort((a, b) => statusRank[a.status] - statusRank[b.status] || a.code.localeCompare(b.code)), [equipment])
  const visibleIncidents = useMemo(() => incidents.filter((item) => {
    if (filter === 'active' && item.status === 'resolved') return false
    if (filter === 'resolved' && item.status !== 'resolved') return false
    if (equipmentFilter && item.equipment_id !== equipmentFilter) return false
    const haystack = `${item.title} ${item.reported_by} ${equipmentById[item.equipment_id]?.name || ''} ${equipmentById[item.equipment_id]?.code || ''}`.toLowerCase()
    return haystack.includes(query.toLowerCase())
  }), [incidents, filter, equipmentFilter, query, equipmentById])

  function navigate(next) { setView(next); setEquipmentFilter(null); setQuery('') }
  function openEquipmentIncidents(item) { setEquipmentFilter(item.id); setView('incidents'); setFilter('active') }

  async function submitRecord(data) {
    setSaving(true)
    try {
      await request(modal === 'incident' ? '/api/incidents' : '/api/equipment', { method: 'POST', body: JSON.stringify(data) })
      setModal(null)
      setNotice(modal === 'incident' ? 'Incident added to the queue.' : 'Equipment added to the lab.')
      await refresh()
    } catch (caught) { setError(caught.message) }
    finally { setSaving(false) }
  }

  async function changeStatus(id, status) {
    try {
      await request(`/api/incidents/${id}`, { method: 'PUT', body: JSON.stringify({ status }) })
      setNotice(status === 'resolved' ? 'Incident resolved.' : 'Work started on this incident.')
      await refresh()
    } catch (caught) { setError(caught.message) }
  }

  const date = new Intl.DateTimeFormat('en-IN', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date())
  const pageTitle = { overview: 'A clear view of every bench.', equipment: 'The equipment ledger.', incidents: 'Incidents in motion.' }[view]
  const pageText = { overview: 'See what is ready for the next class and what needs a closer look.', equipment: 'Every instrument has a place, a code, and a current state.', incidents: 'The repair queue, with the affected equipment attached.' }[view]

  return <div className="app-shell">
    <Sidebar active={view} onNavigate={navigate} summary={summary} />
    <main className="main-content">
      <header className="topbar"><span className="topbar-path">CAMPUS <span>/</span> LAB OPERATIONS <span>/</span> {view.toUpperCase()}</span><span className="topbar-date"><CircleDot size={14} /> {date}</span></header>
      <div className="content-wrap">
        <div className="page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> LIVE WORKSPACE</div><h1>{pageTitle}</h1><p>{pageText}</p></div><div className="heading-actions"><button className="button outline" type="button" onClick={refresh} title="Refresh data"><RefreshCw size={16} />Refresh</button><button className="button primary" type="button" onClick={() => setModal(view === 'equipment' ? 'equipment' : 'incident')} disabled={view !== 'equipment' && equipment.length === 0}><Plus size={17} />{view === 'equipment' ? 'Add equipment' : 'Report incident'}</button></div></div>

        {error && <div className="error-banner" role="alert"><AlertCircle size={18} /><span>{error}</span><button type="button" onClick={() => { setError(''); refresh() }}>Retry</button></div>}
        {notice && <div className="toast" role="status"><Check size={17} />{notice}</div>}

        {loading ? <div className="loading-panel"><div className="loading-line" /><div className="loading-line short" /><span>Checking the lab…</span></div> : <>
          {view === 'overview' && <>
            <section className="status-overview" aria-label="Lab status"><div className="overview-copy"><span className="section-kicker">TODAY AT A GLANCE</span><h2>{summary?.offline ? `${summary.offline} ${summary.offline === 1 ? 'instrument' : 'instruments'} out of service` : 'The lab is ready for the day.'}</h2><p>{summary?.offline ? 'The affected benches are marked below. Start with the open reports to see what needs repair.' : 'No equipment is currently marked out of service. New reports will appear here as they arrive.'}</p></div><div className="overview-numbers"><div><strong>{summary?.equipment_total ?? 0}</strong><span>instruments tracked</span></div><div><strong>{summary?.open_incidents ?? 0}</strong><span>active reports</span></div></div></section>
            <div className="section-heading"><div><span className="section-kicker">THE BENCH LINE</span><h2>Equipment status</h2></div><button className="text-link" type="button" onClick={() => navigate('equipment')}>View all equipment <ArrowRight size={16} /></button></div>
            {equipment.length ? <div className="equipment-grid">{orderedEquipment.slice(0, 6).map((item) => <EquipmentTile key={item.id} item={item} incidentCount={activeIncidents.filter((report) => report.equipment_id === item.id).length} onClick={() => openEquipmentIncidents(item)} />)}</div> : <div className="empty-state equipment-empty"><FlaskConical size={26} /><strong>No instruments yet</strong><span>Add the first piece of equipment to start the lab ledger.</span><button className="button outline" type="button" onClick={() => setModal('equipment')}>Add equipment <ArrowRight size={15} /></button></div>}
            <div className="section-heading incident-section"><div><span className="section-kicker">REPAIR QUEUE</span><h2>Open incidents</h2></div><button className="text-link" type="button" onClick={() => navigate('incidents')}>View all reports <ArrowRight size={16} /></button></div>
            <div className="table-card"><IncidentRows rows={activeIncidents.slice(0, 5)} equipmentById={equipmentById} onStatus={changeStatus} /></div>
          </>}

          {view === 'equipment' && <><section className="ledger-intro"><div><span className="section-kicker">EQUIPMENT REGISTER</span><h2>{summary?.equipment_total || 0} instruments across the lab</h2></div><p>Click an instrument to see its open incident reports. Codes stay attached to the same physical equipment over time.</p></section>{equipment.length ? <div className="equipment-grid ledger-grid">{orderedEquipment.map((item) => <EquipmentTile key={item.id} item={item} incidentCount={activeIncidents.filter((report) => report.equipment_id === item.id).length} onClick={() => openEquipmentIncidents(item)} />)}</div> : <div className="empty-state equipment-empty"><FlaskConical size={26} /><strong>The ledger is empty</strong><span>Add a bench instrument to make incidents traceable.</span><button className="button outline" type="button" onClick={() => setModal('equipment')}>Add equipment <ArrowRight size={15} /></button></div>}</>}

          {view === 'incidents' && <><section className="queue-summary"><div><span className="queue-number">{summary?.open_incidents ?? 0}</span><span>active<br />reports</span></div><p>Every report points back to a specific instrument. Resolve the work here and its bench status updates automatically.</p></section><div className="section-heading queue-heading"><div><span className="section-kicker">INCIDENT REGISTER</span><h2>{equipmentFilter ? `Reports for ${equipmentById[equipmentFilter]?.name || 'equipment'}` : 'All reports'}</h2></div>{equipmentFilter && <button className="text-link" type="button" onClick={() => setEquipmentFilter(null)}>Clear equipment filter <X size={15} /></button>}</div><div className="filters"><div className="filter-tabs" role="group" aria-label="Filter by status">{[['active', 'Active'], ['resolved', 'Resolved'], ['all', 'All']].map(([key, label]) => <button type="button" key={key} onClick={() => setFilter(key)} className={filter === key ? 'selected' : ''}>{label}</button>)}</div><label className="search-box"><Search size={17} /><span className="sr-only">Search incidents</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search incidents" /></label></div><div className="table-card"><IncidentRows rows={visibleIncidents} equipmentById={equipmentById} onStatus={changeStatus} /></div></>}
        </>}
        <footer className="content-footer"><span>LABPULSE / CAMPUS LAB OPERATIONS</span><span>Clear records for shared equipment.</span></footer>
      </div>
    </main>
    {modal && <Modal kind={modal} equipment={equipment} onClose={() => setModal(null)} onSubmit={submitRecord} saving={saving} />}
  </div>
}
