from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

from core.validator import FieldValidator, validate_extraction
from core.schemas import ValidationResult


class TestFieldValidator:
    def test_valid_email(self):
        assert FieldValidator.validate_email("user@example.com")
        assert FieldValidator.validate_email("a.b@c.co")
        assert not FieldValidator.validate_email("not-an-email")
        assert not FieldValidator.validate_email("@domain.com")

    def test_valid_phone(self):
        assert FieldValidator.validate_phone("+1234567890")
        assert FieldValidator.validate_phone("123-456-7890")
        assert FieldValidator.validate_phone("(555) 123-4567")
        assert not FieldValidator.validate_phone("abc")

    def test_valid_date(self):
        assert FieldValidator.validate_date("2024-01-15")
        assert FieldValidator.validate_date("01/15/2024")
        assert FieldValidator.validate_date("15/01/2024")
        assert not FieldValidator.validate_date("not-a-date")
        assert not FieldValidator.validate_date("13-13-2024")

    def test_valid_number(self):
        assert FieldValidator.validate_number(42)
        assert FieldValidator.validate_number("42.5")
        assert not FieldValidator.validate_number("abc")


class TestInvoiceValidation:
    def test_missing_required_fields(self):
        data = {"total": 100.0}
        results = validate_extraction("invoice", data)
        required_errors = [r for r in results if r.status == "error"]
        assert any("invoice_number" in r.field for r in required_errors)

    def test_invalid_date_format(self):
        data = {"invoice_number": "INV-001", "total": 100, "date": "not-a-date", "vendor_name": "Acme"}
        results = validate_extraction("invoice", data)
        date_warnings = [r for r in results if r.field == "date" and r.status == "warning"]
        assert len(date_warnings) > 0

    def test_negative_total_warning(self):
        data = {"invoice_number": "INV-001", "total": -50, "vendor_name": "Acme"}
        results = validate_extraction("invoice", data)
        neg_warnings = [r for r in results if "Negative" in (r.message or "")]
        assert len(neg_warnings) > 0

    def test_subtotal_total_mismatch(self):
        data = {
            "invoice_number": "INV-001",
            "total": 100,
            "subtotal": 500,
            "vendor_name": "Acme",
        }
        results = validate_extraction("invoice", data)
        mismatch = [r for r in results if r.field == "total" and r.status == "warning"]
        assert len(mismatch) > 0


class TestContractValidation:
    def test_missing_parties(self):
        data = {"effective_date": "2024-01-01"}
        results = validate_extraction("contract", data)
        party_errors = [r for r in results if "parties" in r.field]
        assert len(party_errors) > 0


class TestResumeValidation:
    def test_missing_name(self):
        data = {"skills": ["Python"]}
        results = validate_extraction("resume", data)
        name_errors = [r for r in results if "candidate_name" in r.field]
        assert len(name_errors) > 0
