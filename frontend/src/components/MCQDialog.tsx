import { useState, useEffect, useRef } from 'react'
import { X, HelpCircle, Check, ArrowRight } from 'lucide-react'

interface MCQOption {
  id: number
  label: string
  value: string
  explanation: string
}

interface MCQDialogData {
  id: string
  question: string
  options: MCQOption[]
  context_hint: string | null
  default_selection: number
  allow_custom_input: boolean
}

interface Props {
  dialog: MCQDialogData
  fieldName: string
  currentValue: string
  onAnswer: (value: string, optionId: number | null) => void
  onClose: () => void
}

export default function MCQDialog({ dialog, fieldName, currentValue, onAnswer, onClose }: Props) {
  const [selected, setSelected] = useState(dialog.default_selection)
  const [customValue, setCustomValue] = useState('')
  const [isCustom, setIsCustom] = useState(false)
  const [step, setStep] = useState(0)
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'Enter') handleSubmit()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [selected, isCustom, customValue])

  const handleSubmit = () => {
    if (isCustom && customValue.trim()) {
      onAnswer(customValue.trim(), null)
    } else if (!isCustom) {
      const opt = dialog.options[selected]
      onAnswer(opt.value, opt.id)
    }
  }

  const options = dialog.options || []
  const showCustom = dialog.allow_custom_input && (isCustom || selected === options.length - 1)

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={e => e.target === overlayRef.current && onClose()}
    >
      <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-gray-800 flex items-start gap-3">
          <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
            <HelpCircle className="w-5 h-5 text-blue-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-base font-semibold text-gray-100">{dialog.question || `What is the correct ${fieldName}?`}</h2>
            {dialog.context_hint && (
              <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-blue-400 rounded-full inline-block" />
                {dialog.context_hint}
              </p>
            )}
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Current value display */}
        <div className="px-5 py-3 bg-gray-800/50 border-b border-gray-800">
          <p className="text-xs text-gray-500">AI extracted value (confidence: low)</p>
          <p className="text-sm text-yellow-300 font-mono mt-0.5">{currentValue}</p>
        </div>

        {/* Options */}
        <div className="px-5 py-4 space-y-2 max-h-64 overflow-y-auto">
          {options.map((option, idx) => (
            <button
              key={option.id}
              onClick={() => { setSelected(idx); setIsCustom(false) }}
              className={`w-full text-left p-3 rounded-xl border transition-all ${
                selected === idx && !isCustom
                  ? 'border-blue-500 bg-blue-500/10 ring-1 ring-blue-500'
                  : 'border-gray-700 bg-gray-800 hover:border-gray-600'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                  selected === idx && !isCustom ? 'border-blue-400 bg-blue-400' : 'border-gray-600'
                }`}>
                  {selected === idx && !isCustom && <Check className="w-3 h-3 text-white" />}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-200">{option.label}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{option.explanation}</p>
                </div>
              </div>
              {idx === dialog.default_selection && !isCustom && (
                <span className="inline-block mt-1.5 ml-8 text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/50">
                  Recommended
                </span>
              )}
            </button>
          ))}

          {dialog.allow_custom_input && (
            <button
              onClick={() => { setIsCustom(true); setSelected(-1) }}
              className={`w-full text-left p-3 rounded-xl border transition-all ${
                isCustom
                  ? 'border-purple-500 bg-purple-500/10 ring-1 ring-purple-500'
                  : 'border-gray-700 bg-gray-800 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                  isCustom ? 'border-purple-400 bg-purple-400' : 'border-gray-600'
                }`}>
                  {isCustom && <Check className="w-3 h-3 text-white" />}
                </div>
                <span className="text-sm text-gray-300">Enter custom value</span>
              </div>
            </button>
          )}

          {showCustom && (
            <div className="pl-8 animate-[fadeIn_0.2s_ease-in-out]">
              <input
                type="text"
                value={customValue}
                onChange={e => setCustomValue(e.target.value)}
                placeholder={`Enter ${fieldName}`}
                className="w-full p-2.5 bg-gray-800 border border-gray-600 rounded-lg text-sm text-gray-100 placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                autoFocus
              />
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="px-5 py-3 border-t border-gray-800 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3 py-2 text-sm text-gray-400 hover:text-gray-200 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
          >
            Skip
          </button>
          <button
            onClick={handleSubmit}
            disabled={isCustom && !customValue.trim()}
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Confirm <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}
