import { Brain, Cpu, FileText } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white">AI Document Intelligence</h1>
          <p className="text-xs text-gray-400 flex items-center gap-2">
            <FileText className="w-3 h-3" />
            Classification · Extraction · Validation · Learning
            <Cpu className="w-3 h-3 ml-1" />
          </p>
        </div>
      </div>
    </header>
  )
}
