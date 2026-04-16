import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import ChallengeList from './pages/ChallengeList'
import ChallengeDetail from './pages/ChallengeDetail'
import Sandbox from './pages/Sandbox'
import Report from './pages/Report'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-[#0f1117] text-slate-200">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/challenges" element={<ChallengeList />} />
            <Route path="/challenges/:id" element={<ChallengeDetail />} />
            <Route path="/sandbox/:session_id" element={<Sandbox />} />
            <Route path="/report/:session_id" element={<Report />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
