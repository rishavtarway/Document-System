import { useState, useRef } from 'react'
import { Upload, File, Loader2, Sparkles } from 'lucide-react'
import { uploadDocument, processDocument } from '../services/api'

interface UploadZoneProps {
  docTypes: { id: string; name: string }[]
  onUploaded: () => void
}

export default function UploadZone({ docTypes, onUploaded }: UploadZoneProps) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    setError(null)
    setUploading(true)
    try {
      const doc = await uploadDocument(file)
      await processDocument(doc.document_id)
      onUploaded()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-gray-900 border-2 border-dashed border-gray-700 rounded-xl p-6">
      <div
        className={`text-center transition-opacity ${dragging ? 'opacity-60' : ''}`}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif"
          onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }}
        />
        {uploading ? (
          <div className="flex flex-col items-center gap-2 py-4">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            <p className="text-sm text-gray-400">Processing document with AI...</p>
          </div>
        ) : (
          <>
            <div className="flex justify-center mb-2">
              <div className="w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center">
                <Upload className="w-6 h-6 text-blue-400" />
              </div>
            </div>
            <p className="text-gray-300 font-medium">
              Drop a document here or{' '}
              <button
                className="text-blue-400 hover:text-blue-300 underline"
                onClick={() => inputRef.current?.click()}
              >
                browse
              </button>
            </p>
            <p className="text-xs text-gray-500 mt-1">
              PDF, PNG, JPG, TIFF (up to 20MB)
            </p>
            {docTypes.length > 0 && (
              <div className="mt-3 flex justify-center gap-3 text-xs text-gray-500">
                {docTypes.map(t => (
                  <span key={t.id} className="flex items-center gap-1 bg-gray-800 px-2 py-1 rounded-full">
                    <Sparkles className="w-3 h-3 text-blue-400" />
                    {t.name}
                  </span>
                ))}
              </div>
            )}
          </>
        )}
      </div>
      {error && <p className="mt-2 text-sm text-red-400 text-center">{error}</p>}
    </div>
  )
}
