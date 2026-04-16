const difficultyColor = {
  Easy: 'bg-green-900/50 text-green-400 border border-green-700/50',
  Medium: 'bg-yellow-900/50 text-yellow-400 border border-yellow-700/50',
  Hard: 'bg-red-900/50 text-red-400 border border-red-700/50',
}

const categoryColor = {
  'SQL Injection': 'bg-blue-900/40 text-blue-300 border border-blue-700/40',
  'XSS': 'bg-orange-900/40 text-orange-300 border border-orange-700/40',
  'Command Injection': 'bg-red-900/40 text-red-300 border border-red-700/40',
  'Path Traversal': 'bg-yellow-900/40 text-yellow-300 border border-yellow-700/40',
  'Secrets': 'bg-pink-900/40 text-pink-300 border border-pink-700/40',
  'Cryptography': 'bg-purple-900/40 text-purple-300 border border-purple-700/40',
  'Access Control': 'bg-cyan-900/40 text-cyan-300 border border-cyan-700/40',
  'Auth': 'bg-indigo-900/40 text-indigo-300 border border-indigo-700/40',
}

export function DifficultyBadge({ difficulty }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${difficultyColor[difficulty] || 'bg-slate-800 text-slate-400'}`}>
      {difficulty}
    </span>
  )
}

export function CategoryBadge({ category }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${categoryColor[category] || 'bg-slate-800 text-slate-400'}`}>
      {category}
    </span>
  )
}
