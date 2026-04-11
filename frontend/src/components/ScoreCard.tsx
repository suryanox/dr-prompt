import { AnalysisResult } from '../types'

interface Props {
  data: AnalysisResult
}

const gradeColor: Record<string, string> = {
  A: '#5aff8a',
  B: '#5ab4ff',
  C: '#e8ff5a',
  D: '#ff9a3c',
  F: '#ff5a5a',
}

export default function ScoreCard({ data }: Props) {
  const color = gradeColor[data.grade] ?? '#666'
  const s = data.stats

  return (
    <div className="bg-[#111] border border-[#222] rounded-2xl p-8 grid grid-cols-[auto_1fr_auto] gap-8 items-center">
      <div
        className="w-24 h-24 rounded-full flex flex-col items-center justify-center border-2"
        style={{ borderColor: color }}
      >
        <span className="text-3xl leading-none" style={{ fontFamily: "'Instrument Serif', serif", color }}>
          {data.overall_score}
        </span>
        <span className="font-mono text-[10px] text-[#666] uppercase tracking-wider mt-1">/100</span>
      </div>

      <div>
        <div
          className="text-5xl leading-none mb-1"
          style={{ fontFamily: "'Instrument Serif', serif", color }}
        >
          {data.grade}
        </div>
        <div className="text-lg text-[#666] mb-2">{data.verdict}</div>
        <div className="text-sm text-[#555] leading-relaxed max-w-lg">{data.summary}</div>
      </div>

      <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-right">
        {[
          { val: s.word_count, label: 'Words' },
          { val: s.sentence_count, label: 'Sentences' },
          { val: s.instruction_count, label: 'Instructions' },
          { val: `~${s.estimated_tokens}`, label: 'Tokens' },
        ].map(({ val, label }) => (
          <div key={label}>
            <span className="block font-mono text-xl text-[#e8e8e8]">{val}</span>
            <span className="font-mono text-[11px] text-[#555] uppercase tracking-wider">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
