import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, CartesianGrid,
} from 'recharts'
import { Sparkles, AlertTriangle, Coffee, Timer, History, Zap, BookOpen } from 'lucide-react'
import { api, AutoRecalcResponse, DayPlan, RecalcResponse } from '../lib/api'
import { storage } from '../lib/storage'

function todayIso(): string {
  return new Date().toISOString().split('T')[0]
}

const EVENT_PRESETS = [
  {
    id: 'pizza',
    icon: <Coffee className="w-4 h-4" />,
    label: 'Comí algo extra',
    type: 'extra_calories',
    description: 'Comida no planeada',
    delta: 800,
  },
  {
    id: 'skip',
    icon: <AlertTriangle className="w-4 h-4" />,
    label: 'Salté una comida',
    type: 'skipped_meal',
    description: 'No alcancé a comer',
    delta: -500,
  },
  {
    id: 'gym',
    icon: <Timer className="w-4 h-4" />,
    label: 'Menos tiempo de gym',
    type: 'reduced_workout_time',
    description: 'Entrené menos hoy',
    delta: 300,
  },
] as const

export default function Recalc() {
  const userId = storage.getUserId()!
  const [eventType, setEventType] = useState<typeof EVENT_PRESETS[number]['type']>('extra_calories')
  const [description, setDescription] = useState('Pizza con amigos')
  const [kcalDelta, setKcalDelta] = useState(800)
  const [response, setResponse] = useState<RecalcResponse | null>(null)

  const logsQ = useQuery({
    queryKey: ['logs', userId],
    queryFn: () => api.getLogs(userId),
  })

  // Auto-detección desde el diario (F4 ↔ F3)
  const autoMut = useMutation({
    mutationFn: () => api.autoRecalc(userId, todayIso()),
    onSuccess: (res: AutoRecalcResponse) => {
      if (res.adjusted) {
        setResponse(res as unknown as RecalcResponse)
        logsQ.refetch()
      } else {
        alert(res.message)
      }
    },
  })

  const mut = useMutation({
    mutationFn: () =>
      api.reportEvent({
        user_id: userId,
        event_type: eventType,
        event_description: description,
        kcal_delta: kcalDelta,
        target_date: todayIso(),
      }),
    onSuccess: (res) => {
      setResponse(res)
      logsQ.refetch()
    },
  })

  const applyPreset = (preset: typeof EVENT_PRESETS[number]) => {
    setEventType(preset.type)
    setDescription(preset.description)
    setKcalDelta(preset.delta)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-5 h-5 text-brand-600" />
            <h2 className="text-2xl font-bold text-slate-900">Motor de Recálculo Dinámico</h2>
          </div>
          <p className="text-slate-500 text-sm">
            Reporta un imprevisto o deja que el motor detecte la desviación de tu diario automáticamente.
          </p>
        </div>
        <button
          onClick={() => autoMut.mutate()}
          disabled={autoMut.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-sm font-semibold rounded-lg shadow-sm transition disabled:opacity-50 shrink-0"
        >
          <BookOpen className="w-4 h-4" />
          {autoMut.isPending ? 'Analizando diario…' : 'Detectar desde mi diario de hoy'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-1 bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="font-semibold text-slate-900 mb-4">¿Qué pasó hoy?</h3>

          <div className="space-y-2 mb-5">
            {EVENT_PRESETS.map((p) => (
              <button
                key={p.id}
                onClick={() => applyPreset(p)}
                className={`w-full text-left px-4 py-3 rounded-lg border-2 flex items-center gap-3 transition ${
                  eventType === p.type
                    ? 'border-brand-500 bg-brand-50'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className={`p-2 rounded-lg ${eventType === p.type ? 'bg-brand-100 text-brand-600' : 'bg-slate-100 text-slate-500'}`}>
                  {p.icon}
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-slate-900">{p.label}</div>
                  <div className="text-xs text-slate-500">{p.description}</div>
                </div>
              </button>
            ))}
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-1">Descripción</label>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
            />
          </div>

          <div className="mb-5">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Desviación en kcal
            </label>
            <input
              type="number"
              value={kcalDelta}
              onChange={(e) => setKcalDelta(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none tabular-nums"
            />
            <p className="text-xs text-slate-500 mt-1">
              {kcalDelta > 0 ? `Excedí mi plan en ${kcalDelta} kcal` : kcalDelta < 0 ? `Tengo déficit de ${Math.abs(kcalDelta)} kcal` : 'Sin desviación'}
            </p>
          </div>

          {mut.isError && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {(mut.error as Error).message}
            </div>
          )}

          <button
            onClick={() => mut.mutate()}
            disabled={mut.isPending}
            className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-700 hover:from-brand-700 hover:to-brand-900 text-white font-semibold rounded-lg shadow-sm transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Zap className="w-4 h-4" />
            {mut.isPending ? 'Recalculando…' : 'Recalibrar mi plan'}
          </button>
        </div>

        {/* Result */}
        <div className="lg:col-span-2 space-y-6">
          {!response ? (
            <div className="bg-white border border-dashed border-slate-300 rounded-2xl p-12 text-center text-slate-500">
              <Sparkles className="w-10 h-10 mx-auto text-slate-300 mb-3" />
              <p className="font-medium">Reporta un evento para ver el plan recalibrado.</p>
              <p className="text-sm">El motor priorizará la proteína y nunca propondrá un déficit mayor al 30%.</p>
            </div>
          ) : (
            <ResultPanel response={response} />
          )}

          {/* Logs históricos */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-slate-400" />
                <h3 className="font-semibold text-slate-900">Histórico de recálculos</h3>
              </div>
              <span className="text-xs text-slate-400">{logsQ.data?.length || 0} eventos</span>
            </div>
            <div className="divide-y divide-slate-50 max-h-64 overflow-y-auto">
              {logsQ.data?.length === 0 ? (
                <p className="px-5 py-4 text-sm text-slate-400 italic">Sin recálculos previos.</p>
              ) : (
                logsQ.data?.map((log) => (
                  <div key={log.id} className="px-5 py-3 hover:bg-slate-50">
                    <div className="flex items-baseline justify-between">
                      <p className="font-medium text-slate-900 text-sm">{log.event_description}</p>
                      <span className="text-xs text-slate-400 tabular-nums">{new Date(log.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      Δ {log.kcal_delta > 0 ? '+' : ''}{log.kcal_delta} kcal · propagado a {log.propagated_days + 1} día(s)
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ResultPanel({ response }: { response: RecalcResponse }) {
  const chartData = response.days.map((d) => ({
    date: d.date.slice(5),
    Original: d.original.kcal,
    Ajustado: d.adjusted.kcal,
  }))

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-br from-brand-50 to-white border border-brand-200 rounded-2xl p-5 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-brand-100 rounded-lg">
            <Sparkles className="w-5 h-5 text-brand-700" />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-slate-900 mb-1">Plan actualizado</h4>
            <p className="text-sm text-slate-700">{response.message}</p>
          </div>
        </div>
      </div>

      {/* Gráfico antes/después */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
        <h4 className="font-semibold text-slate-900 mb-3">Calorías por día — Original vs Ajustado</h4>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
              cursor={{ fill: 'rgba(59,130,246,0.05)' }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Original" fill="#cbd5e1" radius={[6, 6, 0, 0]} />
            <Bar dataKey="Ajustado" fill="#2563eb" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detalle por día */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {response.days.map((d) => (
          <DayCard key={d.date} day={d} />
        ))}
      </div>
    </div>
  )
}

function DayCard({ day }: { day: DayPlan }) {
  const delta = day.adjusted.kcal - day.original.kcal
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-baseline justify-between mb-3">
        <h5 className="font-semibold text-slate-900 text-sm">{day.date}</h5>
        <span className={`text-xs font-medium tabular-nums ${delta < 0 ? 'text-red-600' : delta > 0 ? 'text-emerald-600' : 'text-slate-400'}`}>
          {delta > 0 ? '+' : ''}{delta.toFixed(0)} kcal
        </span>
      </div>
      <div className="space-y-2 text-xs">
        <Row label="kcal" original={day.original.kcal} adjusted={day.adjusted.kcal} />
        <Row label="Proteína" original={day.original.protein_g} adjusted={day.adjusted.protein_g} unit="g" />
        <Row label="Carbohidratos" original={day.original.carbs_g} adjusted={day.adjusted.carbs_g} unit="g" />
        <Row label="Grasa" original={day.original.fat_g} adjusted={day.adjusted.fat_g} unit="g" />
      </div>
      <p className="text-xs text-slate-400 italic mt-3">{day.note}</p>
    </div>
  )
}

function Row({ label, original, adjusted, unit = '' }: { label: string; original: number; adjusted: number; unit?: string }) {
  const changed = Math.abs(original - adjusted) > 0.5
  return (
    <div className="flex items-center justify-between">
      <span className="text-slate-500">{label}</span>
      <span className="tabular-nums">
        <span className="text-slate-400 line-through mr-1">{original.toFixed(0)}{unit}</span>
        <span className={changed ? 'font-semibold text-slate-900' : 'text-slate-700'}>
          {adjusted.toFixed(0)}{unit}
        </span>
      </span>
    </div>
  )
}
