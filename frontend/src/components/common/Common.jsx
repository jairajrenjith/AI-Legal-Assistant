import './Common.css'

/* ─── Card ──────────────────────────────────────────────────── */
export function Card({ children, className = '', onClick }) {
  return (
    <div className={`card ${className}`} onClick={onClick} role={onClick ? 'button' : undefined}>
      {children}
    </div>
  )
}

export function CardHeader({ children, action }) {
  return (
    <div className="card__header">
      <div className="card__header-content">{children}</div>
      {action && <div className="card__header-action">{action}</div>}
    </div>
  )
}

export function CardTitle({ children }) {
  return <h2 className="card__title">{children}</h2>
}

export function CardBody({ children }) {
  return <div className="card__body">{children}</div>
}

/* ─── Badge ─────────────────────────────────────────────────── */
const BADGE_VARIANTS = {
  default:    'badge--default',
  primary:    'badge--primary',
  success:    'badge--success',
  warning:    'badge--warning',
  danger:     'badge--danger',
  info:       'badge--info',
  gray:       'badge--gray',
  // status shorthands
  draft:      'badge--gray',
  in_progress:'badge--info',
  completed:  'badge--success',
  archived:   'badge--default',
  // evidence
  pending:    'badge--warning',
  collected:  'badge--success',
  unavailable:'badge--danger',
  // priority
  high:       'badge--danger',
  medium:     'badge--warning',
  low:        'badge--gray',
}

export function Badge({ children, variant = 'default' }) {
  const cls = BADGE_VARIANTS[variant] || BADGE_VARIANTS.default
  return <span className={`badge ${cls}`}>{children}</span>
}

/* ─── Button ────────────────────────────────────────────────── */
export function Button({
  children, onClick, variant = 'primary', size = 'md',
  disabled, loading, icon, type = 'button', className = '',
}) {
  return (
    <button
      type={type}
      className={`btn btn--${variant} btn--${size} ${className} ${loading ? 'btn--loading' : ''}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? (
        <span className="btn__spinner" aria-hidden="true" />
      ) : icon ? (
        <span className="btn__icon">{icon}</span>
      ) : null}
      {children}
    </button>
  )
}

/* ─── Spinner ───────────────────────────────────────────────── */
export function Spinner({ size = 24, className = '' }) {
  return (
    <div
      className={`spinner ${className}`}
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  )
}

export function PageSpinner({ message = 'Loading...' }) {
  return (
    <div className="page-spinner">
      <Spinner size={40} />
      <p className="page-spinner__text">{message}</p>
    </div>
  )
}

/* ─── EmptyState ────────────────────────────────────────────── */
export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state__icon">{icon}</div>}
      <h3 className="empty-state__title">{title}</h3>
      {description && <p className="empty-state__desc">{description}</p>}
      {action && <div className="empty-state__action">{action}</div>}
    </div>
  )
}

/* ─── ScoreBar ──────────────────────────────────────────────── */
export function ScoreBar({ label, score, explanation, colorClass }) {
  const pct = Math.min(Math.max(score || 0, 0), 100)
  const auto = pct >= 70 ? 'score-bar--high' : pct >= 40 ? 'score-bar--medium' : 'score-bar--low'
  return (
    <div className="score-bar">
      <div className="score-bar__header">
        <span className="score-bar__label">{label}</span>
        <span className="score-bar__value">{pct.toFixed(1)}%</span>
      </div>
      <div className="score-bar__track">
        <div
          className={`score-bar__fill ${colorClass || auto}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {explanation && <p className="score-bar__explanation">{explanation}</p>}
    </div>
  )
}

/* ─── Alert ─────────────────────────────────────────────────── */
export function Alert({ type = 'info', children }) {
  return <div className={`alert alert--${type}`}>{children}</div>
}

/* ─── Section Header ────────────────────────────────────────── */
export function SectionHeader({ icon, title, subtitle, action }) {
  return (
    <div className="section-header">
      <div className="section-header__left">
        {icon && <span className="section-header__icon">{icon}</span>}
        <div>
          <h2 className="section-header__title">{title}</h2>
          {subtitle && <p className="section-header__subtitle">{subtitle}</p>}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
