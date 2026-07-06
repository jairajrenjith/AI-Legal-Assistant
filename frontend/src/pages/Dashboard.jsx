import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FolderOpen, Scale, CheckCircle, Clock, PlusCircle, ArrowRight, AlertTriangle } from 'lucide-react'
import { casesApi } from '../services/api'
import { Card, CardHeader, CardTitle, CardBody, Badge, Button, PageSpinner, EmptyState } from '../components/common/Common'
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from 'recharts'
import './Dashboard.css'

function StatCard({ icon: Icon, label, value, color, sublabel }) {
  return (
    <div className="stat-card" style={{ '--stat-color': color }}>
      <div className="stat-card__icon"><Icon size={20} /></div>
      <div className="stat-card__info">
        <div className="stat-card__value">{value}</div>
        <div className="stat-card__label">{label}</div>
        {sublabel && <div className="stat-card__sublabel">{sublabel}</div>}
      </div>
    </div>
  )
}

const CATEGORY_COLORS = {
  criminal: '#dc2626', property: '#d97706', family: '#7c3aed',
  consumer: '#0284c7', labor: '#059669', cyber: '#db2777', administrative: '#6b7280',
}

export default function Dashboard() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    casesApi.list({ limit: 100 }).then((r) => {
      setCases(r.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <PageSpinner message="Loading dashboard..." />

  const total = cases.length
  const byStatus = cases.reduce((a, c) => { a[c.status] = (a[c.status] || 0) + 1; return a }, {})
  const byCategory = cases.reduce((a, c) => { if (c.category) a[c.category] = (a[c.category] || 0) + 1; return a }, {})

  const chartData = Object.entries(byCategory).map(([cat, count]) => ({
    name: cat.charAt(0).toUpperCase() + cat.slice(1),
    value: count,
    fill: CATEGORY_COLORS[cat] || '#6b7280',
  }))

  const recent = [...cases].slice(0, 5)

  return (
    <div className="dashboard">
      <div className="dashboard__welcome">
        <div>
          <h1 className="dashboard__heading">Welcome back</h1>
          <p className="dashboard__sub">Here is a summary of your legal case portfolio.</p>
        </div>
        <Button icon={<PlusCircle size={16} />} onClick={() => navigate('/cases/new')}>
          New Case
        </Button>
      </div>

      {/* Stats */}
      <div className="dashboard__stats">
        <StatCard icon={FolderOpen}   label="Total Cases"   value={total}                         color="var(--color-primary-600)"  sublabel="All time" />
        <StatCard icon={Clock}        label="In Progress"   value={byStatus.in_progress || 0}    color="var(--color-info)"         sublabel="Active" />
        <StatCard icon={CheckCircle}  label="Completed"     value={byStatus.completed || 0}      color="var(--color-success)"      sublabel="Resolved" />
        <StatCard icon={Scale}        label="Drafts"        value={byStatus.draft || 0}          color="var(--color-accent)"       sublabel="Pending action" />
      </div>

      <div className="dashboard__grid">
        {/* Recent Cases */}
        <Card className="dashboard__recent">
          <CardHeader action={
            <Button variant="ghost" size="sm" onClick={() => navigate('/cases')}
              icon={<ArrowRight size={14} />}>View all</Button>
          }>
            <CardTitle>Recent Cases</CardTitle>
          </CardHeader>
          <CardBody>
            {recent.length === 0 ? (
              <EmptyState
                icon={<FolderOpen size={24} />}
                title="No cases yet"
                description="Create your first case to get started."
                action={<Button size="sm" onClick={() => navigate('/cases/new')}>Create Case</Button>}
              />
            ) : (
              <div className="recent-cases">
                {recent.map((c) => (
                  <div key={c.id} className="recent-case" onClick={() => navigate(`/cases/${c.id}`)}>
                    <div className="recent-case__info">
                      <span className="recent-case__title">{c.title}</span>
                      <span className="recent-case__meta">
                        {c.category || 'Unclassified'} · {new Date(c.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <Badge variant={c.status}>{c.status.replace('_', ' ')}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        {/* Category Distribution */}
        <Card className="dashboard__chart">
          <CardHeader><CardTitle>Cases by Category</CardTitle></CardHeader>
          <CardBody>
            {chartData.length === 0 ? (
              <EmptyState icon={<Scale size={24} />} title="No categorised cases" description="Classify cases to see distribution." />
            ) : (
              <div className="category-chart">
                <ResponsiveContainer width="100%" height={200}>
                  <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="80%" data={chartData}>
                    <RadialBar dataKey="value" label={{ position: 'insideStart', fill: '#fff', fontSize: 10 }} />
                    <Tooltip formatter={(v, n) => [v, n]} />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="category-legend">
                  {chartData.map((d) => (
                    <div key={d.name} className="category-legend__item">
                      <span className="category-legend__dot" style={{ background: d.fill }} />
                      <span className="category-legend__name">{d.name}</span>
                      <span className="category-legend__count">{d.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
