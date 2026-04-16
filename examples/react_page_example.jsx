// ── React Page Pattern ────────────────────────────────────────────────────────
// Reference: frontend/src/pages/Report.jsx, ChallengeDetail.jsx
// Pattern: functional components + hooks only, Tailwind dark theme, polling pattern

import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getSession } from '../api'

// ── Sub-component pattern ──────────────────────────────────────────────────────
// Small, focused sub-components defined above the main export
function StatusBadge({ status }) {
  const styles = {
    done:       'bg-green-900/60 border-green-700/60 text-green-300',
    processing: 'bg-yellow-900/60 border-yellow-700/60 text-yellow-300',
    error:      'bg-red-900/60 border-red-700/60 text-red-300',
  }
  return (
    <span className={`text-xs font-semibold border rounded px-2 py-0.5 ${styles[status] ?? ''}`}>
      {status}
    </span>
  )
}

// ── Loading state pattern ──────────────────────────────────────────────────────
function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <span className="animate-spin w-7 h-7 border-2 border-white/10 border-t-purple-400 rounded-full" />
      <p className="text-slate-500 text-sm">Loading…</p>
    </div>
  )
}

// ── Error state pattern ────────────────────────────────────────────────────────
function ErrorMessage({ message }) {
  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-lg p-4">
        {message}
      </div>
    </div>
  )
}

// ── Main page component ────────────────────────────────────────────────────────
export default function ExamplePage() {
  const { session_id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // ── Polling pattern for async results ────────────────────────────────────
  useEffect(() => {
    let cancelled = false

    const poll = () => {
      getSession(session_id)
        .then(res => {
          if (cancelled) return
          if (res.status === 'processing') {
            setTimeout(poll, 2000)   // retry after 2s
          } else {
            setData(res)
            setLoading(false)
          }
        })
        .catch(() => {
          if (!cancelled) {
            setError('Resource not found or expired.')
            setLoading(false)
          }
        })
    }

    poll()
    return () => { cancelled = true }   // cleanup on unmount
  }, [session_id])

  if (loading) return <LoadingSpinner />
  if (error)   return <ErrorMessage message={error} />

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">

      {/* ── Breadcrumb pattern ─────────────────────────────────────────── */}
      <div className="text-sm text-slate-500 mb-6">
        <Link to="/challenges" className="hover:text-white transition-colors">Challenges</Link>
        <span className="mx-2">/</span>
        <span className="text-slate-300">{data.challenge_id}</span>
      </div>

      {/* ── Card panel pattern ─────────────────────────────────────────── */}
      <div className="bg-slate-900/80 border border-slate-700/60 rounded-xl p-6 mb-6">
        <div className="flex items-center gap-3 mb-2">
          <h2 className="text-white font-semibold text-base">Result</h2>
          <StatusBadge status={data.status} />
        </div>
        <p className="text-slate-400 text-sm">{data.challenge_id}</p>
      </div>

      {/* ── Action buttons pattern ─────────────────────────────────────── */}
      <div className="flex gap-3">
        <Link
          to="/challenges"
          className="border border-slate-700 hover:border-slate-500 text-slate-300
                     font-medium px-5 py-2 rounded-lg transition-colors text-sm"
        >
          Back
        </Link>
        <button
          onClick={() => window.location.reload()}
          className="bg-purple-600 hover:bg-purple-500 text-white font-medium
                     px-5 py-2 rounded-lg transition-colors text-sm ml-auto"
        >
          Refresh
        </button>
      </div>
    </div>
  )
}
