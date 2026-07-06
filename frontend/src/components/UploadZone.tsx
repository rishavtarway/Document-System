import { useState, useRef } from 'react'
import { Upload, File, Loader2 } from 'lucide-react'
import { uploadDocument, processDocument } from '../api/documents'

interface UploadZoneProps {
  docTypes: { id: string; name: string }[]
  onUploaded: () => void
}

export default function UploadZone({ docTypes, onUploaded }: UploadZoneProps) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    setError(null)
    setUploading(true)
    try {
      const doc = await uploadDocument(file)
      setProcessing(doc.id)
      await processDocument(doc.id)
      onUploaded()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed')
    } finally {
      setUploading(false)
      setProcessing(null)
    }
  }

  return (
    <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-8">
      <div
        className={`text-center ${dragging ? 'opacity-50' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.txt,.docx"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f) }}
        />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
            <p className="text-sm text-gray-600">
              {processing ? 'Processing document...' : 'Uploading...'}
            </p>
          </div>
        ) : (
          <>
            <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 font-medium">
              Drop a document here, or{' '}
              <button
                className="text-blue-600 hover:text-blue-700 underline"
                onClick={() => inputRef.current?.click()}
              >
                browse
              </button>
            </p>
            <p className="text-sm text-gray-400 mt-1">
              Supports PDF, PNG, JPG, TIFF, TXT, DOCX (max 20MB)
            </p>
            {docTypes.length > 0 && (
              <div className="mt-4 flex justify-center gap-4 text-xs text-gray-400">
                {docTypes.map((t) => (
                  <span key={t.id} className="flex items-center gap-1">
                    <File className="w-3 h-3" /> {t.name}
                  </span>
                ))}
              </div>
            )}
          </>
        )}
      </div>
      {error && (
        <p className="mt-3 text-sm text-red-600 text-center">{error}</p>
      )}
    </div>
  )
}
