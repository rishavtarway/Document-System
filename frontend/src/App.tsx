import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import DocumentList from './components/DocumentList'
import DocumentViewer from './components/DocumentViewer'
import { listDocuments, getDocTypes } from './services/api'

export default function App() {
  const [documents, setDocuments] = useState<any[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [docTypes, setDocTypes] = useState<{ id: string; name: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshDocs = useCallback(async () => {
    try {
      setError(null)
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (e) {
      setError('Failed to load documents. Ensure the backend is running.')
    }
  }, [])

  useEffect(() => {
    Promise.all([
      refreshDocs(),
      getDocTypes().then(r => setDocTypes(r.types)).catch(() => {}),
    ]).finally(() => setLoading(false))
  }, [refreshDocs])

  return (
    <div className="min-h-screen bg-gray-950">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded-lg text-red-200 text-sm">
            {error}
          </div>
        )}
        
        <UploadZone docTypes={docTypes} onUploaded={refreshDocs} />
        
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <DocumentList
              documents={documents}
              loading={loading}
              selectedId={selectedId}
              onSelect={setSelectedId}
              onRefresh={refreshDocs}
            />
          </div>
          <div className="lg:col-span-2">
            {selectedId ? (
              <DocumentViewer
                documentId={selectedId}
                onUpdated={refreshDocs}
              />
            ) : (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
                <div className="text-gray-500 text-lg">Select a document to view details</div>
                <p className="text-gray-600 text-sm mt-2">Upload a document first to get started</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
