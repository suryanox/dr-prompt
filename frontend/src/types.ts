export interface RedundantPair {
  sentence_1: string
  sentence_2: string
  similarity: number
}

export interface Contradiction {
  sentence_1: string
  sentence_2: string
  reason: string
  severity: string
}

export interface AmbiguousPhrase {
  phrase: string
  reason: string
  suggestion: string
  rewrite: string
  severity: string
}

export interface CoverageGap {
  gap: string
  example: string
  impact: string
}

export interface QuickFix {
  issue: string
  fix: string
  category: string
}

export interface TopIssue {
  title: string
  description: string
  severity: string
  category: string
}

export interface ClarityReport {
  score: number
  avg_sentence_length: number
  hedge_phrases_found: string[]
  weak_modal_count: number
  passive_voice_count: number
}

export interface RedundancyReport {
  score: number
  redundant_pairs: RedundantPair[]
  redundancy_percent: number
}

export interface PromptStats {
  word_count: number
  sentence_count: number
  instruction_count: number
  avg_words_per_sentence: number
  estimated_tokens: number
}

export interface AnalysisResult {
  overall_score: number
  grade: string
  verdict: string
  summary: string
  stats: PromptStats
  top_issues: TopIssue[]
  quick_fixes: QuickFix[]
  clarity: ClarityReport
  redundancy: RedundancyReport
  contradictions: Contradiction[]
  ambiguous_phrases: AmbiguousPhrase[]
  coverage_gaps: CoverageGap[]
}
