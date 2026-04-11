import { AnalysisResult } from '../types'
import ScoreCard from './ScoreCard'
import TopIssues from './TopIssues'
import QuickFixes from './QuickFixes'
import ClarityCard from './ClarityCard'
import RedundancyCard from './RedundancyCard'
import IssueList from './IssueList'

interface Props {
  data: AnalysisResult
}

export default function Results({ data }: Props) {
  return (
    <div className="flex flex-col gap-4 mt-8">
      <ScoreCard data={data} />
      <TopIssues issues={data.top_issues} />
      <QuickFixes fixes={data.quick_fixes} />
      <div className="grid grid-cols-2 gap-4">
        <ClarityCard clarity={data.clarity} />
        <RedundancyCard redundancy={data.redundancy} />
      </div>
      <IssueList
        title="Contradictions"
        dot="dot-red"
        count={data.contradictions.length}
        items={data.contradictions.map(c => ({
          phrase: c.sentence_1,
          sub: c.sentence_2,
          reason: c.reason,
          severity: c.severity,
        }))}
        emptyMsg="No contradictions found"
      />
      <IssueList
        title="Ambiguous Phrases"
        dot="dot-orange"
        count={data.ambiguous_phrases.length}
        items={data.ambiguous_phrases.map(a => ({
          phrase: `"${a.phrase}"`,
          reason: a.reason,
          severity: a.severity,
          rewrite: a.rewrite,
        }))}
        emptyMsg="No ambiguous phrases found"
      />
      <IssueList
        title="Coverage Gaps"
        dot="dot-blue"
        count={data.coverage_gaps.length}
        items={data.coverage_gaps.map(g => ({
          phrase: g.gap,
          reason: g.example,
          severity: g.impact,
        }))}
        emptyMsg="No coverage gaps found"
      />
    </div>
  )
}
