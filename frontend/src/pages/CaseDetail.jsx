import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Brain, Scale, Shield, ClipboardList, BarChart2,
  AlertCircle, Lightbulb, Clock, FileText, ChevronDown,
  ChevronUp, CheckCircle, Circle, XCircle, Zap, Download,
  ArrowLeft, Upload
} from 'lucide-react'
import { casesApi, analysisApi, questionnaireApi, documentsApi } from '../services/api'
import {
  Card, CardHeader, CardTitle, CardBody,
  Badge, Button, PageSpinner, EmptyState, ScoreBar, Alert, SectionHeader
} from '../components/common/Common'
import toast from 'react-hot-toast'
import './CaseDetail.css'

/* ── Helpers ──────────────────────────────────────────────────── */
function SectionToggle({ id, icon: Icon, title, badge, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <Card className="case-section">
      <button className="case-section__toggle" onClick={() => setOpen((o) => !o)}>
        <div className="case-section__toggle-left">
          <span className="case-section__toggle-icon"><Icon size={16} /></span>
          <span className="case-section__toggle-title">{title}</span>
          {badge != null && <Badge variant="primary">{badge}</Badge>}
        </div>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      {open && <div className="case-section__body">{children}</div>}
    </Card>
  )
}

const EVIDENCE_STATUS_ICONS = {
  collected:   { icon: CheckCircle, color: 'var(--color-success)' },
  pending:     { icon: Circle,      color: 'var(--color-warning)' },
  unavailable: { icon: XCircle,     color: 'var(--color-danger)'  },
}

