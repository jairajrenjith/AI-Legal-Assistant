import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import './AppLayout.css'

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/cases': 'All Cases',
  '/cases/new': 'New Case',
  '/settings': 'Settings',
}

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()

  const title =
    PAGE_TITLES[location.pathname] ||
    (location.pathname.startsWith('/cases/') ? 'Case Details' : 'Legal Assistant')

  return (
    <div className={`app-layout${collapsed ? ' app-layout--collapsed' : ''}`}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />
      <div className="app-layout__main">
        <Header title={title} />
        <main className="app-layout__content">
          <div className="app-layout__inner animate-fadeIn">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
