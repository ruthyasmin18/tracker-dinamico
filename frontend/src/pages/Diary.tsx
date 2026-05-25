import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Search, Plus, Trash2, Utensils, X, Flame, Beef, Wheat, Droplet, Zap, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api, AutoRecalcResponse, FoodSearchResult, Meal } from '../lib/api'
import { storage } from '../lib/storage'
import MacroBar from '../components/MacroBar'

const MEAL_LABELS: Record<Meal, string> = {
  breakfast: 'Desayuno',
  lunch: 'Almuerzo',
  dinner: 'Cena',
  snack: 'Snack',
}
const MEAL_ORDER: Meal[] = ['breakfast', 'lunch', 'dinner', 'snack']

function todayIso(): string {
  return new Date().toISOString().split('T')[0]
}

export default function Diary() {
  const userId = storage.getUserId()!
  const qc = useQueryClient()
  const navigate = useNavigate()                          // ← siempre antes de cualquier return
  const [date, setDate] = useState(todayIso())
  const [showSearch, setShowSearch] = useState(false)
  const [selectedMeal, setSelectedMeal] = useState<Meal>('breakfast')

  const diaryQ = useQuery({
    queryKey: ['diary', userId, date],
    queryFn: () => api.getDiary(userId, date),
  })

  const deleteM = useMutation({
    mutationFn: (id: string) => api.deleteEntry(userId, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['diary', userId, date] }),
  })

  if (diaryQ.isLoading) {
    return <div className="text-center text-slate-500 py-12">Cargando diario…</div>
  }
  if (diaryQ.isError) {
    return <div className="text-red-600">Error: {(diaryQ.error as Error).message}</div>
  }

  const data = diaryQ.data!
  const grouped: Record<Meal, typeof data.entries> = {
    breakfast: [], lunch: [], dinner: [], snack: [],
  }
  data.entries.forEach((e) => grouped[e.meal as Meal]?.push(e))

  return (
    <div className="space-y-6">
      {/* Banner F4: auto-recálculo desde diario */}
      {data.recalc_suggestion?.adjusted && (
        <RecalcBanner suggestion={data.recalc_suggestion} onDetails={() => navigate('/recalc')} />
      )}

      {/* Header */}
      <div className="flex items-end justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Diario alimenticio</h2>
          <p className="text-slate-500 text-sm">Registra lo que comes y mira tu progreso en tiempo real.</p>
        </div>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="px-3 py-2 border border-slate-300 rounded-lg bg-white"
        />
      </div>

      {/* Macros del día */}
      {data.goal && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
            <StatCard
              icon={<Flame className="w-5 h-5" />}
              label="Calorías"
              current={data.totals.kcal}
              target={data.goal.kcal}
              unit="kcal"
              color="text-orange-600 bg-orange-50"
            />
            <StatCard
              icon={<Beef className="w-5 h-5" />}
              label="Proteína"
              current={data.totals.protein_g}
              target={data.goal.protein_g}
              unit="g"
              color="text-red-600 bg-red-50"
            />
            <StatCard
              icon={<Wheat className="w-5 h-5" />}
              label="Carbohidratos"
              current={data.totals.carbs_g}
              target={data.goal.carbs_g}
              unit="g"
              color="text-amber-600 bg-amber-50"
            />
            <StatCard
              icon={<Droplet className="w-5 h-5" />}
              label="Grasa"
              current={data.totals.fat_g}
              target={data.goal.fat_g}
              unit="g"
              color="text-emerald-600 bg-emerald-50"
            />
          </div>
          <div className="space-y-3">
            <MacroBar label="Calorías" current={data.totals.kcal} target={data.goal.kcal} unit="kcal" color="bg-orange-500" />
            <MacroBar label="Proteína" current={data.totals.protein_g} target={data.goal.protein_g} color="bg-red-500" />
            <MacroBar label="Carbohidratos" current={data.totals.carbs_g} target={data.goal.carbs_g} color="bg-amber-500" />
            <MacroBar label="Grasa" current={data.totals.fat_g} target={data.goal.fat_g} color="bg-emerald-500" />
          </div>
        </div>
      )}

      {/* Comidas */}
      <div className="space-y-4">
        {MEAL_ORDER.map((meal) => (
          <div key={meal} className="bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Utensils className="w-4 h-4 text-slate-400" />
                <h3 className="font-semibold text-slate-900">{MEAL_LABELS[meal]}</h3>
                <span className="text-xs text-slate-400">
                  {grouped[meal].length} {grouped[meal].length === 1 ? 'item' : 'items'}
                </span>
              </div>
              <button
                onClick={() => { setSelectedMeal(meal); setShowSearch(true) }}
                className="text-sm text-brand-600 hover:text-brand-700 font-medium flex items-center gap-1"
              >
                <Plus className="w-4 h-4" /> Añadir
              </button>
            </div>
            <div className="divide-y divide-slate-50">
              {grouped[meal].length === 0 ? (
                <p className="px-5 py-4 text-sm text-slate-400 italic">Sin registros — añade lo que comiste.</p>
              ) : (
                grouped[meal].map((entry) => (
                  <div key={entry.id} className="px-5 py-3 flex items-center justify-between hover:bg-slate-50">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-900 truncate">{entry.food_name}</p>
                      <p className="text-xs text-slate-500">
                        {entry.grams.toFixed(0)} g · {entry.kcal.toFixed(0)} kcal · P{entry.protein_g.toFixed(0)} / C{entry.carbs_g.toFixed(0)} / G{entry.fat_g.toFixed(0)}
                      </p>
                    </div>
                    <button
                      onClick={() => deleteM.mutate(entry.id)}
                      className="ml-3 p-2 text-slate-400 hover:text-red-600 transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>

      {showSearch && (
        <SearchModal
          userId={userId}
          meal={selectedMeal}
          date={date}
          onClose={() => setShowSearch(false)}
          onSaved={() => {
            setShowSearch(false)
            qc.invalidateQueries({ queryKey: ['diary', userId, date] })
          }}
        />
      )}
    </div>
  )
}

function StatCard({
  icon, label, current, target, unit, color,
}: { icon: React.ReactNode; label: string; current: number; target: number; unit: string; color: string }) {
  const remaining = target - current
  return (
    <div className="flex gap-3 items-start">
      <div className={`p-2 rounded-lg ${color}`}>{icon}</div>
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-lg font-bold text-slate-900 tabular-nums">
          {current.toFixed(0)} <span className="text-xs font-normal text-slate-400">/ {target.toFixed(0)} {unit}</span>
        </p>
        <p className={`text-xs ${remaining >= 0 ? 'text-slate-400' : 'text-red-600'}`}>
          {remaining >= 0 ? `${remaining.toFixed(0)} ${unit} restantes` : `+${Math.abs(remaining).toFixed(0)} de exceso`}
        </p>
      </div>
    </div>
  )
}

function SearchModal({
  userId, meal, date, onClose, onSaved,
}: { userId: string; meal: Meal; date: string; onClose: () => void; onSaved: () => void }) {
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<FoodSearchResult | null>(null)
  const [grams, setGrams] = useState(100)

  const searchQ = useQuery({
    queryKey: ['search', query],
    queryFn: () => api.searchFoods(query),
    enabled: query.length >= 2,
  })

  const addM = useMutation({
    mutationFn: () => api.createEntry(userId, {
      food_name: selected!.name,
      off_id: selected!.off_id,
      grams,
      kcal_per_100g: selected!.kcal_per_100g,
      protein_per_100g: selected!.protein_per_100g,
      carbs_per_100g: selected!.carbs_per_100g,
      fat_per_100g: selected!.fat_per_100g,
      meal,
      consumed_on: date,
    }),
    onSuccess: onSaved,
  })

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-20">
      <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <h3 className="font-semibold text-slate-900">Añadir a {MEAL_LABELS[meal]}</h3>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        {!selected ? (
          <>
            <div className="p-4 border-b border-slate-100">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  autoFocus
                  placeholder='Buscar alimentos (ej. "huevo", "arroz", "pollo a la brasa")…'
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <p className="text-xs text-slate-400 mt-2 px-1">
                🇵🇪 Búsqueda híbrida: biblioteca peruana/latinoamericana + OpenFoodFacts
              </p>
            </div>
            <div className="flex-1 overflow-y-auto px-2 py-2">
              {searchQ.isLoading && <p className="text-center text-sm text-slate-500 py-6">Buscando…</p>}
              {searchQ.isError && <p className="text-center text-sm text-red-600 py-6">Error de búsqueda</p>}
              {searchQ.data?.length === 0 && (
                <p className="text-center text-sm text-slate-500 py-6">Sin resultados — intenta otra palabra.</p>
              )}
              {searchQ.data?.map((food, i) => {
                const isLocal = food.brand === 'Biblioteca local'
                return (
                  <button
                    key={`${food.off_id ?? food.name}-${i}`}
                    onClick={() => setSelected(food)}
                    className="w-full text-left px-3 py-3 hover:bg-slate-50 rounded-lg transition"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900 flex-1">{food.name}</span>
                      {isLocal ? (
                        <span className="shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                          🇵🇪 Local
                        </span>
                      ) : food.brand ? (
                        <span className="shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-sky-100 text-sky-700">
                          {food.brand}
                        </span>
                      ) : null}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {food.kcal_per_100g} kcal · P{food.protein_per_100g}g / C{food.carbs_per_100g}g / G{food.fat_per_100g}g · por 100 g
                    </div>
                  </button>
                )
              })}
            </div>
          </>
        ) : (
          <div className="p-6">
            <p className="font-semibold text-slate-900">{selected.name}</p>
            {selected.brand && <p className="text-sm text-slate-500">{selected.brand}</p>}
            <p className="text-xs text-slate-500 mt-1">
              Base: {selected.kcal_per_100g} kcal/100g · P{selected.protein_per_100g} / C{selected.carbs_per_100g} / G{selected.fat_per_100g}
            </p>

            <div className="my-6">
              <label className="block text-sm font-medium text-slate-700 mb-1">Gramos consumidos</label>
              <input
                type="number"
                min="1" max="5000"
                value={grams}
                onChange={(e) => setGrams(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-4 gap-3 p-4 bg-slate-50 rounded-lg mb-6">
              <Stat label="kcal" value={(selected.kcal_per_100g * grams / 100).toFixed(0)} />
              <Stat label="P (g)" value={(selected.protein_per_100g * grams / 100).toFixed(1)} />
              <Stat label="C (g)" value={(selected.carbs_per_100g * grams / 100).toFixed(1)} />
              <Stat label="G (g)" value={(selected.fat_per_100g * grams / 100).toFixed(1)} />
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setSelected(null)}
                className="flex-1 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50"
              >
                Volver
              </button>
              <button
                onClick={() => addM.mutate()}
                disabled={addM.isPending || grams <= 0}
                className="flex-1 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"
              >
                {addM.isPending ? 'Guardando…' : 'Añadir'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <div className="text-lg font-bold text-slate-900 tabular-nums">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  )
}

// ---------- Banner de recálculo automático (F4 ↔ F3) ----------
function RecalcBanner({ suggestion, onDetails }: { suggestion: AutoRecalcResponse; onDetails: () => void }) {
  const [dismissed, setDismissed] = useState(false)
  if (dismissed) return null

  const today = suggestion.days[0]
  const delta = today ? today.adjusted.kcal - today.original.kcal : 0
  const isExcess = delta < 0

  return (
    <div className={`rounded-2xl border p-4 flex items-start gap-4 shadow-sm ${
      isExcess ? 'bg-amber-50 border-amber-200' : 'bg-sky-50 border-sky-200'
    }`}>
      <div className={`p-2 rounded-lg shrink-0 ${isExcess ? 'bg-amber-100' : 'bg-sky-100'}`}>
        <Zap className={`w-5 h-5 ${isExcess ? 'text-amber-700' : 'text-sky-700'}`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-slate-900 text-sm">Motor de recálculo activado automáticamente</p>
        <p className="text-sm text-slate-600 mt-0.5">{suggestion.message}</p>
        {today && (
          <p className="text-xs text-slate-500 mt-1 tabular-nums">
            Ajuste de hoy: <span className="font-medium">{today.original.kcal.toFixed(0)} kcal</span>
            {' → '}
            <span className={`font-semibold ${isExcess ? 'text-amber-700' : 'text-sky-700'}`}>
              {today.adjusted.kcal.toFixed(0)} kcal
            </span>
          </p>
        )}
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={onDetails}
          className="text-xs font-medium text-brand-600 hover:text-brand-700 flex items-center gap-1"
        >
          Ver detalles <ArrowRight className="w-3 h-3" />
        </button>
        <button onClick={() => setDismissed(true)} className="text-slate-400 hover:text-slate-600 ml-1">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
