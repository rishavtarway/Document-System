const BASE = '/api'

export async function uploadDocument(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function processDocument(id: string) {
  const res = await fetch(`${BASE}/documents/process/${id}`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function listDocuments() {
  const res = await fetch(`${BASE}/documents/`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getDocument(id: string) {
  const res = await fetch(`${BASE}/documents/${id}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function correctDocument(id: string, corrections: { field_path: string; corrected_value: unknown }[]) {
  const res = await fetch(`${BASE}/documents/${id}/correct`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ corrections }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function exportDocument(id: string) {
  const res = await fetch(`${BASE}/documents/${id}/export`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getDocTypes() {
  const res = await fetch(`${BASE}/types`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function healthCheck() {
  const res = await fetch(`${BASE}/health`)
  return res.json()
}
