import { ClarityReport } from '../types'

interface Props {
  clarity: ClarityReport
}

export default function ClarityCard({ clarity }: Props) {
  return (
    <div className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[#222] flex items-center justify-between">
        <div className="flex items-center gap-2 font-mono text-[11px] text-[#666] uppercase tracking-widest">
          <span className="w-1.5 h-1.5 rounded-full bg-[#e8ff5a]" />
          Clarity
        </div>
        <span className="font-mono text-[13px] text-[#e8e8e8]">{clarity.score} / 100</span>
      </div>
      <div className="p-5">
        <div className="mb-4">
          <div className="h-1 bg-[#222] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-[#e8ff5a] transition-all duration-1000"
              style={{ width: `${clarity.score}%` }}
            />
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {[
            { label: 'Avg sentence', val: `${clarity.avg_sentence_length} words` },
            { label: 'Passive voice', val: clarity.passive_voice_count },
            { label: 'Weak modals', val: clarity.weak_modal_count },
          ].map(({ label, val }) => (
            <div key={label} className="font-mono text-[11px] px-3 py-1.5 bg-[#1a1a1a] border border-[#222] rounded-full text-[#555]">
              {label} <span className="text-[#e8e8e8]">{val}</span>
            </div>
          ))}
          {clarity.hedge_phrases_found.map(p => (
            <div key={p} className="font-mono text-[11px] px-3 py-1.5 bg-[#1a1a1a] border border-[#222] rounded-full text-[#555]">
              ⚠ <span className="text-[#e8ff5a]">{p}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
