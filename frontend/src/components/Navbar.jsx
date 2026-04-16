import { Link, NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="border-b border-slate-800 bg-[#0f1117] sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-semibold text-white text-lg">
          <span className="text-purple-400">&#9964;</span>
          SecureCraft
        </Link>
        <div className="flex items-center gap-6 text-sm">
          <NavLink
            to="/challenges"
            className={({ isActive }) =>
              isActive ? 'text-purple-400 font-medium' : 'text-slate-400 hover:text-white transition-colors'
            }
          >
            Challenges
          </NavLink>
        </div>
      </div>
    </nav>
  )
}