const STATUS_OPTIONS = [
  { value: 'draft',       label: 'Draft' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed',   label: 'Completed' },
]

/* Manual case-status control. Renders the current status as a Badge inside a
   trigger button; clicking opens a small menu of the other statuses. Closes
   on outside click or Escape. */
function StatusMenu({ status, onChange, updating }) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const handlePointer = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false)
    }
    const handleKey = (e) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', handlePointer)
    document.addEventListener('keydown', handleKey)
    return () => {
      document.removeEventListener('mousedown', handlePointer)
      document.removeEventListener('keydown', handleKey)
    }
  }, [open])

  return (
    <div className="status-menu" ref={rootRef}>
      <button
        type="button"
        className="status-menu__trigger"
        onClick={() => setOpen((o) => !o)}
        disabled={updating}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <Badge variant={status}>{status.replace('_', ' ')}</Badge>
        <ChevronDown size={14} className="status-menu__chevron" />
      </button>
      {open && (
        <div className="status-menu__list" role="listbox">
          {STATUS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              role="option"
              aria-selected={status === opt.value}
              className="status-menu__option"
              onClick={() => { setOpen(false); if (opt.value !== status) onChange(opt.value) }}
            >
              <Badge variant={opt.value}>{opt.label}</Badge>
              {status === opt.value && <CheckCircle size={14} className="status-menu__check" />}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

/* ── Main Component ───────────────────────────────────────────── */
export default function CaseDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [submittingQ, setSubmittingQ] = useState(false)
  const [genDoc, setGenDoc] = useState({ type: 'complaint_draft', format: 'pdf' })
  const [generatingDoc, setGeneratingDoc] = useState(false)
  const [uploadingFile, setUploadingFile] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)

  const load = useCallback(() => {
    casesApi.get(id).then((r) => {
      setCaseData(r.data)
      setLoading(false)
    }).catch(() => { toast.error('Could not load case.'); setLoading(false) })
  }, [id])

  useEffect(() => { load() }, [load])

  const runFullAnalysis = async () => {
    setRunning(true)
    try {
      const res = await analysisApi.fullAnalysis(id)
      setCaseData(res.data)
      // Load questionnaire questions after classification
      if (res.data.category && res.data.category !== 'unknown') {
        questionnaireApi.getQuestions(id).then((qr) => setQuestions(qr.data)).catch(() => {})
      }
      toast.success('Full analysis complete.')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setRunning(false)
    }
  }

  useEffect(() => {
    if (caseData?.category && caseData.category !== 'unknown') {
      questionnaireApi.getQuestions(id).then((r) => setQuestions(r.data)).catch(() => {})
      questionnaireApi.getResponses(id).then((r) => {
        const map = {}
        r.data.forEach((resp) => { map[resp.question_id] = resp.answer })
        setAnswers(map)
      }).catch(() => {})
    }
  }, [caseData?.category, id])

  const handleAnswerChange = (questionId, value) => {
    setAnswers((a) => ({ ...a, [questionId]: value }))
  }

  const submitQuestionnaire = async () => {
    setSubmittingQ(true)
    try {
      const responses = questions.map((q) => ({
        question_id: q.id,
        question_text: q.text,
        question_type: q.question_type,
        answer: answers[q.id] ?? null,
      })).filter((r) => r.answer !== null && r.answer !== '')
      await questionnaireApi.submitResponses(id, responses)
      toast.success('Responses saved.')
      // Recompute scores
      await analysisApi.computeScores(id)
      await analysisApi.generateGaps(id)
      await analysisApi.generateTimeline(id)
      load()
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSubmittingQ(false)
    }
  }

  const updateCaseStatus = async (status) => {
    setUpdatingStatus(true)
    try {
      const res = await casesApi.update(id, { status })
      setCaseData(res.data)
      toast.success(`Case marked as ${status.replace('_', ' ')}.`)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setUpdatingStatus(false)
    }
  }

  const updateEvidenceStatus = async (evidenceId, status) => {
    try {
      await analysisApi.updateEvidenceStatus(id, evidenceId, status)
      load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const generateDocument = async () => {
    setGeneratingDoc(true)
    try {
      const res = await documentsApi.generate(id, genDoc.type, genDoc.format)
      const dlUrl = documentsApi.downloadUrl(res.data.id)
      window.open(dlUrl, '_blank')
      toast.success('Document generated and download started.')
      load()
    } catch (err) {
      toast.error(err.message)
    } finally {
      setGeneratingDoc(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploadingFile(true)
    try {
      await casesApi.uploadDocument(id, file)
      toast.success('Document uploaded.')
      load()
    } catch (err) {
      toast.error(err.message)
    } finally {
      setUploadingFile(false)
      e.target.value = ''
    }
  }

  if (loading) return <PageSpinner message="Loading case…" />
  if (!caseData) return <EmptyState title="Case not found" description="This case does not exist." action={<Button onClick={() => navigate('/cases')}>Back to Cases</Button>} />

  const c = caseData
  const isClassified = c.category && c.category !== 'unknown'

  return (
    <div className="case-detail">
      {/* Back + Header */}
      <div className="case-detail__top">
        <button className="case-detail__back" onClick={() => navigate('/cases')}>
          <ArrowLeft size={16} /> All Cases
        </button>
        <div className="case-detail__header">
          <div className="case-detail__header-info">
            <span className="case-detail__ref">LA-{String(c.id).padStart(5, '0')}</span>
            <h1 className="case-detail__title">{c.title}</h1>
            <div className="case-detail__meta">
              <StatusMenu status={c.status} onChange={updateCaseStatus} updating={updatingStatus} />
              {isClassified && <Badge variant="primary">{c.category}</Badge>}
              {c.subcategory && <span className="case-detail__subcat">{c.subcategory}</span>}
              {c.classification_confidence != null && (
                <span className="case-detail__confidence">
                  {Math.round(c.classification_confidence * 100)}% confidence
                </span>
              )}
            </div>
          </div>
          <Button
            onClick={runFullAnalysis}
            loading={running}
            icon={!running && <Zap size={16} />}
          >
            {running ? 'Running AI Analysis…' : 'Run Full Analysis'}
          </Button>
        </div>
      </div>

      {!isClassified && (
        <Alert type="info">
          This case has not been classified yet. Click <strong>Run Full Analysis</strong> to classify it and generate AI insights.
        </Alert>
      )}

      {/* MODULE 2: Classification + Summary */}
      {isClassified && (
        <Card>
          <CardHeader><CardTitle>AI Case Summary</CardTitle></CardHeader>
          <CardBody>
            <p className="case-detail__summary">{c.ai_summary || c.description}</p>
            {c.extracted_entities && Object.values(c.extracted_entities).some((v) => v.length > 0) && (
              <div className="entities-grid">
                {Object.entries(c.extracted_entities).map(([key, vals]) =>
                  vals.length > 0 ? (
                    <div key={key} className="entity-group">
                      <span className="entity-group__label">{key}</span>
                      <div className="entity-group__tags">
                        {vals.map((v, i) => <span key={i} className="entity-tag">{v}</span>)}
                      </div>
                    </div>
                  ) : null
                )}
              </div>
            )}
          </CardBody>
        </Card>
      )}

      {/* MODULE 7: Scores */}
      {c.scores && (
        <SectionToggle id="scores" icon={BarChart2} title="Case Strength Assessment" defaultOpen={true}>
          <div className="scores-grid">
            <ScoreBar label="Claim Strength"          score={c.scores.claim_strength_score}             explanation={c.scores.claim_strength_explanation} />
            <ScoreBar label="Evidence Strength"       score={c.scores.evidence_strength_score}          explanation={c.scores.evidence_strength_explanation} />
            <ScoreBar label="Case Completeness"       score={c.scores.case_completeness_score}          explanation={c.scores.case_completeness_explanation} />
            <ScoreBar label="Counterargument Risk"    score={c.scores.counterargument_opportunity_score} explanation={c.scores.counterargument_explanation}
              colorClass={c.scores.counterargument_opportunity_score > 60 ? 'score-bar--low' : 'score-bar--high'} />
          </div>
        </SectionToggle>
      )}

      {/* MODULE 8: Gap Analysis */}
      {c.gap_analyses?.length > 0 && (
        <SectionToggle id="gaps" icon={AlertCircle} title="Gap Analysis" badge={c.gap_analyses.filter((g) => !g.resolved).length} defaultOpen>
          <div className="gap-list">
            {c.gap_analyses.map((g) => (
              <div key={g.id} className={`gap-item gap-item--${g.severity}`}>
                <div className="gap-item__header">
                  <span className="gap-item__type">{g.gap_type.replace(/_/g, ' ')}</span>
                  <Badge variant={g.severity === 'high' ? 'danger' : g.severity === 'medium' ? 'warning' : 'gray'}>{g.severity}</Badge>
                </div>
                <p className="gap-item__desc">{g.gap_description}</p>
                {g.suggestion && <p className="gap-item__suggestion">💡 {g.suggestion}</p>}
              </div>
            ))}
          </div>
        </SectionToggle>
      )}

      {/* MODULE 5: Applicable Laws */}
      {c.applicable_laws?.length > 0 && (
        <SectionToggle id="laws" icon={Scale} title="Applicable Laws" badge={c.applicable_laws.length}>
          <div className="laws-list">
            {c.applicable_laws.map((law) => (
              <div key={law.id} className="law-card">
                <div className="law-card__header">
                  <div className="law-card__act-info">
                    <span className="law-card__section">Section {law.section_number}</span>
                    <span className="law-card__title">{law.section_title}</span>
                    <span className="law-card__act">{law.act_name}</span>
                  </div>
                  <div className="law-card__meta">
                    <div className="law-card__confidence">
                      <span className="law-card__conf-label">Confidence</span>
                      <span className="law-card__conf-value">{Math.round(law.confidence_score * 100)}%</span>
                    </div>
                    {law.nature_of_offence && <Badge variant="info">{law.nature_of_offence.split(',')[0]}</Badge>}
                  </div>
                </div>
                <p className="law-card__meaning">{law.section_meaning}</p>
                <div className="law-card__footer">
                  {law.punishment && (
                    <div className="law-card__punishment">
                      <span className="law-card__punishment-label">Punishment:</span> {law.punishment}
                    </div>
                  )}
                  <div className="law-card__reason">
                    <span className="law-card__reason-label">Why recommended:</span> {law.reason_for_recommendation}
                  </div>
                  {law.triggering_facts?.length > 0 && (
                    <div className="law-card__triggers">
                      {law.triggering_facts.map((f, i) => <span key={i} className="trigger-tag">{f}</span>)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </SectionToggle>
      )}

      {/* MODULE 4: Evidence */}
      {c.evidence_items?.length > 0 && (
        <SectionToggle id="evidence" icon={Shield} title="Evidence Checklist" badge={c.evidence_items.length}>
          <div className="evidence-list">
            {c.evidence_items.map((ev) => {
              const { icon: StatusIcon, color } = EVIDENCE_STATUS_ICONS[ev.status] || EVIDENCE_STATUS_ICONS.pending
              return (
                <div key={ev.id} className={`evidence-item evidence-item--${ev.importance}`}>
                  <StatusIcon size={18} style={{ color, flexShrink: 0 }} />
                  <div className="evidence-item__info">
                    <span className="evidence-item__name">{ev.name}</span>
                    <span className="evidence-item__meta">{ev.evidence_type} · {ev.importance} priority</span>
                  </div>
                  <div className="evidence-item__actions">
                    {['pending', 'collected', 'unavailable'].map((s) => (
                      <button
                        key={s}
                        className={`evidence-btn${ev.status === s ? ' evidence-btn--active' : ''}`}
                        onClick={() => updateEvidenceStatus(ev.id, s)}
                      >{s}</button>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </SectionToggle>
      )}

      {/* MODULE 3: Questionnaire */}
      {isClassified && (
        <SectionToggle id="questionnaire" icon={ClipboardList} title="Case Questionnaire" badge={questions.length}>
          {questions.length === 0 ? (
            <p className="case-section__empty">No questions available. Run full analysis first.</p>
          ) : (
            <div className="questionnaire">
              {questions.map((q) => (
                <div key={q.id} className="q-group">
                  <label className="q-label">{q.text}{q.required && <span className="form-required"> *</span>}</label>
                  {q.question_type === 'text' || q.question_type === 'date' ? (
                    <input
                      type={q.question_type === 'date' ? 'date' : 'text'}
                      className="form-input"
                      value={answers[q.id] || ''}
                      onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                    />
                  ) : q.question_type === 'multiple_choice' ? (
                    <div className="q-options">
                      {q.options?.map((opt) => (
                        <label key={opt.value} className={`q-option${answers[q.id] === opt.value ? ' q-option--selected' : ''}`}>
                          <input type="radio" name={q.id} value={opt.value}
                            checked={answers[q.id] === opt.value}
                            onChange={() => handleAnswerChange(q.id, opt.value)} />
                          {opt.label}
                        </label>
                      ))}
                    </div>
                  ) : q.question_type === 'dropdown' ? (
                    <select className="form-input" value={answers[q.id] || ''} onChange={(e) => handleAnswerChange(q.id, e.target.value)}>
                      <option value="">Select…</option>
                      {q.options?.map((opt) => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                    </select>
                  ) : q.question_type === 'checkbox' ? (
                    <div className="q-options">
                      {q.options?.map((opt) => {
                        const current = answers[q.id] || []
                        const checked = Array.isArray(current) && current.includes(opt.value)
                        return (
                          <label key={opt.value} className={`q-option${checked ? ' q-option--selected' : ''}`}>
                            <input type="checkbox" value={opt.value} checked={checked}
                              onChange={(e) => {
                                const updated = checked ? current.filter((v) => v !== opt.value) : [...current, opt.value]
                                handleAnswerChange(q.id, updated)
                              }} />
                            {opt.label}
                          </label>
                        )
                      })}
                    </div>
                  ) : null}
                </div>
              ))}
              <div className="questionnaire__actions">
                <Button onClick={submitQuestionnaire} loading={submittingQ}>
                  {submittingQ ? 'Saving…' : 'Save Responses & Refresh Analysis'}
                </Button>
              </div>
            </div>
          )}
        </SectionToggle>
      )}

      {/* MODULE 9: Recommendations */}
      {c.recommendations?.length > 0 && (
        <SectionToggle id="recommendations" icon={Lightbulb} title="Recommended Actions" badge={c.recommendations.length}>
          <div className="rec-list">
            {c.recommendations.map((r, i) => (
              <div key={r.id} className={`rec-item rec-item--${r.priority}`}>
                <span className="rec-item__num">{i + 1}</span>
                <div className="rec-item__body">
                  <p className="rec-item__action">{r.action}</p>
                  {r.reasoning && <p className="rec-item__reasoning">{r.reasoning}</p>}
                </div>
                <Badge variant={r.priority}>{r.priority}</Badge>
              </div>
            ))}
          </div>
        </SectionToggle>
      )}

      {/* MODULE 10: Timeline */}
      {c.timeline_events?.length > 0 && (
        <SectionToggle id="timeline" icon={Clock} title="Case Timeline" badge={c.timeline_events.length}>
          <div className="timeline">
            {[...c.timeline_events].sort((a, b) => a.sequence_order - b.sequence_order).map((ev, i) => (
              <div key={ev.id} className="timeline-event">
                <div className="timeline-event__dot" />
                <div className="timeline-event__content">
                  {ev.event_date && <span className="timeline-event__date">{ev.event_date}</span>}
                  <p className="timeline-event__desc">{ev.event_description}</p>
                  {ev.event_type && <Badge variant="gray">{ev.event_type.replace(/_/g, ' ')}</Badge>}
                </div>
              </div>
            ))}
          </div>
        </SectionToggle>
      )}

      {/* MODULE 11: Document Generation */}
      <SectionToggle id="documents" icon={FileText} title="Generate Documents" defaultOpen={false}>
        <div className="doc-gen">
          <div className="doc-gen__options">
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Document Type</label>
              <select className="form-input" value={genDoc.type} onChange={(e) => setGenDoc((d) => ({ ...d, type: e.target.value }))}>
                <option value="complaint_draft">Complaint Draft</option>
                <option value="fir_draft">FIR Draft</option>
                <option value="legal_notice">Legal Notice</option>
                <option value="case_summary">Case Summary</option>
                <option value="investigation_report">Investigation Report</option>
              </select>
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">Format</label>
              <select className="form-input" value={genDoc.format} onChange={(e) => setGenDoc((d) => ({ ...d, format: e.target.value }))}>
                <option value="pdf">PDF</option>
                <option value="docx">DOCX (Word)</option>
              </select>
            </div>
            <Button onClick={generateDocument} loading={generatingDoc} icon={!generatingDoc && <Download size={16} />}>
              {generatingDoc ? 'Generating…' : 'Generate & Download'}
            </Button>
          </div>

          {c.generated_documents?.length > 0 && (
            <div className="doc-history">
              <h4 className="doc-history__title">Previously Generated</h4>
              {c.generated_documents.map((d) => (
                <div key={d.id} className="doc-history__item">
                  <FileText size={15} />
                  <span className="doc-history__name">{d.document_type.replace(/_/g, ' ')} ({d.document_format.toUpperCase()})</span>
                  <span className="doc-history__date">{new Date(d.generated_at).toLocaleString()}</span>
                  <a href={documentsApi.downloadUrl(d.id)} target="_blank" rel="noreferrer" className="doc-history__dl">
                    <Download size={14} />
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </SectionToggle>

      {/* Uploaded Documents */}
      <SectionToggle id="uploads" icon={Upload} title="Case Documents" badge={c.documents?.length || 0}>
        <div className="uploads-section">
          <label className="file-upload-mini">
            <Upload size={14} />
            {uploadingFile ? 'Uploading…' : 'Upload Document'}
            <input type="file" className="sr-only" onChange={handleFileUpload} disabled={uploadingFile} />
          </label>
          {c.documents?.length === 0 ? (
            <p className="case-section__empty">No documents uploaded.</p>
          ) : (
            c.documents.map((d) => (
              <div key={d.id} className="upload-item">
                <FileText size={15} />
                <span className="upload-item__name">{d.original_filename}</span>
                <span className="upload-item__meta">{(d.file_size / 1024).toFixed(0)} KB · {new Date(d.uploaded_at).toLocaleDateString()}</span>
              </div>
            ))
          )}
        </div>
      </SectionToggle>
    </div>
  )
}
