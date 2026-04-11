interface Props {
  severity: string
}

const styles: Record<string, string> = {
  high: 'bg-red-500/15 text-red-400 border border-red-500/20',
  medium: 'bg-orange-500/15 text-orange-400 border border-orange-500/20',
  low: 'bg-blue-400/15 text-blue-400 border border-blue-400/20',
}

export default function SeverityBadge({ severity }: Props) {
  const key = severity?.toLowerCase()
  const cls = styles[key] ?? styles.low
  return (
    <span className={`font-mono text-[10px] px-2 py-0.5 rounded uppercase tracking-wider whitespace-nowrap ${cls}`}>
      {severity}
    </span>
  )
}
