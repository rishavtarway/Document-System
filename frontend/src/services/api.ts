const BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  return res.json()
}

export async function uploadDocument(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function processDocument(id: string) {
  return request<any>(`${BASE}/documents/${id}/process`, { method: 'POST' })
}

export async function getDocumentStatus(id: string) {
  return request<any>(`${BASE}/documents/${id}/status`)
}

export async function getExtractions(id: string) {
  return request<any>(`${BASE}/documents/${id}/extractions`)
}

export async function submitCorrection(
  documentId: string,
  corrections: { extraction_id: string; corrected_value: string; selected_mcq_option?: number }[]
) {
  return request<any>(`${BASE}/documents/${documentId}/corrections`, {
    method: 'POST',
    body: JSON.stringify({ corrections }),
  })
}

export async function exportDocument(id: string) {
  return request<any>(`${BASE}/documents/${id}/export`)
}

export async function listDocuments() {
  return request<any[]>(`${BASE}/documents`)
}

export async function getDocTypes() {
  return request<any>(`${BASE}/types`)
}

export async function healthCheck() {
  return request<any>(`${BASE}/health`)
}
