import SeverityBadge from './SeverityBadge'

interface IssueItem {
  phrase: string
  sub?: string
  reason: string
  severity: string
  rewrite?: string
}

interface Props {
  title: string
  dot: string
  count: number
  items: IssueItem[]
  emptyMsg: string
}

const dotColors: Record<string, string> = {
  'dot-red': '#ff5a5a',
  'dot-orange': '#ff9a3c',
  'dot-blue': '#5ab4ff',
}

export default function IssueList({ title, dot, count, items, emptyMsg }: Props) {
  return (
    <div className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[#222] flex items-center justify-between">
        <div className="flex items-center gap-2 font-mono text-[11px] text-[#666] uppercase tracking-widest">
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: dotColors[dot] ?? '#666' }} />
          {title}
        </div>
        <span className="font-mono text-[13px] text-[#e8e8e8]">{count} found</span>
      </div>
      <div className="p-5 flex flex-col gap-3">
        {items.length === 0 ? (
          <div className="text-center py-6 font-mono text-sm text-[#444]">✓ {emptyMsg}</div>
        ) : (
          items.map((item, i) => (
            <div key={i} className="bg-[#1a1a1a] border border-[#222] rounded-xl p-4">
              <div className="flex items-start justify-between gap-3 mb-2">
                <span className="font-mono text-xs text-[#e8ff5a] flex-1 leading-relaxed">{item.phrase}</span>
                <SeverityBadge severity={item.severity} />
              </div>
              {item.sub && (
                <div className="font-mono text-xs text-[#e8ff5a] mb-2 leading-relaxed">{item.sub}</div>
              )}
              <div className="text-xs text-[#555] leading-relaxed mb-2">{item.reason}</div>
              {item.rewrite && (
                <>
                  <div className="font-mono text-[10px] text-[#444] uppercase tracking-wider mb-1">Rewrite →</div>
                  <div className="font-mono text-xs text-[#5aff8a] bg-[#5aff8a]/5 border border-[#5aff8a]/15 rounded-lg p-3 leading-relaxed">
                    {item.rewrite}
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
