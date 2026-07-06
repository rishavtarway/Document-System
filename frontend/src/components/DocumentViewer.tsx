import { useState, useCallback, useEffect } from 'react'
import {
  Loader2, RefreshCw, Download, FileText, CheckCircle,
  AlertTriangle, XCircle, HelpCircle,
} from 'lucide-react'
import { getExtractions, submitCorrection, exportDocument, getDocumentStatus } from '../services/api'
import MCQDialog from './MCQDialog'

interface Props {
  documentId: string
  onUpdated: () => void
}

const CONFIDENCE_COLOR = (c: number) =>
  c >= 0.8 ? 'text-green-400' : c >= 0.5 ? 'text-yellow-400' : 'text-red-400'

const CONFIDENCE_BG = (c: number) =>
  c >= 0.8 ? 'bg-green-500/10 border-green-500/30' : c >= 0.5 ? 'bg-yellow-500/10 border-yellow-500/30' : 'bg-red-500/10 border-red-500/30'

export default function DocumentViewer({ documentId, onUpdated }: Props) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [edits, setEdits] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState(false)
  const [activeMcq, setActiveMcq] = useState<any>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [status, extractions] = await Promise.all([
        getDocumentStatus(documentId),
        getExtractions(documentId),
      ])
      setData({ status, extractions })
    } catch (e) {
      setError('Failed to load document data')
    } finally {
      setLoading(false)
    }
  }, [documentId])

  useEffect(() => { load() }, [load])

  const handleExport = useCallback(async () => {
    const json = await exportDocument(documentId)
    const blob = new Blob([JSON.stringify(json, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${data?.status?.filename || 'document'}_export.json`
    a.click()
    URL.revokeObjectURL(url)
  }, [documentId, data])

  const handleSaveAll = useCallback(async () => {
    setSaving(true)
    try {
      const corrections = Object.entries(edits).map(([fieldKey, value]) => ({
        extraction_id: fieldKey,
        corrected_value: value,
      }))
      if (corrections.length > 0) {
        await submitCorrection(documentId, corrections)
        setEdits({})
        onUpdated()
        load()
      }
    } finally {
      setSaving(false)
    }
  }, [documentId, edits, onUpdated, load])

  const handleMcqAnswer = useCallback(async (extractionId: string, value: string, optionId: number | null) => {
    setEdits(prev => ({ ...prev, [extractionId]: value }))
    setActiveMcq(null)
    // Auto-save MCQ answers
    await submitCorrection(documentId, [{
      extraction_id: extractionId,
      corrected_value: value,
      ...(optionId != null ? { selected_mcq_option: optionId } : {}),
    }])
    onUpdated()
    load()
  }, [documentId, onUpdated, load])

  if (loading) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700 rounded-xl p-6 text-red-300">
        {error}
        <button onClick={load} className="ml-2 underline">Retry</button>
      </div>
    )
  }

  const extractions = data?.extractions?.extractions || []
  const docStatus = data?.status
  const hasMcq = extractions.some((e: any) => e.mcq_dialogs?.length > 0 && !e.corrected_value)
  const needsReview = extractions.some((e: any) => e.needs_review && !e.corrected_value)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-blue-400" />
            <div>
              <h2 className="text-base font-semibold text-gray-100">{docStatus?.filename}</h2>
              <div className="flex items-center gap-2 mt-1">
                {docStatus?.document_type && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-300 border border-gray-700">
                    {docStatus.document_type.replace('_', ' ')}
                  </span>
                )}
                <span className={`text-xs font-medium ${CONFIDENCE_COLOR(docStatus?.type_confidence || 0)}`}>
                  {Math.round((docStatus?.type_confidence || 0) * 100)}% confidence
                </span>
                <span className="text-xs text-gray-500 capitalize">Status: {docStatus?.status}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={load} className="flex items-center gap-1 px-2.5 py-1.5 text-xs text-gray-400 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors">
              <RefreshCw className="w-3 h-3" /> Refresh
            </button>
            <button onClick={handleExport} className="flex items-center gap-1 px-2.5 py-1.5 text-xs text-gray-400 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors">
              <Download className="w-3 h-3" /> Export
            </button>
          </div>
        </div>
      </div>

      {/* Review banner */}
      {hasMcq && (
        <div className="bg-yellow-900/30 border border-yellow-700/50 rounded-xl p-3 flex items-center gap-2 text-yellow-300 text-sm">
          <HelpCircle className="w-4 h-4 flex-shrink-0" />
          Some fields need your input. Review and correct below.
        </div>
      )}

      {/* Extractions */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl">
        <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-200">Extracted Fields</h3>
          {Object.keys(edits).length > 0 && (
            <button
              onClick={handleSaveAll}
              disabled={saving}
              className="flex items-center gap-1 px-3 py-1 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : null}
              Save {Object.keys(edits).length} correction{Object.keys(edits).length > 1 ? 's' : ''}
            </button>
          )}
        </div>
        <div className="divide-y divide-gray-800">
          {extractions.length === 0 && (
            <div className="p-6 text-center text-gray-500 text-sm">No extractions available</div>
          )}
          {extractions.map((ext: any) => (
            <ExtractionRow
              key={ext.id}
              extraction={ext}
              editValue={edits[ext.id] ?? ext.corrected_value ?? ext.extracted_value ?? ''}
              onEdit={(v) => setEdits(prev => ({ ...prev, [ext.id]: v }))}
              onOpenMcq={() => setActiveMcq(ext)}
            />
          ))}
        </div>
      </div>

      {/* MCQ Dialog */}
      {activeMcq && activeMcq.mcq_dialogs?.[0] && (
        <MCQDialog
          dialog={activeMcq.mcq_dialogs[0]}
          fieldName={activeMcq.field_name}
          currentValue={activeMcq.extracted_value}
          onAnswer={(value, optionId) => handleMcqAnswer(activeMcq.id, value, optionId)}
          onClose={() => setActiveMcq(null)}
        />
      )}
    </div>
  )
}

function ExtractionRow({ extraction, editValue, onEdit, onOpenMcq }: any) {
  const mcq = extraction.mcq_dialogs?.[0]
  const isReviewed = !!extraction.corrected_value
  
  return (
    <div className={`px-4 py-3 ${extraction.needs_review ? 'bg-yellow-900/10' : ''} ${isReviewed ? 'bg-green-900/10' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-300">{extraction.field_name.replace(/_/g, ' ')}</span>
            {extraction.is_gibberish && (
              <span className="text-[10px] px-1 py-0.5 rounded bg-red-900/50 text-red-300 border border-red-700">gibberish</span>
            )}
            {isReviewed && <CheckCircle className="w-3 h-3 text-green-400" />}
            {extraction.needs_review && !isReviewed && (
              <AlertTriangle className="w-3 h-3 text-yellow-400" />
            )}
          </div>
          <div className="mt-1 flex items-center gap-2">
            <input
              type="text"
              value={editValue}
              onChange={e => onEdit(e.target.value)}
              className={`flex-1 text-sm bg-transparent border-b ${
                editValue !== extraction.extracted_value && !isReviewed
                  ? 'border-yellow-600 text-yellow-200'
                  : isReviewed
                  ? 'border-green-600 text-green-200'
                  : 'border-transparent text-gray-100'
              } focus:border-blue-500 focus:outline-none px-1 py-0.5`}
            />
            {mcq && !isReviewed && (
              <button
                onClick={onOpenMcq}
                className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 bg-blue-900/30 px-2 py-1 rounded-lg border border-blue-700"
              >
                <HelpCircle className="w-3 h-3" /> Clarify
              </button>
            )}
          </div>
        </div>
        <div className={`ml-3 text-right ${CONFIDENCE_BG(extraction.confidence_score)} border rounded-lg px-2 py-1`}>
          <span className={`text-xs font-bold ${CONFIDENCE_COLOR(extraction.confidence_score)}`}>
            {Math.round(extraction.confidence_score * 100)}%
          </span>
          {extraction.reasoning && (
            <p className="text-[10px] text-gray-500 mt-0.5 max-w-[120px] truncate" title={extraction.reasoning}>
              {extraction.reasoning}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
