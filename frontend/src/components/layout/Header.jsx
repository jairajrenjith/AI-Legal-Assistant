import { Sun, Moon, Bell } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import './Header.css'

export default function Header({ title }) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="header">
      <div className="header__left">
        <h1 className="header__title">{title}</h1>
      </div>
      <div className="header__actions">
        <button
          className="header__btn"
          onClick={toggleTheme}
          aria-label="Toggle theme"
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
        </button>
      </div>
    </header>
  )
}
