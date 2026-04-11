import { TopIssue } from '../types'
import SeverityBadge from './SeverityBadge'

interface Props {
  issues: TopIssue[]
}

export default function TopIssues({ issues }: Props) {
  return (
    <div className="bg-[#111] border border-[#222] rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-[#222] flex items-center justify-between">
        <div className="flex items-center gap-2 font-mono text-[11px] text-[#666] uppercase tracking-widest">
          <span className="w-1.5 h-1.5 rounded-full bg-[#ff5a5a]" />
          Top Issues
        </div>
        <span className="font-mono text-[13px] text-[#e8e8e8]">{issues.length} found</span>
      </div>
      <div className="p-5">
        {issues.length === 0 ? (
          <div className="text-center py-6 font-mono text-sm text-[#444]">No critical issues found</div>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {issues.map((issue, i) => (
              <div key={i} className="bg-[#1a1a1a] border border-[#222] rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <SeverityBadge severity={issue.severity} />
                  <span className="font-mono text-[10px] text-[#555] uppercase tracking-wider">{issue.category}</span>
                </div>
                <div className="text-sm font-medium text-[#e8e8e8] mb-2 leading-snug">{issue.title}</div>
                <div className="text-xs text-[#555] leading-relaxed">{issue.description}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
