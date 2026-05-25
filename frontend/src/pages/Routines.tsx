import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Dumbbell, Zap, Timer, ChevronRight, RefreshCw,
  Check, Target, Flame, BarChart2,
} from 'lucide-react'
import { api, ExpressRoutineRequest, GoalKind, WorkoutDay } from '../lib/api'
import { storage } from '../lib/storage'

const TIME_OPTIONS = [15, 20, 30, 45, 60] as const

const EQUIPMENT_OPTIONS = [
  { value: 'bodyweight', label: 'Sin equipo', desc: 'Solo peso corporal', icon: '🏠' },
  { value: 'dumbbell',   label: 'Mancuernas', desc: 'Peso corporal + mancuernas', icon: '🏋️' },
  { value: 'full',       label: 'Gym completo', desc: 'Barra, máquinas, etc.', icon: '🏟️' },
] as const

const MUSCLE_OPTIONS = [
  { value: 'all',       label: 'Full Body',  icon: '⚡' },
  { value: 'chest',     label: 'Pecho',      icon: '💪' },
  { value: 'back',      label: 'Espalda',    icon: '🔙' },
  { value: 'legs',      label: 'Piernas',    icon: '🦵' },
  { value: 'arms',      label: 'Brazos',     icon: '💪' },
  { value: 'shoulders', label: 'Hombros',    icon: '🏋️' },
  { value: 'core',      label: 'Core',       icon: '🎯' },
] as const

const EQUIPMENT_LABELS: Record<string, string> = {
  bodyweight: 'Peso corporal',
  dumbbell: 'Mancuernas',
  barbell: 'Barra',
  machine: 'Máquina',
}

