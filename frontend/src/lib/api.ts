// Cliente HTTP del backend
import { storage } from './storage'

const BASE = '/api'

type RequestOpts = RequestInit & { json?: unknown }

async function request<T>(path: string, opts: RequestOpts = {}): Promise<T> {
  const { json, headers, ...rest } = opts
  const token = storage.getToken()
  const res = await fetch(`${BASE}${path}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${detail}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// ===== Types =====
export type Gender = 'male' | 'female'
export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
export type GoalKind = 'lose' | 'maintain' | 'gain'
export type Meal = 'breakfast' | 'lunch' | 'dinner' | 'snack'

// F1 — Auth
export interface TokenOut {
  access_token: string
  token_type: string
  user_id: string
}

// F4 — Auto-recálculo
export interface AutoRecalcResponse {
  adjusted: boolean
  message: string
  days: DayPlan[]
  log_id?: string
}

export interface User {
  id: string
  name: string
  email?: string
  age: number
  weight_kg: number
  height_cm: number
  gender: string
  activity_level: string
  goal: string
  created_at: string
}

export interface NutritionGoal {
  id: string
  user_id: string
  kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
  bmr: number
  tdee: number
  formula: string
  created_at: string
}

export interface FoodSearchResult {
  off_id: string | null
  name: string
  brand: string | null
  kcal_per_100g: number
  protein_per_100g: number
  carbs_per_100g: number
  fat_per_100g: number
}

export interface FoodEntry {
  id: string
  user_id: string
  food_name: string
  off_id: string | null
  grams: number
  kcal_per_100g: number
  protein_per_100g: number
  carbs_per_100g: number
  fat_per_100g: number
  meal: string
  consumed_on: string
  source: string
  created_at: string
  kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface DiarySummary {
  consumed_on: string
  entries: FoodEntry[]
  totals: { kcal: number; protein_g: number; carbs_g: number; fat_g: number }
  goal: NutritionGoal | null
  remaining: { kcal: number; protein_g: number; carbs_g: number; fat_g: number }
  recalc_suggestion: AutoRecalcResponse | null
}

export interface MacroPlan {
  kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

export interface DayPlan {
  date: string
  original: MacroPlan
  adjusted: MacroPlan
  note: string
}

export interface RecalcResponse {
  message: string
  days: DayPlan[]
  log_id: string
}

// ===== Plans =====
export interface PlannedFood {
  name: string
  grams: number
  kcal: number
  protein_g: number
  carbs_g: number
  fat_g: number
  kcal_per_100g: number
  protein_per_100g: number
  carbs_per_100g: number
  fat_per_100g: number
}
export interface PlannedMeal {
  meal: string
  foods: PlannedFood[]
  total_kcal: number
  total_protein_g: number
  total_carbs_g: number
  total_fat_g: number
}
export interface PlannedDay {
  day_label: string
  meals: PlannedMeal[]
  total_kcal: number
  total_protein_g: number
  total_carbs_g: number
  total_fat_g: number
}
export interface MealPlan {
  target_kcal: number
  target_protein_g: number
  target_carbs_g: number
  target_fat_g: number
  days: PlannedDay[]
}

export interface Exercise {
  name: string
  muscle: string
  sets: number
  reps: string
  rest_seconds: number
  equipment: string
}
export interface WorkoutDay {
  day_label: string
  focus: string
  duration_min: number
  exercises: Exercise[]
  rest: boolean
}
export interface WorkoutPlan {
  activity_level: string
  goal: string
  days: WorkoutDay[]
}

// ===== F5 — Rutinas Express =====
export interface ExpressRoutineRequest {
  available_time_min: number
  equipment: 'bodyweight' | 'dumbbell' | 'full'
  target_muscle: 'all' | 'chest' | 'back' | 'legs' | 'arms' | 'shoulders' | 'core'
  goal: GoalKind
}

// ===== F6 — Dashboard =====
export interface DailyStats {
  date: string
  kcal_consumed: number
  kcal_goal: number
  protein_g: number
  carbs_g: number
  fat_g: number
  adherence_pct: number
}

export interface WeeklyDashboard {
  user_id: string
  period_start: string
  period_end: string
  adherence_pct: number
  kcal_promedio: number
  kcal_objetivo: number
  racha_actual: number
  dias_con_datos: number
  macro_avg: { protein_g: number; carbs_g: number; fat_g: number }
  daily_stats: DailyStats[]
}

export interface RecalcLog {
  id: string
  user_id: string
  event_type: string
  event_description: string
  kcal_delta: number
  target_date: string
  original_plan: Record<string, number>
  adjusted_plan: { days: { date: string; adjusted: Record<string, number> }[] }
  propagated_days: number
  message: string
  created_at: string
}

// ===== Calls =====
export const api = {
  // F1 — Auth
  register: (payload: {
    name: string
    email: string
    password: string
    age: number
    weight_kg: number
    height_cm: number
    gender: Gender
    activity_level: ActivityLevel
    goal: GoalKind
  }) => request<TokenOut>('/auth/register', { method: 'POST', json: payload }),

  login: (payload: { email: string; password: string }) =>
    request<TokenOut>('/auth/login', { method: 'POST', json: payload }),

  createUser: (payload: {
    name: string
    age: number
    weight_kg: number
    height_cm: number
    gender: Gender
    activity_level: ActivityLevel
    goal: GoalKind
  }) => request<User>('/users', { method: 'POST', json: payload }),

  getUser: (id: string) => request<User>(`/users/${id}`),

  getGoal: (userId: string) => request<NutritionGoal>(`/users/${userId}/goal`),

  recalculateGoal: (userId: string) =>
    request<NutritionGoal>(`/users/${userId}/goal/recalculate`, { method: 'POST' }),

  searchFoods: (q: string) =>
    request<FoodSearchResult[]>(`/foods/search?q=${encodeURIComponent(q)}`),

  getDiary: (userId: string, on?: string) =>
    request<DiarySummary>(`/users/${userId}/diary${on ? `?on=${on}` : ''}`),

  createEntry: (userId: string, payload: {
    food_name: string
    off_id?: string | null
    grams: number
    kcal_per_100g: number
    protein_per_100g: number
    carbs_per_100g: number
    fat_per_100g: number
    meal: Meal
    consumed_on: string
    source?: string
  }) => request<FoodEntry>(`/users/${userId}/diary`, { method: 'POST', json: payload }),

  deleteEntry: (userId: string, entryId: string) =>
    request<void>(`/users/${userId}/diary/${entryId}`, { method: 'DELETE' }),

  reportEvent: (payload: {
    user_id: string
    event_type: string
    event_description: string
    kcal_delta: number
    target_date: string
  }) => request<RecalcResponse>('/recalc/event', { method: 'POST', json: payload }),

  getLogs: (userId: string) => request<RecalcLog[]>(`/recalc/users/${userId}/logs`),

  autoRecalc: (userId: string, targetDate: string) =>
    request<AutoRecalcResponse>('/recalc/auto', {
      method: 'POST',
      json: { user_id: userId, target_date: targetDate },
    }),

  logout: () => request<void>('/auth/logout', { method: 'POST' }),

  getMealPlan: (userId: string) => request<MealPlan>(`/users/${userId}/meal-plan`),

  getWorkoutPlan: (userId: string) => request<WorkoutPlan>(`/users/${userId}/workout-plan`),

  // F5 — Rutinas Express
  generateExpressRoutine: (payload: ExpressRoutineRequest) =>
    request<WorkoutDay>('/routines/quick', { method: 'POST', json: payload }),

  // F6 — Dashboard semanal
  getWeeklyDashboard: (userId: string) =>
    request<WeeklyDashboard>(`/users/${userId}/dashboard/weekly`),
}
