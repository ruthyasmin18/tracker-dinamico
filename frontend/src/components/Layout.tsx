import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Activity, BookOpen, Sparkles, User, LogOut, Calendar } from 'lucide-react'
import { storage } from '../lib/storage'

export default function Layout() {
  const navigate = useNavigate()

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
      isActive
        ? 'bg-brand-600 text-white shadow-sm'
        : 'text-slate-600 hover:bg-slate-100'
    }`

  const handleLogout = () => {
    storage.clear()
    navigate('/onboarding')
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white/80 backdrop-blur border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-slate-900 leading-none">Tracker Dinámico</h1>
              <p className="text-xs text-slate-500">Nutrición + Gimnasio adaptativo</p>
            </div>
          </div>
          <nav className="flex items-center gap-2">
            <NavLink to="/plan" className={linkClass}>
              <Calendar className="w-4 h-4" /> Mi Plan
            </NavLink>
            <NavLink to="/diary" className={linkClass}>
              <BookOpen className="w-4 h-4" /> Diario
            </NavLink>
            <NavLink to="/recalc" className={linkClass}>
              <Sparkles className="w-4 h-4" /> Recálculo
            </NavLink>
            <NavLink to="/profile" className={linkClass}>
              <User className="w-4 h-4" /> Perfil
            </NavLink>
            <button
              onClick={handleLogout}
              className="ml-2 p-2 text-slate-400 hover:text-slate-700 transition"
              title="Cerrar sesión"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-6xl mx-auto px-6 py-8 w-full">
        <Outlet />
      </main>
      <footer className="text-center text-xs text-slate-400 py-4">
        Taller 4 · Ciclo de Vida del Producto Ágil
      </footer>
    </div>
  )
}
