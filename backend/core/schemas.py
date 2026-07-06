from __future__ import annotations

import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class DocumentType(str, Enum):
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"
    CONTRACT = "contract"
    RESUME = "resume"
    UNKNOWN = "unknown"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    REVIEWED = "reviewed"
    FAILED = "failed"


class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None
    sku: Optional[str] = None


class InvoiceData(BaseModel):
    invoice_number: str
    date: Optional[date] = None
    due_date: Optional[date] = None
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    total: Decimal
    currency: str = "USD"
    payment_terms: Optional[str] = None


class PurchaseOrderItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None
    sku: Optional[str] = None


class PurchaseOrderData(BaseModel):
    po_number: str
    date: Optional[date] = None
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    ship_to_address: Optional[str] = None
    bill_to_address: Optional[str] = None
    items: list[PurchaseOrderItem] = Field(default_factory=list)
    total: Optional[Decimal] = None
    delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    requisitioner: Optional[str] = None


class ContractParty(BaseModel):
    name: str
    role: Optional[str] = None


class ContractData(BaseModel):
    contract_title: Optional[str] = None
    parties: list[ContractParty] = Field(default_factory=list)
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    contract_value: Optional[Decimal] = None
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    key_terms: list[str] = Field(default_factory=list)
    termination_clause: Optional[str] = None
    renewal_terms: Optional[str] = None


class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None


class ResumeData(BaseModel):
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    summary: Optional[str] = None


class ValidationResult(BaseModel):
    field: str
    status: str  # passed, warning, error
    message: Optional[str] = None
    suggested_value: Optional[str] = None


class ExtractionResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    document_type: DocumentType
    confidence: float = Field(ge=0.0, le=1.0)
    data: dict
    validations: list[ValidationResult] = Field(default_factory=list)
    status: DocumentStatus = DocumentStatus.EXTRACTED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: Optional[str] = None
    file_size: int
    document_type: Optional[DocumentType] = None
    status: DocumentStatus
    extraction: Optional[ExtractionResult] = None
    created_at: datetime
    updated_at: datetime


class CorrectionRequest(BaseModel):
    field_path: str
    corrected_value: str | int | float | bool | list | dict | None


class CorrectionBatch(BaseModel):
    corrections: list[CorrectionRequest]
