import { useState, KeyboardEvent } from 'react'

interface Props {
  onAnalyze: (prompt: string) => void
  loading: boolean
}

export default function PromptInput({ onAnalyze, loading }: Props) {
  const [prompt, setPrompt] = useState('')

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      onAnalyze(prompt)
    }
  }

  return (
    <div className="mb-10">
      <div style={{ fontFamily: "'Instrument Serif', serif" }} className="text-center mb-8">
        <h1 className="text-5xl md:text-6xl tracking-tight leading-tight mb-3">
          Diagnose your{' '}
          <em className="text-[#e8ff5a]">system prompt</em>
        </h1>
        <p className="text-[#666] text-base max-w-md mx-auto leading-relaxed">
          Find contradictions, ambiguities, and coverage gaps before they silently break your LLM app.
        </p>
      </div>

      <div className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
        <div className="px-5 pt-4 font-mono text-[11px] text-[#666] uppercase tracking-widest">
          System Prompt
        </div>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Paste your system prompt here..."
          className="w-full min-h-[180px] bg-transparent outline-none px-5 py-3 font-mono text-sm text-[#e8e8e8] placeholder-[#333] resize-y leading-relaxed"
        />
        <div className="border-t border-[#222] px-5 py-3 flex items-center justify-between">
          <span className="font-mono text-[11px] text-[#444]">
            {prompt.length.toLocaleString()} characters · ⌘↵ to analyze
          </span>
          <button
            onClick={() => onAnalyze(prompt)}
            disabled={loading || !prompt.trim()}
            className="flex items-center gap-2 bg-[#e8ff5a] text-[#0a0a0a] font-semibold text-sm px-6 py-2 rounded-lg hover:bg-[#d4eb3a] transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Diagnosing...
              </>
            ) : (
              <>🩺 Diagnose</>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
