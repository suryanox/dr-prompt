import { QuickFix } from '../types'

interface Props {
  fixes: QuickFix[]
}

export default function QuickFixes({ fixes }: Props) {
  return (
    <div className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[#222] flex items-center justify-between">
        <div className="flex items-center gap-2 font-mono text-[11px] text-[#666] uppercase tracking-widest">
          <span className="w-1.5 h-1.5 rounded-full bg-[#5aff8a]" />
          Quick Fixes
        </div>
        <span className="font-mono text-[13px] text-[#e8e8e8]">{fixes.length} available</span>
      </div>
      <div className="p-5 flex flex-col gap-3">
        {fixes.length === 0 ? (
          <div className="text-center py-6 font-mono text-sm text-[#444]">No quick fixes needed</div>
        ) : (
          fixes.map((fix, i) => (
            <div key={i} className="bg-[#1a1a1a] border border-[#222] rounded-xl p-4">
              <div className="mb-2">
                <span className="font-mono text-[10px] text-[#555] bg-[#222] px-2 py-1 rounded uppercase tracking-wider">
                  {fix.category}
                </span>
              </div>
              <div className="text-xs text-[#555] leading-relaxed mb-3">{fix.issue}</div>
              <div className="font-mono text-xs text-[#5aff8a] bg-[#5aff8a]/5 border border-[#5aff8a]/15 rounded-lg p-3 leading-relaxed">
                {fix.fix}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
