import { Link } from 'react-router-dom'
import { DifficultyBadge, CategoryBadge } from './Badge'

export default function ChallengeCard({ challenge }) {
  return (
    <Link
      to={`/challenges/${challenge.id}`}
      className="block bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-purple-700/60 hover:bg-slate-800/60 transition-all group"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="text-white font-medium text-base leading-snug group-hover:text-purple-300 transition-colors">
          {challenge.title}
        </h3>
        <DifficultyBadge difficulty={challenge.difficulty} />
      </div>
      <p className="text-slate-400 text-sm leading-relaxed line-clamp-2 mb-4">
        {challenge.description}
      </p>
      <CategoryBadge category={challenge.category} />
    </Link>
  )
}
