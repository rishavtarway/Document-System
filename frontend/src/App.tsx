import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import DocumentList from './components/DocumentList'
import DocumentViewer from './components/DocumentViewer'
import { listDocuments, getDocTypes, healthCheck } from './api/documents'
import type { DocumentResponse } from './types'

export default function App() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([])
  const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null)
  const [docTypes, setDocTypes] = useState<{ id: string; name: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshDocs = useCallback(async () => {
    try {
      setError(null)
      const docs = await listDocuments()
      setDocuments(docs)
    } catch {
      setError('Failed to load documents. Is the backend running?')
    }
  }, [])

  useEffect(() => {
    Promise.all([
      refreshDocs(),
      getDocTypes().then(r => setDocTypes(r.types)).catch(() => {}),
      healthCheck().catch(() => {}),
    ]).finally(() => setLoading(false))
  }, [refreshDocs])

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
        <UploadZone docTypes={docTypes} onUploaded={refreshDocs} />

        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Documents</h2>
            <DocumentList
              documents={documents}
              loading={loading}
              selectedId={selectedDoc?.id ?? null}
              onSelect={setSelectedDoc}
              onRefresh={refreshDocs}
            />
          </div>
          <div className="lg:col-span-2">
            {selectedDoc ? (
              <DocumentViewer
                doc={selectedDoc}
                onUpdated={(updated) => {
                  setSelectedDoc(updated)
                  refreshDocs()
                }}
              />
            ) : (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center text-gray-400">
                <p className="text-lg">Select a document to view details</p>
                <p className="mt-1 text-sm">Upload a document first to get started</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
