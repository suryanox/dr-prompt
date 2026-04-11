import { RedundancyReport } from '../types'

interface Props {
  redundancy: RedundancyReport
}

export default function RedundancyCard({ redundancy }: Props) {
  return (
    <div className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[#222] flex items-center justify-between">
        <div className="flex items-center gap-2 font-mono text-[11px] text-[#666] uppercase tracking-widest">
          <span className="w-1.5 h-1.5 rounded-full bg-[#ff9a3c]" />
          Redundancy
        </div>
        <span className="font-mono text-[13px] text-[#e8e8e8]">{redundancy.score} / 100</span>
      </div>
      <div className="p-5">
        <div className="mb-4">
          <div className="h-1 bg-[#222] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-[#ff9a3c] transition-all duration-1000"
              style={{ width: `${redundancy.score}%` }}
            />
          </div>
        </div>
        {redundancy.redundant_pairs.length === 0 ? (
          <div className="text-center py-4 font-mono text-sm text-[#444]">No redundant sentences detected</div>
        ) : (
          <div className="flex flex-col gap-3">
            {redundancy.redundant_pairs.map((pair, i) => (
              <div key={i} className="bg-[#1a1a1a] border border-[#222] rounded-xl p-3">
                <div className="flex flex-col gap-2 mb-2">
                  <div className="font-mono text-xs text-[#e8e8e8] bg-[#222] px-3 py-2 rounded-lg">{pair.sentence_1}</div>
                  <div className="font-mono text-xs text-[#e8e8e8] bg-[#222] px-3 py-2 rounded-lg">{pair.sentence_2}</div>
                </div>
                <div className="font-mono text-[11px] text-[#ff9a3c]">Similarity: {pair.similarity}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
