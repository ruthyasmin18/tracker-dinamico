import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Flame, Beef, Wheat, Droplet, RefreshCw, User as UserIcon, LogOut } from 'lucide-react'
import { api } from '../lib/api'
import { storage } from '../lib/storage'

const ACTIVITY_LABELS: Record<string, string> = {
  sedentary: 'Sedentario',
  light: 'Ligero',
  moderate: 'Moderado',
  active: 'Activo',
  very_active: 'Muy activo / atleta',
}
const GOAL_LABELS: Record<string, string> = {
  lose: 'Pérdida',
  maintain: 'Mantenimiento',
  gain: 'Ganancia',
}

export default function Profile() {
  const userId = storage.getUserId()!
  const qc = useQueryClient()
  const navigate = useNavigate()

  const userQ = useQuery({ queryKey: ['user', userId], queryFn: () => api.getUser(userId) })
  const goalQ = useQuery({ queryKey: ['goal', userId], queryFn: () => api.getGoal(userId) })

  const recalcM = useMutation({
    mutationFn: () => api.recalculateGoal(userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['goal', userId] }),
  })

  const logoutM = useMutation({
    mutationFn: () => api.logout(),
    onSettled: () => {
      storage.clear()
      navigate('/onboarding')
    },
  })

  if (userQ.isLoading || goalQ.isLoading) {
    return <div className="text-slate-500 text-center py-12">Cargando perfil…</div>
  }
  if (!userQ.data) return <div>Usuario no encontrado</div>

  const u = userQ.data
  const g = goalQ.data

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900">Tu perfil</h2>
        <button
          onClick={() => logoutM.mutate()}
          disabled={logoutM.isPending}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-red-600 transition disabled:opacity-50"
        >
          <LogOut className="w-4 h-4" />
          Cerrar sesión
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center gap-4 mb-5">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-white">
            <UserIcon className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-slate-900">{u.name}</h3>
            {u.email && <p className="text-xs text-slate-400">{u.email}</p>}
            <p className="text-sm text-slate-500">
              {u.age} años · {u.weight_kg} kg · {u.height_cm} cm
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <Field label="Género" value={u.gender === 'male' ? 'Masculino' : 'Femenino'} />
          <Field label="Actividad" value={ACTIVITY_LABELS[u.activity_level] || u.activity_level} />
          <Field label="Objetivo" value={GOAL_LABELS[u.goal] || u.goal} />
          <Field label="Fórmula" value="Mifflin-St Jeor" />
        </div>
      </div>

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
            <Stat icon={<Beef />} label="Proteína" value={g.protein_g} unit="g" color="bg-red-50 text-red-700" />
            <Stat icon={<Wheat />} label="Carbs" value={g.carbs_g} unit="g" color="bg-amber-50 text-amber-700" />
            <Stat icon={<Droplet />} label="Grasa" value={g.fat_g} unit="g" color="bg-emerald-50 text-emerald-700" />
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

function Stat({ icon, label, value, unit, color }: { icon: React.ReactNode; label: string; value: number; unit: string; color: string }) {
  return (
    <div className="flex gap-3">
      <div className={`p-2 rounded-lg ${color}`}>{icon}</div>
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-xl font-bold text-slate-900 tabular-nums">{value.toFixed(0)} <span className="text-xs font-normal text-slate-400">{unit}</span></p>
      </div>
    </div>
  )
}
