import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Upload, X, ArrowRight } from 'lucide-react'
import { casesApi } from '../services/api'
import { Card, CardHeader, CardTitle, CardBody, Button, Alert } from '../components/common/Common'
import toast from 'react-hot-toast'
import './NewCase.css'

export default function NewCase() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [files, setFiles] = useState([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files)
    setFiles((prev) => [...prev, ...newFiles])
    e.target.value = ''
  }

  const removeFile = (idx) => setFiles((f) => f.filter((_, i) => i !== idx))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim() || title.trim().length < 3) {
      setError('Title must be at least 3 characters.')
      return
    }
    if (!description.trim() || description.trim().length < 10) {
      setError('Description must be at least 10 characters.')
      return
    }
    setError('')
    setSaving(true)

    try {
      const res = await casesApi.create({ title: title.trim(), description: description.trim() })
      const caseId = res.data.id

      // Upload attached files
      for (const file of files) {
        try {
          await casesApi.uploadDocument(caseId, file)
        } catch {
          toast.error(`Could not upload ${file.name}`)
        }
      }

      toast.success('Case created successfully.')
      navigate(`/cases/${caseId}`)
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }

  return (
    <div className="new-case">
      <div className="new-case__header">
        <h1 className="new-case__title">Create New Case</h1>
        <p className="new-case__sub">Fill in the details below. After creation, AI analysis will be available.</p>
      </div>

      <form onSubmit={handleSubmit} className="new-case__form" noValidate>
        <Card>
          <CardHeader>
            <CardTitle>Case Information</CardTitle>
          </CardHeader>
          <CardBody>
            {error && <Alert type="danger" className="mb-4">{error}</Alert>}

            <div className="form-group">
              <label className="form-label" htmlFor="case-title">
                Case Title <span className="form-required">*</span>
              </label>
              <input
                id="case-title"
                className="form-input"
                type="text"
                placeholder="e.g. Theft complaint against John Doe at MG Road"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={500}
                required
              />
              <span className="form-hint">{title.length}/500 characters</span>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="case-description">
                Case Description <span className="form-required">*</span>
              </label>
              <textarea
                id="case-description"
                className="form-textarea"
                placeholder="Describe the incident in detail. Include dates, locations, persons involved, and what happened. The more detail you provide, the better the AI analysis."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={8}
                required
              />
              <span className="form-hint">{description.length} characters</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Attach Documents (Optional)</CardTitle>
          </CardHeader>
          <CardBody>
            <label className="file-upload-area">
              <Upload size={24} className="file-upload-area__icon" />
              <span className="file-upload-area__text">Click to upload or drag files here</span>
              <span className="file-upload-area__hint">PDF, JPG, PNG, DOCX — max 10MB each</span>
              <input
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.docx,.doc"
                onChange={handleFileChange}
                className="sr-only"
              />
            </label>

            {files.length > 0 && (
              <div className="file-list">
                {files.map((f, i) => (
                  <div key={i} className="file-item">
                    <FileText size={16} className="file-item__icon" />
                    <span className="file-item__name">{f.name}</span>
                    <span className="file-item__size">{(f.size / 1024).toFixed(0)} KB</span>
                    <button
                      type="button"
                      className="file-item__remove"
                      onClick={() => removeFile(i)}
                      aria-label="Remove file"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        <div className="new-case__actions">
          <Button type="button" variant="secondary" onClick={() => navigate('/cases')}>
            Cancel
          </Button>
          <Button
            type="submit"
            loading={saving}
            icon={!saving && <ArrowRight size={16} />}
          >
            {saving ? 'Creating case…' : 'Create Case'}
          </Button>
        </div>
      </form>
    </div>
  )
}
