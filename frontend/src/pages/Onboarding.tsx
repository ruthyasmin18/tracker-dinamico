import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Activity, ChevronRight, Sparkles, LogIn, UserPlus } from 'lucide-react'
import { api, ActivityLevel, Gender, GoalKind } from '../lib/api'
import { storage } from '../lib/storage'

type Tab = 'register' | 'login'

// ---------- Register ----------
function RegisterForm() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    age: 24,
    weight_kg: 75,
    height_cm: 175,
    gender: 'male' as Gender,
    activity_level: 'moderate' as ActivityLevel,
    goal: 'maintain' as GoalKind,
  })

  const mutation = useMutation({
    mutationFn: () => api.register(form),
    onSuccess: (data) => {
      storage.setSession(data.user_id, data.access_token)
      navigate('/plan')
    },
  })

  const set = <K extends keyof typeof form>(key: K, value: typeof form[K]) =>
    setForm((f) => ({ ...f, [key]: value }))

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); mutation.mutate() }}
      className="space-y-5"
    >
      <div className="my-4 p-4 bg-brand-50 border border-brand-100 rounded-lg flex items-start gap-3">
        <Sparkles className="w-5 h-5 text-brand-600 mt-0.5 shrink-0" />
        <p className="text-sm text-slate-700">
          Calcularemos tus objetivos usando la fórmula <span className="font-semibold">Mifflin-St Jeor</span>.
          Tu contraseña se almacena con <span className="font-semibold">bcrypt</span> — nunca en texto plano.
        </p>
      </div>

      {/* Credenciales */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
        <input
          type="email"
          required
          placeholder="tu@email.com"
          value={form.email}
          onChange={(e) => set('email', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Contraseña</label>
        <input
          type="password"
          required
          minLength={8}
          placeholder="Mínimo 8 caracteres"
          value={form.password}
          onChange={(e) => set('password', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        {form.password.length > 0 && (
          <div className="mt-1.5 flex gap-3 text-xs flex-wrap">
            <span className={/[A-Z]/.test(form.password) ? 'text-emerald-600' : 'text-slate-400'}>
              {/[A-Z]/.test(form.password) ? '✓' : '○'} Mayúscula
            </span>
            <span className={/\d/.test(form.password) ? 'text-emerald-600' : 'text-slate-400'}>
              {/\d/.test(form.password) ? '✓' : '○'} Número
            </span>
            <span className={/[!@#$%^&*()\-_=+\[\]{};:'",.<>/?\\|`~]/.test(form.password) ? 'text-emerald-600' : 'text-slate-400'}>
              {/[!@#$%^&*()\-_=+\[\]{};:'",.<>/?\\|`~]/.test(form.password) ? '✓' : '○'} Especial
            </span>
            <span className={form.password.length >= 8 ? 'text-emerald-600' : 'text-slate-400'}>
              {form.password.length >= 8 ? '✓' : '○'} 8+ caracteres
            </span>
          </div>
        )}
      </div>

      {/* Perfil */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Nombre</label>
        <input
          type="text"
          required
          value={form.name}
          onChange={(e) => set('name', e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
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
          {(mutation.error as Error).message}
        </div>
      )}

      <button
        type="submit"
        disabled={mutation.isPending}
        className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-lg shadow-sm transition flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {mutation.isPending ? 'Registrando…' : (
          <>
            <UserPlus className="w-4 h-4" />
            Crear cuenta y calcular mi plan
          </>
        )}
      </button>
    </form>
  )
}

// ---------- Login ----------
function LoginForm() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const mutation = useMutation({
    mutationFn: () => api.login({ email, password }),
    onSuccess: (data) => {
      storage.setSession(data.user_id, data.access_token)
      navigate('/plan')
    },
  })

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); mutation.mutate() }}
      className="space-y-5 mt-6"
    >
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
        <input
          type="email"
          required
          placeholder="tu@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Contraseña</label>
        <input
          type="password"
          required
          placeholder="Tu contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      {mutation.isError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {(mutation.error as Error).message}
        </div>
      )}

      <button
        type="submit"
        disabled={mutation.isPending}
        className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-lg shadow-sm transition flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {mutation.isPending ? 'Ingresando…' : (
          <>
            <LogIn className="w-4 h-4" />
            Iniciar sesión
            <ChevronRight className="w-4 h-4" />
          </>
        )}
      </button>

      <p className="text-xs text-center text-slate-500">
        La sesión dura 60 días — no necesitarás volver a ingresar tus credenciales.
      </p>
    </form>
  )
}

// ---------- Main ----------
export default function Onboarding() {
  const [tab, setTab] = useState<Tab>('register')

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-2xl w-full p-8">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Tracker Dinámico</h1>
            <p className="text-sm text-slate-500">Tu copiloto de salud inteligente</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex rounded-lg border border-slate-200 p-1 mb-2 bg-slate-50">
          <button
            onClick={() => setTab('register')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition flex items-center justify-center gap-2 ${
              tab === 'register'
                ? 'bg-white text-brand-700 shadow-sm border border-slate-200'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <UserPlus className="w-4 h-4" /> Nueva cuenta
          </button>
          <button
            onClick={() => setTab('login')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition flex items-center justify-center gap-2 ${
              tab === 'login'
                ? 'bg-white text-brand-700 shadow-sm border border-slate-200'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <LogIn className="w-4 h-4" /> Ya tengo cuenta
          </button>
        </div>

        {tab === 'register' ? <RegisterForm /> : <LoginForm />}
      </div>
    </div>
  )
}
