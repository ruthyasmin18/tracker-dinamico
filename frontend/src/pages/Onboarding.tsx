import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Activity, ChevronRight, Sparkles } from 'lucide-react'
import { api, ActivityLevel, Gender, GoalKind } from '../lib/api'
import { storage } from '../lib/storage'

export default function Onboarding() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: 'Mateo',
    age: 24,
    weight_kg: 75,
    height_cm: 175,
    gender: 'male' as Gender,
    activity_level: 'moderate' as ActivityLevel,
    goal: 'maintain' as GoalKind,
  })

  const mutation = useMutation({
    mutationFn: () => api.createUser(form),
    onSuccess: (user) => {
      storage.setUserId(user.id)
      navigate('/plan')
    },
  })

  const set = <K extends keyof typeof form>(key: K, value: typeof form[K]) =>
    setForm((f) => ({ ...f, [key]: value }))

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-2xl w-full p-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Tracker Dinámico</h1>
            <p className="text-sm text-slate-500">Configura tu perfil — toma 30 segundos</p>
          </div>
        </div>

        <div className="my-6 p-4 bg-brand-50 border border-brand-100 rounded-lg flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-brand-600 mt-0.5 shrink-0" />
          <p className="text-sm text-slate-700">
            Calcularemos tus objetivos usando la fórmula <span className="font-semibold">Mifflin-St Jeor</span>
            {' '}y distribución de macros según tu meta. Podrás recalcular cuando cambien tus datos.
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            mutation.mutate()
          }}
          className="space-y-5"
        >
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nombre</label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => set('name', e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Edad</label>
              <input
                type="number" min="14" max="100" required
                value={form.age}
                onChange={(e) => set('age', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Peso (kg)</label>
              <input
                type="number" step="0.1" min="30" max="300" required
                value={form.weight_kg}
                onChange={(e) => set('weight_kg', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Altura (cm)</label>
              <input
                type="number" step="0.1" min="100" max="250" required
                value={form.height_cm}
                onChange={(e) => set('height_cm', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Género</label>
            <div className="grid grid-cols-2 gap-2">
              {(['male', 'female'] as Gender[]).map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => set('gender', g)}
                  className={`px-4 py-2 rounded-lg border-2 font-medium transition ${
                    form.gender === g
                      ? 'border-brand-500 bg-brand-50 text-brand-700'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {g === 'male' ? 'Masculino' : 'Femenino'}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nivel de actividad</label>
            <select
              value={form.activity_level}
              onChange={(e) => set('activity_level', e.target.value as ActivityLevel)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="sedentary">Sedentario (1.2)</option>
              <option value="light">Ligero (1.375)</option>
              <option value="moderate">Moderado (1.55)</option>
              <option value="active">Activo (1.725)</option>
              <option value="very_active">Muy activo / atleta (1.9)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Objetivo</label>
            <div className="grid grid-cols-3 gap-2">
              {([
                { v: 'lose', l: 'Perder grasa', d: '-20% kcal' },
                { v: 'maintain', l: 'Mantener', d: 'TDEE' },
                { v: 'gain', l: 'Ganar masa', d: '+10% kcal' },
              ] as { v: GoalKind; l: string; d: string }[]).map((opt) => (
                <button
                  key={opt.v}
                  type="button"
                  onClick={() => set('goal', opt.v)}
                  className={`px-3 py-3 rounded-lg border-2 transition text-left ${
                    form.goal === opt.v
                      ? 'border-brand-500 bg-brand-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="font-semibold text-sm text-slate-900">{opt.l}</div>
                  <div className="text-xs text-slate-500">{opt.d}</div>
                </button>
              ))}
            </div>
          </div>

          {mutation.isError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              Error: {(mutation.error as Error).message}
            </div>
          )}

          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-lg shadow-sm transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {mutation.isPending ? 'Calculando...' : (
              <>
                Calcular mi plan
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
