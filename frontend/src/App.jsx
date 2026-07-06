import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider } from './context/ThemeContext'
import AppLayout from './components/layout/AppLayout'
import Dashboard from './pages/Dashboard'
import CasesList from './pages/CasesList'
import NewCase from './pages/NewCase'
import CaseDetail from './pages/CaseDetail'
import Settings from './pages/Settings'
import './styles/globals.css'

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/"           element={<Dashboard />} />
            <Route path="/cases"      element={<CasesList />} />
            <Route path="/cases/new"  element={<NewCase />} />
            <Route path="/cases/:id"  element={<CaseDetail />} />
            <Route path="/settings"   element={<Settings />} />
            <Route path="*"           element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--surface-card)',
            color: 'var(--text-primary)',
            border: '1px solid var(--surface-border)',
            fontSize: '14px',
          },
          success: { iconTheme: { primary: 'var(--color-success)', secondary: 'white' } },
          error:   { iconTheme: { primary: 'var(--color-danger)',  secondary: 'white' } },
        }}
      />
    </ThemeProvider>
  )
}
