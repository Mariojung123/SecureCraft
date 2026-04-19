export default function HighlightedCode({ code = '', vulnerableLines = [] }) {
  const vulnSet = new Set(vulnerableLines)
  const lines = code.split('\n')

  return (
    <div className="rounded-lg border border-slate-700 overflow-auto text-xs font-mono leading-relaxed"
         style={{ maxHeight: '420px' }}>
      <table className="w-full border-collapse">
        <tbody>
          {lines.map((line, i) => {
            const lineNum = i + 1
            const isVuln = vulnSet.has(lineNum)
            return (
              <tr key={lineNum} className={isVuln ? 'bg-red-950/60' : 'hover:bg-slate-800/30'}>
                <td className={`select-none text-right pr-4 pl-3 py-0.5 border-r w-10 shrink-0
                               ${isVuln ? 'border-red-700/60 text-red-500' : 'border-slate-700/50 text-slate-600'}`}>
                  {lineNum}
                </td>
                <td className={`pl-4 pr-3 py-0.5 whitespace-pre
                               ${isVuln ? 'text-red-300' : 'text-slate-300'}`}>
                  {isVuln && (
                    <span className="mr-2 text-red-500 text-[10px] font-sans font-bold
                                     bg-red-900/50 border border-red-700/50 rounded px-1 py-px">
                      VULN
                    </span>
                  )}
                  {line || ' '}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
