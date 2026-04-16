import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import { DifficultyBadge, CategoryBadge } from '../components/Badge'
import { getChallenge, submitCode, getSession } from '../api'

// How often (ms) to poll /api/sessions/<id> after submission
const POLL_INTERVAL = 2000

const LANG_LABELS = { python: 'Python', php: 'PHP', java: 'Java' }

export default function ChallengeDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [challenge, setChallenge] = useState(null)
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState('')
  // skeleton cache: { python: '...', php: null, java: null }
  const skeletonCache = useRef({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [submitPhase, setSubmitPhase] = useState(null)
  const [error, setError] = useState(null)
  const [showHint, setShowHint] = useState(false)

  const pollRef = useRef(null)

  // ── Load challenge on mount ────────────────────────────────────────────────
  useEffect(() => {
    getChallenge(id, 'python')
      .then(data => {
        setChallenge(data)
        skeletonCache.current['python'] = data.skeleton ?? ''
        setCode(data.skeleton ?? '')
      })
      .catch(() => setError('Challenge not found.'))
      .finally(() => setLoading(false))
  }, [id])

  // ── Handle language switch ─────────────────────────────────────────────────
  const handleLanguageChange = async (lang) => {
    setLanguage(lang)

    // Use cache or re-fetch
    if (skeletonCache.current[lang] != null) {
      setCode(skeletonCache.current[lang])
      return
    }

    try {
      const data = await getChallenge(id, lang)
      skeletonCache.current[lang] = data.skeleton ?? ''
      setCode(data.skeleton ?? '')
    } catch {
      setCode('')
    }
  }

  // ── Clean up polling interval on unmount ───────────────────────────────────
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // ── Submit handler ────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    setSubmitting(true)
    setSubmitPhase('building')
    setError(null)

    try {
      const { session_id } = await submitCode(id, code, language)

      setSubmitPhase('waiting')

      pollRef.current = setInterval(async () => {
        try {
          const session = await getSession(session_id)

          if (session.status === 'error') {
            clearInterval(pollRef.current)
            setError(session.error || 'An error occurred during submission.')
            setSubmitting(false)
            setSubmitPhase(null)
            return
          }

          if (session.port !== null) {
            clearInterval(pollRef.current)
            navigate(`/sandbox/${session_id}`)
            return
          }

          if (session.status === 'done') {
            clearInterval(pollRef.current)
            navigate(`/sandbox/${session_id}`)
          }
        } catch {
          clearInterval(pollRef.current)
          setError('Lost connection while waiting for sandbox. Please try again.')
          setSubmitting(false)
          setSubmitPhase(null)
        }
      }, POLL_INTERVAL)
    } catch {
      setError('Submission failed. Is the backend running?')
      setSubmitting(false)
      setSubmitPhase(null)
    }
  }

  // ── Render helpers ─────────────────────────────────────────────────────────
  const submitLabel = () => {
    if (!submitting) return 'Submit Code'
    if (submitPhase === 'building') return 'Building sandbox…'
    return 'Waiting for sandbox…'
  }

  const submitHint = () => {
    if (!submitting) return null
    if (submitPhase === 'building')
      return 'Running attack payloads against your code. This can take 15–30 s.'
    return 'Sandbox container is starting up…'
  }

  const availableLanguages = challenge?.languages ?? ['python']
  const pythonSkeleton = skeletonCache.current['python'] ?? ''
  const hasEditor = code !== null && code !== ''

  // ── Early-return states ────────────────────────────────────────────────────
  if (loading) {
    return <div className="text-center py-20 text-slate-500">Loading…</div>
  }

  if (error && !challenge) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-lg p-4">
          {error}
        </div>
      </div>
    )
  }

  // ── Main layout ────────────────────────────────────────────────────────────
  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Breadcrumb */}
      <div className="text-sm text-slate-500 mb-6">
        <Link to="/challenges" className="hover:text-white transition-colors">
          Challenges
        </Link>
        <span className="mx-2">/</span>
        <span className="text-slate-300">{challenge.title}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* ── Left: Description panel ─────────────────────────────────────── */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <DifficultyBadge difficulty={challenge.difficulty} />
            <CategoryBadge category={challenge.category} />
          </div>

          <h1 className="text-2xl font-bold text-white mb-4">{challenge.title}</h1>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-4">
            <h2 className="text-white font-medium mb-2 text-sm uppercase tracking-wide opacity-60">
              Description
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
              {challenge.description}
            </p>
          </div>

          {challenge.hint && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <button
                onClick={() => setShowHint(h => !h)}
                className="flex items-center justify-between w-full text-left"
              >
                <span className="text-white font-medium text-sm uppercase tracking-wide opacity-60">
                  Hint
                </span>
                <span className="text-slate-500 text-xs">{showHint ? 'hide' : 'show'}</span>
              </button>
              {showHint && (
                <p className="text-yellow-300/80 text-sm mt-3 leading-relaxed">
                  {challenge.hint}
                </p>
              )}
            </div>
          )}
        </div>

        {/* ── Right: Language selector + Editor + submit ──────────────────── */}
        <div>
          {/* Language tabs */}
          <div className="flex items-center gap-1 mb-3 bg-slate-900 border border-slate-800 rounded-lg p-1 w-fit">
            {availableLanguages.map(lang => (
              <button
                key={lang}
                onClick={() => handleLanguageChange(lang)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  language === lang
                    ? 'bg-purple-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {LANG_LABELS[lang] ?? lang}
              </button>
            ))}
          </div>

          {hasEditor ? (
            <>
              <div className="flex items-center justify-between mb-3">
                <span className="text-slate-400 text-sm">
                  Edit the code below to fix the vulnerability
                </span>
                <button
                  onClick={() => setCode(skeletonCache.current[language] ?? '')}
                  className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
                >
                  Reset
                </button>
              </div>

              <CodeEditor value={code} onChange={setCode} />

              {error && (
                <div className="mt-3 bg-red-900/30 border border-red-700/50 text-red-300 rounded-lg px-4 py-3 text-sm">
                  {error}
                </div>
              )}

              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="mt-4 w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {submitting && (
                  <span className="animate-spin inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
                )}
                {submitLabel()}
              </button>

              {submitting && (
                <p className="text-slate-500 text-xs text-center mt-2">{submitHint()}</p>
              )}

              {submitting && (
                <div className="mt-3 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-purple-500 rounded-full transition-all duration-500 ${
                      submitPhase === 'building' ? 'w-1/2' : 'w-full animate-pulse'
                    }`}
                  />
                </div>
              )}
            </>
          ) : (
            /* Coming Soon placeholder for Java */
            <div className="flex flex-col items-center justify-center bg-slate-900 border border-slate-800 rounded-xl h-72 gap-3">
              <span className="text-3xl">🚧</span>
              <p className="text-white font-semibold">
                {LANG_LABELS[language] ?? language} — Coming Soon
              </p>
              <p className="text-slate-500 text-sm text-center max-w-xs">
                The {LANG_LABELS[language] ?? language} version of this challenge is under
                development. Switch back to Python to practice now.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
