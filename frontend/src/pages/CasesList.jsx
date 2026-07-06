import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PlusCircle, Search, Trash2, Eye, FolderOpen } from 'lucide-react'
import { casesApi } from '../services/api'
import { Card, Badge, Button, PageSpinner, EmptyState } from '../components/common/Common'
import toast from 'react-hot-toast'
import './CasesList.css'

export default function CasesList() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleting, setDeleting] = useState(null)
  const navigate = useNavigate()

  const load = (q = '') => {
    setLoading(true)
    casesApi.list({ search: q || undefined }).then((r) => {
      setCases(r.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSearch = (e) => {
    setSearch(e.target.value)
    const v = e.target.value
    const tid = setTimeout(() => load(v), 350)
    return () => clearTimeout(tid)
  }

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this case? This cannot be undone.')) return
    setDeleting(id)
    try {
      await casesApi.delete(id)
      setCases((cs) => cs.filter((c) => c.id !== id))
      toast.success('Case deleted.')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="cases-list">
      <div className="cases-list__toolbar">
        <div className="cases-list__search">
          <Search size={16} className="cases-list__search-icon" />
          <input
            className="cases-list__search-input"
            placeholder="Search cases…"
            value={search}
            onChange={handleSearch}
          />
        </div>
        <Button icon={<PlusCircle size={16} />} onClick={() => navigate('/cases/new')}>
          New Case
        </Button>
      </div>

      {loading ? (
        <PageSpinner message="Loading cases…" />
      ) : cases.length === 0 ? (
        <EmptyState
          icon={<FolderOpen size={28} />}
          title="No cases found"
          description={search ? `No results for "${search}"` : 'Start by creating your first case.'}
          action={!search && <Button onClick={() => navigate('/cases/new')}>Create Case</Button>}
        />
      ) : (
        <Card>
          <table className="cases-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id} onClick={() => navigate(`/cases/${c.id}`)} className="cases-table__row">
                  <td className="cases-table__id">LA-{String(c.id).padStart(5, '0')}</td>
                  <td className="cases-table__title">{c.title}</td>
                  <td>
                    {c.category ? (
                      <Badge variant="primary">{c.category}</Badge>
                    ) : (
                      <span className="cases-table__unclassified">Unclassified</span>
                    )}
                  </td>
                  <td><Badge variant={c.status}>{c.status.replace('_', ' ')}</Badge></td>
                  <td className="cases-table__date">{new Date(c.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="cases-table__actions" onClick={(e) => e.stopPropagation()}>
                      <button className="cases-table__action-btn" onClick={() => navigate(`/cases/${c.id}`)} title="View">
                        <Eye size={15} />
                      </button>
                      <button
                        className="cases-table__action-btn cases-table__action-btn--danger"
                        onClick={(e) => handleDelete(c.id, e)}
                        disabled={deleting === c.id}
                        title="Delete"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="cases-list__footer">
            {cases.length} case{cases.length !== 1 ? 's' : ''}
          </div>
        </Card>
      )}
    </div>
  )
}
