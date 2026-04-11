export default function Header() {
  return (
    <header className="border-b border-[#222] sticky top-0 z-50 backdrop-blur-md bg-[#0a0a0a]/90">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl">🩺</span>
          <span style={{ fontFamily: "'Instrument Serif', serif" }} className="text-xl text-[#e8ff5a]">
            Dr<span className="text-[#e8e8e8]">Prompt</span>
          </span>
        </div>
        <span className="font-mono text-xs text-[#666]">
          A Doctor for your system prompts
        </span>
      </div>
    </header>
  )
}