export default function Routines() {
  const userId = storage.getUserId()!

  const [form, setForm] = useState<ExpressRoutineRequest>({
    available_time_min: 30,
    equipment: 'bodyweight',
    target_muscle: 'all',
    goal: 'maintain',
  })
  const [result, setResult] = useState<WorkoutDay | null>(null)

  // Plan semanal de gimnasio
  const weeklyQ = useQuery({
    queryKey: ['workout-plan', userId],
    queryFn: () => api.getWorkoutPlan(userId),
  })

  const generateM = useMutation({
    mutationFn: () => api.generateExpressRoutine(form),
    onSuccess: (data) => setResult(data),
  })

  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Dumbbell className="w-5 h-5 text-brand-600" />
          <h2 className="text-2xl font-bold text-slate-900">Generador de Rutinas Express</h2>
        </div>
        <p className="text-slate-500 text-sm">
          Dime cuánto tiempo tienes y qué equipo usarás — te genero una rutina en segundos.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Configurador ── */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
          {/* Tiempo */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              <Timer className="w-4 h-4 inline mr-1" />
              Tiempo disponible
            </label>
            <div className="flex flex-wrap gap-2">
              {TIME_OPTIONS.map((t) => (
                <button
                  key={t}
                  onClick={() => setForm((f) => ({ ...f, available_time_min: t }))}
                  className={`px-4 py-2 rounded-lg border-2 text-sm font-semibold transition ${
                    form.available_time_min === t
                      ? 'border-brand-500 bg-brand-50 text-brand-700'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  {t} min
                </button>
              ))}
            </div>
          </div>

          {/* Equipo */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              <Dumbbell className="w-4 h-4 inline mr-1" />
              Equipo disponible
            </label>
            <div className="space-y-2">
              {EQUIPMENT_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setForm((f) => ({ ...f, equipment: opt.value }))}
                  className={`w-full text-left px-4 py-3 rounded-lg border-2 flex items-center gap-3 transition ${
                    form.equipment === opt.value
                      ? 'border-brand-500 bg-brand-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <span className="text-xl">{opt.icon}</span>
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{opt.label}</div>
                    <div className="text-xs text-slate-500">{opt.desc}</div>
                  </div>
                  {form.equipment === opt.value && (
                    <Check className="w-4 h-4 text-brand-600 ml-auto" />
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Músculo objetivo */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              <Target className="w-4 h-4 inline mr-1" />
              Grupo muscular
            </label>
            <div className="grid grid-cols-2 gap-2">
              {MUSCLE_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setForm((f) => ({ ...f, target_muscle: opt.value }))}
                  className={`px-3 py-2 rounded-lg border-2 text-sm font-medium transition flex items-center gap-2 ${
                    form.target_muscle === opt.value
                      ? 'border-brand-500 bg-brand-50 text-brand-700'
                      : 'border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  <span>{opt.icon}</span> {opt.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => generateM.mutate()}
            disabled={generateM.isPending}
            className="w-full py-3 bg-gradient-to-r from-brand-600 to-brand-700 hover:from-brand-700 hover:to-brand-900 text-white font-semibold rounded-lg shadow-sm transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Zap className="w-4 h-4" />
            {generateM.isPending ? 'Generando…' : 'Generar rutina Express'}
          </button>

          {generateM.isError && (
            <p className="text-sm text-red-600">{(generateM.error as Error).message}</p>
          )}
        </div>

        {/* ── Resultado Express ── */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <ExpressResult day={result} onReset={() => { setResult(null); generateM.reset() }} />
          ) : (
            <div className="bg-white border border-dashed border-slate-300 rounded-2xl p-12 text-center text-slate-500">
              <Zap className="w-10 h-10 mx-auto text-slate-300 mb-3" />
              <p className="font-medium">Configura tu ventana de tiempo y genera una rutina.</p>
              <p className="text-sm mt-1">Garantizamos ≥ 4 ejercicios ajustados a tu objetivo.</p>
            </div>
          )}

          {/* Plan semanal completo */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-slate-400" />
              <h3 className="font-semibold text-slate-900">Tu plan semanal de gimnasio</h3>
              {weeklyQ.data && (
                <span className="ml-auto text-xs text-slate-400 capitalize">
                  {weeklyQ.data.activity_level} · {weeklyQ.data.goal}
                </span>
              )}
            </div>
            {weeklyQ.isLoading ? (
              <p className="px-5 py-6 text-sm text-slate-500">Cargando plan…</p>
            ) : weeklyQ.data ? (
              <div className="divide-y divide-slate-50">
                {weeklyQ.data.days.map((day, i) => (
                  <WeekDayRow key={i} day={day} />
                ))}
              </div>
            ) : (
              <p className="px-5 py-6 text-sm text-slate-400">No hay plan disponible.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function ExpressResult({ day, onReset }: { day: WorkoutDay; onReset: () => void }) {
  return (
    <div className="bg-white rounded-2xl border border-brand-200 shadow-sm overflow-hidden">
      <div className="bg-gradient-to-r from-brand-600 to-brand-700 px-5 py-4 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-lg">{day.focus}</h3>
            <p className="text-brand-200 text-sm">{day.day_label}</p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-brand-100">
              <Timer className="w-4 h-4" />
              <span className="font-semibold">{day.duration_min} min</span>
            </div>
            <p className="text-xs text-brand-200">{day.exercises.length} ejercicios</p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-slate-50">
        {day.exercises.map((ex, i) => (
          <div key={i} className="px-5 py-4 flex items-start justify-between hover:bg-slate-50">
            <div className="flex items-start gap-3">
              <div className="w-7 h-7 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                {i + 1}
              </div>
              <div>
                <p className="font-semibold text-slate-900">{ex.name}</p>
                <p className="text-xs text-slate-500">{ex.muscle}</p>
              </div>
            </div>
            <div className="text-right shrink-0 ml-4">
              <p className="text-sm font-semibold text-slate-900">{ex.sets} × {ex.reps}</p>
              <p className="text-xs text-slate-400">
                {EQUIPMENT_LABELS[ex.equipment] ?? ex.equipment} · {ex.rest_seconds}s descanso
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="px-5 py-3 bg-slate-50 border-t border-slate-100 flex justify-between items-center">
        <div className="flex items-center gap-1 text-emerald-600 text-sm font-medium">
          <Flame className="w-4 h-4" />
          ~{Math.round(day.duration_min * 6)} kcal estimadas
        </div>
        <button
          onClick={onReset}
          className="flex items-center gap-1 text-sm text-brand-600 hover:text-brand-700 font-medium"
        >
          <RefreshCw className="w-3 h-3" /> Generar otra
        </button>
      </div>
    </div>
  )
}

function WeekDayRow({ day }: { day: WorkoutDay }) {
  const [open, setOpen] = useState(false)
  return (
    <div>
      <button
        onClick={() => !day.rest && setOpen((v) => !v)}
        className={`w-full px-5 py-3 flex items-center justify-between text-left ${
          day.rest ? 'opacity-60 cursor-default' : 'hover:bg-slate-50'
        }`}
      >
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-slate-700 w-16">{day.day_label}</span>
          <span className={`text-sm ${day.rest ? 'text-slate-400 italic' : 'text-slate-900'}`}>
            {day.focus}
          </span>
          {!day.rest && (
            <span className="text-xs text-slate-400">{day.exercises.length} ejercicios · {day.duration_min} min</span>
          )}
        </div>
        {!day.rest && (
          <ChevronRight className={`w-4 h-4 text-slate-400 transition ${open ? 'rotate-90' : ''}`} />
        )}
      </button>
      {open && !day.rest && (
        <div className="px-5 pb-3 space-y-1 bg-slate-50">
          {day.exercises.map((ex, i) => (
            <div key={i} className="flex items-center justify-between py-1.5 border-b border-slate-100 last:border-0">
              <span className="text-sm text-slate-800">{ex.name}</span>
              <span className="text-xs text-slate-500 tabular-nums">
                {ex.sets}×{ex.reps} · {EQUIPMENT_LABELS[ex.equipment] ?? ex.equipment}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
