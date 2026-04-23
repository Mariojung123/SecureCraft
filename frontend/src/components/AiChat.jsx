import { useState, useEffect, useRef } from 'react'
import { sendChatMessage } from '../api'
import { TypingIndicator } from './ReportComponents'

const genId = () => (crypto.randomUUID ? genId() : Math.random().toString(36).slice(2))

export default function AiChat({ sessionId, report }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)
  const userHasInteracted = useRef(false)

  useEffect(() => {
    if (!userHasInteracted.current) return
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  useEffect(() => {
    if (!report) return
    const greeting = `I've analyzed your submission for the "${report.title}" challenge. ${
      report.vulnerability_explanation
        ? report.vulnerability_explanation
        : report.passed
          ? 'Your fix looks correct — the attack was successfully blocked.'
          : 'The vulnerability is still present in your code.'
    } What would you like to know more about?`
    setMessages([{ id: 'greeting', role: 'assistant', content: greeting }])
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const send = async (text) => {
    const trimmed = text.trim()
    if (!trimmed || typing) return

    const newHistory = [...messages]
    userHasInteracted.current = true
    setMessages(prev => [...prev, { id: genId(), role: 'user', content: trimmed }])
    setInput('')
    setTyping(true)

    try {
      const { reply, error } = await sendChatMessage(sessionId, trimmed, newHistory)
      setMessages(prev => [
        ...prev,
        { id: genId(), role: 'assistant', content: error ? `(AI unavailable: ${error})` : reply },
      ])
    } catch {
      setMessages(prev => [...prev, { id: genId(), role: 'assistant', content: '(Network error — please try again.)' }])
    } finally {
      setTyping(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  return (
    <section className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-purple-400 text-xl">🤖</span>
        <h2 className="text-white font-semibold text-base">Ask AI About This Challenge</h2>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="flex flex-col gap-3 p-4 overflow-y-auto" style={{ maxHeight: '400px' }}>
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words
                ${msg.role === 'user'
                  ? 'bg-purple-700 text-white rounded-br-sm'
                  : 'bg-slate-800 text-slate-200 rounded-bl-sm border border-slate-700/60'
                }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {typing && (
            <div className="flex justify-start">
              <div className="bg-slate-800 border border-slate-700/60 rounded-2xl rounded-bl-sm">
                <TypingIndicator />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-slate-800 p-3 flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={typing}
            placeholder="Ask a question about this vulnerability…"
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm
                       text-slate-200 placeholder-slate-500 outline-none
                       focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30
                       disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={() => send(input)}
            disabled={typing || !input.trim()}
            className="bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed
                       text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shrink-0"
          >
            Send
          </button>
        </div>
      </div>
    </section>
  )
}
