import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Utensils, Dumbbell, Flame, Beef, Wheat, Droplet, Clock, ChevronDown, ChevronUp, Bed,
} from 'lucide-react'
import { api, PlannedDay, WorkoutDay } from '../lib/api'
import { storage } from '../lib/storage'

const MEAL_LABELS: Record<string, string> = {
  breakfast: 'Desayuno',
  lunch: 'Almuerzo',
  dinner: 'Cena',
  snack: 'Snack',
}
const MEAL_EMOJI: Record<string, string> = {
  breakfast: '🍳',
  lunch: '🥗',
  dinner: '🍽️',
  snack: '🍎',
}

export default function Plan() {
  const userId = storage.getUserId()!
  const [tab, setTab] = useState<'meals' | 'workout'>('meals')
  const [openDay, setOpenDay] = useState<number>(0)

  const mealQ = useQuery({
    queryKey: ['meal-plan', userId],
    queryFn: () => api.getMealPlan(userId),
  })
  const workoutQ = useQuery({
    queryKey: ['workout-plan', userId],
    queryFn: () => api.getWorkoutPlan(userId),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Mi plan semanal</h2>
        <p className="text-slate-500 text-sm">
          Plan personalizado basado en tu perfil. Lo puedes seguir tal cual o adaptarlo y registrar lo que realmente comas en el diario.
        </p>
      </div>

      {/* Tabs */}
      <div className="inline-flex bg-white rounded-xl border border-slate-200 p-1 shadow-sm">
        <button
          onClick={() => setTab('meals')}
          className={`px-5 py-2 rounded-lg font-medium text-sm transition flex items-center gap-2 ${
            tab === 'meals' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Utensils className="w-4 h-4" />
          Alimentación
        </button>
        <button
          onClick={() => setTab('workout')}
          className={`px-5 py-2 rounded-lg font-medium text-sm transition flex items-center gap-2 ${
            tab === 'workout' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Dumbbell className="w-4 h-4" />
          Entrenamiento
        </button>
      </div>

      {tab === 'meals' ? (
        <MealPlanView
          plan={mealQ.data}
          isLoading={mealQ.isLoading}
          openDay={openDay}
          setOpenDay={setOpenDay}
        />
      ) : (
        <WorkoutPlanView
          plan={workoutQ.data}
          isLoading={workoutQ.isLoading}
          openDay={openDay}
          setOpenDay={setOpenDay}
        />
      )}
    </div>
  )
}

// ==================== MEAL PLAN ====================
function MealPlanView({ plan, isLoading, openDay, setOpenDay }: {
  plan: ReturnType<typeof api.getMealPlan> extends Promise<infer T> ? T | undefined : never
  isLoading: boolean
  openDay: number
  setOpenDay: (n: number) => void
}) {
  if (isLoading) return <p className="text-slate-500">Generando tu plan…</p>
  if (!plan) return null

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-br from-brand-50 to-white border border-brand-200 rounded-2xl p-5">
        <p className="text-sm text-slate-600 mb-3">Tu objetivo nutricional diario:</p>
        <div className="grid grid-cols-4 gap-4">
          <SummaryStat icon={<Flame className="w-4 h-4" />} label="Calorías" value={plan.target_kcal} unit="kcal" color="text-orange-700" />
          <SummaryStat icon={<Beef className="w-4 h-4" />} label="Proteína" value={plan.target_protein_g} unit="g" color="text-red-700" />
          <SummaryStat icon={<Wheat className="w-4 h-4" />} label="Carbs" value={plan.target_carbs_g} unit="g" color="text-amber-700" />
          <SummaryStat icon={<Droplet className="w-4 h-4" />} label="Grasa" value={plan.target_fat_g} unit="g" color="text-emerald-700" />
        </div>
      </div>

      <div className="space-y-2">
        {plan.days.map((day: PlannedDay, idx: number) => (
          <DayCard
            key={day.day_label}
            isOpen={openDay === idx}
            onToggle={() => setOpenDay(openDay === idx ? -1 : idx)}
            header={
              <div className="flex items-center justify-between flex-1">
                <h3 className="font-semibold text-slate-900">{day.day_label}</h3>
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  <span><span className="font-semibold text-slate-700 tabular-nums">{day.total_kcal.toFixed(0)}</span> kcal</span>
                  <span>P{day.total_protein_g.toFixed(0)} · C{day.total_carbs_g.toFixed(0)} · G{day.total_fat_g.toFixed(0)}</span>
                </div>
              </div>
            }
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
              {day.meals.map((meal) => (
                <div key={meal.meal} className="bg-slate-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-sm text-slate-900 flex items-center gap-1">
                      <span>{MEAL_EMOJI[meal.meal]}</span>
                      {MEAL_LABELS[meal.meal]}
                    </h4>
                    <span className="text-xs text-slate-500 tabular-nums">{meal.total_kcal.toFixed(0)} kcal</span>
                  </div>
                  <ul className="space-y-1">
                    {meal.foods.map((f, i) => (
                      <li key={i} className="text-xs text-slate-700 flex items-baseline justify-between gap-2">
                        <span>{f.name}</span>
                        <span className="text-slate-500 tabular-nums shrink-0">{f.grams}g · {f.kcal}kcal</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </DayCard>
        ))}
      </div>
    </div>
  )
}

// ==================== WORKOUT PLAN ====================
function WorkoutPlanView({ plan, isLoading, openDay, setOpenDay }: {
  plan: ReturnType<typeof api.getWorkoutPlan> extends Promise<infer T> ? T | undefined : never
  isLoading: boolean
  openDay: number
  setOpenDay: (n: number) => void
}) {
  if (isLoading) return <p className="text-slate-500">Generando tu rutina…</p>
  if (!plan) return null

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-br from-brand-50 to-white border border-brand-200 rounded-2xl p-5">
        <p className="text-sm text-slate-600">
          Rutina adaptada a tu nivel <span className="font-semibold capitalize">{plan.activity_level.replace('_', ' ')}</span>
          {' '}con objetivo de <span className="font-semibold">{
            plan.goal === 'lose' ? 'pérdida de grasa' : plan.goal === 'gain' ? 'ganancia muscular' : 'mantenimiento'
          }</span>.
        </p>
      </div>

      <div className="space-y-2">
        {plan.days.map((day: WorkoutDay, idx: number) => (
          day.rest ? (
            <div key={day.day_label} className="bg-white rounded-xl border border-slate-200 px-5 py-4 flex items-center gap-3">
              <Bed className="w-5 h-5 text-slate-400" />
              <div>
                <h3 className="font-semibold text-slate-700">{day.day_label}</h3>
                <p className="text-xs text-slate-500">Descanso activo — recuperación</p>
              </div>
            </div>
          ) : (
            <DayCard
              key={day.day_label}
              isOpen={openDay === idx}
              onToggle={() => setOpenDay(openDay === idx ? -1 : idx)}
              header={
                <div className="flex items-center justify-between flex-1">
                  <div>
                    <h3 className="font-semibold text-slate-900">{day.day_label}</h3>
                    <p className="text-xs text-slate-500">{day.focus}</p>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {day.duration_min} min</span>
                    <span>{day.exercises.length} ejercicios</span>
                  </div>
                </div>
              }
            >
              <div className="mt-3 overflow-hidden rounded-lg border border-slate-200">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 text-slate-600 text-xs">
                    <tr>
                      <th className="text-left px-3 py-2 font-medium">Ejercicio</th>
                      <th className="text-left px-3 py-2 font-medium">Músculo</th>
                      <th className="text-center px-3 py-2 font-medium">Series</th>
                      <th className="text-center px-3 py-2 font-medium">Reps</th>
                      <th className="text-center px-3 py-2 font-medium">Descanso</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {day.exercises.map((ex, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="px-3 py-2 font-medium text-slate-900">{ex.name}</td>
                        <td className="px-3 py-2 text-slate-600">{ex.muscle}</td>
                        <td className="px-3 py-2 text-center tabular-nums">{ex.sets}</td>
                        <td className="px-3 py-2 text-center tabular-nums">{ex.reps}</td>
                        <td className="px-3 py-2 text-center text-slate-500 tabular-nums">{ex.rest_seconds}s</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </DayCard>
          )
        ))}
      </div>
    </div>
  )
}

// ==================== shared ====================
function DayCard({ header, isOpen, onToggle, children }: { header: React.ReactNode; isOpen: boolean; onToggle: () => void; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-5 py-3 hover:bg-slate-50 transition text-left"
      >
        {header}
        {isOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>
      {isOpen && <div className="px-5 pb-4">{children}</div>}
    </div>
  )
}

function SummaryStat({ icon, label, value, unit, color }: { icon: React.ReactNode; label: string; value: number; unit: string; color: string }) {
  return (
    <div>
      <p className={`text-xs flex items-center gap-1 ${color}`}>{icon} {label}</p>
      <p className="text-lg font-bold text-slate-900 tabular-nums">{value.toFixed(0)} <span className="text-xs font-normal text-slate-400">{unit}</span></p>
    </div>
  )
}
