import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import AiChat from '../components/AiChat'
import HighlightedCode from '../components/HighlightedCode'
import { SeverityBadge, StepBadge, BeforeAfter } from '../components/ReportComponents'
import { getSessionReport } from '../api'

export default function Report() {
  const { session_id } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    const poll = () => {
      getSessionReport(session_id)
        .then(data => {
          if (cancelled) return
          if (data.status === 'processing') {
            setTimeout(poll, 2000)
          } else {
            setReport(data)
            setLoading(false)
          }
        })
        .catch(() => {
          if (!cancelled) {
            setError('Report not found. It may have expired.')
            setLoading(false)
          }
        })
    }

    poll()
    return () => { cancelled = true }
  }, [session_id])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <span className="animate-spin w-7 h-7 border-2 border-white/10 border-t-purple-400 rounded-full" />
        <p className="text-slate-500 text-sm">Waiting for validation to finish…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-10">
        <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-lg p-4">{error}</div>
      </div>
    )
  }

  const passed = report.passed
  const hasFlow = Array.isArray(report.attack_flow) && report.attack_flow.length > 0
  const hasVulnLines = Array.isArray(report.vulnerable_lines) && report.vulnerable_lines.length > 0
  return (
    <div className="max-w-4xl mx-auto px-6 py-10">

      {/* ── Breadcrumb ──────────────────────────────────────────────────────── */}
      <div className="text-sm text-slate-500 mb-6">
        <Link to="/challenges" className="hover:text-white transition-colors">Challenges</Link>
        <span className="mx-2">/</span>
        <Link to={`/challenges/${report.challenge_id}`} className="hover:text-white transition-colors">
          {report.title}
        </Link>
        <span className="mx-2">/</span>
        <span className="text-slate-300">Report</span>
      </div>

      {/* ── Result banner ───────────────────────────────────────────────────── */}
      <div className={`rounded-xl border p-6 mb-8
        ${passed
          ? 'bg-green-900/20 border-green-700/50'
          : 'bg-red-900/20 border-red-700/50'}`}>
        <div className={`text-3xl font-bold mb-1 ${passed ? 'text-green-400' : 'text-red-400'}`}>
          {passed ? '✓ Vulnerability Fixed' : '✗ Still Vulnerable'}
        </div>
        <p className={`text-sm ${passed ? 'text-green-300/70' : 'text-red-300/70'}`}>
          {passed
            ? 'The attack was blocked. Your fix correctly prevents the exploit.'
            : 'The attack succeeded. The vulnerability is still present in your code.'}
        </p>
        {report.attack_payload && (
          <div className="mt-3 inline-flex items-center gap-2 bg-slate-900/60 border border-slate-700/60
                          rounded-lg px-3 py-1.5 text-xs font-mono">
            <span className="text-slate-500">Payload used:</span>
            <span className="text-yellow-300">{report.attack_payload}</span>
          </div>
        )}
      </div>

      {/* ── AI unavailable notice ────────────────────────────────────────── */}
      {report.ai_error && (
        <div className="mb-6 bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-2.5
                        text-slate-400 text-xs flex items-center gap-2">
          <span>⚠</span>
          <span>AI analysis unavailable — using static detection. Error: {report.ai_error}</span>
        </div>
      )}

      {/* ══ FAILED PATH ══════════════════════════════════════════════════════ */}
      {!passed && (
        <>
          {/* 1. Vulnerable Code */}
          {report.submitted_code && (
            <section className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full
                                 bg-red-900/60 border border-red-700/60 text-red-400 text-xs font-bold">
                  1
                </span>
                <h2 className="text-white font-semibold text-base">Vulnerable Code</h2>
                <SeverityBadge severity={report.severity} />
                {hasVulnLines && (
                  <span className="text-xs text-red-400/80 bg-red-900/30 border border-red-800/40
                                   rounded px-2 py-0.5">
                    {report.vulnerable_lines.length} vulnerable line{report.vulnerable_lines.length > 1 ? 's' : ''} highlighted
                  </span>
                )}
              </div>
              <p className="text-slate-500 text-xs mb-3">
                Lines marked <span className="text-red-400 font-semibold">VULN</span> are
                the root cause of the vulnerability in your submitted code.
              </p>
              <HighlightedCode
                code={report.submitted_code}
                vulnerableLines={report.vulnerable_lines ?? []}
              />
              {report.vulnerability_explanation && (
                <div className="mt-3 bg-red-950/30 border border-red-800/40 rounded-xl p-4
                                text-red-200/80 text-sm leading-relaxed">
                  <span className="font-semibold text-red-300">What makes this vulnerable: </span>
                  {report.vulnerability_explanation}
                </div>
              )}
              {report.fix_hint && (
                <div className="mt-2 bg-blue-950/30 border border-blue-800/40 rounded-xl p-4
                                text-blue-200/80 text-sm leading-relaxed">
                  <span className="font-semibold text-blue-300">How to fix it: </span>
                  {report.fix_hint}
                </div>
              )}
            </section>
          )}

          {/* 2. Attack Flow */}
          {hasFlow && (
            <section className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full
                                 bg-orange-900/60 border border-orange-700/60 text-orange-400 text-xs font-bold">
                  2
                </span>
                <h2 className="text-white font-semibold text-base">Attack Flow</h2>
              </div>
              <p className="text-slate-500 text-xs mb-3">
                Step-by-step breakdown of how the attack exploited your code.
              </p>
              <div className="bg-slate-900/80 border border-slate-700/60 rounded-xl p-5 space-y-3">
                {report.attack_flow.map((step, i) => (
                  <div key={step.label} className="flex items-start gap-3">
                    <StepBadge n={i} />
                    <div className="flex-1 min-w-0">
                      <span className="text-slate-500 text-xs uppercase tracking-wider font-medium
                                       mr-3 inline-block w-28 shrink-0">
                        {step.label}
                      </span>
                      <span className="font-mono text-sm text-slate-200 break-all">
                        {step.value}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 3. Raw attack output */}
          <section className="mb-8">
            <div className="flex items-center gap-3 mb-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full
                               bg-slate-700 border border-slate-600 text-slate-400 text-xs font-bold">
                3
              </span>
              <h2 className="text-white font-semibold text-base">Attack Output</h2>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono
                            text-xs text-slate-400 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
              {report.attack_output || '(no output)'}
            </div>
          </section>

          {/* 4. How to Fix */}
          {(report.fixed_code || report.canonical_fix) && (
            <section className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full
                                 bg-blue-900/60 border border-blue-700/60 text-blue-400 text-xs font-bold">
                  4
                </span>
                <h2 className="text-white font-semibold text-base">How to Fix</h2>
              </div>
              <BeforeAfter
                before={report.submitted_code ?? ''}
                after={report.fixed_code || report.canonical_fix}
              />
              {report.explanation && (
                <div className="mt-4 bg-blue-950/30 border border-blue-800/40 rounded-xl p-4
                                text-blue-200/80 text-sm leading-relaxed">
                  <span className="font-semibold text-blue-300">Why this fix works: </span>
                  {report.explanation}
                </div>
              )}
            </section>
          )}
        </>
      )}

      {/* ══ PASSED PATH ══════════════════════════════════════════════════════ */}
      {passed && (
        <>
          {(report.why_blocked || report.explanation) && (
            <section className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-green-400 text-xl">🛡️</span>
                <h2 className="text-white font-semibold text-base">Why the Attack Was Blocked</h2>
              </div>
              <div className="bg-green-950/30 border border-green-700/40 rounded-xl p-5
                              text-green-200/80 text-sm leading-relaxed">
                {report.why_blocked || report.explanation}
              </div>
              {report.fix_hint && (
                <div className="mt-2 bg-blue-950/30 border border-blue-800/40 rounded-xl p-4
                                text-blue-200/80 text-sm leading-relaxed">
                  <span className="font-semibold text-blue-300">Note: </span>
                  {report.fix_hint}
                </div>
              )}
            </section>
          )}

          {report.submitted_code && (
            <section className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-green-400 text-xl">✅</span>
                <h2 className="text-white font-semibold text-base">Your Fix</h2>
              </div>
              <div className="rounded-lg border border-green-800/40 overflow-hidden">
                <CodeEditor value={report.submitted_code} readOnly language="python" />
              </div>
            </section>
          )}

          <section className="mb-8">
            <h2 className="text-white font-semibold text-base mb-3">Attack Output (blocked)</h2>
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono
                            text-xs text-slate-400 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
              {report.attack_output || '(no output)'}
            </div>
          </section>

          {(report.fixed_code || report.canonical_fix) && (
            <section className="mb-8">
              <h2 className="text-white font-semibold text-base mb-3">Reference Solution</h2>
              <div className="rounded-lg border border-slate-700/60 overflow-hidden">
                <CodeEditor value={report.fixed_code || report.canonical_fix} readOnly language="python" />
              </div>
            </section>
          )}
        </>
      )}

      {/* ── Validation result ───────────────────────────────────────────────── */}
      <section className="mb-8">
        <h2 className="text-white font-semibold text-base mb-3">Validation Result</h2>
        <div className={`rounded-lg p-4 font-mono text-xs leading-relaxed whitespace-pre-wrap border
          ${passed
            ? 'bg-green-900/10 border-green-800/40 text-green-300'
            : 'bg-red-900/10 border-red-800/40 text-red-300'}`}>
          {report.check_output || '(no output)'}
        </div>
      </section>

      {/* ── AI Chat ────────────────────────────────────────────────────────── */}
      <AiChat sessionId={session_id} report={report} />

      {/* ── Actions ────────────────────────────────────────────────────────── */}
      <div className="flex gap-3">
        <Link
          to={`/challenges/${report.challenge_id}`}
          className="border border-slate-700 hover:border-slate-500 text-slate-300
                     font-medium px-5 py-2 rounded-lg transition-colors text-sm"
        >
          {passed ? 'Try Again' : 'Back to Challenge'}
        </Link>
        <Link
          to={`/sandbox/${session_id}`}
          className="border border-slate-700 hover:border-slate-500 text-slate-300
                     font-medium px-5 py-2 rounded-lg transition-colors text-sm"
        >
          Open Sandbox
        </Link>
        <Link
          to="/challenges"
          className="bg-purple-600 hover:bg-purple-500 text-white font-medium
                     px-5 py-2 rounded-lg transition-colors text-sm ml-auto"
        >
          {passed ? 'Next Challenge →' : 'All Challenges'}
        </Link>
      </div>
    </div>
  )
}
