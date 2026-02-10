import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const WS_BASE = import.meta.env.VITE_WS_BASE || `ws://${window.location.hostname}:8000/ws/energy/`

const statusColors = {
  active: 'bg-success/20 text-success border-success/40',
  inactive: 'bg-warning/20 text-warning border-warning/40',
}

const initialTrend = Array.from({ length: 12 }).map((_, index) => ({
  time: `${index + 1}:00`,
  power: 0,
}))

export default function App() {
  const [summary, setSummary] = useState({
    total_power_kw: 0,
    workshop_breakdown: [],
    top_machines: [],
    alerts: [],
  })
  const [trend, setTrend] = useState(initialTrend)
  const [machines, setMachines] = useState([])

  const cards = useMemo(
    () => [
      { label: 'Total Factory Power', value: `${summary.total_power_kw.toFixed(2)} kW` },
      { label: 'Active Alerts', value: `${summary.alerts.length}` },
      { label: 'Workshops Monitored', value: `${summary.workshop_breakdown.length}` },
      { label: 'Machines Online', value: `${machines.filter((m) => m.status === 'active').length}` },
    ],
    [summary, machines]
  )

  useEffect(() => {
    axios.get(`${API_BASE}/dashboard/summary/`).then((res) => setSummary(res.data))
    axios.get(`${API_BASE}/machines/`).then((res) => setMachines(res.data))
    axios.get(`${API_BASE}/energy-records/?ordering=-timestamp`).then((res) => {
      const latest = res.data.slice(0, 12).reverse()
      setTrend(
        latest.map((record, index) => ({
          time: `${index + 1}m`,
          power: record.power_kw,
        }))
      )
    })
  }, [])

  useEffect(() => {
    const socket = new WebSocket(WS_BASE)
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      if (payload.record) {
        setTrend((prev) => {
          const next = [...prev.slice(1), {
            time: new Date().toLocaleTimeString().slice(0, 5),
            power: payload.record.power_kw,
          }]
          return next
        })
        setSummary((prev) => ({
          ...prev,
          total_power_kw: prev.total_power_kw + payload.record.power_kw,
        }))
      }
      if (payload.alert) {
        setSummary((prev) => ({
          ...prev,
          alerts: [payload.alert, ...prev.alerts].slice(0, 10),
        }))
      }
    }
    return () => socket.close()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      <aside className="w-64 bg-panel border-r border-slate-800 p-6 hidden lg:flex flex-col gap-6">
        <div>
          <h1 className="text-xl font-semibold text-white">Factory EMS</h1>
          <p className="text-sm text-slate-400">Industrial Energy Control</p>
        </div>
        <nav className="flex flex-col gap-3 text-sm">
          {['Dashboard', 'Machines', 'Realtime', 'Alerts', 'Reports'].map((item) => (
            <button
              key={item}
              className="text-left px-3 py-2 rounded-lg bg-panel-light hover:bg-slate-700 transition"
            >
              {item}
            </button>
          ))}
        </nav>
        <div className="mt-auto text-xs text-slate-500">
          Offline LAN Mode
        </div>
      </aside>

      <main className="flex-1">
        <header className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 px-6 py-5 border-b border-slate-800 bg-panel">
          <div>
            <h2 className="text-2xl font-semibold">Industrial Energy Management Dashboard</h2>
            <p className="text-sm text-slate-400">Realtime monitoring for the mechanical repair workshop</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs uppercase tracking-wide text-slate-400">Status</span>
            <span className="px-3 py-1 rounded-full border border-success/40 bg-success/20 text-success text-sm">Operational</span>
          </div>
        </header>

        <section className="p-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {cards.map((card) => (
            <div key={card.label} className="bg-panel-light border border-slate-800 rounded-xl p-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide">{card.label}</p>
              <p className="text-2xl font-semibold mt-2">{card.value}</p>
            </div>
          ))}
        </section>

        <section className="grid grid-cols-1 xl:grid-cols-3 gap-6 px-6 pb-6">
          <div className="xl:col-span-2 bg-panel-light border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Live Power Trend</h3>
              <span className="text-xs text-slate-400">Auto-updating</span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trend}>
                  <defs>
                    <linearGradient id="powerGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b' }} />
                  <Area type="monotone" dataKey="power" stroke="#38bdf8" fill="url(#powerGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-panel-light border border-slate-800 rounded-xl p-5 flex flex-col">
            <h3 className="font-semibold mb-4">Active Alerts</h3>
            <div className="space-y-3 overflow-y-auto">
              {summary.alerts.length === 0 && (
                <div className="text-sm text-slate-500">No active alerts.</div>
              )}
              {summary.alerts.map((alert) => (
                <div key={alert.id} className="border border-danger/40 bg-danger/10 rounded-lg p-3">
                  <p className="text-sm font-semibold text-danger">{alert.machine_name}</p>
                  <p className="text-xs text-slate-300">{alert.message}</p>
                  <p className="text-[11px] text-slate-400 mt-1">{new Date(alert.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 xl:grid-cols-3 gap-6 px-6 pb-8">
          <div className="bg-panel-light border border-slate-800 rounded-xl p-5">
            <h3 className="font-semibold mb-4">Consumption by Workshop</h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={summary.workshop_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="machine__workshop_area" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b' }} />
                  <Bar dataKey="total" fill="#4ade80" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-panel-light border border-slate-800 rounded-xl p-5">
            <h3 className="font-semibold mb-4">Top 5 Energy Consumers</h3>
            <ul className="space-y-3">
              {summary.top_machines.map((machine) => (
                <li key={machine.machine__name} className="flex items-center justify-between text-sm">
                  <span>{machine.machine__name}</span>
                  <span className="text-accent">{machine.total.toFixed(2)} kW</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-panel-light border border-slate-800 rounded-xl p-5">
            <h3 className="font-semibold mb-4">Machine Status</h3>
            <div className="space-y-3">
              {machines.map((machine) => (
                <div key={machine.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{machine.name}</p>
                    <p className="text-xs text-slate-400">{machine.workshop_area}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 border rounded-full ${statusColors[machine.status]}`}>
                    {machine.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
