import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Flame, Beef, Wheat, Droplet, RefreshCw, User as UserIcon,
  LogOut, Pencil, X, Check, TrendingDown, Minus, TrendingUp,
} from 'lucide-react'
import { api, ActivityLevel, GoalKind } from '../lib/api'
import { storage } from '../lib/storage'

const ACTIVITY_OPTIONS: { value: ActivityLevel; label: string; desc: string }[] = [
  { value: 'sedentary',   label: 'Sedentario',       desc: 'Sin ejercicio' },
  { value: 'light',       label: 'Ligero',            desc: '1–3 días/sem' },
  { value: 'moderate',    label: 'Moderado',          desc: '3–5 días/sem' },
  { value: 'active',      label: 'Activo',            desc: '6–7 días/sem' },
  { value: 'very_active', label: 'Muy activo',        desc: 'Atleta / físico intenso' },
]

const GOAL_OPTIONS: { value: GoalKind; label: string; icon: React.ReactNode; color: string }[] = [
  { value: 'lose',     label: 'Pérdida',        icon: <TrendingDown className="w-4 h-4" />, color: 'border-blue-400 bg-blue-50 text-blue-700' },
  { value: 'maintain', label: 'Mantenimiento',  icon: <Minus className="w-4 h-4" />,        color: 'border-emerald-400 bg-emerald-50 text-emerald-700' },
  { value: 'gain',     label: 'Ganancia',       icon: <TrendingUp className="w-4 h-4" />,  color: 'border-orange-400 bg-orange-50 text-orange-700' },
]

const ACTIVITY_LABELS: Record<string, string> = {
  sedentary: 'Sedentario', light: 'Ligero', moderate: 'Moderado',
  active: 'Activo', very_active: 'Muy activo / atleta',
}
const GOAL_LABELS: Record<string, string> = {
  lose: 'Pérdida', maintain: 'Mantenimiento', gain: 'Ganancia',
}

