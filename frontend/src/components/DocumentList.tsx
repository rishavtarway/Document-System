import { FileText, RefreshCw, Loader2, AlertTriangle } from 'lucide-react'

interface Props {
  documents: any[]
  loading: boolean
  selectedId: string | null
  onSelect: (id: string) => void
  onRefresh: () => void
}

const TYPE_BADGES: Record<string, string> = {
  invoice: 'bg-green-900/50 text-green-300 border border-green-700',
  purchase_order: 'bg-blue-900/50 text-blue-300 border border-blue-700',
  contract: 'bg-purple-900/50 text-purple-300 border border-purple-700',
  resume: 'bg-orange-900/50 text-orange-300 border border-orange-700',
}

const STATUS_DOT: Record<string, string> = {
  uploaded: 'bg-gray-500',
  processing: 'bg-yellow-400 animate-pulse',
  completed: 'bg-green-400',
  review_needed: 'bg-yellow-400',
  failed: 'bg-red-400',
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  return bytes < 1048576 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1048576).toFixed(1)} MB`
}

export default function DocumentList({ documents, loading, selectedId, onSelect, onRefresh }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
        <span className="text-sm text-gray-400">{documents.length} document{documents.length !== 1 ? 's' : ''}</span>
        <button onClick={onRefresh} className="p-1.5 hover:bg-gray-800 rounded-lg text-gray-500 hover:text-gray-300 transition-colors">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-10"><Loader2 className="w-6 h-6 text-blue-400 animate-spin" /></div>
      ) : documents.length === 0 ? (
        <div className="text-center py-10 px-4">
          <FileText className="w-8 h-8 text-gray-600 mx-auto mb-2" />
          <p className="text-sm text-gray-500">No documents yet</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-800 max-h-[500px] overflow-y-auto">
          {documents.map(doc => (
            <button
              key={doc.id}
              onClick={() => onSelect(doc.id)}
              className={`w-full text-left px-4 py-3 hover:bg-gray-800/50 transition-colors ${
                selectedId === doc.id ? 'bg-blue-900/30 border-l-2 border-l-blue-500' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <span className={`inline-block w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${STATUS_DOT[doc.status] || 'bg-gray-500'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-200 truncate">{doc.filename}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{formatSize(doc.file_size)}</p>
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    {doc.document_type && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                        TYPE_BADGES[doc.document_type] || 'bg-gray-800 text-gray-400 border border-gray-700'
                      }`}>
                        {doc.document_type.replace('_', ' ')}
                      </span>
                    )}
                    {doc.type_confidence != null && (
                      <span className={`text-[10px] font-medium ${
                        doc.type_confidence >= 0.8 ? 'text-green-400' : doc.type_confidence >= 0.5 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {Math.round(doc.type_confidence * 100)}%
                      </span>
                    )}
                    {doc.status === 'review_needed' && (
                      <AlertTriangle className="w-3 h-3 text-yellow-400" />
                    )}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
