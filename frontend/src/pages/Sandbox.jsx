import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import { DifficultyBadge, CategoryBadge } from '../components/Badge'
import { getChallenge, getSession } from '../api'

const POLL_INTERVAL = 2000 // ms between port-readiness polls
const MAX_POLL_ATTEMPTS = 30 // 30 × 2s = 60s timeout

export default function Sandbox() {
  const { session_id } = useParams()

  const [challenge, setChallenge] = useState(null)
  const [challengeId, setChallengeId] = useState(null)
  const [submittedCode, setSubmittedCode] = useState('')
  const [port, setPort] = useState(null)
  const [loadingPage, setLoadingPage] = useState(true)  // initial data fetch
  const [iframeLoaded, setIframeLoaded] = useState(false)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)
  const pollAttempts = useRef(0)

  // ── On mount: fetch session + challenge, then poll until port is ready ──────
  useEffect(() => {
    let cancelled = false

    const init = async () => {
      try {
        // 1. Fetch session (contains challenge_id, code, port)
        const session = await getSession(session_id)
        if (cancelled) return

        setChallengeId(session.challenge_id)
        setSubmittedCode(session.code ?? '')

        // 2. Fetch challenge metadata (title, difficulty, etc.)
        const challengeData = await getChallenge(session.challenge_id)
        if (cancelled) return
        setChallenge(challengeData)

        // Fall back to skeleton if code was somehow not stored
        if (!session.code) setSubmittedCode(challengeData.skeleton ?? '')

        setLoadingPage(false)

        // 3. Port already available (sandbox was ready before we arrived)
        if (session.port) {
          setPort(session.port)
          return
        }

        // 4. Port not ready — poll every POLL_INTERVAL ms (up to MAX_POLL_ATTEMPTS)
        pollRef.current = setInterval(async () => {
          if (cancelled) return
          pollAttempts.current += 1

          if (pollAttempts.current > MAX_POLL_ATTEMPTS) {
            clearInterval(pollRef.current)
            setError('Sandbox container failed to start within 60 seconds. The container may have crashed — check your code for errors.')
            return
          }

          try {
            const updated = await getSession(session_id)
            if (cancelled) return
            if (updated.port) {
              clearInterval(pollRef.current)
              setPort(updated.port)
            }
          } catch {
            // Network blip — keep polling
          }
        }, POLL_INTERVAL)
      } catch {
        if (!cancelled) setLoadingPage(false)
      }
    }

    init()

    return () => {
      cancelled = true
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [session_id])

  // ── Derived values ─────────────────────────────────────────────────────────
  const sandboxUrl = port ? `http://${window.location.hostname}:${port}` : null

  // ── Loading splash ─────────────────────────────────────────────────────────
  if (loadingPage) {
    return <div className="text-center py-20 text-slate-500">Loading…</div>
  }

  // ── Main layout ────────────────────────────────────────────────────────────
  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="text-sm text-slate-500 mb-1">
            <Link to="/challenges" className="hover:text-white transition-colors">
              Challenges
            </Link>
            <span className="mx-2">/</span>
            <Link
              to={`/challenges/${challengeId}`}
              className="hover:text-white transition-colors"
            >
              {challenge?.title}
            </Link>
            <span className="mx-2">/</span>
            <span className="text-slate-300">Sandbox</span>
          </div>
          <div className="flex items-center gap-2 mt-1">
            {challenge && <DifficultyBadge difficulty={challenge.difficulty} />}
            {challenge && <CategoryBadge category={challenge.category} />}
          </div>
        </div>

        <Link
          to={`/report/${session_id}`}
          className="text-xs text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 px-3 py-1.5 rounded-lg transition-colors"
        >
          View Report →
        </Link>
      </div>

      {/* Two-column body */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ── Left: read-only submitted code ──────────────────────────────── */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-300 text-sm font-medium">Submitted Code</span>
            <span className="text-xs text-slate-600 italic">read-only</span>
          </div>
          <CodeEditor value={submittedCode} readOnly />
        </div>

        {/* ── Right: live sandbox iframe ───────────────────────────────────── */}
        <div>
          {/* Toolbar above the iframe */}
          <div className="flex items-center justify-between mb-2 h-6">
            <span className="text-slate-300 text-sm font-medium">Live Sandbox</span>
            {sandboxUrl ? (
              <a
                href={sandboxUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300 border border-purple-700/50 hover:border-purple-500 px-2.5 py-1 rounded-lg transition-colors"
              >
                Open in new tab
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            ) : (
              <span className="text-xs text-slate-600">Waiting for container…</span>
            )}
          </div>

          {/* iframe or waiting state */}
          {error ? (
            <div
              className="rounded-lg border border-red-800/60 bg-red-950/30 flex flex-col items-center justify-center gap-3 px-6 text-center"
              style={{ height: '420px' }}
            >
              <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <p className="text-red-400 text-sm font-medium">Container failed to start</p>
              <p className="text-slate-400 text-xs max-w-sm">{error}</p>
            </div>
          ) : sandboxUrl ? (
            <div className="relative rounded-lg overflow-hidden border border-slate-700" style={{ height: '420px' }}>
              {/* Subtle loading overlay until the iframe fires onLoad */}
              {!iframeLoaded && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 z-10 gap-3">
                  <span className="animate-spin w-6 h-6 border-2 border-white/20 border-t-purple-400 rounded-full" />
                  <span className="text-slate-500 text-xs">Connecting to sandbox…</span>
                </div>
              )}
              <iframe
                src={sandboxUrl}
                title="Live Sandbox"
                className="w-full h-full bg-white"
                onLoad={() => setIframeLoaded(true)}
                // Sandbox attributes — allow forms/scripts but keep it contained
                sandbox="allow-forms allow-scripts allow-same-origin"
              />
            </div>
          ) : (
            /* Port not yet assigned — spinner placeholder matching editor height */
            <div
              className="rounded-lg border border-slate-800 bg-slate-900 flex flex-col items-center justify-center gap-3"
              style={{ height: '420px' }}
            >
              <span className="animate-spin w-6 h-6 border-2 border-white/10 border-t-purple-400 rounded-full" />
              <p className="text-slate-500 text-sm">Sandbox container is starting…</p>
              <p className="text-slate-600 text-xs">Checking every {POLL_INTERVAL / 1000} s</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