export default function Profile() {
  const userId = storage.getUserId()!
  const qc = useQueryClient()
  const navigate = useNavigate()
  const [editing, setEditing] = useState(false)

  const userQ = useQuery({ queryKey: ['user', userId], queryFn: () => api.getUser(userId) })
  const goalQ = useQuery({ queryKey: ['goal', userId], queryFn: () => api.getGoal(userId) })

  // Estado de edición — inicializado cuando se abre el panel
  const [draft, setDraft] = useState<{
    goal: GoalKind
    activity_level: ActivityLevel
    weight_kg: number
    age: number
  } | null>(null)

  const openEdit = () => {
    if (!userQ.data) return
    setDraft({
      goal: userQ.data.goal as GoalKind,
      activity_level: userQ.data.activity_level as ActivityLevel,
      weight_kg: userQ.data.weight_kg,
      age: userQ.data.age,
    })
    setEditing(true)
  }

  const updateM = useMutation({
    mutationFn: () => api.updateUser(userId, draft!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['user', userId] })
      qc.invalidateQueries({ queryKey: ['goal', userId] })
      qc.invalidateQueries({ queryKey: ['dashboard', userId] })
      qc.invalidateQueries({ queryKey: ['workout-plan', userId] })
      qc.invalidateQueries({ queryKey: ['meal-plan', userId] })
      setEditing(false)
    },
  })

  const recalcM = useMutation({
    mutationFn: () => api.recalculateGoal(userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['goal', userId] }),
  })

  const logoutM = useMutation({
    mutationFn: () => api.logout(),
    onSettled: () => { storage.clear(); navigate('/onboarding') },
  })

  if (userQ.isLoading || goalQ.isLoading)
    return <div className="text-slate-500 text-center py-12">Cargando perfil…</div>
  if (!userQ.data) return <div>Usuario no encontrado</div>

  const u = userQ.data
  const g = goalQ.data

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Encabezado */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900">Tu perfil</h2>
        <button
          onClick={() => logoutM.mutate()}
          disabled={logoutM.isPending}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-red-600 transition disabled:opacity-50"
        >
          <LogOut className="w-4 h-4" /> Cerrar sesión
        </button>
      </div>

      {/* Tarjeta de datos personales */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-start gap-4 mb-5">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-white shrink-0">
            <UserIcon className="w-6 h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg text-slate-900">{u.name}</h3>
            {u.email && <p className="text-xs text-slate-400">{u.email}</p>}
            <p className="text-sm text-slate-500">
              {u.age} años · {u.weight_kg} kg · {u.height_cm} cm
            </p>
          </div>
          {!editing && (
            <button
              onClick={openEdit}
              className="flex items-center gap-1.5 text-sm text-brand-600 hover:text-brand-700 font-medium border border-brand-200 rounded-lg px-3 py-1.5 hover:bg-brand-50 transition"
            >
              <Pencil className="w-3.5 h-3.5" /> Editar
            </button>
          )}
        </div>

        {editing && draft ? (
          /* ── Panel de edición ── */
          <div className="space-y-5 pt-4 border-t border-slate-100">

            {/* Objetivo */}
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Objetivo</p>
              <div className="grid grid-cols-3 gap-2">
                {GOAL_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setDraft((d) => d ? { ...d, goal: opt.value } : d)}
                    className={`flex flex-col items-center gap-1 py-3 px-2 rounded-xl border-2 font-semibold text-sm transition ${
                      draft.goal === opt.value
                        ? opt.color + ' border-2'
                        : 'border-slate-200 text-slate-500 hover:border-slate-300'
                    }`}
                  >
                    {opt.icon}
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Nivel de actividad */}
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Nivel de actividad</p>
              <div className="space-y-1.5">
                {ACTIVITY_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setDraft((d) => d ? { ...d, activity_level: opt.value } : d)}
                    className={`w-full flex items-center justify-between text-left px-3 py-2 rounded-lg border text-sm transition ${
                      draft.activity_level === opt.value
                        ? 'border-brand-400 bg-brand-50 text-brand-700'
                        : 'border-slate-200 text-slate-600 hover:border-slate-300'
                    }`}
                  >
                    <span className="font-medium">{opt.label}</span>
                    <span className="text-xs text-slate-400">{opt.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Peso y edad */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Peso actual (kg)</label>
                <input
                  type="number"
                  min={30} max={300} step={0.5}
                  value={draft.weight_kg}
                  onChange={(e) => setDraft((d) => d ? { ...d, weight_kg: parseFloat(e.target.value) || d.weight_kg } : d)}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Edad</label>
                <input
                  type="number"
                  min={14} max={100}
                  value={draft.age}
                  onChange={(e) => setDraft((d) => d ? { ...d, age: parseInt(e.target.value) || d.age } : d)}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
                />
              </div>
            </div>

            {/* Aviso */}
            <p className="text-xs text-slate-400">
              Al guardar se recalcularán automáticamente tus calorías y macros.
            </p>

            {updateM.isError && (
              <p className="text-sm text-red-600">{(updateM.error as Error).message}</p>
            )}

            {/* Acciones */}
            <div className="flex gap-2">
              <button
                onClick={() => updateM.mutate()}
                disabled={updateM.isPending}
                className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold rounded-lg transition disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                {updateM.isPending ? 'Guardando…' : 'Guardar cambios'}
              </button>
              <button
                onClick={() => setEditing(false)}
                disabled={updateM.isPending}
                className="flex items-center gap-2 px-4 py-2 border border-slate-200 text-slate-600 text-sm rounded-lg hover:bg-slate-50 transition disabled:opacity-50"
              >
                <X className="w-4 h-4" /> Cancelar
              </button>
            </div>
          </div>
        ) : (
          /* ── Vista normal ── */
          <div className="grid grid-cols-2 gap-4 text-sm">
            <Field label="Género" value={u.gender === 'male' ? 'Masculino' : 'Femenino'} />
            <Field label="Actividad" value={ACTIVITY_LABELS[u.activity_level] || u.activity_level} />
            <Field label="Objetivo" value={GOAL_LABELS[u.goal] || u.goal} />
            <Field label="Fórmula" value="Mifflin-St Jeor" />
          </div>
        )}
      </div>

      {/* Plan nutricional */}
      {g && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <div className="flex items-baseline justify-between mb-4">
            <h3 className="font-semibold text-slate-900">Plan nutricional diario</h3>
            <button
              onClick={() => recalcM.mutate()}
              disabled={recalcM.isPending}
              className="text-sm text-brand-600 hover:text-brand-700 font-medium flex items-center gap-1 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${recalcM.isPending ? 'animate-spin' : ''}`} />
              Recalcular
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-5">
            <Stat icon={<Flame />} label="Calorías" value={g.kcal} unit="kcal" color="bg-orange-50 text-orange-700" />
            <Stat icon={<Beef />}  label="Proteína" value={g.protein_g} unit="g" color="bg-red-50 text-red-700" />
            <Stat icon={<Wheat />} label="Carbs"    value={g.carbs_g}   unit="g" color="bg-amber-50 text-amber-700" />
            <Stat icon={<Droplet />} label="Grasa"  value={g.fat_g}     unit="g" color="bg-emerald-50 text-emerald-700" />
          </div>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100 text-sm">
            <Field label="TMB (Mifflin-St Jeor)" value={`${g.bmr.toFixed(0)} kcal`} />
            <Field label="TDEE" value={`${g.tdee.toFixed(0)} kcal`} />
          </div>
        </div>
      )}
    </div>
  )
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-slate-500">{label}</p>
      <p className="font-medium text-slate-900">{value}</p>
    </div>
  )
}

function Stat({ icon, label, value, unit, color }: {
  icon: React.ReactNode; label: string; value: number; unit: string; color: string
}) {
  return (
    <div className="flex gap-3">
      <div className={`p-2 rounded-lg ${color}`}>{icon}</div>
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-xl font-bold text-slate-900 tabular-nums">
          {value.toFixed(0)} <span className="text-xs font-normal text-slate-400">{unit}</span>
        </p>
      </div>
    </div>
  )
}
