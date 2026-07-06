export interface Document {
  id: string
  filename: string
  document_type: string | null
  type_confidence: number | null
  status: string
  file_size: number
  is_new_type: boolean
  created_at: string | null
}

export interface ExtractionField {
  id: string
  field_name: string
  extracted_value: string | null
  confidence_score: number
  needs_review: boolean
  is_gibberish: boolean
  reasoning: string | null
  alternatives: string[] | null
  corrected_value: string | null
  mcq_dialogs: MCQDialog[]
}

export interface MCQDialog {
  id: string
  question: string
  options: MCQOption[]
  context_hint: string | null
  default_selection: number
  allow_custom_input: boolean
  resolved: boolean
}

export interface MCQOption {
  id: number
  label: string
  value: string
  explanation: string
}

export interface ExtractionsResponse {
  document_id: string
  document_type: string | null
  extractions: ExtractionField[]
  review_needed: boolean
}

export interface DocumentStatus {
  document_id: string
  filename: string
  document_type: string | null
  type_confidence: number | null
  status: string
  is_new_type: boolean
  created_at: string | null
}
