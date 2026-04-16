import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import ChallengeCard from '../components/ChallengeCard'
import { getChallenges } from '../api'

export default function ChallengeList() {
  const [challenges, setChallenges] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchParams, setSearchParams] = useSearchParams()

  const activeCategory = searchParams.get('category') || 'All'

  useEffect(() => {
    getChallenges()
      .then(setChallenges)
      .catch(() => setError('Failed to load challenges. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const categories = ['All', ...new Set(challenges.map(c => c.category))]
  const filtered = activeCategory === 'All'
    ? challenges
    : challenges.filter(c => c.category === activeCategory)

  const setCategory = (cat) => {
    if (cat === 'All') {
      setSearchParams({})
    } else {
      setSearchParams({ category: cat })
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-1">Challenges</h1>
        <p className="text-slate-400">Fix vulnerabilities and test your fixes against real attacks.</p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
              activeCategory === cat
                ? 'bg-purple-600 border-purple-500 text-white'
                : 'border-slate-700 text-slate-400 hover:border-slate-500 hover:text-white'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading && (
        <div className="text-center py-20 text-slate-500">Loading challenges...</div>
      )}

      {error && (
        <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(challenge => (
            <ChallengeCard key={challenge.id} challenge={challenge} />
          ))}
          {filtered.length === 0 && (
            <p className="text-slate-500 col-span-3 py-10 text-center">No challenges in this category yet.</p>
          )}
        </div>
      )}
    </div>
  )
}
