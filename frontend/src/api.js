import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// ── Challenges ────────────────────────────────────────────────────────────────
export const getChallenges = () => api.get('/challenges').then(r => r.data)
export const getChallenge = (id, language = 'python') =>
  api.get(`/challenges/${id}`, { params: { language } }).then(r => r.data)

// ── Async submit + session polling ────────────────────────────────────────────

/** POST /api/submit → { session_id, status } */
export const submitCode = (challenge_id, code, language = 'python') =>
  api.post('/submit', { challenge_id, code, language }).then(r => r.data)

/** GET /api/sessions/<session_id> → { status, port, challenge_id, report?, error? } */
export const getSession = (sessionId) =>
  api.get(`/sessions/${sessionId}`).then(r => r.data)

/** GET /api/report/<session_id> → report dict (or { status: "processing" }) */
export const getSessionReport = (sessionId) =>
  api.get(`/report/${sessionId}`).then(r => r.data)

// ── AI Chat ───────────────────────────────────────────────────────────────────

/** POST /api/chat → { reply, error } */
export async function sendChatMessage(sessionId, message, history) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message, history }),
  })
  return res.json()
}

// ── Legacy synchronous endpoints (kept for backwards compat) ──────────────────
export const submitChallenge = (id, code) =>
  api.post(`/challenges/${id}/submit`, { code }).then(r => r.data)
export const getReport = (reportId) => api.get(`/reports/${reportId}`).then(r => r.data)
