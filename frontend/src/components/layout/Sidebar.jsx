import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FolderOpen, PlusCircle, Scale,
  Settings, ChevronLeft, ChevronRight, Shield
} from 'lucide-react'
import './Sidebar.css'

const NAV_ITEMS = [
  { to: '/',         icon: LayoutDashboard, label: 'Dashboard'    },
  { to: '/cases',    icon: FolderOpen,      label: 'All Cases'    },
  { to: '/cases/new',icon: PlusCircle,      label: 'New Case'     },
  { to: '/settings', icon: Settings,        label: 'Settings'     },
]

export default function Sidebar({ collapsed, onToggle }) {
  return (
    <aside className={`sidebar${collapsed ? ' sidebar--collapsed' : ''}`}>
      <div className="sidebar__brand">
        <div className="sidebar__logo">
          <Shield size={22} />
        </div>
        {!collapsed && (
          <div className="sidebar__brand-text">
            <span className="sidebar__brand-name">LegalAI</span>
            <span className="sidebar__brand-sub">Government Platform</span>
          </div>
        )}
      </div>

      <nav className="sidebar__nav">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `sidebar__link${isActive ? ' sidebar__link--active' : ''}`
            }
            title={collapsed ? label : undefined}
          >
            <Icon size={18} className="sidebar__icon" />
            {!collapsed && <span className="sidebar__label">{label}</span>}
          </NavLink>
        ))}
      </nav>

      <button className="sidebar__toggle" onClick={onToggle} aria-label="Toggle sidebar">
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  )
}
