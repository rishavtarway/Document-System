import { useState, useCallback } from 'react'
import {
  CheckCircle, XCircle, AlertTriangle, RefreshCw, Download,
  Save, FileText, Loader2, ChevronDown, ChevronRight,
} from 'lucide-react'
import { processDocument, correctDocument, exportDocument } from '../api/documents'
import type { DocumentResponse } from '../types'

interface Props {
  doc: DocumentResponse
  onUpdated: (doc: DocumentResponse) => void
}

const TYPE_BADGES: Record<string, string> = {
  invoice: 'bg-green-100 text-green-700',
  purchase_order: 'bg-blue-100 text-blue-700',
  contract: 'bg-purple-100 text-purple-700',
  resume: 'bg-orange-100 text-orange-700',
  unknown: 'bg-gray-100 text-gray-600',
}

const CONFIDENCE_BADGE = (c: number) =>
  c >= 0.8 ? 'text-green-600 bg-green-50' : c >= 0.6 ? 'text-yellow-600 bg-yellow-50' : 'text-red-600 bg-red-50'

export default function DocumentViewer({ doc, onUpdated }: Props) {
  const [processing, setProcessing] = useState(false)
  const [edits, setEdits] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState(false)
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set())

  const handleReprocess = useCallback(async () => {
    setProcessing(true)
    try {
      const updated = await processDocument(doc.id)
      onUpdated(updated)
    } finally {
      setProcessing(false)
    }
  }, [doc.id, onUpdated])

  const handleSave = useCallback(async () => {
    setSaving(true)
    try {
      const corrections = Object.entries(edits).map(([field, value]) => ({
        field_path: field,
        corrected_value: value,
      }))
      if (corrections.length > 0) {
        const updated = await correctDocument(doc.id, corrections)
        onUpdated(updated)
      }
      setEdits({})
    } finally {
      setSaving(false)
    }
  }, [doc.id, edits, onUpdated])

  const handleExport = useCallback(async () => {
    const data = await exportDocument(doc.id)
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${doc.filename}_export.json`
    a.click()
    URL.revokeObjectURL(url)
  }, [doc.id, doc.filename])

  const data = doc.extraction?.data ?? {}
  const validations = doc.extraction?.validations ?? []
  const confidence = doc.extraction?.confidence ?? 0
  const isEditable = doc.status === 'extracted' || doc.status === 'validated'

  const toggleCollapse = (key: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-blue-500" />
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{doc.filename}</h2>
              <div className="flex items-center gap-2 mt-1">
                {doc.document_type && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      TYPE_BADGES[doc.document_type] || TYPE_BADGES.unknown
                    }`}
                  >
                    {doc.document_type.replace('_', ' ')}
                  </span>
                )}
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${CONFIDENCE_BADGE(confidence)}`}>
                  {Math.round(confidence * 100)}% confidence
                </span>
                <span className="text-xs text-gray-400 capitalize">Status: {doc.status}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReprocess}
              disabled={processing}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              {processing ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <RefreshCw className="w-3.5 h-3.5" />
              )}
              Reprocess
            </button>
            <button
              onClick={handleExport}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Validations */}
      {validations.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Validation Results</h3>
          <div className="space-y-2">
            {validations.map((v, i) => (
              <div
                key={i}
                className={`flex items-start gap-2 p-2.5 rounded-lg text-sm ${
                  v.status === 'error' ? 'bg-red-50 text-red-700' :
                  v.status === 'warning' ? 'bg-yellow-50 text-yellow-700' :
                  'bg-green-50 text-green-700'
                }`}
              >
                {v.status === 'error' ? (
                  <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                ) : v.status === 'warning' ? (
                  <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                ) : (
                  <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <span className="font-medium">{v.field}</span>
                  {v.message && <span>: {v.message}</span>}
                  {v.suggested_value && (
                    <span className="block text-xs mt-0.5">
                      Suggested: <code className="bg-white/50 px-1 rounded">{v.suggested_value}</code>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Data */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700">Extracted Data</h3>
          {isEditable && (
            <p className="text-xs text-gray-400 mt-0.5">
              You can edit fields below. Click a value to correct it, then save.
            </p>
          )}
        </div>
        <div className="p-4 space-y-1">
          {renderFields(data, '', 0, collapsed, toggleCollapse, edits, setEdits, isEditable)}
          {Object.keys(data).length === 0 && (
            <p className="text-sm text-gray-400 text-center py-4">No data extracted yet</p>
          )}
          {isEditable && Object.keys(edits).length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-end">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                Save Corrections ({Object.keys(edits).length})
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function renderFields(
  data: unknown,
  prefix: string,
  depth: number,
  collapsed: Set<string>,
  toggleCollapse: (key: string) => void,
  edits: Record<string, string>,
  setEdits: React.Dispatch<React.SetStateAction<Record<string, string>>>,
  editable: boolean,
): React.ReactNode {
  if (depth > 4) return <span className="text-xs text-gray-400">(nested data)</span>

  if (data === null || data === undefined) {
    return <span className="text-gray-300 italic">null</span>
  }

  if (Array.isArray(data)) {
    if (data.length === 0) return <span className="text-gray-300 italic">empty list</span>
    return (
      <div className="space-y-1">
        {data.map((item, i) => (
          <div key={i} className="ml-4 border-l border-gray-200 pl-3">
            <span className="text-xs text-gray-400">[{i}]</span>
            {renderFields(item, `${prefix}[${i}]`, depth + 1, collapsed, toggleCollapse, edits, setEdits, editable)}
          </div>
        ))}
      </div>
    )
  }

  if (typeof data === 'object') {
    const entries = Object.entries(data as Record<string, unknown>)
    if (entries.length === 0) return <span className="text-gray-300 italic">empty</span>

    return (
      <div className="space-y-0.5">
        {entries.map(([key, value]) => {
          const fieldKey = prefix ? `${prefix}.${key}` : key
          const isCollapsible = value && typeof value === 'object' && !Array.isArray(value)
          const isCollapsed = collapsed.has(fieldKey)

          return (
            <div key={fieldKey}>
              <div className="flex items-start gap-2 py-0.5 group">
                {isCollapsible && (
                  <button
                    onClick={() => toggleCollapse(fieldKey)}
                    className="mt-0.5 p-0.5 hover:bg-gray-100 rounded"
                  >
                    {isCollapsed ? (
                      <ChevronRight className="w-3 h-3 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-3 h-3 text-gray-400" />
                    )}
                  </button>
                )}
                <div className={`flex-1 min-w-0 ${!isCollapsible ? 'ml-5' : ''}`}>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">{key}:</span>
                    {renderFieldValue(key, value, fieldKey, edits, setEdits, editable)}
                  </div>
                </div>
              </div>
              {isCollapsible && !isCollapsed && (
                <div className="ml-6">
                  {renderFields(value, fieldKey, depth + 1, collapsed, toggleCollapse, edits, setEdits, editable)}
                </div>
              )}
            </div>
          )
        })}
      </div>
    )
  }

  return <span className="text-sm text-gray-900">{String(data)}</span>
}

function renderFieldValue(
  key: string,
  value: unknown,
  fieldKey: string,
  edits: Record<string, string>,
  setEdits: React.Dispatch<React.SetStateAction<Record<string, string>>>,
  editable: boolean,
): React.ReactNode {
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    const strVal = String(value)
    const isEdited = fieldKey in edits
    const currentVal = isEdited ? edits[fieldKey] : strVal

    if (editable && key !== 'raw_text') {
      return (
        <input
          type="text"
          value={currentVal}
          onChange={(e) =>
            setEdits((prev) => ({ ...prev, [fieldKey]: e.target.value }))
          }
          className={`flex-1 min-w-0 text-sm bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5 ${
            isEdited ? 'border-yellow-300 bg-yellow-50 rounded' : ''
          }`}
        />
      )
    }
    return <span className="text-sm text-gray-900">{strVal}</span>
  }
  return null
}
