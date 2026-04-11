import { useState } from 'react'
import { AnalysisResult } from './types'
import Header from './components/Header'
import PromptInput from './components/PromptInput'
import Results from './components/Results'

export default function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function analyze(prompt: string) {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system_prompt: prompt }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || 'Unknown error')
      }
      const data: AnalysisResult = await res.json()
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#e8e8e8]" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <Header />
      <main className="max-w-5xl mx-auto px-6 py-12">
        <PromptInput onAnalyze={analyze} loading={loading} />
        {error && (
          <div className="mt-4 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 font-mono text-sm">
            Error: {error}
          </div>
        )}
        {result && <Results data={result} />}
      </main>
    </div>
  )
}
