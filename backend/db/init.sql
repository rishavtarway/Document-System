-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables for the document processing system

CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024),
    file_size INTEGER DEFAULT 0,
    content_type VARCHAR(128),
    document_type VARCHAR(100),
    type_confidence FLOAT,
    status VARCHAR(50) DEFAULT 'uploaded',
    raw_text TEXT,
    processed_data JSONB,
    is_new_type BOOLEAN DEFAULT FALSE,
    suggested_type VARCHAR(100),
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS extractions (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) REFERENCES documents(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    extracted_value TEXT,
    confidence_score FLOAT DEFAULT 0.0,
    extraction_method VARCHAR(50) DEFAULT 'ai',
    needs_review BOOLEAN DEFAULT FALSE,
    is_gibberish BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP,
    corrected_value TEXT,
    alternatives JSONB,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mcq_dialogues (
    id VARCHAR(36) PRIMARY KEY,
    extraction_id VARCHAR(36) REFERENCES extractions(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    options JSONB,
    context_hint TEXT,
    default_selection INTEGER DEFAULT 0,
    allow_custom_input BOOLEAN DEFAULT TRUE,
    user_selection INTEGER,
    user_custom_value TEXT,
    confidence_before FLOAT,
    confidence_after FLOAT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_schemas (
    id VARCHAR(36) PRIMARY KEY,
    document_type VARCHAR(100) UNIQUE NOT NULL,
    version INTEGER DEFAULT 1,
    schema_definition JSONB NOT NULL,
    extraction_prompts JSONB,
    validation_rules JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_corrections (
    id VARCHAR(36) PRIMARY KEY,
    extraction_id VARCHAR(36),
    original_value TEXT,
    corrected_value TEXT,
    field_name VARCHAR(100) NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    applied_to_model BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS extraction_patterns (
    id VARCHAR(36) PRIMARY KEY,
    document_type VARCHAR(100) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    pattern_text TEXT,
    keywords JSONB,
    position_hint VARCHAR(255),
    regex_pattern VARCHAR(512),
    confidence_boost FLOAT DEFAULT 0.1,
    success_count INTEGER DEFAULT 0,
    example_value VARCHAR(255),
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_extractions_document ON extractions(document_id);
CREATE INDEX IF NOT EXISTS idx_extractions_needs_review ON extractions(needs_review);
CREATE INDEX IF NOT EXISTS idx_mcq_resolved ON mcq_dialogues(resolved);
CREATE INDEX IF NOT EXISTS idx_patterns_type_field ON extraction_patterns(document_type, field_name);
CREATE INDEX IF NOT EXISTS idx_patterns_embedding ON extraction_patterns USING ivfflat (embedding vector_cosine_ops);

-- Seed default schemas
INSERT INTO document_schemas (id, document_type, schema_definition, extraction_prompts, validation_rules, is_active) VALUES
(
    'a0000000-0000-0000-0000-000000000001',
    'invoice',
    '{"fields": [{"name": "invoice_number", "type": "string", "required": true}, {"name": "date", "type": "date", "required": true}, {"name": "due_date", "type": "date", "required": false}, {"name": "vendor_name", "type": "string", "required": true}, {"name": "vendor_address", "type": "string", "required": false}, {"name": "customer_name", "type": "string", "required": true}, {"name": "customer_address", "type": "string", "required": false}, {"name": "line_items", "type": "array", "required": false}, {"name": "subtotal", "type": "number", "required": false}, {"name": "tax", "type": "number", "required": false}, {"name": "total", "type": "number", "required": true}, {"name": "currency", "type": "string", "required": false}, {"name": "payment_terms", "type": "string", "required": false}]}',
    '{}',
    '{}',
    TRUE
),
(
    'a0000000-0000-0000-0000-000000000002',
    'purchase_order',
    '{"fields": [{"name": "po_number", "type": "string", "required": true}, {"name": "date", "type": "date", "required": true}, {"name": "vendor_name", "type": "string", "required": true}, {"name": "vendor_address", "type": "string", "required": false}, {"name": "ship_to_address", "type": "string", "required": false}, {"name": "bill_to_address", "type": "string", "required": false}, {"name": "items", "type": "array", "required": false}, {"name": "total", "type": "number", "required": false}, {"name": "delivery_date", "type": "date", "required": false}, {"name": "payment_terms", "type": "string", "required": false}, {"name": "requisitioner", "type": "string", "required": false}]}',
    '{}',
    '{}',
    TRUE
),
(
    'a0000000-0000-0000-0000-000000000003',
    'contract',
    '{"fields": [{"name": "contract_title", "type": "string", "required": false}, {"name": "parties", "type": "array", "required": true}, {"name": "effective_date", "type": "date", "required": true}, {"name": "expiration_date", "type": "date", "required": false}, {"name": "contract_value", "type": "number", "required": false}, {"name": "governing_law", "type": "string", "required": false}, {"name": "jurisdiction", "type": "string", "required": false}, {"name": "key_terms", "type": "array", "required": false}, {"name": "termination_clause", "type": "string", "required": false}, {"name": "renewal_terms", "type": "string", "required": false}]}',
    '{}',
    '{}',
    TRUE
),
(
    'a0000000-0000-0000-0000-000000000004',
    'resume',
    '{"fields": [{"name": "candidate_name", "type": "string", "required": true}, {"name": "email", "type": "string", "required": false}, {"name": "phone", "type": "string", "required": false}, {"name": "address", "type": "string", "required": false}, {"name": "skills", "type": "array", "required": false}, {"name": "experience", "type": "array", "required": false}, {"name": "education", "type": "array", "required": false}, {"name": "certifications", "type": "array", "required": false}, {"name": "summary", "type": "string", "required": false}]}',
    '{}',
    '{}',
    TRUE
)
ON CONFLICT (document_type) DO NOTHING;
