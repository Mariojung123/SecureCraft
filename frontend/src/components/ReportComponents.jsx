import CodeEditor from './CodeEditor'

export function SeverityBadge({ severity }) {
  if (!severity || severity === 'NONE') return null
  const styles = {
    HIGH:   'bg-red-900/60 border-red-700/60 text-red-300',
    MEDIUM: 'bg-orange-900/60 border-orange-700/60 text-orange-300',
    LOW:    'bg-yellow-900/60 border-yellow-700/60 text-yellow-300',
  }
  return (
    <span className={`text-xs font-semibold border rounded px-2 py-0.5 ${styles[severity] ?? styles.MEDIUM}`}>
      {severity}
    </span>
  )
}

export function StepBadge({ n }) {
  const labels = ['①', '②', '③', '④', '⑤']
  return (
    <span className="text-purple-400 font-bold text-lg select-none w-6 shrink-0">
      {labels[n] ?? `${n + 1}.`}
    </span>
  )
}

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  )
}

export function BeforeAfter({ before = '', after = '' }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
          <span className="text-red-400 text-xs font-semibold uppercase tracking-wide">
            Before (vulnerable)
          </span>
        </div>
        <div className="rounded-lg border border-red-800/40 overflow-hidden">
          <CodeEditor value={before} readOnly language="python" />
        </div>
      </div>
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
          <span className="text-green-400 text-xs font-semibold uppercase tracking-wide">
            After (fixed)
          </span>
        </div>
        <div className="rounded-lg border border-green-800/40 overflow-hidden">
          <CodeEditor value={after} readOnly language="python" />
        </div>
      </div>
    </div>
  )
}
