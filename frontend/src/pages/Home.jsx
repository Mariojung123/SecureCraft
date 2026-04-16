import { Link } from 'react-router-dom'

const categories = [
  { name: 'SQL Injection', icon: '🗄️', count: 2, color: 'border-blue-700/40 hover:border-blue-500/60' },
  { name: 'XSS', icon: '📜', count: 2, color: 'border-orange-700/40 hover:border-orange-500/60' },
  { name: 'Command Injection', icon: '💻', count: 1, color: 'border-red-700/40 hover:border-red-500/60' },
  { name: 'Path Traversal', icon: '📁', count: 1, color: 'border-yellow-700/40 hover:border-yellow-500/60' },
  { name: 'Secrets', icon: '🔑', count: 1, color: 'border-pink-700/40 hover:border-pink-500/60' },
  { name: 'Cryptography', icon: '🔒', count: 1, color: 'border-purple-700/40 hover:border-purple-500/60' },
  { name: 'Access Control', icon: '🛡️', count: 1, color: 'border-cyan-700/40 hover:border-cyan-500/60' },
  { name: 'Auth', icon: '🔐', count: 1, color: 'border-indigo-700/40 hover:border-indigo-500/60' },
]

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      {/* Hero */}
      <div className="text-center mb-16">
        <div className="inline-flex items-center gap-2 bg-purple-900/30 border border-purple-700/40 text-purple-300 text-xs font-medium px-3 py-1 rounded-full mb-6">
          <span>&#9679;</span> Learn by fixing real vulnerabilities
        </div>
        <h1 className="text-5xl font-bold text-white mb-4 leading-tight tracking-tight">
          Master Secure Coding
        </h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto mb-8 leading-relaxed">
          Practice fixing real-world security vulnerabilities in an interactive editor.
          Submit your fix and watch it get tested against live attacks in isolated Docker containers.
        </p>
        <div className="flex gap-3 justify-center">
          <Link
            to="/challenges"
            className="bg-purple-600 hover:bg-purple-500 text-white font-medium px-6 py-2.5 rounded-lg transition-colors"
          >
            Browse Challenges
          </Link>
          <a
            href="https://owasp.org/www-project-top-ten/"
            target="_blank"
            rel="noreferrer"
            className="border border-slate-700 hover:border-slate-500 text-slate-300 font-medium px-6 py-2.5 rounded-lg transition-colors"
          >
            OWASP Top 10
          </a>
        </div>
      </div>

      {/* How it works */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 mb-12">
        <h2 className="text-white font-semibold text-xl mb-6">How it works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { step: '01', title: 'Read the vulnerability', desc: 'Each challenge shows vulnerable code with a description of what\'s wrong and why it\'s dangerous.' },
            { step: '02', title: 'Fix it in the editor', desc: 'Edit the code directly in the Monaco editor — the same editor used in VS Code.' },
            { step: '03', title: 'Watch the attack run', desc: 'Your fix gets deployed in a Docker container. A real attack script runs against it. Pass or fail.' },
          ].map(({ step, title, desc }) => (
            <div key={step} className="flex gap-4">
              <span className="text-purple-400 font-mono text-sm font-bold shrink-0 mt-0.5">{step}</span>
              <div>
                <h3 className="text-white font-medium mb-1">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Categories */}
      <h2 className="text-white font-semibold text-xl mb-4">Categories</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {categories.map(({ name, icon, count, color }) => (
          <Link
            key={name}
            to={`/challenges?category=${encodeURIComponent(name)}`}
            className={`bg-slate-900 border rounded-lg p-4 text-center transition-colors ${color}`}
          >
            <div className="text-2xl mb-1">{icon}</div>
            <div className="text-white text-sm font-medium">{name}</div>
            <div className="text-slate-500 text-xs mt-0.5">{count} challenge{count !== 1 ? 's' : ''}</div>
          </Link>
        ))}
      </div>
    </div>
  )
}
