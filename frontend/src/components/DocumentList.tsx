import { FileText, RefreshCw, Loader2, FileWarning } from 'lucide-react'
import type { DocumentResponse } from '../types'

interface Props {
  documents: DocumentResponse[]
  loading: boolean
  selectedId: string | null
  onSelect: (doc: DocumentResponse) => void
  onRefresh: () => void
}

const TYPE_COLORS: Record<string, string> = {
  invoice: 'bg-green-100 text-green-700',
  purchase_order: 'bg-blue-100 text-blue-700',
  contract: 'bg-purple-100 text-purple-700',
  resume: 'bg-orange-100 text-orange-700',
  unknown: 'bg-gray-100 text-gray-600',
}

const STATUS_INDICATORS: Record<string, string> = {
  uploaded: 'bg-gray-400',
  processing: 'bg-yellow-400 animate-pulse',
  extracted: 'bg-blue-400',
  validated: 'bg-yellow-400',
  reviewed: 'bg-green-400',
  failed: 'bg-red-400',
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const CONFIDENCE_COLOR = (c: number) =>
  c >= 0.8 ? 'text-green-600' : c >= 0.6 ? 'text-yellow-600' : 'text-red-600'

export default function DocumentList({ documents, loading, selectedId, onSelect, onRefresh }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200">
      <div className="p-4 border-b border-gray-100 flex items-center justify-between">
        <span className="text-sm text-gray-500">{documents.length} document{documents.length !== 1 ? 's' : ''}</span>
        <button
          onClick={onRefresh}
          className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-600 transition-colors"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 px-4">
          <FileText className="w-8 h-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-400">No documents yet</p>
          <p className="text-xs text-gray-300 mt-1">Upload a document to get started</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
          {documents.map((doc) => (
            <button
              key={doc.id}
              onClick={() => onSelect(doc)}
              className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                selectedId === doc.id ? 'bg-blue-50 border-l-2 border-l-blue-500' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  <span
                    className={`inline-block w-2 h-2 rounded-full mt-1.5 ${
                      STATUS_INDICATORS[doc.status] || 'bg-gray-300'
                    }`}
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{doc.filename}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{formatSize(doc.file_size)}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    {doc.document_type && (
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                          TYPE_COLORS[doc.document_type] || TYPE_COLORS.unknown
                        }`}
                      >
                        {doc.document_type.replace('_', ' ')}
                      </span>
                    )}
                    {doc.extraction?.confidence != null && (
                      <span className={`text-[10px] font-medium ${CONFIDENCE_COLOR(doc.extraction.confidence)}`}>
                        {Math.round(doc.extraction.confidence * 100)}%
                      </span>
                    )}
                  </div>
                </div>
                {(doc.validations?.length ?? 0) > 0 && (
                  <FileWarning className="w-4 h-4 text-yellow-400 flex-shrink-0" />
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
