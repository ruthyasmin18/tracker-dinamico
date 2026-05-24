import { Navigate, Route, Routes } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Layout from './components/Layout'
import Onboarding from './pages/Onboarding'
import Diary from './pages/Diary'
import Recalc from './pages/Recalc'
import Profile from './pages/Profile'
import Plan from './pages/Plan'
import { storage } from './lib/storage'

function RequireUser({ children }: { children: React.ReactNode }) {
  const userId = storage.getUserId()
  if (!userId) return <Navigate to="/onboarding" replace />
  return <>{children}</>
}

export default function App() {
  const [ready, setReady] = useState(false)
  useEffect(() => setReady(true), [])
  if (!ready) return null

  return (
    <Routes>
      <Route path="/onboarding" element={<Onboarding />} />
      <Route
        element={
          <RequireUser>
            <Layout />
          </RequireUser>
        }
      >
        <Route path="/" element={<Navigate to="/plan" replace />} />
        <Route path="/plan" element={<Plan />} />
        <Route path="/diary" element={<Diary />} />
        <Route path="/recalc" element={<Recalc />} />
        <Route path="/profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/plan" replace />} />
    </Routes>
  )
}
