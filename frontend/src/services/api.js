import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'An error occurred'
    return Promise.reject(new Error(Array.isArray(msg) ? msg[0]?.msg : msg))
  }
)

// ── Cases ────────────────────────────────────────────────────────────────────
export const casesApi = {
  list: (params = {}) => api.get('/cases', { params }),
  get: (id) => api.get(`/cases/${id}`),
  create: (data) => api.post('/cases', data),
  update: (id, data) => api.patch(`/cases/${id}`, data),
  delete: (id) => api.delete(`/cases/${id}`),
  uploadDocument: (id, file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/cases/${id}/documents`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ── Analysis ─────────────────────────────────────────────────────────────────
export const analysisApi = {
  classify: (id) => api.post(`/analysis/${id}/classify`),
  identifyLaws: (id) => api.post(`/analysis/${id}/laws`),
  recommendEvidence: (id) => api.post(`/analysis/${id}/evidence`),
  updateEvidenceStatus: (caseId, evidenceId, status) =>
    api.patch(`/analysis/${caseId}/evidence/${evidenceId}`, { status }),
  computeScores: (id) => api.post(`/analysis/${id}/scores`),
  generateRecommendations: (id) => api.post(`/analysis/${id}/recommendations`),
  generateGaps: (id) => api.post(`/analysis/${id}/gaps`),
  generateTimeline: (id) => api.post(`/analysis/${id}/timeline`),
  fullAnalysis: (id) => api.post(`/analysis/${id}/full-analysis`),
}

// ── Questionnaire ─────────────────────────────────────────────────────────────
export const questionnaireApi = {
  getQuestions: (id) => api.get(`/questionnaire/${id}/questions`),
  submitResponses: (id, responses) =>
    api.post(`/questionnaire/${id}/responses`, { case_id: id, responses }),
  getResponses: (id) => api.get(`/questionnaire/${id}/responses`),
}

// ── Documents ─────────────────────────────────────────────────────────────────
export const documentsApi = {
  generate: (caseId, documentType, documentFormat) =>
    api.post('/documents/generate', { case_id: caseId, document_type: documentType, document_format: documentFormat }),
  listForCase: (caseId) => api.get(`/documents/case/${caseId}`),
  downloadUrl: (docId) => `/api/v1/documents/download/${docId}`,
}

// ── Settings ──────────────────────────────────────────────────────────────────
export const settingsApi = {
  getAll: () => api.get('/settings'),
  get: (key) => api.get(`/settings/${key}`),
  set: (key, value) => api.put('/settings', { key, value }),
}

export default api
