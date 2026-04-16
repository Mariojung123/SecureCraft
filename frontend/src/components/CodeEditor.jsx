import Editor from '@monaco-editor/react'

export default function CodeEditor({ value, onChange, language = 'python', readOnly = false }) {
  return (
    <div className="rounded-lg overflow-hidden border border-slate-700">
      <Editor
        height="420px"
        language={language}
        value={value}
        onChange={onChange}
        theme="vs-dark"
        options={{
          fontSize: 13,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          lineNumbers: 'on',
          readOnly,
          automaticLayout: true,
          padding: { top: 12, bottom: 12 },
        }}
      />
    </div>
  )
}
