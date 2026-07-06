import { useState, useEffect } from 'react'
import { Sun, Moon, Key, Building } from 'lucide-react'
import { settingsApi } from '../services/api'
import { Card, CardHeader, CardTitle, CardBody, Button, Alert } from '../components/common/Common'
import { useTheme } from '../context/ThemeContext'
import toast from 'react-hot-toast'
import './Settings.css'

export default function Settings() {
  const { theme, toggleTheme } = useTheme()
  const [apiKey, setApiKey] = useState('')
  const [orgName, setOrgName] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    settingsApi.getAll().then((r) => {
      const map = {}
      r.data.forEach((s) => { map[s.key] = s.value })
      setApiKey(map.openai_api_key || '')
      setOrgName(map.organization_name || 'Government Legal Services')
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await Promise.all([
        settingsApi.set('openai_api_key', apiKey),
        settingsApi.set('organization_name', orgName),
      ])
      toast.success('Settings saved.')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="settings-page">
      <div className="settings-page__header">
        <h1 className="settings-page__title">Settings</h1>
        <p className="settings-page__sub">Configure your legal assistant platform.</p>
      </div>

      {/* Theme */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="settings-row">
            <div className="settings-row__info">
              <span className="settings-row__label">Theme</span>
              <span className="settings-row__desc">Switch between light and dark mode.</span>
            </div>
            <div className="theme-toggle-group">
              <button
                className={`theme-btn${theme === 'light' ? ' theme-btn--active' : ''}`}
                onClick={() => theme !== 'light' && toggleTheme()}
              >
                <Sun size={15} /> Light
              </button>
              <button
                className={`theme-btn${theme === 'dark' ? ' theme-btn--active' : ''}`}
                onClick={() => theme !== 'dark' && toggleTheme()}
              >
                <Moon size={15} /> Dark
              </button>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* API & Organization */}
      <Card>
        <CardHeader><CardTitle>AI & Platform Configuration</CardTitle></CardHeader>
        <CardBody>
          <Alert type="info" style={{ marginBottom: 'var(--space-5)' }}>
            An OpenAI API key enables advanced AI classification, law identification, and case analysis.
            Without it, the platform uses a built-in rule-based engine which is fully functional.
          </Alert>

          <div className="form-group">
            <label className="form-label" htmlFor="api-key">
              <Key size={14} style={{ display: 'inline', marginRight: 6 }} />
              OpenAI API Key
            </label>
            <input
              id="api-key"
              type="password"
              className="form-input"
              placeholder="sk-…"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <span className="form-hint">Your key is stored locally and never shared.</span>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="org-name">
              <Building size={14} style={{ display: 'inline', marginRight: 6 }} />
              Organization Name
            </label>
            <input
              id="org-name"
              type="text"
              className="form-input"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              maxLength={200}
            />
            <span className="form-hint">Appears in generated documents.</span>
          </div>

          <div className="settings-page__save">
            <Button onClick={handleSave} loading={saving}>{saving ? 'Saving…' : 'Save Settings'}</Button>
          </div>
        </CardBody>
      </Card>

      {/* About */}
      <Card>
        <CardHeader><CardTitle>About</CardTitle></CardHeader>
        <CardBody>
          <div className="about-grid">
            {[
              ['Platform', 'AI Legal Assistant for Government'],
              ['Version', '1.0.0'],
              ['Legal Domains', 'Criminal, Property, Family, Consumer, Labor, Cyber, Administrative'],
              ['AI Engine', 'OpenAI GPT-4o-mini + Hybrid Rule Engine'],
              ['Database', 'SQLite (upgradeable to PostgreSQL)'],
            ].map(([k, v]) => (
              <div key={k} className="about-row">
                <span className="about-row__key">{k}</span>
                <span className="about-row__val">{v}</span>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
