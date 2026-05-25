import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
  PieChart, Pie, Cell,
} from 'recharts'
import { TrendingUp, Flame, Target, Zap, Calendar, Award } from 'lucide-react'
import { api } from '../lib/api'
import { storage } from '../lib/storage'

const MACRO_COLORS = {
  protein_g: '#ef4444',  // rojo
  carbs_g:   '#f59e0b',  // ámbar
  fat_g:     '#10b981',  // verde
}

const DAY_LABELS: Record<string, string> = {
  '0': 'Dom', '1': 'Lun', '2': 'Mar', '3': 'Mié',
  '4': 'Jue', '5': 'Vie', '6': 'Sáb',
}

function shortDate(isoDate: string): string {
  const d = new Date(isoDate + 'T12:00:00')
  return `${d.getDate()}/${d.getMonth() + 1}`
}

function dayName(isoDate: string): string {
  const d = new Date(isoDate + 'T12:00:00')
  return DAY_LABELS[String(d.getDay())] ?? isoDate.slice(5)
}

export default function Dashboard() {
  const userId = storage.getUserId()!

  const dashQ = useQuery({
    queryKey: ['dashboard', userId],
    queryFn: () => api.getWeeklyDashboard(userId),
    refetchOnWindowFocus: false,
  })

  if (dashQ.isLoading) {
    return <div className="text-center text-slate-500 py-16">Cargando dashboard…</div>
  }
  if (dashQ.isError) {
    return (
      <div className="text-red-600 text-center py-12">
        Error: {(dashQ.error as Error).message}
      </div>
    )
  }

  const d = dashQ.data!

  // Datos para el gráfico de barras diario
  const barData = d.daily_stats.map((s) => ({
    name: `${dayName(s.date)}\n${shortDate(s.date)}`,
    Consumido: Math.round(s.kcal_consumed),
    Objetivo: Math.round(s.kcal_goal),
  }))

  // Datos para el donut de macros (promedio semanal)
  const totalMacros = d.macro_avg.protein_g + d.macro_avg.carbs_g + d.macro_avg.fat_g
  const pieData = totalMacros > 0 ? [
    { name: 'Proteína', value: Math.round(d.macro_avg.protein_g), color: MACRO_COLORS.protein_g },
    { name: 'Carbohidratos', value: Math.round(d.macro_avg.carbs_g), color: MACRO_COLORS.carbs_g },
    { name: 'Grasa', value: Math.round(d.macro_avg.fat_g), color: MACRO_COLORS.fat_g },
  ] : []

  const adherenceColor = d.adherence_pct >= 80 ? 'text-emerald-600' : d.adherence_pct >= 50 ? 'text-amber-600' : 'text-red-600'

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp className="w-5 h-5 text-brand-600" />
          <h2 className="text-2xl font-bold text-slate-900">Dashboard de Progreso</h2>
        </div>
        <p className="text-slate-500 text-sm">
          Últimos 7 días · {new Date(d.period_start + 'T12:00:00').toLocaleDateString()} – {new Date(d.period_end + 'T12:00:00').toLocaleDateString()}
        </p>
      </div>

      {/* ── KPIs principales ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard
          icon={<Target className="w-5 h-5" />}
          label="Adherencia"
          value={`${d.adherence_pct.toFixed(0)}%`}
          sub="promedio semanal"
          color="bg-blue-50 text-blue-700"
          valueClass={adherenceColor}
        />
        <KpiCard
          icon={<Flame className="w-5 h-5" />}
          label="Kcal promedio"
          value={d.kcal_promedio.toFixed(0)}
          sub={`objetivo: ${d.kcal_objetivo.toFixed(0)}`}
          color="bg-orange-50 text-orange-700"
        />
        <KpiCard
          icon={<Award className="w-5 h-5" />}
          label="Racha actual"
          value={`${d.racha_actual} día${d.racha_actual !== 1 ? 's' : ''}`}
          sub="días consecutivos con registro"
          color="bg-emerald-50 text-emerald-700"
        />
        <KpiCard
          icon={<Calendar className="w-5 h-5" />}
          label="Días con datos"
          value={`${d.dias_con_datos} / 7`}
          sub="días con al menos 1 entrada"
          color="bg-purple-50 text-purple-700"
        />
      </div>

      {/* ── Adherencia diaria visual ── */}
      <div className="grid grid-cols-7 gap-2">
        {d.daily_stats.map((s) => {
          const pct = Math.min(s.adherence_pct, 100)
          const hasData = s.kcal_consumed > 0
          return (
            <div key={s.date} className="flex flex-col items-center gap-1">
              <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    !hasData ? 'bg-slate-200' : pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-400' : 'bg-red-400'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-500">{dayName(s.date)}</span>
              <span className="text-[10px] font-semibold text-slate-700 tabular-nums">
                {hasData ? `${pct.toFixed(0)}%` : '—'}
              </span>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Gráfico de barras kcal ── */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4 text-slate-400" />
            <h3 className="font-semibold text-slate-900">Calorías consumidas vs objetivo</h3>
          </div>
          {d.dias_con_datos === 0 ? (
            <div className="h-52 flex items-center justify-center text-slate-400 text-sm">
              Sin registros en el período — empieza a registrar en el Diario.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
                  cursor={{ fill: 'rgba(59,130,246,0.04)' }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="Objetivo" fill="#e2e8f0" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Consumido" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* ── Donut distribución macros ── */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-4 h-4 text-slate-400" />
            <h3 className="font-semibold text-slate-900">Distribución de macros</h3>
            <span className="text-xs text-slate-400 ml-auto">promedio diario</span>
          </div>
          {pieData.length === 0 ? (
            <div className="h-52 flex items-center justify-center text-slate-400 text-sm text-center">
              Sin datos suficientes aún.
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: number, name: string) => [`${val} g`, name]}
                    contentStyle={{ borderRadius: 8, fontSize: 12 }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-2">
                {pieData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-slate-600">{item.name}</span>
                    </div>
                    <span className="font-semibold text-slate-900 tabular-nums">{item.value} g</span>
                  </div>
                ))}
                <div className="pt-2 border-t border-slate-100 flex justify-between text-xs text-slate-500">
                  <span>Total macros</span>
                  <span className="tabular-nums">{Math.round(totalMacros)} g / día</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ── Tabla detallada por día ── */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-900">Detalle diario</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-slate-500 bg-slate-50">
                <th className="px-5 py-3 text-left">Día</th>
                <th className="px-4 py-3 text-right tabular-nums">Consumido</th>
                <th className="px-4 py-3 text-right tabular-nums">Objetivo</th>
                <th className="px-4 py-3 text-right tabular-nums">Proteína</th>
                <th className="px-4 py-3 text-right tabular-nums">Carbs</th>
                <th className="px-4 py-3 text-right tabular-nums">Grasa</th>
                <th className="px-4 py-3 text-right">Adherencia</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {d.daily_stats.map((s) => {
                const hasData = s.kcal_consumed > 0
                const adh = s.adherence_pct
                return (
                  <tr key={s.date} className={`hover:bg-slate-50 ${!hasData ? 'opacity-50' : ''}`}>
                    <td className="px-5 py-3 font-medium text-slate-900">
                      {dayName(s.date)} <span className="text-slate-400 text-xs">{shortDate(s.date)}</span>
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-slate-700">
                      {hasData ? `${s.kcal_consumed.toFixed(0)} kcal` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-slate-400">
                      {s.kcal_goal.toFixed(0)} kcal
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-red-600">
                      {hasData ? `${s.protein_g.toFixed(0)}g` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-amber-600">
                      {hasData ? `${s.carbs_g.toFixed(0)}g` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-emerald-600">
                      {hasData ? `${s.fat_g.toFixed(0)}g` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {hasData ? (
                        <span className={`font-semibold tabular-nums ${
                          adh >= 80 ? 'text-emerald-600' : adh >= 50 ? 'text-amber-600' : 'text-red-600'
                        }`}>
                          {adh.toFixed(0)}%
                        </span>
                      ) : (
                        <span className="text-slate-300">—</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function KpiCard({
  icon, label, value, sub, color, valueClass,
}: {
  icon: React.ReactNode
  label: string
  value: string
  sub: string
  color: string
  valueClass?: string
}) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-3 ${color}`}>
        {icon}
      </div>
      <p className="text-xs text-slate-500 mb-0.5">{label}</p>
      <p className={`text-2xl font-bold tabular-nums ${valueClass ?? 'text-slate-900'}`}>{value}</p>
      <p className="text-xs text-slate-400 mt-1">{sub}</p>
    </div>
  )
}
