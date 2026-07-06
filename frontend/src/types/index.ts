export interface DocumentResponse {
  id: string
  filename: string
  content_type: string | null
  file_size: number
  document_type: string | null
  status: string
  extraction: ExtractionResult | null
  created_at: string
  updated_at: string
}

export interface ExtractionResult {
  id: string
  document_id: string
  document_type: string
  confidence: number
  data: Record<string, unknown>
  validations: ValidationResult[]
  status: string
  created_at: string
  updated_at: string
}

export interface ValidationResult {
  field: string
  status: string
  message: string | null
  suggested_value: string | null
}

export interface CorrectionRequest {
  field_path: string
  corrected_value: unknown
}
